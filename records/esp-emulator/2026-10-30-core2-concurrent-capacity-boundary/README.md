# M5Stack ESP Emulator Core2 concurrent capacity boundary

- 日期：`2026-10-30`
- 结果：`PARTIAL`（virtual-device validation；八实例默认容量保持，九实例拒绝）
- 工作类型：`code_change`
- 问题来源：`CORE2-02` Core2 单设备并发容量与 ACK 稳定性
- 源码版本：`m5stack-esp-emulator @ 66e5b8071622b6bf7727811f5327d9d8fb248e15`
- 交付：PR #57 已合并为 `ccbfa71c60f62df2682fd6c449ce8abdaedfd871`
- 环境：macOS arm64、Python 3.12、Device Service `/api/v1`、QEMU unified Core2

## 结论

Core2 单设备并发默认上限保持 8。三次独立零错峰九实例尝试分别得到
`9/9 PASS`、`9/9 PASS` 和 `8/9 FAIL`；第三次失败在真实并发 9 时触发
NimBLE `ble_hs_hci_process_ack` `LoadProhibited`，匹配 ELF 的 PC 为
`0x402630cc`。后续 `0x40092e43` panic 位于复位过程中的 I2S/memset 路径，
属于次生故障。一次可复现 guest panic 足以拒绝九实例准入。

当前固件/ELF/QEMU/工具哈希下，两批独立零错峰 `2x60s` 均为 `2/2 PASS`。
guest 网络重检改为最多三次、间隔 1 秒；最终仍要求累计 HTTP/公网成功次数，
PSRAM error 与可恢复 network error 分字段记录。当前 120 秒持续压力 floor
重绑为 `hold/40`，最低三次连续 1 MiB PSRAM sweep。

## 关键证据

- 九实例通过 A：
  `67f755e6d7aebe0174f453b3fc991fb046f88e707e2ac4162ce846dc4755dd25`
- 九实例通过 B：
  `70926d8cd1f8fdc1ae5241f9b8c9fc62abeb11e1da826a06add1e760ba2581f2`
- 九实例失败 control：
  `24c4d62aac73ff5a048f4104de514a6e9714be8aa1f6063745753e5adedf71b1`
- 当前 2x60s 通过 A：
  `dfd80cead1f73cdd94f8ccee8f79322e3c55105945637e08c01bece47b2ba146`
- 当前 2x60s 通过 B：
  `1a65e9612473ffa79c7df4c76fa5900168271293721c77cd1387aac269d0e382`
- Platform suite：`1,665` tests，`1,664 PASS + 1 skip`
- 四个生成器一致性检查、compileall、scoped Ruff `E9/F`、PR scope：
  `PASS`
- PR CI：`4/4 PASS`

## 文件

- `report.md`：问题、改动、执行、边界与回滚
- `run.json`：机器可读记录
- `evidence/summary.json`：脱敏哈希和检查摘要
- `patches/`：不适用；代码与 evidence 在主仓库提交
- `code/`：不适用；runner/tests 位于主仓库

## 未覆盖项

- 当前高负载宿主条件下的八实例 cold-start tool-hash 重绑尚未 PASS。
- 九实例的 ACK 竞态未修复，容量 9 未准入。
- 物理 PSRAM/cache timing、bit-exact BT controller/baseband、RF、
  电气与真机均 `NOT RUN`。
