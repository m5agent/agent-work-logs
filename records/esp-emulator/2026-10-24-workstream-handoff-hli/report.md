# ESP Emulator 工作流交接与 Core2 HLI 诊断报告

## 背景

项目已连续推进网络策略、FirmwareManifest/WebBurner、多设备 unified runtime
和 Core2 native HCI。主状态页虽持续更新，但同一阶段事实仍散落在 README、
工作流台账、Backlog、代码地图、网络方案、QEMU 矩阵、统一运行时专题页和
测试 README。读者很难快速判断：

1. 哪些能力已有同路径 evidence；
2. 哪些只是诊断性 spike；
3. 现在最短的下一步是什么；
4. 代码热点和未完成 workstream 在哪里。

本轮目标是完成一次可交接的代码与文档重整，并把最新的 HLI queue 诊断按
真实边界归档。

## 结论

### P0 网络

单机 namespace、controlled DNS、TLS/Host allowlist、exact IPv4 egress、
veth/NAT、pcap、错误密码、radio/AP 恢复、DHCP renewal、双 guest lab fabric
和本地 worker lifecycle 已有虚拟设备证据。仍需远程 worker、活动 QEMU
re-attach 和外部 IPv6。

### P0 Core2

stock native-VHCI → Bumble 的完整外部 NUS GATT 已在 standalone 和同 guest
unified 路径通过，但 Device Service 仍依赖 GDB 控制面，重复 lease 只能
`1/2`。QEMU native-HCI 的 transport、首包 H2C、诊断性单包 C2H 和 API
boundary 审计都已完成各自窄门禁，但 `HCI-3b` 仍未闭合。

最新 HLI 诊断确认固件启用了 `CONFIG_BTDM_CTRL_HLI=1`，QEMU 可以写入
`g_rw_schd_queue`/meta queue 并置 `INTSET[29]`。guest 串口随后输出预期的
queue-full marker，QOM 无 HLI error，HLI/meta queue depth 都归零。这说明
guest HLI ISR 和 controller task 消费了 QOM 投递项，提供了后续 C2H 的设备/
IRQ 交付 seam。

该实验只把 event 13 指向 `ets_printf`：

- 没有投递 HCI Reset Complete；
- 没有 ACL buffer、append/free、ACK 或 flow-control；
- 没有 GATT transaction；
- `hli-consumed` 观察计数存在比较 bug，不能引用；
- 实验代码未保留，无法从当前提交直接复现。

因此 `HCI-3b` 仍为 `OPEN`。下一最小交付是使用 guest
`ble_transport_alloc_evt(0)` 分配的 event buffer 和
`ble_transport_to_hs_evt_impl` callback，经 HLI event 13 投递真实 Reset
Complete；随后调查 `ble_transport_alloc_acl_from_ll` /
`ble_transport_to_hs_acl_impl` 的 mbuf 生命周期，再结合 API-boundary H2C
transaction。

### P0 固件审查

Manifest、WebBurner/M5Burner/ESP-IDF 导入、浏览器可恢复上传、静态审查、
安全配置分层、SBOM 和 LittleFS/FAT12/16/32/SPIFFS 清单已有实现与证据。
运行时权限/许可策略、真机 key/eFuse 闭环和跨厂商回归仍开放。

## 代码整理

本轮没有进行高风险的大型拆分。`platform/tools/device_service.py` 仍是 7610
行编排热区，`test_device_service.py` 4138 行，外设矩阵 2874 行；拆分顺序与
契约门禁继续由 `SVC-03` 管理。

完成的低风险代码卫生修正：

- 移除 `generate_catalog.py`、`peripheral_inventory.py` 和测试中的未使用导入；
- 移除 `network_fabric.py` 未使用的 loop 变量；
- 移除 `qemu_network_preflight.py` 未使用的 `details`；
- 保留 ELF section-name table 的读取校验，但不保存未使用返回值。

Ruff 的未使用导入、未定义/重复名和未使用局部变量规则在当前
`platform/tools`、`platform/tests` 上全部通过。

## 验证

```text
platform tests                         267/267 PASS
GitHub Actions platform-contracts       PASS
GitHub Actions network-namespace-policy PASS
Node WebBurner unit tests              2/2 PASS
runtime coverage                       PASS
peripheral catalog                     PASS
QEMU profiles                          PASS
documentation contracts                PASS
Python compileall                      PASS
Ruff F401/F821/F822/F823/F841          PASS
JSON parse                             PASS
git diff --check                       PASS
```

源码已推送：

```text
base    7d274bcf3b8f7759f4d0d721bd6b234f6a67a928
result  543f900225457c6b7cbd03f30a3ef01844119359
CI      40044278162 (success)
```

## 验证边界

- 本次未重跑 QEMU 67-case 全矩阵，引用既有 `67/67`、`274/274` evidence；
- 本次未重跑网络 namespace、TLS、Core2 BLE 或文件系统功能测试；
- HLI 只证明 guest 消费 event-13 marker，不证明 HCI/GATT；
- 物理硬件、RF、功耗、声学、光学、机械和电气等价性均为 `NOT RUN`；
- 由于 HLI 实验代码未保留，该 evidence 是诊断归档，不是可重放测试。

## 风险与回滚

源码回滚提交 `543f900225457c6b7cbd03f30a3ef01844119359` 会恢复旧状态页、
工作台账、HCI 描述、6 个未使用变量和旧文档契约；不会改变已构建 QEMU、
固件、Device Service 数据或物理设备。
