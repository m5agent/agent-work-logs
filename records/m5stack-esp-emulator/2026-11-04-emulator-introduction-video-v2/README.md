# M5Stack 模拟器介绍视频 V2：快剪、3D 运镜与独立运行取证

- 日期：`2026-11-04`（Asia/Shanghai）
- 结果：`PASS`（限定成片交付与 virtual-device validation）。最终媒体身份和 QA 已闭合；三组原生演示、工作台实录与独立 browser-WASM 启动/画面验证分别通过，所建会话及服务已清理。browser-WASM 输入与物理硬件 `NOT RUN`。
- 工作类型：`report`
- 问题来源：用户反馈 V1 节奏偏慢，要求重做介绍片；无对应 Issue/PR。
- 源码版本：[m5stack-esp-emulator @ b41eba70eb61f7ddc5c41e0b981341064f9d1d1f](https://github.com/m5agent/m5stack-esp-emulator/tree/b41eba70eb61f7ddc5c41e0b981341064f9d1d1f)
- 环境：原生 QEMU / Device Service `/api/v1`、独立 QEMU-WASM 浏览器客体、Three.js 模型渲染。未使用物理硬件。

## 结论

V2 成片为 60 秒、1920×1080、30 fps、H.264/AAC，采用 140 BPM 原创配乐、短句中文旁白和真实 3D 摄像机/灯光动画。九段旁白实际约 25.45 秒，其余时段留给运行演示和节拍。它是对 [V1](../2026-11-04-emulator-introduction-video/) 的独立迭代，保留前版记录。

本轮新取证的原生素材包含 Cardputer ADV 键盘打砖块、CoreS3 触摸绘图，以及 Pelican 骑行动画与 BMI270 仿真输入；另有实际上传、交互、串口和代码编辑器运行的工作台实录。各自保留固件、运行时、源码、输入、画面及停止清理证据，没有继承 V1 的 PASS。独立 browser-WASM 运行获得 CoreS3 fixture 的 ready marker、真实 framebuffer 和 Worker/iframe 清理证据；浏览器输入未验证。

最终 MP4 已通过 1800 帧全流解码、Chromium 实际播放与 17 次跳转、最终关键帧复核和独立视觉审查。编码 AAC 测得 `−16.08 LUFS / −0.39 dBTP / LRA 2.80`。Arcade 底部提示、上传界面和双运行画面的标题裁切已修正；原始 guest 帧不变。

成片 `M5Stack-Emulator-Intro-V2-1080p.mp4`，`22,627,515` bytes，SHA256 `a9162b0737e98a20eebe80b0c29378a5d414e9209431f4a103c0aa7bd155d143`。视频本体单独交付，不提交到记录仓库；完整规格与验证见[媒体摘要](evidence/media-summary.json)。

## 关键证据

- 构建或运行：[原生演示摘要](evidence/native-summary.json)、[独立 browser-WASM 摘要](evidence/browser-wasm-summary.json)。本轮未重新构建固件或运行时。
- 产物或部署：[3D 渲染摘要](evidence/cinema-summary.json)、[媒体摘要](evidence/media-summary.json)；本任务不包含站点部署。
- 实机或服务执行：原生演示与 browser-WASM 分别取证；物理硬件 `NOT RUN`。
- 日志、测量或协议：上述摘要保留固定哈希、串口 marker、帧身份和清理结果；[代码身份摘要](evidence/code-summary.json)绑定代表性 guest 源码，[独立完整性检查](evidence/archive-integrity-summary.json)核对源码、逐帧哈希及 ZIP。

## 文件

- [report.md](report.md)：背景、分层证据、复现与边界。
- [run.json](run.json)：机器可读状态、最终文件身份与通过的媒体检查。
- `evidence/`：小型、明确标注为派生摘要的 JSON；不包含原始 ZIP、帧序列、完整请求或视频。
- [code/README.md](code/README.md)：Arcade、Touch Studio、Pelican 源码导航及 MIT 归属。
- `patches/`：不适用；未修改模拟器实现。

## 未覆盖项

- 物理硬件、RF、电气、功耗、声学、光学和机械属性：`NOT RUN`。
- browser-WASM 输入，以及本轮固定 fixture 以外的固件/设备兼容性：`NOT RUN`。
- Pelican 姿态数据由虚拟 BMI270 控制器注入，不是物理传感器精度测量。
- 3D 运镜是视觉渲染；屏幕贴图来自独立实录，不代表渲染器内重新运行或操控了固件。
- 缓存 Piano 候选镜像启动失败；后续成功游戏为新 Arcade 演示，不能称作 Piano 通过。

