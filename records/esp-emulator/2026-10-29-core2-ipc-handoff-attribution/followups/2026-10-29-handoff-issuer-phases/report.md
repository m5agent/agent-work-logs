# ESP Emulator Core2 handoff issuer and IPC phases 报告

## 背景

- 来源：`RUNTIME-03`，PR
  [#44](https://github.com/m5agent/m5stack-esp-emulator/pull/44)。
- 前序：正常 WDT 在 reset 前存在约 12.6k 次 handoff，CPU0 累计 wait
  约占 57% 预算。
- 目标：确认重复成本来自 Flash 数据量、具体命令，还是 IPC/handoff 固定
  延迟。

## 结论

issuer/episode 关联和无 issuer episode 都约需 `0.86-0.89 ms`，所以 64-byte
read 的数据长度不是主成本。initiator 内部 phase split 把主要时间定位到
`esp_ipc_call` source-shape 往返：约 `615.595 us`。

这支持下一步研究跨核 IPC 的调度/wakeup 路径，而不是继续调整 SSI 传输或
只扩大 read 长度。

## 改动范围

本次只增加默认关闭的 BIN-bound issuer/phase 诊断说明和 evidence，没有修改
guest、QEMU controller、WDT、RR quantum 或 peripheral 路径。两个负控实验
未保留为补丁。

## 执行

- QEMU WiFi Device Service 会话；
- `icount shift=5`；
- normal WDT；
- 默认关闭的 contended-CAS candidate 用于匹配当前 RUNTIME-03 lane；
- issuer correlation 30 秒 wall-time；
- initiator phase split 10 秒 wall-time；
- 额外 `100 us` quantum 和 immediate-yield 50 秒负控。

## 结果

issuer 分组：

| 内容 | 数量 | mean | p50 | max |
| --- | ---: | ---: | ---: | ---: |
| 1 fast read + 1 status | `6,806` | `860.591 us` | `891.776 us` | `1.1048 ms` |
| 无 fast/status issuer | `1,342` | `888.354 us` | `887.904 us` | `4.750784 ms` |
| 仅 status | `48` | `894.786 us` | `888.832 us` | `1.020256 ms` |

initiator mean phases：

| phase | mean |
| --- | ---: |
| prepare → IPC return | `615.595 us` |
| can_start poll exit | `2.181 us` |
| vTaskSuspendAll source shape | `1.322 us` |
| priority change source shape | `34.083 us` |
| first cache-disable source shape | `101.104 us` |
| second cache-disable source shape | `52.053 us` |
| block wait → complete | `63.733 us` |

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | QEMU diagnostic build 与 PC trace |
| transport | PASS | 真实 Device Service/QEMU 串口和 frame |
| device_response | PASS | PC/issue/handoff 关联 |
| data_behavior | PARTIAL | 预算已归因，启动仍失败 |
| visual_or_physical | NOT RUN | 黑帧且无硬件测量 |

平台文档/index/snapshot contracts 与 CI 两个 platform job、两个 network
policy job 均 PASS。PR merge
`3788aeaedc7de9566ac45a15092f133122f82d8a`。

## 验证边界

PC 与函数名是 BIN/source-shape，不是 exact linker symbol。结果不证明物理
cache/Flash timing。`100 us` 与 immediate-yield 负控没有保留代码，不能作为
可继承修复。

## 风险与回滚

仅文档/evidence 变更，回滚 merge 即可；没有持久设备或数据变更。
