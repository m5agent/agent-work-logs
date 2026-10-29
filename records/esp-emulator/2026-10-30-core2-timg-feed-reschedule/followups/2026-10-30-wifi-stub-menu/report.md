# Core2 legacy WiFi stub menu follow-up 报告

## 背景

- 来源：`RUNTIME-03` legacy UIFlow 启动。
- 现象：原厂镜像在 WiFi 配置/UI 路径长期等待，且先前证据无法区分
  display/LVGL 是否仍阻塞。
- 目标：保留正常 guest display/DMA/QOM 路径，只隔离 WiFi 配置行为，
  验证完整启动菜单是否能够绘制。

## 结论

- 状态：`PARTIAL`。
- 关键判断：当前 display/LVGL/menu 路径已经可渲染完整 Core2 主菜单。
- 改动范围：诊断 VFS 在 `sys.modules` 中注入 `wifiWebCfg` stub；
  `config_by_web()` 返回 true。未伪造 panel 像素、SPI/DMA transaction、
  QOM 输入或 Python interpreter 行为。

原厂镜像专用 `wifi` 分区为空，stub 绕过了真实配置生命周期，因此不能
作为原厂 `RUNTIME-03` PASS。

## 证据

### 运行条件

```text
device=core2
machine=m5core2
runtime=qemu-wifi
profile=core2-openmac
icount shift=2
per_vcpu_cap=disabled
diagnostic_wdt_disabled=true
```

### 串口

```text
BOARD NAME: M5STACK-CORE2
APIKEY: 7621FAE2
CORE2_LEGACY_ORIGINAL_BOOT_START
CORE2_LEGACY_ORIGINAL_BOOT_DONE
CORE2_LEGACY_WIFI_STUB_INSTALLED
CORE2_LEGACY_WIFI_STUB_CONFIG_BY_WEB
```

### 最终帧

```text
320x240
nonblack_pixels=76760
unique_colors=417
png_sha256=a4f683468cfb9edc70468efaabd23c226abbed7a3cdeaf6a397cab09c52a6078
```

画面包含 UIFlow 标题、Core2 版本以及 App/Flow/Setup 三个菜单项。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | diagnostic QEMU source rebuild |
| transport | `PASS` | real Device Service session; guest QEMU Wi-Fi backend |
| device_response | `PARTIAL` | BOARD/APIKEY and boot.py reached; WiFi config stubbed |
| data_behavior | `PASS` | panel/DMA/QOM path unchanged; real guest display commands |
| visual_or_physical | `PARTIAL` | complete virtual menu frame; physical display `NOT RUN` |
| review | `PASS` | docs contracts and project snapshot |

## 验证边界

本记录是 virtual-device validation。它不证明真实 WiFi 配置、RF、
normal-WDT 稳定性、电气、物理 cache/PSRAM 或硬件行为。`RUNTIME-03`
继续开放。

## 风险与回滚

只新增诊断文档和 fixture 说明；产品代码回滚为 revert `1b2a376e`。
