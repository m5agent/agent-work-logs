# Tab5 SDMMC 槽位 0 的 Device Service 验证

- 日期为 2026-11-18。工作类型为原生存储集成与验证。
- 结果为 PASS，覆盖固定 Tab5 SDK 探针的原生 SDMMC、HTTP 复位和停机导出。
- 本轮跟进 [esp-emu 1.1.0 的 P4 SDMMC 评估](../../README.md)。
- 环境为 Device Service 1.90.0 构建 57d39746 和 002c4900、Tab5 P4 rev0 ROM、ST7123 和原生 esp-emu 1.1.0。源码、OpenAPI、固件和运行时 SHA-256 见回执。验证类型为 virtual-device validation。

32 MiB FAT16 的写入只发生在会话私有副本。标准 HTTP 复位重新启动 P4 与 C6。新 P4 启动之前，镜像 inode 与复位前的写入结果 SHA-256 一致。来宾重新挂载并写读后，服务验证停机文件内容并导出不可变 artifact，随后新会话以该 artifact 建立独立副本。

[完整报告](report.md) · [执行清单](run.json) · [HTTP 复位](evidence/tab5-sdmmc-http-reset-summary.json) · [无复位对照](evidence/tab5-sdmmc-http-no-reset-summary.json) · [容量对照](evidence/tab5-sdmmc-slot0-geometry-summary.json)

合成 SDK 固件覆盖控制器和 API。98TAB5 原版自然启动仍为 PARTIAL。C6 网络、真实卡、热插拔、画面、触控及浏览器未在该里程碑执行。未提交 Burner。
