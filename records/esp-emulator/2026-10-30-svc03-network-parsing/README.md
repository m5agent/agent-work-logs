# ESP Emulator SVC-03 network parsing boundary

- 日期：`2026-10-30`
- 结果：`PASS`（platform-contract validation）
- 工作类型：`code_change`
- 问题来源：`SVC-03` Device Service 边界拆分
- 源码版本：`m5stack-esp-emulator @ 16c92b04436b354f8162ae26f16242cc85d54878`
- 环境：macOS arm64；Python 3.12

## 结论

把 Device Service 中的 network policy 和 CNAME 请求解析移到无状态模块
`platform/tools/device_service_network.py`。`device_service.py` 继续
re-export 同名对象，因此调用方、错误码、implicit endpoint merge、bounded
CNAME binding 和 public symbol identity 均保持不变。

这是代码边界与平台契约验证，不是运行时仿真能力提升。HTTP 路由、network
sandbox、session 状态、evidence 字段和硬件行为没有改变。

## 关键证据

- 源码改动：`12` 个文件，`+284/-75`。
- 定向测试：network boundary `6/6 PASS`，parser boundary `7/7 PASS`。
- 完整平台回归：`1,589` 项，`1,588 PASS + 1 skip`。
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  `PASS`。
- Python compileall 与 `git diff --check`：`PASS`。

## 文件

- `report.md`：改动背景、执行命令、验证边界和回滚方式。
- `run.json`：机器可读记录。
- `evidence/verification-summary.json`：精确检查结果摘要。
- `patches/`：不适用；改动已作为源码提交交付。
- `code/`：不适用；可重建测试位于源码仓库的 `platform/tests/`。

## 未覆盖项

物理硬件、RF、电气行为和 QEMU 功能路径均为 `NOT RUN`。这次验证只证明
无状态解析边界的行为和 public symbol identity 没有回归。
