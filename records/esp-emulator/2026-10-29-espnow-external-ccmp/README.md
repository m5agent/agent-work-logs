# ESP Emulator external ESP-NOW key-bound CCMP

- 日期：`2026-10-29`
- 结果：`PASS`（限定 key-fixture controller AES-CCMP）/ `PARTIAL`（`RUNTIME-06` 总体）
- 工作类型：`code_change`
- 问题来源：`RUNTIME-06` 中 external peer 加密、错误 LMK 和 key 泄漏边界
- Base：[m5stack-esp-emulator@ee15f761](https://github.com/m5agent/m5stack-esp-emulator/commit/ee15f7614f822dce7178188a89d57a0333b71f2a)
- 结果提交：[m5stack-esp-emulator@82118424](https://github.com/m5agent/m5stack-esp-emulator/commit/82118424bca82266041015480ef32b5920c205da)
- 环境：macOS arm64；QEMU virtual device；stock UIFlow2 `v2.5.3`；
  trusted-local Device Service fixture

## 结论

`0077` 在 external ESP-NOW bridge 边界加入真实 AES-CCMP/MIC。PMK 以
AES-128-ECB wrap LMK，controller state 不保存 plaintext LMK；TX 去掉
guest hardware envelope 后使用新 PN/8-byte MIC，RX 在正常 DMA 注入前验证
MIC，失败帧直接丢弃。

StopWatch↔StickS3 完成 plaintext、encrypted、wrong-LMK 和
wrong-PMK/same-LMK；Core2↔StopWatch 完成 encrypted 和 wrong-LMK。
正确 key 均双向收到对方 payload，错误 LMK 的所有方向均为
`EXPECTED_DROP` 且 `rx_packets=0`。PMK/LMK 已从 API snapshot 和 persisted
session JSON 脱敏。

该结果关闭 key-fixture controller CCMP 正负控，但 `RUNTIME-06` 仍为
`PARTIAL`，因为 guest `set_pmk`/`add_peer` key-state 传播、key rotation、
peer lifecycle、replay、loss/retry、RF 和真机尚未完成。

## 关键证据

- QEMU SHA256：`5340171ca484ce7ee3b13a0538a35c5f22fcd3a2ff726fa7a902424ff4d7d179`
- `0077` patch SHA256：`4a0aa4fa4d92ddf00d02e62136c4bc881b4a5b6e73edeb78a835feb94a74e095`
- runner SHA256：`8c1530688da51bd4a3d7c5730af90462fd92282128c0ad9bf4b7bdbc191f96d0`
- 12 个独立 session 路径；正确 key 双向交付，wrong-LMK 全方向
  `EXPECTED_DROP`，wrong-PMK/same-LMK 按 ESP-NOW 语义 PASS
- platform tests：`1470 OK + 1 skipped`
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  PASS
- GitHub CI：[40808027140](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40808027140)，
  `platform-contracts` 与 `network-namespace-policy` 均 PASS
- 主仓证据：[external ESP-NOW CCMP](https://github.com/m5agent/m5stack-esp-emulator/blob/82118424bca82266041015480ef32b5920c205da/docs/evidence/2026-10-29-espnow-external-ccmp/README.md)

## 文件

- `report.md`：实现、失败控制、执行、验证边界和回滚
- `run.json`：机器可读记录
- `evidence/summary.json`：脱敏 machine summary
- `evidence/patch-check.txt`：patch forward/current/reverse 验证
- `patches/0001-esp32-espnow-external-ccmp.patch`：`0077` 原样 patch
- `patches/README.md`：preimage 与 patch 校验说明
- [follow-up：single-peer CCMP replay drop](followups/2026-10-29-ccmp-replay/)：
  `0078` authenticated PN guard 与真实 UDP replay proxy 负控
- [follow-up：64-frame CCMP replay window](followups/2026-10-29-ccmp-replay-window/)：
  `0079` bounded reorder window、duplicate 负控和 Core2 回归
- [follow-up：stock guest key-state](followups/2026-10-29-guest-key-state/)：
  `0080` classic/S3 controller key store、wrong-LMK 和 key rotation
- [follow-up：three-guest shared-LMK fabric](followups/2026-10-29-peer-fabric/)：
  `0081` 三 guest source-peer routing、8×64 replay state 和精确 replay 负控
- [follow-up：per-peer LMK routing](followups/2026-10-29-per-peer-key-routing/)：
  `0082` stock key-entry peer metadata、pairwise LMK 选择和 cross-wire 负控

## 未覆盖项

- guest key-state、peer lifecycle、replay、shared-LMK fabric 和 per-peer
  LMK routing 已由上述 follow-up 分别覆盖，本记录不反填这些结果；
- PN wrap、loss/retry、channel/rate、bit-exact controller；
- RF、antenna、AP coexistence、电气、timing 和 physical hardware。

以上均不继承本次 virtual-device PASS。
