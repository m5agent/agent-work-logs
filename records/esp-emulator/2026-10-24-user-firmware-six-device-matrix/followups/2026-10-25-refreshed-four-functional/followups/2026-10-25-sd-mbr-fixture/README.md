# ESP Emulator session-isolated SD fixture and CrossPoint closure

- 日期：`2026-10-25`
- 结果：`PASS`（存储 fixture + virtual-device）
- 工作类型：`code_change`
- 问题来源：CrossPoint 在无 SD media 的 generic session 中显示 `SD card error`
- 源码版本：`m5agent/m5stack-esp-emulator @ 437d417a84794f861e40910422849113707c79a6`
- 基线版本：`259533cef424ffa0418369e2767a38862dc1b7d4`
- 环境：macOS Apple Silicon、Device Service `/api/v1`、QEMU；无物理硬件

## 结论

Device Service 现在支持把内容寻址的 raw SD image 复制到每个 session，再以
writable `if=sd` 挂载。source artifact 不会直接作为可写磁盘使用。

矩阵把 SD fixture SHA 纳入 result key，因此同一 firmware SHA 在无卡和
有卡条件下不会复用错误结果。使用仓库内纯 Python 生成的 64 MiB
FAT32+MBR fixture 后：

- CrossPoint 从 `SD card error` 进入 recent-books 主菜单；
- EDC Book 保持启动/续读 UI PASS；
- XiaoZhi 保持配网 UI PASS；
- OpenAI Voice Assistant 仍因 NVS user data 缺失黑屏。

四个当前公开固件最终为 `3 PASS / 1 PARTIAL / 0 FAIL`。CrossPoint 之前的
`runtime_fixture_gap` 保留为历史对照，不能归因成固件 FAIL。

## 关键证据

- 平台测试：`363/363 PASS`；
- user firmware matrix：`18/18 PASS`；
- SD image tests：`4/4 PASS`；
- 文档契约：`19/19 PASS`；
- Node：`2/2 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot、
  compileall 与 JSON 校验全部通过；
- GitHub Actions run `40127676353`：两个 job 均 `PASS`；
- SD fixture：64 MiB FAT32+MBR，SHA256
  `b720d6f7f932bb22accc8b9133f3016e5c060f5d292523f78b3c636c036a5139`；
- CrossPoint session 在服务重启后仍恢复 storage summary；
- evidence ZIP 包含 `frames/current.png`、`storage/summary.json` 和
  `manifest.json`，SHA256 `883834b6ac1a30c4ba535000b4a9a78bee07d906f400897540df803a3d279bce`。

源码 evidence：
[refreshed four with SD MBR](https://github.com/m5agent/m5stack-esp-emulator/blob/437d417a84794f861e40910422849113707c79a6/tests/firmware/evidence-2026-10-25-refreshed-four-functional-sd-mbr/evidence.json)

## 文件

- `report.md`：API、根因、执行和边界。
- `run.json`：结构化结果。
- `evidence/verification-summary.json`：脱敏验证摘要。
- `patches/`、`code/`：不适用；生成器、API 和测试已进入源码仓库。

## 未覆盖项

- OpenAI Voice Assistant NVS 首次启动数据；
- XiaoZhi 配网完成、语音、音频和云连接；
- CrossPoint 书籍导入、EPUB 渲染、Wi-Fi/OPDS 和跨重启状态；
- 完整 7 台设备/更多固件族回归；
- 物理硬件验证。
