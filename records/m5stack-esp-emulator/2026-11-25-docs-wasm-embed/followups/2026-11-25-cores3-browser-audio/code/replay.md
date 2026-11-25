# 复跑 CoreS3 文档音频

准备当前集成分支的完整源码构建和项目固定的 LittleFS 组合器。以下命令使用新的缓存目录。已有公开虚拟设备运行结果的精确 SHA-256 见 [浏览器摘要](../evidence/browser-audio.summary.json)。重新构建后应保存新的清单和 WASM SHA-256 并复跑两例。

    python3 platform/tools/bootstrap_qemu_browser_runtime.py --check
    python3 platform/tools/bootstrap_qemu_browser_runtime.py --cache work/audio-build --output work/audio-runtime --jobs 2
    python3 platform/tools/build_public_site.py --output work/audio-site --qemu-runtime work/audio-runtime --littlefs-runtime "$LITTLEFS_RUNTIME" --qemu-sd-media "$DEMO_SD_MEDIA" --qemu-cores3-audio

示例 microSD 目录使用 #253 的外部清单格式，包含准确绑定 CoreS3 WAV 固件 SHA-256 的 64 MiB FAT32 原始镜像。浏览器需要在一台独立端口的静态站点运行。允许站点的 Service Worker 提供隔离，并确认页面已处于跨源隔离状态。使用桌面 Chromium，进入 CoreS3 的浏览器运行模式。保持前台标签页。

1. 验证原始合并固件为 16,777,216 字节及 SHA-256 22eb0ffce846a6175de97e2c2f82c02bbef092724874b317297cf5c95751bff5。原始 Sketch SHA-256 341749ed7942ee611f123483652da13f152167ccac79bcd231c24b817b399994。匹配的 FAT32 镜像 SHA-256 93a9550a6d325ec8be0d9710eb7c079af24ba7d5ffb8c5c2db423c26e6fb1233，根目录中的 sample-12s.wav 为 384,044 字节及 SHA-256 f24b12a40e74bc9f3dc0977f127d55923b7d73183445ad2a9c23f1410f65604c。
2. 选择本地固件、上传该 BIN、勾选播放模拟器音频，然后点击 Start。确认串口没有致命错误，屏幕出现并更新 WAV 播放。确认借手势恢复的 48 kHz AudioContext 连接实际输出目标。对连接的 Worklet 添加独立浏览器 AnalyserNode 并采集时间序列与频谱。预览中观察到 575,037 个非零数字采样，且数字音量较低。点击 Stop 执行正常退出并确认上下文、iframe 和 Worker 清理。
3. 选默认 UIFlow 本地 MicroPython 编程。勾选音频并点击 Start。校验编程基底及组合固件，等待 M5_UIFLOW_WORKBENCH_READY。用工作台导入原始 cores3_mic_example.py，校验 1,192 字节及 SHA-256 dc6979cf1209ead19085bb97450c91e644bbf45ae28d0d2faa702f189d7e0a8e，再点击代码 Run。
4. 观察录制、播放及完成画面，确认 AudioContext 中约 440 Hz 的虚拟回放。精确种子为单声道 16 kHz signed-16 LE，使用 round(12000 × sin(2π × 440 × i / 16000)) 生成 16,000 个采样。SHA-256 为 97baea0a56c5b48504ea4b65b41148c6d55dc494d22652b3db7cedb295876efe。用编辑器真正执行中断，等待同一会话应答。然后点 Stop 并重复清理检查。
5. 参考 [实际结果](../evidence/browser-audio.summary.json)，分别记录固件输入和运行 SHA-256、WASM 和清单、虚拟时钟配置、屏幕 RGB565 摘要、Web Audio 输出和清理。物理主机声学结果需要另行执行实验。

两条命令用于独立的主机契约检查。

    node platform/tests/test_public_qemu_audio.mjs
    PYTHONPATH=platform/tools python3 -m unittest discover -s platform/tests -p test_public_site.py

[Arduino 原始例程](https://docs.m5stack.com/en/arduino/m5cores3/wav) · [UIFlow2 Mic 固定源码](https://github.com/m5stack/uiflow-micropython/blob/a61a29409f09f1f4bebae05e15c4bd6dcc4956b6/examples/hardware/mic/cores3_mic_example.py) · [公开 microSD 格式与先前证据](https://github.com/m5agent/m5stack-esp-emulator/issues/253)
