# ESP Emulator ESP-NOW CCMP PN exhaustion and rekey

- 日期：`2026-10-29`
- 结果：`PASS`（限定 48-bit virtual CCMP PN lifecycle）
  / `PARTIAL`（`RUNTIME-06` 总体）
- 工作类型：`code_change`
- 问题来源：`RUNTIME-06` 的 PN wrap、same-key 重写和 new-key recovery
- Base：[m5stack-esp-emulator@be09ca89](https://github.com/m5agent/m5stack-esp-emulator/commit/be09ca89f2fe9a415568ee572557ce50fc193796)
- 功能提交：[m5stack-esp-emulator@b6b3c603](https://github.com/m5agent/m5stack-esp-emulator/commit/b6b3c603)
- 文档/快照/契约修复：[m5stack-esp-emulator@8f9f7439](https://github.com/m5agent/m5stack-esp-emulator/commit/8f9f7439)
- 环境：macOS arm64；QEMU virtual device；stock UIFlow2 `v2.5.3`

## 结论

`0083` 在 CCMP transmit PN 达到 48-bit 上限时 fail closed，不把 PN 回绕
到 zero。StopWatch↔StickS3 通过真实 encrypted barrier 后发送 128 个 burn
frame，双方均记录 PN exhaustion；安装新 LMK 后 PN 从 zero 重启并恢复
双向 payload。

same-LMK 负控确认只重写相同 key 不会清 PN/replay，也不会恢复 payload。
实现只在 peer metadata 或 LMK 实际变化时重置该 slot。shared-LMK、
pairwise-LMK 和 cross-wire 回归均通过。

全部为 **virtual-device validation**。loss/retry、channel/rate、
bit-exact controller、RF、电气和真机仍 `NOT RUN`。

## 关键证据

- QEMU SHA256：`1f3bb7dbbf4b2b32f29e065c02dbe20f08188518c01bd39ec5eb00c724574262`
- `0083` patch SHA256：`3e9d54b16b0ec3429347bb9d36efe96755935e2cff3d045cf3af3b0b82adcfa9`
- runner SHA256：`1105cf71e09c3ba2ae69f77fdcdba2a53eea6ba1dfb09cf3ad608e32f513d9db`
- new-LMK：StopWatch/StickS3 exhaustion `65/65`，post payload `164/163`
- same-LMK：双方 exhaustion `183/183`，post payload `0/0`
- shared-LMK、pairwise 正控、B/A cross-wire：全部 PASS
- 13 个 session 全部 `purge=0`、stopped、PID gone、history retained
- ESP-NOW contracts：`51/51 PASS`
- platform tests：`1510 OK + 1 skipped`
- GitHub CI：[40823585571](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40823585571)：
  `platform-contracts` 与 `network-namespace-policy` 均 PASS
- 主仓证据：[PN exhaustion](https://github.com/m5agent/m5stack-esp-emulator/blob/8f9f7439/docs/evidence/2026-10-29-espnow-ccmp-pn-exhaustion/README.md)

## 文件

- `report.md`：PN 状态机、失败负控、执行和边界
- `run.json`：机器可读记录
- `evidence/summary.json`：脱敏 machine summary
- `evidence/patch-check.txt`：forward/current/reverse patch 验证
- `patches/0001-esp32-espnow-ccmp-pn-exhaustion.patch`：`0083` 原样 patch
- `patches/README.md`：patch 与 preimage 校验说明

## 未覆盖项

- loss/retry；
- channel/rate；
- bit-exact controller；
- RF、antenna、电气、timing 和 physical hardware。
