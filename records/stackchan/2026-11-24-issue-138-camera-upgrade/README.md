# StackChan Issue #138 K151 摄像头升级可行性

- 日期：`2026-11-24`
- 结果：`REVIEW`
- 工作类型：`issue`
- 问题来源：https://github.com/m5stack/StackChan/issues/138
- GitHub 回复（首轮）：https://github.com/m5stack/StackChan/issues/138#issuecomment-7143018501
- GitHub 回复（第二轮）：`PENDING`
- 源码版本：`m5stack/StackChan @ 28b9f0c8bd6acd81cb3c70f1a93c3e373b39d400`（v1.6.2 main）
- 依赖：`esp_video 2.5.0`、`esp_cam_sensor 2.6.0`、`esp32-camera 2.1.8`
- 环境：macOS，源码与公开原理图/文档只读检视；无 StackChan 实机；未构建固件

## 结论

K151 的摄像头位于 `J2` 24-pin `AFC34-S24FIA-00` 摄像头/传感子板上，主机侧是标准 8-bit
DVP + SCCB（`I2C_SYS` 100 kHz）、固定 20 MHz 外部 XCLK、三路供电（`AVDD`/`DVDD`/
`VDDCAM_3V3`），因此换用 OV2640/OV3660/OV5640 一类 DVP 模组在电气上不是不可行；但子板
FPC 引脚定义与 BOM 未公开，公开原理图止于 `J2`，无法确认任何“直插兼容”的型号，通常需要
转接板或自制子板。固件当前只启用 GC0308、按 320×240 YUV422 采集（官方 Arduino 例程
同为 QVGA），并非文档里的 640×480。分辨率上限受三件事分别约束：传感器标称、当前
`esp_cam_sensor` DVP 模式表、8 MB PSRAM 与共享带宽；在当前固件栈里 OV5640 的 DVP 上限
（800×600）反而低于 OV2640（JPEG 1600×1200）。LTR-553ALS-WA 与摄像头同属子板器件，
换子板会一并失去，需在新板上保留。官方升级计划无公开信息，不作推断。

首轮结论层级为源码级验证（schema + firmware + 组件模式表 + 官方文档），实机与虚拟设备均未执行。
第二轮的 StackChan VGA 结论仍为 code-level verification；GC0308 VGA 模式另有 AtomS3R-CAM
虚拟设备数据点（不同采集栈），详见下文。

## 关键证据

- 原理图：`J2` 24-pin 承载 `CAM_D2-D9`、`CAM_PCLK/VSYNC/HREF`、`CAM_RST/PWDN`、
  `CAM_MCLK`、`I2C_SYS_SDA/SCL`、`AVDD`/`DVDD`/`VDDCAM_3V3`；`CAM_MCLK` 由 `X2` 20 MHz
  经 `R31` 51 Ω 固定输入；`CAM_RST` 接 AW9523B `P1_0`。
- 固件：`firmware/main/hal/board/config.h:42-62`（`XCLK/RESET/PWDN/SIOD/SIOC = NC`，
  20 MHz 外部时钟）；`stackchan.cc:632-675`（`CAM_CTLR_DATA_WIDTH_8`、SCCB 复用系统 I2C
  100 kHz）；`sdkconfig.defaults:58-59`（`CONFIG_CAMERA_GC0308=y`，YUV422 320×240@20）。
- 组件：`esp_cam_sensor` v2.6.0 DVP 表 —— GC0308 640×480@16、OV2640 JPEG 1600×1200@12、
  OV3660 JPEG 1280×720@12、OV5640 仅 800×600@10；SCCB 地址 GC0308 `0x21`、OV2640 `0x30`、
  OV3660/OV5640 `0x3C`。
- `esp32-camera` 2.1.8：OV2640/OV3660/OV5640 标称上限 1600×1200 / 2048×1536 / 2592×1944；
  YUV/RGB 受 PSRAM 带宽限制会丢帧，建议 JPEG。
- 官方文档：StackChan camera 例程 `FRAMESIZE_QVGA` + `PIXFORMAT_RGB565` + 2 个 PSRAM
  frame buffer；LTR553 例程存在，说明接近/环境光器件为真实配置项。
- 相关线程：#77（K151 上 `0x23` 不 ACK，关闭且无维护者回复）、#70（端侧算力不足，
  改为把识别放到主机）。

## 第二轮追问（2026-11-24）

作者新增两个问题：能否获得子板原理图 / 完整 24-pin FPC 定义 / 电源轨规格；以及只启用
GC0308 VGA 模式是否足够 640×480。

- **子板文档**：不能获得或代为发布。公开 K151 资料是 11 页整机原理图（CoreS3 7 页 +
  Adapter/Power/Ring/Touch 4 页），止于 `J2`，没有子板页、BOM 或 pin 1–24；公开页只给
  信号组、AXP2101 电源拓扑（BLDO→`AVDD`/`DVDD`，ALDO→`VDDCAM_3V3`）与
  `CAM_MCLK`→`J2` pin 12。建议作者走 M5Stack support/FAE 或代理工单，按 SKU + 批次索取。
- **VGA**：对官方 StackChan 固件，启用 `CONFIG_CAMERA_GC0308_DVP_YUV422_640X480_16FPS=y`
  对采集尺寸本身是必要且充分的；`esp_video` 从 `VIDIOC_G_FMT` 取尺寸，frame copy、
  preview 与 JPEG 都动态分配，无需改 capture 代码。但需验证 PSRAM（VGA 峰值约 1.8 MB vs
  QVGA 约 0.46 MB）、带宽/CPU（约 9.8 MB/s vs 3.1 MB/s）与单 buffer 流式行为。若走 Arduino
  例程，还要改 `setup()` 里的 `set_framesize(..., FRAMESIZE_QVGA)`，且 `pushImage` 在
  VGA 下只是左上角裁剪。
- **证据等级**：StackChan 固件路径为 code-level verification；GC0308 VGA 模式另有
  AtomS3R-CAM（`esp32-camera` 路径）的 virtual-device 数据点（640×480 / 614,400 B，
  与 host oracle 一致）。StackChan 虚拟设备 VGA `NOT RUN`：其 `m5_lcd_cam` 固定
  320×240，GC0308 几何绑定只接到 AtomS3R-CAM。

## 文件

- `report.md`：完整分析、逐问结论与限制
- `run.json`：结构化记录
- `evidence/01-issue-context.txt`：原帖正文与评论数
- `evidence/02-firmware-camera-path.txt`：引脚、DVP/SCCB 初始化、依赖解析版本
- `evidence/03-schematic-camera-interface.txt`：StackChan Core 原理图 J2/时钟/电源/复位摘录
- `evidence/04-sensor-format-ceilings.txt`：esp_cam_sensor v2.6.0 模式表、地址、esp32-camera 表
- `evidence/05-official-docs.txt`：官方 camera / LTR553 例程与产品规格
- `evidence/06-related-threads.txt`：#77、#70 关键内容
- `evidence/07-device-service-profile.json`：本机 StackChan 虚拟设备 profile 摘要
- `evidence/08-reply.md`：首轮 GitHub 回复原文
- `evidence/09-followup-context.txt`：第二轮评论原文与新增问题
- `evidence/10-vga-config-and-buffers.txt`：VGA 模式、动态 buffer、PSRAM 估算与 Arduino 例程
- `evidence/11-atoms3r-cam-vga-record.txt`：AtomS3R-CAM 虚拟设备 VGA 数据点及 StackChan 模型限制
- `evidence/12-reply-followup.md`：第二轮 GitHub 回复原文

## 未覆盖项

- 实机 `NOT RUN`：无 K151，无法测量 J2 引脚、供电电平、复位极性、镜头/FOV/机构配合与热。
- 虚拟设备 `NOT RUN`：本机有 StackChan profile（ESP32-S3、320×240、模拟外设），但其
  摄像头是 GC0308 DVP 帧源模型，无法表达另一颗物理传感器的引脚、供电、SCCB ID 与光学，
  跑起来只能重复确认现有通路。
- StackChan 虚拟设备 VGA `NOT RUN`：`m5stackchan.c` 把 `m5_lcd_cam` 固定在 320×240，
  `m5sw_gc0308_bind_lcd_cam` 只接到 AtomS3R-CAM；不改模型无法表达 640×480。
- VGA 构建/烧录/PSRAM/音频实测 `NOT RUN`：未编译 VGA 固件，未测最大连续 PSRAM 块、
  带宽与音频并发。
- 构建 `NOT RUN`：未启用 OV 驱动重新编译，未验证 `esp_video` V4L2 是否接受 JPEG DVP 模式。
- 子板原理图/BOM 未公开，J2 各脚定义来自主板网络名推断，未与实物核对。
- LTR-553 在 K151 各批次是否贴装未有官方确认（#77 报告过 `0x23` 不 ACK）。
- 官方产品路线图无公开信息，回复中明确不代答。
