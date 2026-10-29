# ESP Emulator external ESP-NOW plaintext peers

- 日期：`2026-10-29`
- 结果：`PASS`（限定两个独立 guest 的未加密 action-frame exchange）/ `PARTIAL`（`RUNTIME-06` 总体）
- 工作类型：`code_change`
- 问题来源：`RUNTIME-06` 中“外部 ESP-NOW peer 未建模”的剩余缺口
- 源码版本：[m5stack-esp-emulator@32213028](https://github.com/m5agent/m5stack-esp-emulator/commit/322130288ea4fb2c2aab49b689e232bb2beef7f7)
- 结果提交：[m5stack-esp-emulator@38a7e8be](https://github.com/m5agent/m5stack-esp-emulator/commit/38a7e8be606aa0d0ca8d8b75aae62773dc520710)
- 环境：macOS arm64；QEMU virtual device；stock UIFlow2 `v2.5.3`；
  两个独立 Device Service session

## 结论

`0076` 新增默认关闭的 external peer bridge，用成对的 host-local UDP
fixture 连接两个独立 controller。guest 的 action frame 仍从正常
controller TX DMA 发出，peer frame 仍通过目标 controller 的正常 RX DMA
注入；Python host 不合成 payload 或 callback。

StopWatch↔StickS3 与 Core2↔StopWatch 两对独立 guest 均完成双向明文
exchange，source MAC 与 role payload 全部匹配。四个 session 均保留
evidence，使用 `purge=0` 停止，并确认 QEMU PID 消失。

该结果关闭“两个独立 guest 的未加密 action-frame exchange”里程碑，
但不关闭 PMK/LMK/CCMP、错误 key、完整 peer 生命周期、RF 或真机验证。

## 关键证据

- QEMU SHA256：`df0e20f176494a9de8e32361dbc865688c5e72791207793d0bdb0b5a947b616a`
- `0076` patch SHA256：`de39dd922d15bc2ad3827a13293d86dc2a2f0dafcfe2036783730dfab8037c62`
- StopWatch↔StickS3：双方分别收到 `57/57` 与 `58/58` 个匹配 payload
- Core2↔StopWatch：双方分别收到 `14/14` 与 `44/44` 个匹配 payload
- platform tests：`1440` 项，`OK (skipped=10)`
- GitHub CI：[40804667393](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40804667393)，
  `platform-contracts` 与 `network-namespace-policy` 均 PASS
- 主仓证据：[external ESP-NOW peer](https://github.com/m5agent/m5stack-esp-emulator/blob/38a7e8be606aa0d0ca8d8b75aae62773dc520710/docs/evidence/2026-10-29-espnow-external-peer/README.md)

## 文件

- `report.md`：实现、执行、证据、边界和回滚
- `run.json`：机器可读记录
- `evidence/summary.json`：脱敏 machine summary
- `patches/0001-esp32-external-espnow-peer-bridge.patch`：`0076` 原样 patch
- `code/`：不适用；可重建 runner 已随主仓提交

## 未覆盖项

- PMK/LMK、CCMP、错误 key 和加密 payload；
- peer add/update/delete、replay、loss/retry 和完整生命周期；
- 多于两个 peer 的 fabric、channel/rate、bit-exact controller；
- RF、天线、AP 共存、电气时序及物理硬件同路径验证。

以上均为 `NOT RUN`；本次结论是 `virtual-device validation`。
