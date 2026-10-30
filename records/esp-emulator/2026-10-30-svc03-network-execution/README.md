# M5Stack ESP Emulator SVC-03 network execution parsing boundary

- 日期：`2026-10-30`
- 结果：`PASS`（platform-contract validation）
- 工作类型：`code_change`
- 问题来源：`SVC-03` Device Service 编排拆分
- 源码版本：`m5stack-esp-emulator @ cbc33dbddfa26202a07d9c4adfa7dc042123639e`
- 交付：PR #59 已合并为 `9c1652dfd9a57307fb1834f4d135b818126b749f`
- 环境：macOS arm64、Python 3.12

## 结论

`parse_network_execution` 已从 `device_service.py` 移至
`device_service_network_execution.py`。新模块只依赖 `ServiceError`、
共享 SHA256/capture parser、`DeviceSpec` 和 network-lane normalizer；
原模块以 same-object 方式 re-export。

profile 默认值、WiFi/BLE/TCP booleans、hostfwd/I2C normalization、ELF
要求、PSRAM/expected-marker bounds、network pcap rejection 和返回结构
保持不变。

## 关键证据

- 专向 network-execution parser tests：`4/4 PASS`
- 现有 Device Service unit tests：`126/126 PASS`
- Platform suite：`1,674` tests，`1,673 PASS + 1 skip`
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  `PASS`
- compileall、scoped Ruff `E9/F`、`git diff --check`、PR scope：
  `PASS`
- PR CI：`4/4 PASS`

## 文件

- `report.md`：边界、验证、风险和回滚
- `run.json`：机器可读记录
- `evidence/summary.json`：脱敏检查摘要
- `patches/`：不适用；代码位于主仓库提交
- `code/`：不适用；测试位于主仓库

## 未覆盖项

- 不改变 HTTP/API、network runtime、session、evidence 或 QEMU 行为。
- network transport、物理硬件、RF 与电气验证 `NOT RUN`。
- `SVC-03` 的 QEMU WiFi/BLE parser、store、runtime adapter、
  evidence collector、history 和 orchestration 拆分继续开放。
