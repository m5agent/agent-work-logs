# Device Service 单实例 API 契约统一

- 日期：`2026-10-23`
- 结果：`PASS`
- 工作类型：`code_change`
- 源码：`m5stack-esp-emulator @ f2ff7a75b473653ec1440e955c0f42c6b7f22203`
- 验证类别：`virtual-device validation`

## 结论

Device Service 的对外 API 现在统一为以下语义：

- `qemu-unified`：正式的整机单实例 runtime，要求 `*-unified` profile；
- `qemu-wifi`：同一个 QEMU guest 内只验证 board + WiFi；
- `qemu-ble`：兼容旧 unified 调用，以及无线电专用诊断 profile；
- `network`：独立 `esp-emu` 诊断 lane，不被描述为整机验收。

OpenAPI 升至 `1.4.0`，修正了 Session/logs runtime 枚举只允许
`qemu|network` 的旧错误，并新增统一的 `RuntimeName` 与
`NetworkEvidence` 契约。

## 关键结果

- 有效 unified profile 通过 `runtime=qemu-unified` 创建请求；
- Wi-Fi-only profile 搭配 `qemu-unified` 返回
  `qemu_unified_profile_required`；
- 旧 `qemu-ble` unified 调用继续兼容；
- 172 个平台单元测试通过；
- runtime coverage 与 peripheral catalog 检查通过；
- 本机 Device Service 已重启并实际提供 OpenAPI `1.4.0`。

## 文件

- `report.md`：契约设计、兼容性和验证细节
- `run.json`：机器可读结果
- `evidence/api-contract-check.txt`：实际 API 响应
- `evidence/openapi-summary.json`：OpenAPI 版本、枚举与 schema 摘要

## 边界

- 本记录验证 API 和运行时选择契约，不重新声称所有设备均完成物理级仿真。
- 未执行实体硬件、RF、功耗或电气测量。
