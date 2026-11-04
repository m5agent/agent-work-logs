# M5Stack 模拟器中文介绍视频与运行取证

- 日期：`2026-11-04`（Asia/Shanghai）
- 结果：`PASS`（成片交付与限定 CoreS3 原生虚拟设备验证）；物理硬件及 browser-WASM `NOT RUN`。
- 工作类型：`report`
- 问题来源：用户要求交付 M5Stack 风格、具有科技感的模拟器介绍视频；无对应 Issue/PR。
- 源码版本：[m5stack-esp-emulator @ b41eba70eb61f7ddc5c41e0b981341064f9d1d1f](https://github.com/m5agent/m5stack-esp-emulator/tree/b41eba70eb61f7ddc5c41e0b981341064f9d1d1f)
- 环境：专用 Device Service `/api/v1` 会话、原生 QEMU `m5cores3`、UIFlow2、UART REPL 与真实客体 framebuffer；未使用物理硬件。

## 结论

成片为 74 秒、1920×1080、30 fps，带中文旁白、烧录字幕与原创电子配乐。为介绍片新采集的 CoreS3 演示程序在同一客体内执行，收到实际控制器触摸输入后打印 `M5_VIDEO_TOUCH 160 214 MODE 1`，屏幕由蓝色 `READY` 切为绿色 `TOUCH ACTIVE`。23.857 秒采样得到 138 张 PNG、137 个不同哈希。固件、运行时、程序和源码身份已交叉核对，证据 ZIP 在停止前取得，运行时与专用服务已清理。

另新增一次网页工作台本地上传演示：使用独立镜像 `a31ba1df…`，网页连接原生 Device Service 后显示真实 guest 屏幕，随后完成触摸切换与清理。它与前述 UART live 镜像 `0ede4060…` 分别绑定证据，不是 browser-WASM 验证。

两条限定的原生虚拟设备演示路径与成片交付检查均通过。最终 MP4 为 9,225,412 bytes，SHA256 `504eec4151b63cff0ded05b1312127ea98573546d05784471616516ccc5b7e5c`。全流解码、Chromium 播放与 9 次关键帧跳转、解码画面检查通过；最终音轨为 −16.23 LUFS / −1.37 dBTP。详见[媒体摘要](evidence/media-summary.json)。视频本体本地交付，不将大媒体提交到记录仓库。

## 关键证据

- 构建或运行：[运行摘要](evidence/runtime-summary.json)，本轮未重新构建运行时或固件。
- 产物或部署：介绍片不作为站点部署；最终成片身份见媒体摘要，不提交整段视频。
- 实机或服务执行：CoreS3 原生 Device Service `uiflow-live`，物理硬件及 browser-WASM 均 `NOT RUN`。
- 网页工作台：[工作台运行摘要](evidence/workbench-summary.json)及[截图与镜像完整性摘要](evidence/workbench-integrity-summary.json)。
- 日志、测量或协议：[完整性摘要](evidence/archive-integrity-summary.json)、[输入前](evidence/before-touch.png)、[输入后](evidence/after-touch.png)。

## 文件

- [report.md](report.md)：背景、执行、证据与边界。
- [run.json](run.json)：结构化分层结果与最终媒体身份。
- `evidence/`：脱敏运行摘要与两张未经改像素的原始 PNG；完整响应、ZIP 和帧序列不公开。
- [code/demo.py](code/demo.py)：本次实际执行的 Python 演示源码。
- `patches/`：不适用；未修改项目实现。

## 未覆盖项

- 物理硬件、RF、功耗、电气、声学、光学和机械特性：`NOT RUN`。
- browser-WASM、上述两份镜像以外的固件/设备、网络和外设矩阵：`NOT RUN`；不能从原生演示继承。
- 演示波形为程序生成数据；产品参考图与工作流动态图形属于介绍素材，不能视为运行取证。
- MP4 播放检查属于媒体交付验证，不能当作 browser-WASM 固件运行验证。
