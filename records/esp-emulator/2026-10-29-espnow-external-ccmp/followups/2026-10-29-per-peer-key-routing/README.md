# ESP Emulator ESP-NOW per-peer LMK routing

- 日期：`2026-10-29`
- 结果：`PASS`（限定 pairwise-LMK virtual-device routing）
  / `PARTIAL`（`RUNTIME-06` 总体）
- 工作类型：`code_change`
- 问题来源：`RUNTIME-06` 的 peer→LMK routing 和错误 peer-key 负控
- Base：[m5stack-esp-emulator@75d66458](https://github.com/m5agent/m5stack-esp-emulator/commit/75d66458a4e658abbdba945fc24da0fea2c4eb64)
- 功能提交：[m5stack-esp-emulator@fb4845e8](https://github.com/m5agent/m5stack-esp-emulator/commit/fb4845e8)
- 文档/快照：[m5stack-esp-emulator@be09ca89](https://github.com/m5agent/m5stack-esp-emulator/commit/be09ca89f2fe9a415568ee572557ce50fc193796)
- 环境：macOS arm64；QEMU virtual device；stock UIFlow2 `v2.5.3`

## 结论

`0082` 从 stock controller key entry 的 metadata 读取 peer MAC，并按
receiver/transmitter peer 选择 guest LMK。三个不同 pairwise LMK 覆盖三条
undirected link 的六个方向，全部交付；只把 B 对 A 的 LMK 错接到 B-C 后，
broker 仍转发全部路径，但 A↔B 双向归零，A↔C/B↔C 保持。direct
guest-key pair 和三 guest shared-LMK fabric 回归也通过。

全部为 **virtual-device validation**。该结果关闭 `RUNTIME-06` 的
per-peer LMK routing 和错误 peer-key fail-closed 路径。PN wrap、
loss/retry、channel/rate、bit-exact controller、RF、电气和真机仍
`NOT RUN`。

## 关键证据

- 匹配 ELF：stock `wDev_Insert_KeyEntry` 把 6-byte peer address 写入
  descriptor；`hal_crypto_set_key_entry` 把 peer MAC 放在 entry `0..5`，
  LMK 放在 `8..23`。
- QEMU SHA256：`9c36bb527f441b65acc16aff09728ae66e98ea19957a42fbc8bc087d52c9e5e0`
- `0082` patch SHA256：`5405d62fe3e4b6fff9cd1b41129b32d296a56b8a288e927ac19e1770acb88a6c`
- runner SHA256：`642522e681f23a8fc2c8c6ccf41c1802ebc029b59ecdac39c72e6f049cef44f0`
- pairwise 正控：三端 slots `23`、`24`，`guest_key_ready=2`，六方向 PASS
- B/A cross-wire：A/B 对错误 peer 的 source/payload match 均为 `0`，
  A-C/B-C 保持；A/B peer-key/CCMP failure 为 `470/472`，C 为 `0`
- shared-LMK 和 direct guest-key 回归 PASS
- 11 个 session 全部 `purge=0`、stopped、PID gone、history retained
- ESP-NOW contracts：`47/47 PASS`
- platform tests：`1506 OK + 1 skipped`
- GitHub CI：[40819478506](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40819478506)：
  `platform-contracts` 与 `network-namespace-policy` 均 PASS
- 主仓证据：[per-peer key](https://github.com/m5agent/m5stack-esp-emulator/blob/be09ca89f2fe9a415568ee572557ce50fc193796/docs/evidence/2026-10-29-espnow-per-peer-key-routing/README.md)

## 文件

- `report.md`：ELF 依据、路由设计、正负控、边界和回滚
- `run.json`：机器可读记录
- `evidence/summary.json`：脱敏 machine summary
- `evidence/patch-check.txt`：forward/current/reverse patch 验证
- `patches/0001-esp32-espnow-per-peer-key-routing.patch`：`0082` 原样 patch
- `patches/README.md`：patch 与 preimage 校验说明

## 未覆盖项

- PN wrap；
- loss/retry；
- channel/rate；
- bit-exact controller；
- RF、antenna、电气、timing 和 physical hardware。
