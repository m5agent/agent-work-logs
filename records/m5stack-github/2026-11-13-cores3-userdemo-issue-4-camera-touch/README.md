# m5stack/CoreS3-UserDemo #4：退出 Camera 后画面继续刷新但触摸失效

- 日期：`2026-11-13`
- 结果：`PARTIAL`（虚拟设备未复现；代码层发现相机页单向移交内部 I2C 总线）
- 工作类型：`issue` + `review`
- 问题来源：https://github.com/m5stack/CoreS3-UserDemo/issues/4
- 复核对象：`m5stack/CoreS3-UserDemo@1fe846a`（`main`）
- 环境：macOS；本地 Device Service（QEMU `cores3` 后端，esp-emulator `55e5763e`）；
  固件为仓库自带 `firmware/M5StackCoreS3-UserDemo-V0.5-BO-20230601_0x0.bin`
- 证据等级：`code-level verification` + `virtual-device validation`（症状 **未复现**）

## 结论

相机页会把 CoreS3 内部 I2C（触摸 FT6336、AXP2101、AW9523 所在总线）从 M5Unified
手里拿走：`AppCameraModel::CameraInit()` 在 `esp_camera_init()` 前调用
`M5.In_I2C.release()`，而 `AppCamera::onViewUnload()` 只调用 `esp_camera_deinit()`，
之后没有任何 `M5.In_I2C.begin()` / `Wire1.begin()` 把总线交还。显示走 SPI，触摸
（LVGL 唯一输入源）走这条被释放的总线，因此“画面继续刷新、触摸无响应”在代码层
有明确的可疑路径。

但该症状没有在虚拟 CoreS3 上复现：用官方 V0.5 镜像连续做两轮
`HomeMenu → Camera → Home`，随后仍能进入 IMU、WiFi 页面。说明页面切换与事件回调
本身没有问题，真机上的失效更可能落在共享总线的恢复/触摸控制器状态，需真机与
作者环境信息确认。

## 关键证据

- `evidence/03-camera-preview.png`：Camera 页预览与 ALS 柱状图正常（说明进入相机后
  内部 I2C 读取仍可用）。
- `evidence/04-homemenu-after-camera-exit.png`：退出 Camera 后回到 HomeMenu 正常。
- `evidence/05-imu-after-camera-exit.png`、`06-wifi-after-second-camera-cycle.png`：
  退出相机后触摸仍可点击其它应用，第二轮进出相机后依然正常（未复现）。
- `evidence/serial-console.txt`：启动到应用运行的串口；应用日志走 USBSerial，未进
  QEMU 控制台（`NOT RUN`）。
- `evidence/checks.txt`：帧哈希、固件 SHA256、代码位置。

## 文件

- `report.md`：完整分析、复现过程与限制
- `run.json`：结构化记录
- `evidence/`：截图、串口与校验清单

## 未覆盖项

- 无 CoreS3 实机，未做真机触摸复现（`NOT RUN`）。
- 未用 PlatformIO 构建 `main` 后烧录（环境无 pio 工具链；`NOT RUN`）。
- 未在真机测量退出相机后 FT6336（0x38）是否仍 ACK、AW9523 INT 是否正常。
- 虚拟设备不复现不等于缺陷不存在：QEMU 的 I2C 模型不模拟真机总线时钟门控/引脚
  归属与触摸控制器被共享总线扰动的状态。
