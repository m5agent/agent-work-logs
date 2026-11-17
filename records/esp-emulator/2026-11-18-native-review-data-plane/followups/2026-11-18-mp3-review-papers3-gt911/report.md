# 原版 MP3 播放审核及 PaperS3 原生触摸诊断

## 保存快照的 PCM 断言

此前同一 MP3 原版固件已经获得独立的虚拟读卡和播放证据。此次审核服务加入保存快照验证选项 `audio_playback`，要求把声明的输入、按键前后真实 I²S DMA PCM、同一会话身份与证据 ZIP 绑定。执行约束限原生 Cardputer 系列。采样率、频率容差和最低 RMS 由调用者声明。缺少可回核的 PCM 会保留 `PARTIAL`。[此前的原版播放记录](https://github.com/m5agent/agent-work-logs/blob/8cd6338fe554cbeb9d4e8bcb93e6dba4a0adc64a/records/firmware-review-service/2026-11-09-cardputer-adv-mp3-startup/followups/2026-11-09-cardputer-adv-main-and-dry-run/report.md)

正反两条复现计划使用同一个 885,600 字节发布镜像、同一归一化 Flash、同一 64 MiB FAT32 和同一回车计划。一条期望 524 Hz，另一条故意期望 880 Hz。固件、SD 和运行身份记入 [运行清单](run.json)。Reviewer 0.7.0 源码 `22c70e58306e2a5630167203e76923a47c5632ad` 通过 196 项单测、OpenAPI 解析和 JavaScript 语法检查。[公开固件发布](https://github.com/TurbulentGoat/cardputer-adv-mp3-player/releases/tag/v1.0.0)

首批两次复测都在隔离启动封装退出后报 `E_SIM_STARTUP_FAILED`。ZIP 的 QEMU 标准错误指向机器名断言，封装写成 `m5cardputer-adv`，实际 `-M` 指定 `m5cardputeradv`。两次均无来宾串口和帧，固件层为 `NOT EVALUATED`。修正仅发生在隔离复测封装。 [首次启动失败](evidence/mp3-initial-startup-summary.redacted.json)

封装修正后，期望 524 Hz 的正向审核在接收回车后取得两个连续 8,192 样本窗口，调用方声明采样率 48 kHz、单声道 s16le。主频分别为 522.792 和 522.582 Hz，RMS 分别为 791.429 和 948.851。两个窗口均满足 ±8 Hz 和 RMS 至少 100，原版审核完成为 `done / SIM_VERIFIED`。重新从同会话 ZIP 取出相同偏移区间后，逐窗哈希及频率和 RMS 都一致。

同一固件与 SD 期望 880 Hz 时，14 个真实窗口没有匹配，审核显示 `manual_review / SIM_PARTIAL` 和 `E_SIM_AUDIO_ASSERTION_FAILED`。PCM 数据仍包含约 523 Hz 的播放样本。第三条同固件、同 524 Hz 期望的对照禁用 `audio.read`，实时回读被拒绝且证据 ZIP 省略 PCM，审核音频项为 `PARTIAL`，整单 `E_SIM_AUDIO_PARTIAL`。三次独立运行都达 60 秒，已停止并释放可变 Flash，活动租约为零。 [三条同会话审核证据](evidence/mp3-exact-playback-review-summary.redacted.json)

## PaperS3 原版 GT911 原生跟踪

三个证据 ZIP 均绑定同一 16 MiB 虚拟 Flash，其前 1,439,168 字节逐字节匹配 Factory V0.5 合并 BIN，尾部填充 `0xff`。用这份固件、触摸坐标 (113,347) 和 150、300、500 ms 的按压组，在原生 Device Service 隔离运行。诊断运行加入只读 MMIO 和总线观测。用 Xtensa 指令位置回核实际看见的 GPIO 高位读取、IRQ 掩码与 `81 4e 00` 清除字节，绑定来宾驱动的 `getTouchRaw()`。另一个通用 GPIO 读取地址独立计数。数值以原生 QEMU 虚拟时钟为基准。 [锁定版本的 GT911 驱动](https://github.com/m5stack/M5GFX/blob/c6f92dc03226cdc04d67c705a2020f62ad21ad01/src/lgfx/v1/touch/Touch_GT911.cpp#L169)

一次漏响应以按下为零点，7.526 ms 时 GPIO48 指示就绪，两次通用 GPIO 读取之后，确认的驱动位置在 157.832 ms 才读取。随后于 158.189 ms 清除，160.512 ms 松手，165.041 ms 报告为空，181.343 ms 读取空状态 `0x80`。按住期间未发生 `0x81` 读取，稳定图标零变化。另一次 500 ms 输入已经读取按下和松开报告，图标仍未匹配，单独保留。 [逐次观测及对照](evidence/papers3-native-touch-poll-summary.redacted.json)

诊断运行 12 次接触有 10 次准确改变 607 个图标像素。独立的无观测冻结版接受 12 次输入，11 次取得稳定帧，其中 4 次匹配、7 次零变化，最后一次稳定帧超时。另外一次单独的冻结版运行在首个输入前遇到 EPD 过渡帧。诊断版和对照使用不同的观测开销与取帧判据，本记录只用于定位单次来宾驱动采样与报告时序。所有原生会话均先取证再停止，活动租约为零。前台驱动为何延迟仍是 `PARTIAL`，此前浏览器对照保持独立。

## 交付边界

复测使用的 Device Service 源码为 `731817add38c34e6d2a58f8dcde646cd7ded3f46`，主线 `65f40eac4521ceb2af9962298e1a26a6e07aae78` 添加证据与文档。51 项文档检查、范围检查及生成的项目快照、运行覆盖、外设目录与 QEMU 配置校验均通过。 [模拟器主线提交](https://github.com/m5agent/m5stack-esp-emulator/commit/65f40eac4521ceb2af9962298e1a26a6e07aae78)

复测结论限固定原版、固定虚拟运行时和所声明的 I/O。实体 SD、声学、电子纸与触控物理行为为 `NOT RUN`，未提交 Burner。审核功能可在其独立源码仓库撤销提交。原始固件、媒体、音频、指令跟踪、内部运行标识和地址均保留在测试环境。
