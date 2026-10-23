# FirmwareManifest LittleFS 资源清单

- 日期：`2026-10-24`
- 结果：`PASS`
- 工作类型：`code_change`
- 问题来源：P0 通用固件审查中的文件系统资源清单
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`eca4120090ad46b12b64ff74b345c38def80804b`
- 基线版本：`6de2f923735937aac19457ccb37469ae03cfb822`
- 环境：macOS Apple Silicon；Python 3；`littlefs-python 0.19.0`

## 结论

FirmwareManifest 现在可从 merged/segmented flash 的 data partition 直接
识别和挂载 LittleFS，并记录：

- partition、block size/count 和使用块；
- 文件路径、大小和 SHA256；
- 脚本、配置、证书、许可证和普通资源分类；
- `.key`、credential、secret、`.env` 等敏感路径的脱敏标记和路径哈希；
- LICENSE/NOTICE/COPYING 中的 SPDX 许可证声明；
- 文件/目录上限和 truncation。

真实 StickS3 UIFlow2 的 `sys`/`vfs` 两个 LittleFS 分区均成功 round-trip
进入 manifest。SPIFFS/FAT 仍明确为 `UNSUPPORTED`。

## 关键证据

- 真实样本：
  - `sys`：39 个文件、5 个目录、632603 字节；
  - `vfs`：17 个文件、7 个目录、16306 字节；
- LittleFS 文件哈希与敏感路径脱敏测试：PASS；
- SPDX-License-Identifier 提取测试：PASS；
- manifest schema/round-trip：PASS；
- 平台测试：`225/225 PASS`；
- code signature/manifest ID stability：PASS；
- 物理硬件：`NOT RUN`。

## 文件

- `report.md`
- `run.json`
- `evidence/verification.summary.json`

## 未覆盖项

- SPIFFS 和 FAT 文件枚举；
- Unix 运行时权限；
- 实际许可证合规判断；
- 压缩/加密文件系统；
- 恶意固件安全结论；
- 真机安全启动、Flash Encryption 和生产 key 流程。
