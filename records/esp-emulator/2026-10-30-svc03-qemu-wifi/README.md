# M5Stack ESP Emulator SVC-03 QEMU WiFi semantic boundary

- 日期：`2026-10-30`
- 结果：`PASS`（platform-contract validation）
- 工作类型：`code_change`
- 问题来源：`SVC-03` Device Service 编排拆分
- 源码版本：`m5stack-esp-emulator @ b799807b177948f5409adbe7d5a39f50ffc019cd`
- 交付：PR #61 已合并为 `3fc436e4aa99176ef3a4f7a2d35d25c973659219`
- 环境：macOS arm64、Python 3.12

## 结论

QEMU WiFi security parser 与 runtime-env projection 已从
`device_service.py` 移至 `device_service_qemu_wifi.py`：

- `parse_qemu_wifi_security`
- `apply_qemu_wifi_environment`

原模块以 same-object 方式 re-export。open/WPA2-PSK validation、credential
normalization、SSID bounds 和只有 S3 WPA2 设置 trace 的语义保持不变。

## 关键证据

- 专向 QEMU WiFi boundary tests：`4/4 PASS`
- 现有 Device Service unit tests：`126/126 PASS`
- Platform suite：`1,678` tests，`1,677 PASS + 1 skip`
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

- 不改变 HTTP/API、network 配置、QEMU execution、session 或 evidence 行为。
- RF、电气、物理硬件和真机验证 `NOT RUN`。
- `SVC-03` 的 QEMU BLE parser、store、runtime adapter、evidence collector、
  history 和 orchestration 拆分继续开放。
