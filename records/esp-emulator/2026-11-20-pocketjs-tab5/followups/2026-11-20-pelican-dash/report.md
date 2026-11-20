# Pelican Dash 与 Grow Room 快剪验证

## Applet 与来宾会话

Pelican Dash 使用 12 个 256×128 的烘焙帧播放鹈鹕骑车。按下 Tab5 屏幕右上控制区触发 1×／2× 切换。App 使用 TypeScript、Solid、PocketJS 的原生辅助屏组件和触控接口，画稿源于[独立的鹈鹕 SVG 动画](https://github.com/m5agent/agent-work-logs/tree/6c86aaeb270500fb0681a67f3692846056d5efe3/records/svg-animation/2026-11-03-pelican-cycling)。

1. 用 Bun 1.4.2，按 PocketJS `806ac202141ece274f47c938c2899ffe8d30921d` 和 [Pocket M5 v0.1.4 Tab5 host config](https://github.com/pocket-nexus/pocket-m5/blob/db98ac45916a8ec4a2d85fa2a7e9cb09fa95bd1c/programs/m5stack-tab5/pocket.host.config.ts) 执行 `pocket compile`。编译纳入 12 张烘焙图像，独立哈希确认均不同。得到 1,853,912 字节的包。
2. 复用 [Grow Room 的 LittleFS 安装路径](../2026-11-20-grow-room/report.md)。只改发布镜像副本的 `storage` 分区并校验包；原版应用字节保持一致。创建独立 Device Service 会话，经 GT911 在启动器坐标 `(106,99)` 点击 Pelican Dash。
3. 待 `PELICAN_DASH ready speed=1`，在 Tab5 横屏坐标 `(1042,69)` 点击两次，中间留出一个加速观测窗口。两次均为 8/8 GT911 报告确认。串口依次记下 `speed=2` 与 `speed=1`。采集 150 个相邻去重的 720×1280 RGB565 来宾帧；裁出动画区后，在加速前、加速后分别观察到 21、26 个不同哈希。该计数受采样时段影响，用于证明两种模式均有实际动画变化。快剪取其中 120 帧，保留首次点击与屏幕状态变化的先后。
4. 从同一会话拿到证据 ZIP、校验 CRC、停止并释放可写 Flash。固件、Applet、运行时和控制器摘要见[证据](evidence/virtual-device.summary.json)。

最初烘焙重试修正了资源位置、目标纹理尺寸及取景。标准原生配置仍可能复现之前的 P4 TLSF 断言或黑屏。本次成片的 Pelican Dash 段使用断开 ESP-Hosted 的隔离原生会话，软复位后 DSI 恢复，Applet 就绪后该会话内未再次复位。采集读取同一个原生 MIPI-DSI 接收器的 RGB565 帧。用于拍摄的快速读取与失效恢复步骤仅作用于隔离实例。

## 镜头与说明

用[现有 Grove 线缆模块](https://github.com/yuyun2000/m5stack-models/blob/de6cddc065674ecb53bba29c7fe90d9ab4ee32f7/docs/GROVE-CABLE.md)将两端安装在 Tab5 Port A 和超声波 Unit 的插座坐标上。该模块为 HY2.0-4P 双插头和黑／红／黄／白四芯。将超声波 Unit 的走线端移到水箱右上方。对补水段的 366 个输出姿态采样四根线的路径及插头包络，线管表面距水箱保守包络的最小间隙为 11.53 模型毫米，两端插头也全部避开包络。该测试面向三维场景。

Grow Room 的升温和补水继续采用[原先已验证的独立会话](../2026-11-20-grow-room/)的输入、实录和原始响应时间，主剪只压缩操作前后停顿。水箱水面和输入控件为三维演绎。三个演示分别覆盖原版驱动所走的 GT911 触控、Port A GPIO 软件 I²C 与 MIPI-DSI 帧输出。工作没有验证实体水箱、电气热插拔、物理线缆装配、浏览器 WASM 或真机。
