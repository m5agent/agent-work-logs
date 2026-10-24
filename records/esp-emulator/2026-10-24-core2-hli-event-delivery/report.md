# ESP Emulator Core2 HLI 真实 HCI Event 交付报告

## 背景

Core2 stock UIFlow2 使用 `CONFIG_BTDM_CTRL_HLI=1`。此前已经证明 QEMU 能向
firmware `g_rw_schd_queue` 和 meta queue 写入 event-13 work item，并由
guest HLI ISR/controller task 消费。但当时 callback 只是 `ets_printf`
marker，只能证明队列 seam，不能证明 HCI 数据面。

本次目标是交付一个真实 HCI event，并要求 guest 根据该 event 发出下一条
controller command。

## 实现

### 事件缓冲区

- 使用 guest `ble_transport_alloc_evt(0)`，buffer 由 NimBLE event pool
  管理，并在 host 消费后回收；
- 写入 `0e0401030c00`，即 HCI Command Complete / Reset；
- 不写 H4 type byte；
- 固定 pool entry 大小为 70 bytes。

### HLI 交付

QEMU 完成以下步骤：

1. 读取 `s_meta_queue_ptr` 和 `g_rw_schd_queue`；
2. 校验 `hli_queue_t` 动态地址和 element size；
3. 分配并填写 `{argument, callback}` control work item；
4. 将 8-byte event-13 item 写入 controller queue；
5. 将 queue handle 写入 4-byte meta queue；
6. 设置 `INTSET[29]`；
7. firmware `queue_isr_handler` 将事件送入 controller task，后者调用
   `ble_transport_to_hs_evt_impl(event_buffer)`。

同时修正：

- `hli-consumed` 不再错误地比较 meta queue 与主 queue end；
- VHCI H2C length 字段的非最终写入单独记录为
  `h2c-incomplete-writes`，不再误报 malformed packet。

## 复现

```bash
python3 tests/uiflow2/core2_native_hci/test_hli_event.py \
  --image /path/to/stock/core2-uiflow2.bin
```

测试要求：

- peer 收到 `01030c00`；
- guest 发下一条 command `01011000`；
- `hli-posts=1`、`hli-consumed=1`、`hli-event-buffers=1`；
- `hli-errors=0`；
- HLI/meta queue depth 归零；
- malformed/dropped packet 为 0；
- guest 无 panic/assert；
- QEMU clean shutdown。

连续五次结果：

```text
run 1  PASS  01030c00 -> 01011000  posts=1 consumed=1 errors=0
run 2  PASS  01030c00 -> 01011000  posts=1 consumed=1 errors=0
run 3  PASS  01030c00 -> 01011000  posts=1 consumed=1 errors=0
run 4  PASS  01030c00 -> 01011000  posts=1 consumed=1 errors=0
run 5  PASS  01030c00 -> 01011000  posts=1 consumed=1 errors=0
```

## 后续实验边界

之后尝试把 API-boundary H2C bypass 与动态多 event/ACL HLI 交付合并。该实验
可以完成 Reset 和 Read Local Version 的往返，但 host 在后续 command
complete 后没有稳定发出 next command；强制 controller work item 还会触发
controller task 的 cache-disabled。实验代码未保留，QEMU 树已恢复到可重放的
HLI event 5/5 状态。

因此下一阶段仍需要：

- ACL mbuf append/free 与 flow control；
- matching controller ACK；
- API-boundary H2C 和 HLI C2H 的显式 transaction；
- complete Bumble NUS GATT；
- Device Service 5/5。

## 验证

```text
HLI real event                          5/5 PASS
platform tests                          267/267 PASS
runtime coverage                        PASS
peripheral catalog                      PASS
QEMU profiles                           PASS
GitHub Actions 40044998540              PASS
patch forward/reverse apply-check       PASS
physical hardware                       NOT RUN
```

## 风险与回滚

回滚源码 `acd5329c4fecb23d7ac2cb1e5dd6dcf370c673f5` 可移除 HLI event patch、
测试和 evidence，恢复此前 marker-only 状态。不会修改固件、ROM 或物理设备。
