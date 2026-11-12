## 现象

PaperColor（ESP32-S3，`m5papercolor`，400×600 EPD）上运行官方厂测固件 **PaperColor_Factory_Code**（M5Burner `1897200000000000148`，SHA-256 `a3f5ca4ae89d…`）时，guest 的 TinyUSB 设备栈初始化稳定失败：

```
check_dwc2 183: ASSERT FAILED
dwc2_core_init 221: ASSERT FAILED
dcd_init 405: ASSERT FAILED
tud_rhport_init 559: ASSERT FAILED
tusb_rhport_init 103: ASSERT FAILED
E (2404) tinyusb_task: Init TinyUSB stack failed
E (7394) tinyusb_task: Task wasn't able to start TinyUSB stack
E (7394) TinyUSB: tinyusb_driver_install(190): Init TinyUSB task failed
E (7394) hal_storage: tinyusb_driver_install fail: ESP_ERR_TIMEOUT
```

固件随后继续运行（`Startup success`），但依赖 USB 存储/串口的功能不可用；`Cannot open dir: /data` 也和 USB 挂载失败相关。

## 复现

- 设备服务会话（矩阵样本）：`8f6daabab4744a89afe0c4d6f21b3a90`（PaperColor 官方厂测，运行 ~68 s）
- 同固件在另一次复跑中还触发过 QEMU host 断言（见 #217），但本问题是**每次都会出现的 guest 侧 TinyUSB 初始化失败**。
- 串口全文：矩阵缓存 `papercolor-1897200000000000148-serial.log`，关键行如上。

## 分析

`check_dwc2` / `dwc2_core_init` 是 ESP-IDF TinyUSB DCD 对 USB OTG 控制器寄存器状态的自检。断言说明模拟器的 dwc2 寄存器读数与驱动预期不符（控制器未接线、未复位或寄存器未建模）。StickS3 有独立的 USB device-mode 验收通道（`tests/firmware/sticks3_usb_otg`），PaperColor 目前没有任何 USB 配置或验收。

## 影响

- PaperColor 厂测固件无法完成 USB 相关自检；任何使用 TinyUSB（CDC/MSC/HID）的 PaperColor 固件都不可验证。
- 失败以 guest assert 形式出现，容易被误判为固件问题。

## 期望 / 验收

1. 明确 PaperColor 的 USB OTG 建模状态：要么按板级接线实现 dwc2 device-mode（至少让 `tusb_rhport_init` 成功、枚举出描述符），要么在设备 profile 中显式禁用并在会话里报告 `usb: not-supported`，不要让 guest 拿到半初始化控制器。
2. 增加一个 PaperColor USB smoke：`tusb_rhport_init` 成功或显式 not-supported；若实现，完成一次 CDC 控制传输。
3. 回归：既有 PaperColor UI 用例与 StickS3 USB OTG 用例不退化。

## 边界

- virtual-device 验证；不涉及 USB 电气、信号完整性或真机枚举。
