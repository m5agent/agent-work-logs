# ESP Emulator SVC-03 stateless parsing boundary

- 日期：`2026-10-29`
- 结果：`PASS`
- 工作类型：`code_change`
- 问题来源：`SVC-03`
- 源码版本：`m5agent/m5stack-esp-emulator@b978dd793c21230883944f02c8962a37903db9da`
- 环境：macOS Apple Silicon；Python 3.12；Device Service platform contracts

## 结论

完成 `SVC-03` 的第一个无语义移动：`ServiceError` 移到
`platform/tools/device_service_errors.py`，integer/size/pcap/SHA256 parser
移到 `platform/tools/device_service_parsing.py`。`device_service.py` 保留
`ServiceError`、`_is_sha256`、`parse_int`、`parse_size` 和
`parse_capture_pcap` 的同名导入，因此现有调用方与公开导入路径不变。

本里程碑只锁定并迁移无状态解析边界；store、runtime adapter、evidence、
session 状态机和 HTTP orchestration 均未移动。

## 关键证据

- `ServiceError.payload()` 的 code/message/status/extra 结构不变；
- parser 的 decimal/prefixed integer、size、pcap bool-only 与 lowercase
  SHA256 行为由 `7/7` 测试锁定；
- Device Service HTTP/Unit contracts：`124/124 PASS`；
- platform regression：`1569 OK, 10 skipped`；
- runtime coverage/peripheral catalog/QEMU profiles/project snapshot PASS；
- 新模块与测试 Ruff PASS；
- PR #43 已合并，merge commit：
  `206b7960d82fb318420065792e649ccec69bc162`。

## 文件

- `report.md`：移动边界、兼容性、验证和回滚
- `run.json`：结构化记录
- `evidence/verification.summary.json`：测试和交付摘要

## 未覆盖项

`SVC-03` 仍为进行中。其余请求解析、运行参数、设备规格、store、runtime
adapter、evidence collector、lifecycle/history 和 HTTP facade 尚未拆分；
本次没有 QEMU/hardware validation 需求。
