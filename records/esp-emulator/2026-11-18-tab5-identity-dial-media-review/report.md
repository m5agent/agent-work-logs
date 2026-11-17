# Tab5 OTA0 应用身份与 Dial U197 媒体取证

## Tab5 在已准入 Flash 中识别单一 OTA0

Device Service 在原版 merged Flash 中解析应用身份。候选 `d6a22054fbf6527f89845804d90ff5c1ef44d864` 在单一 OTA0 时检查分区表、对齐且全擦除的 OTA data、ESP32-P4 应用及其附加摘要，再发布应用分区和段的身份。该分支按已准入虚拟 Flash 判定。需要选择槽位的多应用布局及符号匹配有独立前置条件。

原版 98TAB5 的 SHA-256 为 `ea4fb0889e4a2c68d472947137908c52c25a663152d3ff78262ce2605440dc6d`。同一 Tab5 1.1.0 GT911/ILI9881C 运行时普通启动后，API 与证据 ZIP 都记录 `app0`、subtype `0x10`、offset `0x10000`、版本 `1.3.0`，选择理由为 `ota0_erased_otadata`。启动串口也报告从 `0x10000` 加载。回核了归一化 Flash 的分区和段摘要。匹配 ELF 与运行时符号仍未取得。

在 60.293 秒窗口内，98TAB5 的 UART 仍有 32 个启动标记与 31 个 `SW_CPU_RESET`。运行中的 29 次画面尝试仍无完整 DSI 帧。原版 CarPlay 保留 factory 应用身份，在 30.911 秒窗口内读到 14 个有效帧，720×1280 的最终画面 SHA-256 与前一次显示正控一致。此次两个来宾的串口摘要也分别与此前同版运行时相同。应用身份验收为 `PASS`，98TAB5 稳定启动与试验中的画面证据仍为 `PARTIAL`。两次均停止、释放 Flash，剩余活动租约为零。 [身份和启动证据](evidence/tab5-ota0-identity-summary.redacted.json)

## Dial U197 的 UART 与实际媒体边界

以同一 vinylM5Dial 1.0 R1F30 原版在 Dial 原生 QEMU 的 Port B 挂接 U197。当来宾自动播放后分别旋转 +3 与 -2 格，N9301 UART 读回曲目 1 → 4 → 2，两个旋转使用默认每边沿 35 ms。控制器保留 8 个发送帧、6 个注入帧、0 个非法帧，索引轨道数为 7。模型状态中的播放位为 1，验收范围是 UART 命令和响应。

16,044 字节 WAV 夹具通过独立解码核对。它包含 8,000 个 16 kHz 单声道 s16le 样本，时长 0.5 秒，主频 440 Hz。上传工件成功后，传给 U197 的 `media-artifact-id` 字段在设备输入处被拒绝，HTTP 400 和 `invalid_unit_input`。同一 Dial 会话的 PCM 获取与注入均返回 HTTP 409 和 `audio_unsupported`。证据 ZIP 无音频成员。实体媒体、解码、实出声和 PCM 输出均为 `NOT RUN`。

首个试验已读到相同曲目和挂载拒绝，随后屏幕核验因工具环境缺少 Pillow 结束。复测完成全部采集，两个隔离会话均停止并释放 Flash，活动租约为零。 [WAV、UART 与路由对照](evidence/dial-u197-real-media-boundary-summary.redacted.json)

## NC1020 来宾 SD 写入与停止后文件审核

Reviewer 0.10.0 在保存快照交互的 `sd_write` 中接收可选的 FAT 文件路径。复验使用同一 NC1020 原版、同一 SD 种子与同一 `key_f12` 交互。先确认虚拟来宾产生写入，再从同会话停止后的保留 SD 清单查找预期文件。两次运行均超过 60 秒且有同会话证据 ZIP。

正向要求 `/nc1020.state`，来宾写入和保留文件都通过，获取到 99,384 字节及内容 SHA-256。整单仍为 `manual_review / SIM_PARTIAL`，保留 `E_INTERACTION_CLAIM_PARTIAL`。负向只将预期改成 `/missing.state`，同一固件仍保存了 `/nc1020.state`，实时写入项为 `PASS`。停止后的清单无法匹配所指定文件，SD 审核保留 `PARTIAL`，整单给出 `E_SIM_SD_WRITE_PARTIAL`。

逐份核对 Reviewer 报告和存档 SD 断言，并用 ZIP 清单回核原版固件、输入 SD 与会话绑定。文件摘要来自同会话停止后清单。变更后的原始 SD 已随隔离运行清理。首批两个尝试因设备模型前置文件不可用在准入终止，固件未评估。有效复验停止并释放 Flash，剩余活动租约为零。未提交 Burner。 [NC1020 正反审核凭据](evidence/nc1020-retained-sd-write-review-summary.redacted.json)


## 源码与校验

模拟器主线为 `31867f0eea21b907328297a8cd2190f295765e79`，Device Service API 为 1.79.0。早期平台套件发现 API Markdown 的版本不一致。更新后全套运行 2,399 项，跳过 10 项，其余通过。51 项文档检查、运行覆盖、外设目录、配置、快照、API 清单和变更范围通过。Reviewer 主线 `4e195d89ee767e51e9e11969c8f1e75ee6bf3f66` 的 203 项单测通过。两边变更可分别撤销。 [模拟器主线](https://github.com/m5agent/m5stack-esp-emulator/commit/31867f0eea21b907328297a8cd2190f295765e79)
