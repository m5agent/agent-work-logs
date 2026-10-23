# ESP Emulator FirmwareManifest FAT12/16/32 文件清单

- 日期：`2026-10-24`
- 结果：`PASS`（实现与合成 fixture）；真实 PaperColor FAT12 样本为 `PARTIAL`
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`97d9a80e1a1abe6a9870e79d2bc2ca81583e6f7d`
- 基线版本：`26090ceb868c66a6b0c338c41f7d242d243f1be2`
- 环境：macOS Apple Silicon；Python 3；静态镜像解析

## 结论

FirmwareManifest 现在可以在不挂载宿主文件系统、不执行镜像的前提下，只读解析
FAT12、FAT16 和 FAT32 数据分区，并生成与 LittleFS 一致的文件资源清单。

实现覆盖：

- BPB/geometry 和 FAT 表容量校验；
- FAT12/16/32 cluster chain、FAT32 root cluster；
- LFN sequence/checksum 和 8.3 fallback；
- 目录递归、多簇文件 SHA256 和 SPDX 提取；
- 敏感路径脱敏，以及敏感目录子树保护；
- cluster loop、越界/bad/free cluster、无效子目录和 malformed image 拒绝；
- erased/zero-filled FAT 分区标记为 `UNFORMATTED`；
- Manifest sensitive-file warning 和 truncation warning。

## 关键结果

- 平台测试：`230/230 PASS`；
- 合成 FAT12、FAT16、FAT32：全部 `PASS`；
- 三种格式均验证 LFN、嵌套目录、多簇文件、敏感 `.key`、SPDX 和
  manifest round-trip；
- malformed boot sector 和循环 cluster chain 不会被误判 PASS；
- 真实 PaperColor FAT12 `storage` 分区解析出 11 个 PNG 及其 SHA256；
- 其中一个未初始化的 `System Volume Information` 子目录被安全拒绝，
  因此真实样本保持 `PARTIAL`，没有枚举垃圾目录；
- 真实固件 image SHA256：
  `a3f5ca4ae89dd724dd8f9b2d800fd9749af84bf0cf2fffbf99cdf822b285f419`；
- 物理硬件：`NOT RUN`。

## 文件

- `report.md`：实现、执行、证据和边界
- `run.json`：结构化记录
- `evidence/verification.summary.json`：聚合验证摘要

## 未覆盖项

- SPIFFS 仍为 `UNSUPPORTED`；
- 不恢复删除文件，不检查 FAT slack space；
- 不证明 runtime 文件权限或许可证合规；
- 本次未重跑 QEMU 功能矩阵，物理硬件与真机安全配置仍为 `NOT RUN`。
