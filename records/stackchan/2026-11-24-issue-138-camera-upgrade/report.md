# StackChan K151 摄像头升级可行性 — 完整分析

## 1. 问题与目标

m5stack/StackChan#138（作者 Hinrixx3026，2026-11-24T19:57Z，OPEN；首轮抓取时 0 评论，
第二轮为 2 条评论）询问能否把
K151 的 GC0308（文档标 640×480）换成 OV2640 / OV3660 / OV5640，并问了五个问题：

1. 是否存在电气与机械兼容的替换模组？
2. 是否需要自制转接板？
3. 接近/环境光传感器能否保留？
4. ESP32-S3 上现实的最大分辨率是多少？
5. M5Stack 是否有官方升级计划？

目标：在不接触实机、不修改任何仓库的前提下，用公开原理图、固件源码、组件模式表与官方文档
给出可复核的边界结论，并明确标出无法回答的部分。

## 2. 方法与取证环境

- 源码：浅克隆 `https://github.com/m5stack/StackChan`，HEAD `28b9f0c8`（v1.6.2 PR #128
  合并提交，2026-11-04）。
- 原理图：`~/Documents/m5stack-schematics-text/zh_CN/schematic/StackChan Core.md`，该文件由
  公开的 StackChan Core（CoreS3 v1.0 七页）PDF 抽取，条目带图像哈希与页码/网格。
- 组件：`esp_cam_sensor` v2.6.0（`espressif/esp-video-components` tag `v2.6.0`）源码；
  `esp32-camera` README（2.1.8，仓库 master 抓取）。
- 官方文档：`nuxt-m5-docs` 本地检出中的 `static/en/arduino/stackchan/camera.md`、
  `ltr553.md`、`static/en/core/StackChan_Core.md`。
- 设备：本机 Device Service 的设备列表（只读查询）存在 `stackchan`
  profile（ESP32-S3、16 MB flash、ILI9342C 320×240、`peripheral_status=simulated`）。

未做的事：没有 K151 实机；没有构建固件；没有对虚拟设备发起会话（原因见第 8 节）。

## 3. 主机侧接口（原理图）

`J2` 为 24-pin `AFC34-S24FIA-00`，原理图条目直接称其为“摄像头/传感子板连接器”，承载：

| 类别 | 信号 |
| --- | --- |
| 像素数据 | `CAM_D2`–`CAM_D9`（8-bit 并行，对应固件 D0–D7 = GPIO39/40/41/42/15/16/48/47） |
| 同步 | `CAM_PCLK`（GPIO45）、`CAM_VSYNC`（GPIO46）、`CAM_HREF`（GPIO38） |
| 控制 | `CAM_RST`、`CAM_PWDN` |
| 总线 | `I2C_SYS_SDA`（GPIO12）/`I2C_SYS_SCL`（GPIO11） |
| 时钟 | `CAM_MCLK`：`X2` 20 MHz ±25 ppm 3.3 V 输出，经 `R31` 51 Ω 到 J2 pin12 |
| 电源 | `AVDD`、`DVDD`、`VDDCAM_3V3`、GND |

`CAM_RST` 同时接 AW9523B 的 `P1_0`（`P1_1` 为 LCD_RST），因此复位在硬件上可由 IO 扩展器
控制；但当前固件把 `CAMERA_PIN_RESET` 设为 `NC`，并未驱动它。

关键限制：公开原理图只到 `J2`。子板的器件、FPC 引脚顺序、各路电压的具体设定值、LTR-553
的地址脚与光学开孔都不在公开页内；抽取记录明确把 `subboard_bom` 标为 `null`，并留下
`review.camera-proximity` 待确认项。

## 4. 固件通路

`M5StackCoreS3Board::InitializeCamera()`（`firmware/main/hal/board/stackchan.cc:632-675`）：

- `esp_cam_ctlr_dvp_pin_config_t`：`data_width = CAM_CTLR_DATA_WIDTH_8`，`xclk_io = NC`。
- `esp_video_init_sccb_config_t`：`init_sccb=false`、复用 `i2c_bus_`、`freq=100000`。
- `esp_video_init_dvp_config_t`：`reset_pin/pwdn_pin = NC`，`xclk_freq=20 MHz`。

`firmware/main/hal/board/config.h:42-62` 与 `firmware/sdkconfig.defaults:58-59` 固定：

```
CONFIG_CAMERA_GC0308=y
CONFIG_CAMERA_GC0308_DVP_YUV422_320X240_20FPS=y
```

因此“文档写的 640×480”是 GC0308 的传感器上限，不是当前采集分辨率：AI.AGENT 固件按
320×240 YUV422 采集；官方 Arduino camera 例程也明确 `FRAMESIZE_QVGA` +
`PIXFORMAT_RGB565` + 2 个 PSRAM frame buffer。GC0308 在 `esp_cam_sensor` 里另有
640×480@16 模式，所以“先提高现有传感器分辨率”只需要改固件配置并重新编译。

依赖解析（`firmware/dependencies.lock`）：`esp32-camera 2.1.8`、`esp_video 2.5.0`、
`esp_cam_sensor 2.6.0`、`esp_sccb_intf 0.0.9`。注意 `idf_component.yml` 写的是
`^2.4.1`，实际锁定 2.5.0。

## 5. 逐问结论

### 5.1 是否有电气/机械兼容的替换？

没有可确认的公开型号。可确认的是“主机侧接口是通用 8-bit DVP + SCCB”，因此任何 8-bit
DVP、支持 20 MHz XCLK 输入、SCCB 地址不冲突、FPC 定义匹配的模组在电气上都可能工作。
候选地址：GC0308 `0x21`（现有）、OV2640 `0x30`、OV3660 `0x3C`、OV5640 `0x3C`；
与系统 I2C 上已记录的 `0x21/0x23/0x34/0x36/0x38/0x40/0x50/0x58/0x68/0x69/0x6F/0x71`
均不冲突。

不能确认的原因是信息缺口，不是技术不可行：子板 FPC 引脚顺序、三路电源的实际电压/时序、
PWDN/RST 极性都没有公开。所谓“直插 OV2640 模组”没有依据。

### 5.2 是否需要转接板？

大概率需要。理由：

1. 24-pin FPC 的引脚定义由子板决定，不同厂家的 24-pin DVP 模组顺序不同；
2. 主板向 `J2` 送的是 `AVDD`/`DVDD`/`VDDCAM_3V3` 三路，而常见 OV 模组多为单 3.3 V 输入、
   板载 LDO 产生 core 电压；若把“裸传感器”直接接到三路电源上，电平与上电时序都要重新核对；
3. `CAM_MCLK` 是板上固定 20 MHz，不能由软件改频；模组必须接受 20 MHz 输入（OV 系列通常
   支持 6–27 MHz，但仍需按具体模组确认）；
4. 机构上还要确认镜头高度、FOV 与面板开孔，公开原理图不包含这些。

被动转接只在“引脚顺序、供电、复位极性、时钟全部一致”时成立；否则需要带 LDO/电平处理
的小板。

### 5.3 接近/环境光能否保留？

LTR-553ALS-WA 是 StackChan 的真实配置项（官方有 LTR5XX 例程，读 PS/ALS）。产品文档把它
与 GC0308 一起归为子板器件，主板原理图只画了 `J2`，没有画这两颗器件。因此：

- 若整块摄像头/传感子板被替换，LTR-553 会一起失去，除非新板保留该器件（同地址 `0x23`、
  同样的光学窗口）；
- 若只改摄像头而保留原子板，则不存在丢失问题——但前提是摄像头上游仍有独立可替换环节，
  这一点同样取决于未公开的子板结构；
- #77 报告过某台 K151 上 `0x23` 不 ACK（该 issue 已关闭且无维护者回复），说明至少存在
  批次/配置差异，替换前应先在自己机器上确认 PS/ALS 可用。

### 5.4 ESP32-S3 上的现实最大分辨率

三层上限必须分开说：

**传感器标称**（esp32-camera 2.1.8 表）：OV2640 1600×1200、OV3660 2048×1536、
OV5640 2592×1944。

**当前固件栈的 DVP 模式表**（`esp_cam_sensor` v2.6.0）：

| 传感器 | DVP 最大模式 | 说明 |
| --- | --- | --- |
| GC0308（现有） | 640×480@16（YUV422/RGB565/GRAY） | 固件选 320×240@20 |
| OV2640 | JPEG 1600×1200@12；YUV/RGB 640×480@6 | 分辨率最高 |
| OV3660 | JPEG 1280×720@12；YUV/RGB 640×480@10 | — |
| OV5640 | 仅 800×600@10（DVP）；MIPI 1280×720 | DVP 表比 OV2640 窄 |

也就是说，在 AI.AGENT 使用的 `esp_video` 通路上，换 OV5640 不会得到 5 MP，反而可能比
OV2640 更低；MIPI 模式在 StackChan 的 24-pin DVP 接口上不可用。

**内存/带宽**：8 MB PSRAM。RGB565 单帧 1600×1200 ≈ 3.8 MB，2592×1944 ≈ 10 MB，后者放不下；
5 MP 只能走 JPEG。esp32-camera 文档也明确：YUV/RGB 写 PSRAM 压力大、可能丢数据，Wi-Fi
开启时更明显，建议 JPEG。当前 320×240 YUV422 的流水线正是为这种共享预算做的折中。

结论：对 StackChan 这种同时跑显示、音频、Wi-Fi、舵机的整机，VGA 级是舒适区，UXGA 级
JPEG 是现实上限；瓶颈是共享 PSRAM/CPU 预算而不是像素数。#70 的社区结论一致：端侧实时
人脸识别在现有负载下不稳定，最终把识别移到主机。

### 5.5 官方升级计划

无公开信息。仓库、issue、文档中都没有官方摄像头升级的路线图条目；回复中明确“不代表
M5Stack 产品计划”，建议作者走官方支持/FAE 渠道。

### 5.6 是否有人成功换过

未找到公开的成功案例。仓库内与 camera 相关的讨论是 #70（把视觉放到主机）、#103
（拍照与语音并发导致音频静音），都不是硬件替换记录。

## 6. 证据强度与边界

- 证据等级：**code-level verification**。
- 依据：公开原理图抽取、锁定到 commit 的固件源码、锁定版本的组件模式表、官方文档。
- 不是 hardware validation：没有实机测量 J2 电平、复位时序、FPC 通断、镜头/机构、热。
- 不是 virtual-device validation：本机 `stackchan` profile 的摄像头是 GC0308 DVP 帧源模型，
  无法表达另一颗传感器的电气/机械/光学差异；跑它只能证明现有通路，不能证明替换可行性。

## 7. 复现命令

```bash
git clone --depth 1 https://github.com/m5stack/StackChan /tmp/StackChan-138
cd /tmp/StackChan-138
git rev-parse HEAD                       # 28b9f0c8...
sed -n '42,62p' firmware/main/hal/board/config.h
sed -n '632,675p' firmware/main/hal/board/stackchan.cc
grep -n 'CAMERA\|SPIRAM' firmware/sdkconfig.defaults
python3 - <<'PY'
import re
t=open('firmware/dependencies.lock').read()
for c in ('esp32-camera','esp_video','esp_cam_sensor'):
    m=re.search(r'^  espressif/%s:\n(.*?)(?=^  \S|\Z)'%c,t,re.M|re.S)
    print(c, re.search(r'^    version: (\S+)$',m.group(1),re.M).group(1))
PY
```

组件模式表：`https://github.com/espressif/esp-video-components/tree/v2.6.0/esp_cam_sensor/sensors`
（`gc0308`/`ov2640`/`ov3660`/`ov5640` 的 `*_format_info` 与 `*_SCCB_ADDR`）。

## 8. 未覆盖项与风险

- 实机 `NOT RUN`（无设备）。
- 虚拟设备 `NOT RUN`：模型不含可替换的物理传感器语义；且本问题核心是电气/机械兼容，
  不是运行时行为，虚拟机无法提供该证据。
- 构建 `NOT RUN`：未把 `CONFIG_CAMERA_OV2640` 等打开后编译，未验证 `esp_video` V4L2 是否
  接受 JPEG DVP 模式；若作者要走这条路，需要一次真实的构建/烧录验证。
- 子板 BOM/原理图缺失：J2 各脚功能来自主板网络名，未与实物核对；不能据此给出转接板网表。
- 批次差异：LTR-553 是否所有 K151 都贴装无官方确认。
- 产品路线图：无公开信息，回复不代答。

## 9. 2026-11-24 第二轮追问（文档索取 + VGA 模式）

作者在首条回复后新增两个问题：

1. 能否从 M5Stack 获得摄像头/传感子板原理图、完整 24-pin FPC 引脚定义与电源轨规格？
2. 只启用现有 GC0308 VGA 模式是否足以得到 640×480，还是 capture pipeline 与 buffer 也要改？

### 9.1 子板文档

不能获得，也不能代为发布。公开的 K151 资料是 11 页整机原理图（CoreS3 7 页 +
Adapter/Power/Ring/Touch 4 页），止于 `J2`，没有摄像头/传感子板页、BOM 或 pin 1–24
定义。公开页只给出：

- `J2` 信号组：`CAM_D2–D9`、`PCLK/VSYNC/HREF`、`RST/PWDN`、`MCLK`、`I2C_SYS`、
  `AVDD`/`DVDD`/`VDDCAM_3V3`/GND；
- 电源拓扑：`AVDD`/`DVDD` 来自 AXP2101 BLDO，`VDDCAM_3V3` 来自 AXP2101 ALDO，
  `X2` 20 MHz 由 `VDDCAM_3V3` 供电；
- 唯一带脚号的网络是 `CAM_MCLK` → `J2` pin 12。

子板各轨电流预算、去耦、pin 顺序均未公开；建议作者走 M5Stack support/FAE 或代理
工单，按 SKU + 批次索取「子板原理图 + BOM、J2 配对引脚定义、每轨电压/电流上限」。
可能是供应商 NDA 资料，官方也可能只给连接器级信息。

### 9.2 VGA 模式

对官方 StackChan 固件（`esp_video` 2.5.0 + `esp_cam_sensor` 2.6.0），启用 GC0308
VGA 模式对「采集尺寸」本身是必要且充分的：

- `esp_cam_sensor` 2.6.0 已有 `640×480@16` YUV422(UYVY)、20 MHz XCLK 模式；
- `esp_video` 从 `VIDIOC_G_FMT` 取 width/height，frame copy、preview、JPEG 都按
  `frame_.width/height/len` 动态分配，没有 320×240 常量；
- 因此不需要改 capture 代码，只需把 `sdkconfig.defaults:59` 的 320×240 模式换成
  `CONFIG_CAMERA_GC0308_DVP_YUV422_640X480_16FPS=y`，并确保
  `CONFIG_CAMERA_GC0308_DVP_DEFAULT_FMT_YUV422_640X480_16FPS=y` 生效（删除旧
  `sdkconfig` 或停用 320 模式，避免 default-format 仍选 320×240）。

但「可靠运行」还需验证：

- **PSRAM**：VGA YUV422 单帧 614,400 B；DVP buffer + frame copy + RGB565 preview
  峰值约 1.8 MB，QVGA 约 0.46 MB。8 MB 能放下，但要测 avatar/LVGL/音频/Wi-Fi
  初始化后的最大连续空闲块。
- **带宽/CPU**：VGA@16 约 9.8 MB/s，QVGA@20 约 3.1 MB/s；再加 640×480 YUV→RGB
  preview 与更大 JPEG。这是可能影响音频/avatar 的部分，需在音频播放 + 动画 +
  Wi-Fi 连着的情况下测，而不是只拍一张。
- **流式 vs 静态**：DVP 路径当前只申请 1 个 V4L2 buffer；静态拍照没问题，连续
  VGA 流会把采集和消费者串行化并丢帧，需要改 buffer 策略。
- **预览**：屏幕 320×240，`SetPreviewImage` 按宽度缩放，640×480 会显示为
  320×240，无需改代码；但要确认 LVGL 缩放和 6 秒预览缓存不会多留一份全尺寸缓冲。

若作者走官方 Arduino/`esp32-camera` 例程，另有两点：

- 例程 `setup()` 里的 `set_framesize(..., FRAMESIZE_QVGA)` 会覆盖
  `camera_config.frame_size`，必须一起改/删；
- `pushImage(0, 0, 320, 240, fb->buf)` 在 VGA 下只是左上角裁剪，不是缩放预览；
  2 个 RGB565 VGA PSRAM buffer 约 1.2 MB，保留 `fb_count=2` 或改 JPEG。

### 9.3 证据等级

- StackChan 固件路径：**code-level verification**（固定 commit 的 sdkconfig、
  board camera init、esp_video/esp_cam_sensor 源码与模式表）。
- 传感器 VGA 数据点：**virtual-device validation**（AtomS3R-CAM，QEMU
  `m5atoms3rcam`，`esp32-camera` 路径，VGA 640×480 / 614,400 B，与 host oracle
  一致）；它不等同于 StackChan `esp_video` 路径。
- StackChan 虚拟设备 VGA：`NOT RUN`。本机 `stackchan` profile 的 `m5_lcd_cam`
  固定 320×240，且 `m5sw_gc0308_bind_lcd_cam` 只接到 AtomS3R-CAM，无法在不改
  模型的情况下表达 VGA。
- 实机：`NOT RUN`（无 K151）。
- 构建/烧录/PSRAM/音频实测：`NOT RUN`。

### 9.4 新增证据文件

- `evidence/09-followup-context.txt`
- `evidence/10-vga-config-and-buffers.txt`
- `evidence/11-atoms3r-cam-vga-record.txt`
- `evidence/12-reply-followup.md`
