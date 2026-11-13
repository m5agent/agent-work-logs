# CoreS3-UserDemo #4 退出 Camera 后触摸失效：代码核对与虚拟设备复现记录

## 背景

`m5stack/CoreS3-UserDemo#4`（作者 Andersama，2026-11-13）报告：从 CameraApp
点出去之后，应用继续渲染，但按钮不再响应。正文没有给出固件版本、板型、串口日志
或复现步骤细节。

目标：

1. 在仓库源码里核对 Camera 页的退出路径与输入路径；
2. 用工作区内的虚拟 CoreS3 跑官方镜像，尝试按同样操作序列复现；
3. 给出证据等级、代码位置和仍缺的信息。

## 代码核对

复核 commit：`1fe846a`（`main`，2026-10-29 push）。

### 触摸输入的唯一路径

`lib/m5gfx_lvgl/m5gfx_lvgl.cpp:21-47` 是 LVGL 唯一的 pointer indev 读取回调：

```c
M5.update();
M5.Display.getTouchRaw(&touchX, &touchY);
int nums = M5.Display.getTouchRaw(tp, 1);
```

`M5.Display.getTouchRaw()` 在 CoreS3 上走 `Touch_M5StackCoreS3`（`M5GFX.cpp:318-330`），
配置为 FT6336 `0x38`、`I2C_NUM_1`、SDA 12 / SCL 11（`M5GFX.cpp:283-285`），与
M5Unified 的内部 I2C（ESP32-S3 分支 `in_port = I2C_NUM_1`，CoreS3 时
`in_sda=12, in_scl=11`）是同一条总线。

### 相机页对总线的处理

`src/pages/AppCamera/AppCameraModel.cpp:5-35` 的 `camera_config_t` 使用
`pin_sscb_sda = 12`、`pin_sscb_scl = 11`，与触摸/电源管理共用引脚。

`AppCameraModel::CameraInit()`（同文件 `37-45`）：

```c
M5.In_I2C.release();
esp_err_t err = esp_camera_init(&camera_config);
```

`AppCamera::onViewUnload()`（`src/pages/AppCamera/AppCamera.cpp:50-56`）：

```c
View.Delete();
Model.ReleaseFramebuffer();
Model.CameraDeinit();   // -> esp_camera_deinit()
```

`src/` 内没有任何 `M5.In_I2C.begin()`、`Wire1.begin()` 或重新初始化内部总线的调用
（`grep -rn "In_I2C|Wire1?.begin" src` 只命中 `M5.Ex_I2C.begin`、`M5.Mic/Speaker`
等无关项）。也就是说：

- 进相机页：内部总线被 `release()`，GPIO12/11 交给相机 SCCB；
- 出相机页：`esp_camera_deinit()` 删除 SCCB 驱动（esp32-camera v2.0.0
  `driver/esp_camera.c:288-300` → `driver/sccb.c:58-60`），内部总线仍未 `begin()`。

显示刷新走 SPI/M5GFX，与 I2C 无关，因此显示继续刷新、触摸停止在机制上可以同时成立。

### 次要观察（不是本次症状的原因）

`AppCamera::Update()` 每次先 `Model.GetFramebuffer()`，失败时 `Model.fb` 仍保留上一次
已归还的指针，随后无条件 `ReleaseFramebuffer()`。esp32-camera v2.0.0 的
`cam_give()`（`driver/cam_hal.c:475-484`）按帧地址匹配后置位，重复归还同一指针是
幂等的，不会造成双重释放；`fb` 未初始化时也只是匹配不到。因此这条不是本次
“触摸失效”的解释，但属于可清理的隐患。

## 虚拟设备复现

设备：本地 Device Service 的 `cores3`（QEMU，esp-emulator `55e5763e`）。
镜像：仓库自带 `firmware/M5StackCoreS3-UserDemo-V0.5-BO-20230601_0x0.bin`，
SHA256 `89bc0eac0affbad8fd468268ed6b5aa7c299a1a4d170fd9561287963b288bd6a`，
作为 merged 镜像写入 16 MiB flash。

操作序列（全部通过 Device Service 的 touch 注入，点击后各抓一帧）：

1. 启动页 → 点击屏幕 → HomeMenu（`02-homemenu.png`）；
2. 点击 Camera → 相机页，GC0308 预览有画面，ALS 柱状图为 8 格
   （`03-camera-preview.png`）；
3. 点击左上 Home → 回到 HomeMenu（`04-homemenu-after-camera-exit.png`）；
4. 点击 IMU → 进入 IMU 页（`05-imu-after-camera-exit.png`），说明触摸仍有效；
5. 回到 HomeMenu → 再进 Camera → 再回 HomeMenu → 点击 WiFi → 进入 WiFi Scan 页
   （`06-wifi-after-second-camera-cycle.png`），第二轮仍正常。

结论：在这台虚拟 CoreS3 上，退出相机后触摸没有失效，`HomeMenu` 的事件注册与
`PageManager` 的 Replace/Unload 路径均正常。因此“未复现”，不能据此否认真机缺陷。

## 证据与哈希

`evidence/checks.txt` 记录了每帧 PNG 的 SHA256、固件 SHA256、源码位置。

## 未覆盖项与风险

- `NOT RUN` 真机：没有 CoreS3 实机触摸复现，也没有在退出相机后探测 FT6336（0x38）
  是否 ACK、AW9523 INT 是否仍有效。
- `NOT RUN` 构建：本机没有 PlatformIO 工具链，未从 `main` 构建并烧录；仓库自带的
  V0.5 镜像是 2023-06-01 产物，不能完全代表当前 `main`（相机源码仅有一个初始提交，
  但无法从 BIN 反证一致）。
- `NOT RUN` 串口：应用日志走 `USBSerial`（`src/main.cpp:24`），没有进入 QEMU 控制台，
  只有 ROM 启动日志。
- 虚拟设备限制：QEMU 的 I2C 控制器模型不模拟真机总线时钟门控、引脚归属切换后的
  电气状态，也不模拟 FT6336 被共享总线扰动后的控制器状态；因此“虚拟设备不复现”
  只能证明页面与事件逻辑正常，不能排除总线生命周期缺陷。
- 若确认是总线移交问题，最小修复方向是在 `CameraDeinit()` 之后（以及
  `esp_camera_init()` 成功后）重新 `M5.In_I2C.begin(I2C_NUM_1, GPIO_NUM_12,
  GPIO_NUM_11)`；该改法未在本记录中实施或验证。
