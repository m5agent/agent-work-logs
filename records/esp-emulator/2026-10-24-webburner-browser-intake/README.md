# ESP Emulator WebBurner 可恢复固件导入

- 日期：`2026-10-24`
- 结果：`PASS`（browser + HTTP contract）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码基线：`0ffaf07b334a09690e2ad62b23078c04ea8b134c`
- 结果提交：`9aa3fd71e9ad0b0002cd3e06f4e12038a833d703`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40022859936>
- 环境：macOS Apple Silicon；Chromium/Playwright；Python 3；GitHub Actions Ubuntu

## 结论

`FW-04` 从只有 chunk backend 推进到可用的 WebBurner 浏览器入口：

- 浏览器流式计算完整 SHA256，不把整个固件读入内存；
- 以 4 MiB chunk 上传，支持进度、瞬态重试、取消和 staging 清理；
- 上传完成后调用 `POST /api/v1/firmware/import`；
- 服务端执行 WebBurner/M5Burner/ESP-IDF 的同一套 Manifest importer；
- 生成 normalized merged-flash artifact，并保留 source format/segment hash；
- 上传完成后刷新页面，无需重新上传即可继续 import；
- 未完成上传刷新后保留 upload ID，重新选择同一文件可从服务端确认 offset
  继续；
- 页面可显示 manifest validation、warnings/errors 并调用 session API。

真实 Chromium 使用 `9.44 MiB` WebBurner ZIP 完成 3 个 chunk 上传、
FirmwareManifest/capability PASS 和 session 前端契约验证。另有强制 import
失败后刷新恢复、上传中途取消/清理测试。

## 关键证据

- 本机 Python：`253` tests，`OK`；
- GitHub Actions：`253` tests，`OK (skipped=2)`；
- Node：`SHA256_OK`、`FIRMWARE_UPLOAD_OK`；
- 浏览器：无 page error，`3` chunks、manifest `PASS`；
- runtime coverage、peripheral catalog、QEMU profiles：`PASS`；
- OpenAPI：`3.1.0` / `1.13.0`，`38` paths；
- 物理硬件与合成固件的真实虚拟设备启动：`NOT RUN`。

## 文件

- `report.md`：改动、验证和边界；
- `run.json`：结构化结果；
- `evidence/verification.summary.json`：本机、CI 和浏览器探针摘要；

后续 WebBurner `parts[]` 完整性校验见
[Follow-up: WebBurner part integrity](followups/2026-10-25-webburner-part-integrity/)。

## 未覆盖项

- 没有用合成测试镜像启动完整虚拟设备；session 创建按钮只验证了前端 API
  契约；
- 没有扩到 ESP-IDF/Arduino/MicroPython/vendor 固件语料；
- SPIFFS、运行时权限和许可策略仍开放；
- 物理硬件仍为 `NOT RUN`。
