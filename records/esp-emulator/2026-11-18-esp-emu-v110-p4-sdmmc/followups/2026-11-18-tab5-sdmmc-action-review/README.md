# Tab5 SDMMC 保存快照复审的动作窗口写入

- 日期为 2026-11-18。工作类型为 Device Service 和固件复审集成。
- 结果为 `PASS`，覆盖 Tab5 ST7123 虚拟设备的合成 SDK 触摸写入、原版无写入对照、旧 API 能力对照和零输入 API 复位。
- 本轮跟进 [Tab5 SDMMC 槽位 0 的 Device Service 验证](../2026-11-18-tab5-sdmmc-device-service/README.md)。
- Device Service 1.91.0 候选和 Reviewer API 0.22.0 候选在独立会话中执行。运行时为原生 esp-emu 1.1.0，板型为 Tab5 P4 rev0 ST7123。 [固定源文件与复现步骤](https://github.com/m5agent/m5stack-esp-emulator/tree/15724035425f9d64cb69d752ebb359e4e2458022/tests/firmware/tab5_sdmmc_action)

保存快照复审点按屏幕中心。合成来宾读取 ST7123 的触点和松手报告后写入两个
FAT16 文件，复审从同一会话取得写入时间戳增量和停机文件哈希。Arduventure
1.0.0 原版也接受触摸，时间戳和卡镜像保持原样。旧 Device Service 仍挂载同一
SD 卡，复审把写入断言记为 `NOT RUN`。API 复位以新 P4 进程继续使用同一张卡，
并轮换写入时间戳的介质身份。

[完整报告](report.md) · [执行清单](run.json) · [四组回执](evidence/tab5-sdmmc-action-review-summary.json) · [冻结发布包复验](evidence/frozen-release-replay-summary.json)

时间戳覆盖采样间隔内落盘的前台和后台操作。合成探针的来宾事件提供了本轮动作归因。
实机、热插拔、控制器读计数、来宾自行复位和浏览器为 `NOT RUN`。未提交 Burner。
