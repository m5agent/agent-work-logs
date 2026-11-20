# Atom Lite「Wifi_Rig_CW(Client)」审查 `E_SIM_APP_READY_PARTIAL` 归因

- 日期：`2026-11-21`
- 结果：`PARTIAL`（归因完成；判定非模拟器启动缺陷，未开 issue）
- 工作类型：`firmware_review_attribution`
- 问题来源：内部固件审查任务 `job-a4dc24b70d32`（lane=`SIM_PARTIAL`、status=`manual_review`、error_code=`E_SIM_APP_READY_PARTIAL`）
- 源码版本：`m5agent/m5stack-esp-emulator @ 55e5763ea`；审查服务 `auto-firmware-review @ 9e62882`
- 环境：macOS arm64；对既有审查任务证据目录做只读归因；Device Service 原生 QEMU（`m5atomlite`）；未使用真机

## 结论

这次是**审查就绪判定收口，不是模拟器启动失败**。guest 启动链路完整：ROM 与二级 bootloader 正常加载
（`entry 0x4008059c`），应用持续运行 60.136 s（13 次采样、末态 `running`），无 panic、无 WDT、无重启，
QEMU stderr 仅 24 B；`qom-diff` 只有 5 项外设前进计数，SK6812/RMT 输出持续工作。因此不存在 QEMU 断言、
启动竞态、镜像/分区解析或模型卡死。

把任务收口为 `E_SIM_APP_READY_PARTIAL` 的两个直接原因都在审查侧口径：

1. Atom Lite 无板载显示屏（`display=null`、`features.screenshot=false`、`frame_bytes=0`、
   `frame_scope=serial_only`）。无屏分支的 `boot_status` 只能由串口 ready marker 证明，而本任务没有配置
   network `ready_markers`，于是 `boot_status` 在结构上必为 `PARTIAL`，与固件和模型表现无关。
   结论文案「首帧已出现」与该分支的实际证据（0 字节帧）自相矛盾。
2. 交互输入是 `NOT RUN`（`accepted=0`、`changed=0`、`input_probe_timing=not_run`），即根本没有注入输入；
   「交互输入未产生足够的功能性画面变化」不是观测结果，而是空探针计划的兜底文案。

第三条限制是设备能力边界而非缺陷：Atom Lite 的 QEMU 机器没有 Wi-Fi NIC（`/machine` 下无 wifi/eth 节点），
`qemu-wifi` 准入只覆盖 Core2 / StickS3 / 通用 ESP32-S3，`qemu-esp32lx6` 其余机型直接
`qemu_wifi_not_supported`（409）。该固件声明的核心功能是 Wi-Fi 客户端，所以同 guest 数据面只能 `NOT RUN`。
设备目录对此是**诚实标注**的（`features.network=false`、`native_sta.reason=board_not_advertised`），
不构成“模拟器谎报能力”，但会长期阻断同类联网固件的验收，需要产品/模拟器侧决定是否补 LX6 STA 数据面。

结论覆盖层级：`virtual-device validation`（启动/运行/外设）＋`code-level verification`（准入与就绪判定代码）。

## 关键证据

- 固件：`Clie_M5AtomLitev1.43.bin`，2,079,024 B，SHA-256
  `9e317f1c84702c9190d95cfb3131195427d08238d16172563d227c1edbc8c87b`；合成 4 MiB 镜像装入前
  SHA-256 `f50290c5a12676a506764efb825a2a90a8ed88588cac369dd80b70fb83818705`，运行 60 s 后回读
  `eab292ab0fbc0359a06398e17b12e69bbb009b2d38a50e56633af896ab99ea96`（差异仅在 NVS）。
- 静态：bootloader `0x1000` 有效（3 段、`entry 0x4008059c`、`flash_size_code=2` = 4 MB）；分区表有效，
  `nvs 0x9000/20480`、`otadata 0xE000/8192`、`app0 0x10000/3145728`（单 app 槽，无 app1）、
  `spiffs 0x310000/917504`、`coredump 0x3F0000/65536`，结束于 `0x400000` 与 4 MiB 一致；`app0` 有效，
  镜像结束 `0x1FB900`（2,078,976 B），IDF `v5.5.4`，Arduino lib-builder，编译日期 `Jun  2 2026`。
- 运行：60.136 s、13 次采样全部 `running`；`qom-diff` 5 项均为外设前进计数——
  `onboard_io/led-frames` 0→187、`output-transitions` 0→187、`rmt-classic/tx-completions` 0→187、
  `tx-symbols` 0→4488、`tx-last-tick-hz` 0→10000000。
- flash：`changed_bytes=4587`、114 段，全部落在 `0x9000`–`0xB4FE`（NVS 分区 `0x9000..0xDFFF`），
  未触碰 app 分区。
- 串口（1,872 B，末尾不再增长，节选）：

  ```text
  rst:0x1 (POWERON_RESET),boot:0x12 (SPI_FAST_FLASH_BOOT)
  mode:DIO, clock div:2
  load:0x3fff0030,len:4640
  load:0x40078000,len:15660
  load:0x40080400,len:3164
  entry 0x4008059c
  [   105][E][esp32-hal-cpu.c:143] addApbChangeCallback(): duplicate func=0x400f9ab0 arg=0x3ffbdd54
  E (249) gpio: gpio_pullup_en(85): GPIO number error (input-only pad has no internal PU)
  [134559][E][NetworkUdp.cpp:255] endPacket(): could not send data: 118
  E (144508) wifi:sta is connecting, cannot set config
  [134561][E][STA.cpp:417] connect(): STA clear config failed! 0x3006: ESP_ERR_WIFI_STATE
  ```

  `gpio_pullup_en(85)` 是 guest 自身用非法 GPIO 号调用 HAL，真机同版本 core 会打印同一行；`0x3006` 是
  STA 仍处 connecting 时固件每 30 s 重入 `WiFi.begin()` 的结果（5 次），与“无 radio 关联”一致，
  都没有指向模型缺陷的独立信号。
- 准入与判定代码：`platform/tools/device_service.py:958` 起 `parse_qemu_wifi_execution`，非 Core2/StickS3/
  ESP32-S3 时抛 `qemu_wifi_not_supported`（:975-980）；审查服务 `service/app.py:3976` 的 `ready_markers`
  只来自任务 network 配置，`:4702-4714` 无屏分支要求 `serial_runtime_ready`，`:5138-5140` 在
  `boot_status != PASS` 时置 `E_SIM_APP_READY_PARTIAL`。

## 与同族 Server 版记录的关系

同一 BIN 家族的 `Wifi_Rig_CW(Server) For AtomLite 1.431`（`job-c5d046d3dd9f`）已按同一口径归因
（`records/m5stack-esp-emulator/2026-11-21-atom-lite-wifi-rig-cw-attribution/`）。本记录是 Client 版的独立
归因，证据形态一致但有三处可区分差异：串口异常从 `0x3001 ESP_ERR_WIFI_NOT_INIT` 变为 `0x3006
ESP_ERR_WIFI_STATE` 的 30 s 重连循环；单 app 槽 3 MiB 分区（Server 版为双槽 1.25 MiB）；NVS 写入
4587 B（Server 版 3199 B）。两者都不改变“非模拟器缺陷”的结论。

## 文件

- `report.md`：完整归因路径、假设排除表、证据分层与未覆盖项
- `run.json`：结构化记录
- `evidence/summary.json`：脱敏后的执行计划、串口、静态分析、QOM/flash 差异与观察摘要
- `patches/`：不适用（本次未改代码）
- `code/`：不适用（无新增可重建工程）

## 未覆盖项

- 真机复现：`NOT RUN`（无 Atom Lite 实机档期；不影响“非模拟器启动缺陷”的结论）。
- 独立重跑第二次虚拟设备会话：`NOT RUN`（只读归因既有任务证据，未新建会话）。
- 交互输入验证：`NOT RUN`（`interactions.json` 0 次接受/0 次变化；本任务未生成输入探针）。
- 网络数据面：`NOT RUN`（设备无 NIC、准入不支持；不得表述为 FAIL 或“网络不通”）。
- 固件功能结论：`NOT EVALUATED`（本次只做失败归因，不评价固件是否违规或可用）。
