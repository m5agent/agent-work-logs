# M5Stack ESP Emulator SVC-03 storage/NVS parsing boundary

- 日期：`2026-10-30`
- 结果：`PASS`（platform-contract validation）
- 工作类型：`code_change`
- 问题来源：`SVC-03` Device Service 编排拆分
- 源码版本：`m5stack-esp-emulator @ 947a1ecf24b2338ab0f2901439e97264a26de292`
- 交付：PR #58 已合并为 `0c26759d9b34daa88e7e3457e88f4c0af9b16668`
- 环境：macOS arm64、Python 3.12

## 结论

storage 与 NVS execution request parser 已从 `device_service.py` 移至
`device_service_execution_parsing.py`。新模块只依赖 `ServiceError`、共享
SHA256 validator 和 `DeviceSpec`；原模块以 same-object 方式 re-export。
错误码、HTTP 状态、unknown-field fail closed、SD capability check、
partition-label bounds 和返回结构保持不变。

## 关键证据

- 专向 execution parser tests：`5/5 PASS`
- 现有 Device Service unit tests：`126/126 PASS`
- Platform suite：`1,670` tests，`1,669 PASS + 1 skip`
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  `PASS`
- compileall、scoped Ruff `E9/F`、`git diff --check`、PR scope：
  `PASS`
- PR CI：`4/4 PASS`

## 文件

- `report.md`：边界、验证和回滚
- `run.json`：机器可读记录
- `evidence/summary.json`：脱敏检查摘要
- `patches/`：不适用；代码位于主仓库提交
- `code/`：不适用；测试位于主仓库

## 未覆盖项

- 本次是源码边界重构，不改变 HTTP/API、session、evidence 或 QEMU 行为。
- 物理硬件、RF 与电气验证 `NOT RUN`。
- `SVC-03` 的 store、runtime adapter、evidence collector、history 和
  orchestration 拆分继续开放。
