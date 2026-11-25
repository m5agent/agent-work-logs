# 原例程补跑

基线使用相同正式资料及 Arduino 板包配置。切换到新锁定 WASM `9c37ace1…1372` 后，按原例执行剩余 Cardputer-Adv 直达 Arduino 例程。保留旧模型失败与新入口结果。

- Display 和 Keyboard 的真实输入和图形见[板型探测专项](../2026-11-25-board-probe-and-guest-reset/README.md)。Quick Start 原库内示例也在新构建中显示动画。
- Battery 和 IMU 运行后分别显示数据。麦克风绘出 REC 初始状态。没有施加可校验的电池或 IMU 注入，也没有验证录放的真实 PCM 内容。
- IR NEC 没有得到可读应用帧及控制器波形。默认 SD 相关程序仍需素材。挂载卡后，最新库的 SD 例程有 SPI 通信和新帧，当前图像文字可读性没有通过。较旧固定库和 8 MiB 的文件读写已独立通过。历史 Speaker SD WAV 镜像在无卡测试中未交出正常 QEMU quit 回执，备用路径释放了实际 Worker。
- 新 WASM 的原 Button 例程采用板包默认 USB CDC 时，两次输入未得到预期串口标记。其中一次记录 `Stack canary watchpoint triggered (ipc1)`；同版本第二次没有该错误。相同源码只切换 `USB CDC On Boot: Disabled`，合并镜像 `111323ee…78cd`，真实 Boot 按下和释放后分别观察到 `Button A Pressed`、`Button A Released`。两套构建三次退出码 0，全部 Worker 回收。上下偏差的具体根因与默认硬件 USB 通路待排查。

这组复验使用 Chrome 和真实来宾；物理 RF、声学、USB 或电气波形没有测试。摘要省略环境地址和原始完整日志，保留原始文件哈希。
