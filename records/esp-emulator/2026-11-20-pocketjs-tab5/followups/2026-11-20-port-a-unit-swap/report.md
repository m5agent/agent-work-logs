# Pocket M5 Unit Swap 原生 Tab5 Port A 复验

## 目标与范围

验证 PocketJS Applet 能以固件的正常软件 I²C 驱动识别并使用两种 M5Stack Unit。设备为 Tab5 `gt911-ili9881c`，通过 Device Service 1.99.5 与 esp-emu 1.1.0 原生运行。目标 Applet 是 [Pocket M5 v0.1.4 自带的 Unit Swap](https://github.com/pocket-nexus/pocket-m5/tree/db98ac45916a8ec4a2d85fa2a7e9cb09fa95bd1c/apps/unit-swap)，固件下载后由 Device Service 扩展到 16 MiB，分区内容保持原版。App 使用 PocketJS 的 worker、Port A 节点和屏幕组件。

## 隔离运行配置

可视模型用于说明设备与 Unit 的外观。固件读数来自隔离采集使用的 ESP Part 和原版驱动。该 Part 在 G53 SDA、G54 SCL 上监听 GPIO 边沿、接收地址和数据位，并驱动 SDA 应答与读数据。SHT30 的转换数据带 CRC，QMP6988 沿用模拟器 ENV III 的合成校准与寄存器布局。RCWL-9620 路径接收 `0x01`，等待 120 ms 虚拟时间并返回三字节微米值。卸下 Unit 时模型停止回应对应地址。该测试配置覆盖这里的工作流和用到的命令。

第一次 Part 构建为 147,532 字节，超过 144 KiB 的 Device Service 产物上限，镜像未进入来宾阶段。改用 Cargo `opt-level = "z"` 后为 136,013 字节。隔离副本以精确 SHA-256 放行 Part，既有准入大小与哈希核验保留。

## 重放方法

1. 在模拟器源码 `cc25a8a8ac083e00608d591281289f1452cc75ac` 上应用[先前 codec 修复](../2026-11-20-codec-and-startup/patches/0001-pocket-m5-tab5-codec-control.patch)，再应用[本次采集补丁](patches/0001-tab5-port-a-unit-capture.patch)。`git apply --check` 已在相同源码内容的隔离 checkout `0b29e2117b569007cf9508723109c12a506e5994` 执行。
2. 在匹配的 Rust 1.88.0 和 `wasm32-unknown-unknown` 环境，运行 `python3 platform/esp-parts/tab5-gt911/build.py --codec-control --output "$PART_DIR"`。保持 ESP Part SDK 锁定版本。将输出 Part 设置为 `M5_TAB5_GT911_PART`，用 [Device Service API](https://github.com/m5agent/m5stack-esp-emulator/blob/cc25a8a8ac083e00608d591281289f1452cc75ac/docs/device-service-api.md) 在隔离会话导入原版 Tab5 发布镜像。固件、运行器、Part 的 SHA-256 见[证据](evidence/virtual-device.summary.json)。
3. 通过 `/input` 在来宾启动器点击 Unit Swap。横屏坐标 (320, 99)，原始触控坐标 (99, 959)，确认 8/8 份 GT911 报告。待串口出现 `unit-swap worker: porta node declared`。
4. 对本次运行器的控制通道按下列顺序发送 `part gt911 input unit:<stimulus>`。在各阶段读取 `part gt911 state`，保留串口与来宾截图。空场景和卸下阶段的模型数据字节数为零。结束前导出证据 ZIP，校验后停止会话（`purge=0`），不保留可写 Flash。

| 刺激 | I²C 地址应答次数 / 模型发出的数据字节数 | 来宾屏幕 |
| --- | --- | --- |
| `none` | 0 / 0 | Plug a unit into Port A |
| `env:22.5:48:101320` | 125 / 293 | 22.5 °C、48.0% RH、1013.2 hPa |
| `env:31.5:67:100800` | 90 / 216 | 31.5 °C、67.0% RH、1008.0 hPa |
| `none` | 0 / 0 | ENV III removed、waiting |
| `sonic:1200` | 153 / 225 | 120.0 cm、最近回波 1200 mm |
| `sonic:560` | 128 / 192 | 56.0 cm、最近回波 560 mm |
| `sonic:220` | 131 / 195 | 22.0 cm、最近回波 220 mm |

## 结果与限制

来宾串口确认两种 Unit 已挂接，依次报告 1200、560、220 mm。ENV III 第二组数值由同一会话的来宾屏幕读取。全程采集 314 个帧样本，151 个不同哈希。冷启动时出现一次 P4 TLSF 断言复位，Applet 启动后该窗口内没有再次触发。虚拟 GPIO 和 I²C 应答用于验证软件行为。未验证物理距离、电气热插拔、总线时序、真机和浏览器。脚本化虚拟挂接专用于采集。常驻服务和公共模拟器版本保持原配置。
