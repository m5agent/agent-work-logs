# M5Stack 模拟器介绍视频 V2 制作与验证报告

## 背景与目标

用户反馈前版介绍片节奏偏慢，要求重做。V2 将目标时长从 74 秒缩短至 60 秒，使用 140 BPM 原创电子配乐、短句旁白、3D 摄像机移动和多种真实运行演示。V1 的素材、成片身份和结论保留在独立历史记录，本次没有覆盖前版证据。

本任务没有要修复的模拟器故障。改动对象是介绍视频、专用演示应用与取证材料。验收分为原生虚拟设备、browser-WASM、视觉渲染和最终媒体交付，分别记录，不用任一层的 PASS 代替其它层。

## 当前结果与改动范围

当前整体为限定任务范围内 `PASS`。最终 MP4 身份已绑定，成片全流解码、实际播放和视觉 QA 已通过。三组原生演示与工作台实录分别绑定身份、输入和画面，证据取得后所建会话、运行时与专用服务全部清理。独立 browser-WASM fixture 的 ready/实际画面/清理通过；浏览器输入与物理硬件验证保持 `NOT RUN`。

新增 Arcade 与 Touch Studio 两个 UIFlow2 演示；Pelican 沿用固定版本仓库中的 MIT 源码。没有修改模拟器实现、上游固件实现或他人服务配置。原始 ZIP、固件、运行时、视频、完整帧序列和请求响应均不进入公开记录。

## 原生演示：独立于浏览器 WASM

三组运行均通过专用 Device Service `/api/v1` 会话，输入进入虚拟设备控制器，画面来自 guest framebuffer。每组 evidence ZIP 在停止前取得；随后会话停止、runtime reaped，活动会话列表为空且专用服务已停止。最终身份与清理见 [native-summary.json](evidence/native-summary.json)。

| 演示 | 设备与应用 | 要求保留的同次会话证据 |
| --- | --- | --- |
| Arcade | Cardputer ADV、矩阵键盘打砖块 | 实际 `a`/`d` 键盘输入、`ARCADE_KEY` 与挡板位置、画面变化、固件/运行时/源码哈希 |
| Touch Studio | CoreS3、触摸绘图 | 调色板点按与绘图区拖动、`TOUCH_STUDIO_INPUT`/颜色 marker、相应笔迹 |
| Pelican | CoreS3、骑行动画与 BMI270 | 控制器 QOM 的 `accel-x`/`gyro-z` 变化、guest IMU 状态与动画、触摸操作、前后帧及运行身份 |

三组共用本次记录的 native QEMU SHA256 `6d9af027e2f744208fc2503128f1772f436d7ca7358f9e53be597bc76800f39d`，但分别绑定应用和会话。Arcade 固件 SHA256 为 `e4b9d8cf7d6217a4c68de1dd40c6eb3ee7c9994c09fe38c849906e49d4603fd1`；Paint/Pelican 使用 `0ede40601c1e37b7ba32c87a3ca55e4da7a448f6cf52957f005763bc7c7c78e8`，分别通过同客体 UART live 提交不同源码。

Arcade 采集 79 帧、75 个不同 SHA；Paint 48 帧、15 个不同 SHA；Pelican 95 帧、90 个不同 SHA，各采样窗口约 13 秒。Arcade 的 `a`/`d` 输入分别出现 `ARCADE_KEY 97`/`100` 与挡板位置；Paint 的调色板 marker 与笔迹对应；Pelican 记录 `PELICAN_IMU_READY True`，控制器 `accel-x` 依次为 `0.75 → -0.75 → 0`，`gyro-z` 为 `65 → -65 → 0`。数值是仿真刺激，不是校准后的物理测量。Pelican 本次 `PELICAN_SPEAKER_READY False`，不作音频输出声明。

工作台的上传镜像另绑定 SHA256 `432d7845a1418b7d9078f581d493ca31390827bef37f944db9c860b674d23027`，实际完成文件选择、artifact 上传、导入、会话建立和同屏交互。代码编辑器片段随后在原 Paint 客体上运行 [workbench-live.py](code/workbench-live.py)，出现 `VIDEO_LIVE_CODE_READY` 和对应屏幕，因此沿用该 Paint 固件身份，而不是工作台上传镜像身份。工作台录制仅用临时 CSS 聚焦真实选中会话并隐藏执行标识；未替换 framebuffer、代码或输出，详见 [workbench-summary.json](evidence/workbench-summary.json)。

独立归档检查重新计算四组 evidence ZIP 的哈希并检查 ZIP 完整性，逐项复核三组时间清单中的全部帧 SHA、计数及不同帧数量，核对四份 guest 源码与捕获摘要一致。详情见 [archive-integrity-summary.json](evidence/archive-integrity-summary.json)。

姿态输入是对虚拟 BMI270 模型的数据注入，经客体的 IMU API 与应用使用。它只能证明该模拟路径的响应，不能说明物理传感器精度、时延或机械行为。模拟器屏幕的倾斜或运动不能代替控制器、应用和帧证据。

保留一次候选素材失败：缓存 Piano 镜像因 segment 与 bootloader stack 重叠而无法启动。该候选没有取得游戏运行 PASS；最终 Arcade 是另一份新演示，不以成功替换前次失败记录。

## 独立 browser-WASM 执行

本轮浏览器执行使用固定 CoreS3 fixture，属于浏览器内 `qemu-wasm`，不是网页连接原生 Device Service。开始时间 `2026-11-04T09:55:14.079Z`，完成时间 `2026-11-04T09:55:56.436Z`，浏览器版本 `157.0.8103.38`。

| 身份 | 值 |
| --- | --- |
| 平台源码 commit | `b41eba70eb61f7ddc5c41e0b981341064f9d1d1f` |
| WASM runtime source commit | `40edccac415693c5130f91c01d84176ae6008566` |
| 站点 manifest SHA256 | `3734ef55be22601dfe3aff8160a89ce3eba49a885620b361ef0ccef8092631f2` |
| WASM SHA256 | `0bd9478743d640484cad4762b9d7f7ae57a222f83ebf12a2114eb764a05194ea` |
| 浏览器 fixture 固件 SHA256 | `e9500994f4c0e1708ec35f5a46146225ac330d210a2427e1fc537c33635d9554` |
| 执行 profile | `cores3-wasm-wallclock-sdk-candidate`，`clockDivisor=1`，`oneInsnPerTb=false` |
| 帧传输 | `shared-rgb565-v1`，实际 guest 画面 `320×240` |

串口按次序出现 `begin`、`m5_ready`、`lvgl_ready` 和 `ready`。ready fixture 为 `cores3-wasm-lvgl-wallclock-v1`；后续 heartbeat 显示 `scheduler_errors=0`，但不将这一项扩展为整个启动过程无错误：此前存在一条 I2C port-not-initialized 提示。

采集窗口 `7.482 s`，记录 `50` 张画面；这只是素材采样，不是性能基准或应用 FPS。末帧 SHA256 为 `747f5192b91c1a520cccd1f9a6c8e4095e3495aab3eda714281308c9a4f5b165`。此次仅声称 ready 和实际 framebuffer；输入验证 `NOT RUN`。其它外形预览设备不会继承该结果。

停止通过 graceful exit 完成，退出码 `0`，嵌套 Worker 数降为 `0`、engine owner 不再存活、iframe 已移除。独立 DevTools 观察到的 `6` 个 Worker 最终均销毁。详见[浏览器摘要](evidence/browser-wasm-summary.json)，其中不含原始请求 URL 或浏览器 target 标识。

## 真实 3D 运镜与呈现边界

三段 3D 素材使用固定仓库的实际设备几何、材质和比例，以 Three.js/WebGL 渲染，分别为近景揭示、设备组装排列和片尾组合。摄像机、灯光与物体整体变换为介绍片的视觉设计，不能用于验证硬件属性。

每段素材 `4 s`、`1920×1080`、`30 fps`、`120` 帧，独立完整解码检查通过。CoreS3 屏幕采样 Pelican 实录，Cardputer ADV 屏幕采样 Arcade 实录，依据原捕获时间选择帧，素材哈希已核对。StickS3、StopWatch 屏幕保持黑色；Atom Matrix 不添加虚构 guest LED 输出。

这些是已捕获 framebuffer 的屏幕贴图。渲染阶段没有再次执行固件，也没有输入功能验证；其 `PASS` 只表示素材渲染与媒体检查。摄像机运动不意味着实物机械运动。详情见 [cinema-summary.json](evidence/cinema-summary.json)。

## 音轨与剪辑设计

配乐为原创程序合成的 140 BPM E minor 电子曲，不使用第三方音乐或采样。节拍间隔约 `0.428571 s`，四拍小节约 `1.714286 s`；两处 drop 为 `15.428571 s` 与 `32.571429 s`，片尾落点为 `58.285714 s`。音效与音乐分别保留。

九段中文神经男声共约 `25.45 s`，采用 `+8%` TTS 语速，没有额外 atempo 加速。语音以外留出连续的演示空间。原始 60 秒混合音轨为 48 kHz 双声道，测得 `−16.0 LUFS`、`−1.5 dBTP`；这是编码前音轨检查，不代替最终 MP4 内 AAC 的测量，也不代表人工全片听审。

最终成片为 `60.000 s / 1920×1080 / 30 fps / H.264 + AAC`，H.264 像素格式 `yuv420p`、limited range、BT.709；AAC 为 48 kHz 双声道。FFmpeg 完整解码 1800 帧，退出码 `0`。Chromium 实际播放推进 `0.612069 s`，17 次跳转无错误；最终解码关键帧、画面/字幕及独立视觉审查通过。编码后的 AAC 测得 `−16.08 LUFS`、`−0.39 dBTP`、`LRA 2.80`。

最终文件 `M5Stack-Emulator-Intro-V2-1080p.mp4` 为 `22,627,515` bytes，SHA256 `a9162b0737e98a20eebe80b0c29378a5d414e9209431f4a103c0aa7bd155d143`。上述完整解码、播放跳转及最终画面复核均绑定这份成片，见 [media-summary.json](evidence/media-summary.json) 与 [run.json](run.json)。

视觉复核后的调整均属于剪辑构图：Arcade 显示视图裁掉源帧底部 7 像素，使底部提示不再显示残缺；上传界面顶部与双运行对比画面的 native 标题完整保留。最终解码的 `7.3 s` 与 `44 s` 画面已复核标题。原始 guest framebuffer 与取证文件未改动。媒体播放/跳转的 PASS 不代表浏览器运行了影片中的任意固件；browser-WASM 结论仍仅来自前述独立执行。

## 复现方式

1. 检出上述固定平台 commit，按该版本的 [Device Service API](https://github.com/m5agent/m5stack-esp-emulator/blob/b41eba70eb61f7ddc5c41e0b981341064f9d1d1f/docs/device-service-api.md) 准备独立服务与匹配的 runtime/firmware；精确哈希以原生摘要为准，不沿用 V1。
2. 为各设备建立独立会话，经 `uiflow-live` 提交 [code/](code/README.md) 中对应程序为 `main.py`。等待应用 marker 与可辨认 framebuffer，不能只看 session running。
3. Arcade 注入键盘输入并核对 `ARCADE_KEY`；Touch Studio 通过同会话触摸和拖动生成笔迹；Pelican 通过 BMI270 的控制器 QOM 设置姿态/角速度，观察 guest 状态与画面。精确输入时间与请求内容分别见 [Arcade](evidence/arcade-summary.json)、[Paint](evidence/paint-summary.json)、[Pelican](evidence/pelican-summary.json) 的 `actions` 数组。
4. 各会话停止前获取 evidence ZIP，停止后保留历史并确认 guest 回收；只清理自建服务。
5. 浏览器测试独立使用上述站点 manifest、WASM/固件哈希与 profile，等待 `CORES3_WASM` ready 和 framebuffer，然后停止并确认 Worker 与 iframe 清理。原生输入结果不转移到浏览器运行。

运行时和固件二进制不在本记录重新分发。恢复同一执行环境需要对应合法来源资产。代码身份、来源和 MIT 声明见 [code-summary.json](evidence/code-summary.json) 与 [code/README.md](code/README.md)。

## 验收分层

| 层级 | 状态 | 边界 |
| --- | --- | --- |
| 新固件或 runtime 构建 | NOT RUN | 使用已有固定哈希资产 |
| 三组原生 guest 演示 | PASS | 实际键盘、触摸或 BMI270 控制器输入，guest marker/画面与完整清理 |
| 原生网页工作台 | PASS | 实际上传/会话 UI 与代码编辑器执行，分别绑定镜像身份 |
| browser-WASM ready/frame | PASS | 固定 CoreS3 fixture；有串口与真实帧 |
| browser-WASM 输入 | NOT RUN | 不从原生键盘、触摸或 IMU 演示继承 |
| 3D 素材渲染 | PASS | 实际模型几何与摄像机运动；不授予功能 PASS |
| 音轨源文件 | PASS | 60 秒、解码与响度检查；不代表最终视频 QA |
| 最终成片 QA | PASS | 60秒1080p30 H.264/AAC，全流解码、Chromium播放+17次跳转、最终关键帧及独立视觉审查、编码AAC响度 |
| 最终文件身份 | PASS | 22,627,515 bytes、完整SHA256与同文件QA绑定；视频本体单独交付 |
| hardware validation | NOT RUN | 未使用物理设备或测量物理属性 |

## 脱敏、风险与回滚

公开目录只保留小型派生摘要和可公开 guest 源码。原始报告身份以 SHA256/字节数绑定，公开摘要删除本机路径、服务 URL、端点、会话/进程/浏览器 target 标识、完整请求和像素数组。原始 ZIP、完整帧序列、视频、固件及运行时二进制不提交。

本次没有修改模拟器源码或持久服务配置；回滚为删除新增媒体与演示文件。任何公开结论均限定到对应固件、runtime、profile、输入与实际输出。V1 保留；Piano 候选失败保留；后续 PASS 不覆盖此前失败。

最终媒体验收与文件身份已闭合；视频本体单独交付。本记录保留 V1、Piano 候选失败与当前各执行层的边界。

