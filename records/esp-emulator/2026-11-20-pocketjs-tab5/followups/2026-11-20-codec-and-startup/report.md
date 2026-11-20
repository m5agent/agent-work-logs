# Pocket M5 Tab5 原版修复报告

## 范围与根因

目标是让 Pocket M5 v0.1.4 的完整镜像正常通过 Device Service 导入，让原版 Tab5 Demo 跨过启动时的音频依赖。下载 BIN SHA-256 为 `26d7bb07fc3e35b759d5a1f2acddef675957d808bf7130b3eb975c6a36f2b99e`，规范化为 16 MiB 后为 `814ffdcc234d60f951c34c39cb1830bc4b6b5497ba209f0dc0463dc79f3ea593`。[发布版本](https://github.com/pocket-nexus/pocket-m5/releases/tag/v0.1.4)

- 静态审查将固件中的 URL 模板当成可解析的 IPv6 URL，异常传播到导入接口。补丁跳过不可解析的候选字符串，保留有效的 IPv6 地址、凭据扫描和原有端口模板检查。
- 原 GT911 配置缺少 ES8388、ES7210 的板上 I²C 控制模型。旧 codec Part 还有 ES7210 `0x15` 寄存器缺口。音频资源初始化失败时，Tab5 Demo 的 `pocket_audio_install` 返回错误，launcher 报 `did not boot`。
- 新 Part 以实际 GPIO31/32 I²C 数据面处理地址 `0x10`、`0x40`，新增 ADC1/2 静音控制寄存器 `0x15` 和 `0x00` 复位值。Device Service 的 `M5_TAB5_GT911_PART` 可以选择新 Part。原 UserDemo 专用数字音频 API 准入保持原有固件约束。[ESP Codec Dev v1.5.11](https://components.espressif.com/components/espressif/esp_codec_dev/versions/1.5.11/readme)

## 复现与证据

1. 在 [m5stack-esp-emulator 固定基线](https://github.com/m5agent/m5stack-esp-emulator/tree/cc25a8a8ac083e00608d591281289f1452cc75ac) 应用 `patches/0001-pocket-m5-tab5-codec-control.patch`。按 Part README 运行 Rust `1.88.0` 加 `wasm32-unknown-unknown`，执行 `python3 platform/esp-parts/tab5-gt911/build.py --codec-control --output "$PART_DIR"`。两次构建的 WASM SHA-256 均为 `9f83038994925b3aa8482d63c13f47c771277219c15377911a855aebdfa6b56d`。
2. 用独立 Device Service 状态目录，启用原生 DSI，配置 `M5_TAB5_DSI_BOARD=gt911-ili9881c`、`M5_TAB5_GT911_PART` 和两个镜像所需的精确准入哈希。原版通过 `POST /api/v1/firmware/import`，原应用字节未改动。展示通过的案例使用原服务的 C6 `2.12.6` 配置。
3. 桌面就绪后在原始 720×1280 帧坐标点按 `(97,1175)`。GT911 读回 8/8 报告。串口确认两个 codec 于 44.1 kHz 成功初始化、Tab5 Demo worker 启动并标识 IMU 就绪。原生 DSI 画面从桌面进入硬件面板。此会话无堆断言或重启。
4. 独立 Unit Swap 会话在桌面点按 `(99,959)`、`(42,120)`、`(360,72)`。三个动作得到控制器 ACK，依次打开应用、显示 `EXT 5V off`、返回桌面。此会话曾出现两次 TLSF 断言及复位，交互发生在复位后的运行阶段。EXT 5V 是该应用的界面状态。
5. 给独立诊断会话的 esp-emu 添加 `--cosim-log` 和 `--i2s-wav --i2s-instance 1`，保持镜像和 GT911 Part 不变。确认 ES8388 的 108 项事务、ES7210 的 274 项事务均 ACK，ES7210 `0x15` 的读回为 `0x00`。I²S1 生成 44.1 kHz 双声道 s16le，非零样本 29,612，数字峰值 9,535。此诊断会话也保留了先前一次复位。原版 UserDemo V0.4 使用相同 Part 和原有 `speaker_capture` 入口，实际点按 Music Test → Play，记录 48 kHz 双声道、255,835 个非零样本。
6. 使用 Pocket M5 发布版的 Unit Swap 应用源码与其锁定的 PocketJS `806ac202`，按 `tab5-home` 运行 `pocket compile`。`.pocket` 输出 SHA-256 `2ae507d913e814ef3e074126f1c0ae46beba8f43c88270163bb0e642f9dd1b33`，在原版镜像中找到完整且唯一的逐字节匹配。
7. 每次在停止前取 evidence ZIP，终态 `stopped`，可写 Flash 与 companion socket 释放。ZIP、串口和原帧哈希见 [脱敏摘要](evidence/virtual-device.summary.json)。

## 剩余冷启动问题

原 C6 `2.12.6` 与原版主机的 ESP-Hosted `3.0.10` 不匹配。为区分版本因素，用 Espressif `esp_hosted` `3.0.10` 的 `examples/wifi/sta/cp` 在 ESP-IDF `6.0.2` 构建 ESP32-C6 coprocessor，使用官方 `CONFIG_EH_TRANSPORT_CP_SDIO_MODE_STREAM=y`，合并镜像供隔离 Device Service 临时替换原 C6。P4 仍运行同一原版 BIN。三个会话均记录到版本匹配与 SDIO/RPC V2 协商。两个会话各出现 4 次软件复位。首个 4 次 `block_trim_free` TLSF 断言，第二个 3 次相同断言；第三个进入 Demo，未观察到断言或软件复位。后续定位需要取得 P4 后端的堆写入与跨核锁观察。版本因素对照无法关闭该待办。[Espressif 3.0.10 组件](https://components.espressif.com/components/espressif/esp_hosted/versions/3.0.10/readme)

本次为虚拟设备验收。没有用相关数据判断真机声学、Wi-Fi 数据面、外接 Unit 供电、RTC 或浏览器表现。证据采集使用隔离实例。常驻服务保留原配置。回退源码改动可逆向应用补丁，回退 Part 配置使用原合格 GT911 模块。
