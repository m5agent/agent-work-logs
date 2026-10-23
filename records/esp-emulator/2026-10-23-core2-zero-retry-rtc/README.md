# Core2 zero-retry deterministic regression and virtual-clock RTC

- 日期：`2026-10-23`
- 结果：`PASS`
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`1ef7f0a081cfdc968a816741ca0ed52e18e6b967`
- 基线版本：`88c88ab46b23da09c9216bc603133d69bacfb250`
- 环境：macOS Apple Silicon；QEMU `9.2.2`；Core2 `m5core2`；官方 UIFlow2 v2.5.3

## 结论

发现全矩阵曾通过自动重试掩盖 `core2-audio` 的首轮 cache-error panic。
修复后 Core2 peripheral、UI、radio/unified 路径统一使用
`tcg,thread=single` + deterministic `icount`；矩阵默认拒绝配置 retry，
诊断重试必须显式传 `--allow-retries`。

同时修复 deterministic guest 的 RTC 时间基准：RX8130/PCF8563 从 device
realize 时捕获的 host epoch 起，按 `QEMU_CLOCK_VIRTUAL` 推进。guest
`sleep_ms(1200)` 与 RTC 秒值因此在 `icount` 下保持一致。

## 关键结果

- 完整 UIFlow2 matrix：`67/67` cases、`274/274` checks
- 每个 case：`attempts=1`、`retry_used=false`
- Core2 peripheral group：`6/6 PASS`，全部首轮
- Core2 touch/RTC/power 重复探针：`5/5 PASS`
- 2026-10-24 Device Service `/api/v1` 复核：`5/5 PASS`，包含两个重叠会话，
  全部 `attempts=1`、`retry_used=false`
- Core2 UI：真实 `qemu-esptool` 写入 16 MiB flash，逐字节校验 `PASS`
- Core2 UI frame：`320x240`，touch marker `0,255,0`
- Platform tests：`216/216 PASS`
- QEMU binary SHA256：
  `cb648115dcbc59184663eb15882d2f65960f48d397805f2605dff0a6a945050d`
- Full-matrix summary SHA256：
  `6fc3e5473600399a559560398b3c665c3f17724c84db27c0239df775f2da3509`
- 物理 cache/PSRAM、bit-exact BT、RF 和真机：`NOT RUN`

## 文件

- `report.md`
- `run.json`
- `evidence/verification.summary.json`
- `evidence/2026-10-24-device-service-followup.summary.json`

## 未覆盖项

- deterministic scheduling 不等于物理 cache/PSRAM 时序；
- stock native-VHCI 仍依赖 GDB bridge；
- bit-exact Espressif BT baseband/controller 未执行；
- 不产生 RF、功耗、声学、光学、机械或真机证据。
