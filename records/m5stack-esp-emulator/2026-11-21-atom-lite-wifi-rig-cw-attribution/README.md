# Atom Lite「Wifi_Rig_CW(Server)」审查 `E_SIM_APP_READY_PARTIAL` 归因

- 日期：`2026-11-21`
- 结果：`PARTIAL`（归因完成；判定非模拟器启动缺陷，未开 issue）
- 工作类型：`firmware_review_attribution`
- 问题来源：内部固件审查任务 `job-c5d046d3dd9f`（lane=`SIM_PARTIAL`、status=`manual_review`、error_code=`E_SIM_APP_READY_PARTIAL`）
- 源码版本：`m5agent/m5stack-esp-emulator @ 55e5763ea`；审查服务 `auto-firmware-review @ 9e62882`
- 环境：macOS arm64；对既有审查任务证据目录做只读归因；Device Service 原生 QEMU（`m5atomlite`）；未使用真机

## 结论

这次**启动本身是成功的**：ROM 与二级 bootloader 正常加载，guest 进入 `entry 0x4008059c` 后连续运行
60.145 s（13 次采样、末态 `running`），无 panic、无 WDT、无重启循环，QEMU stderr 仅
`Adding SPI flash device`。因此不存在 QEMU 断言、启动竞态、镜像/分区解析或模型卡死这类启动缺陷。

把该任务收口为 `E_SIM_APP_READY_PARTIAL` 的原因是判定口径与设备能力边界，而不是模拟器实现缺陷：

1. Atom Lite 无板载显示屏（`display=null`、`screenshot=false`、`frame_bytes=0`、`frame_scope=serial_only`）。
   无屏设备的 `boot_status` 只能依赖串口 ready marker，而该任务没有配置 network `ready_markers`，
   于是 `boot_status` 在结构上必然是 `PARTIAL`，与固件和模型表现无关。
2. Atom Lite 的 QEMU 机器没有 Wi-Fi NIC（`/machine` 下无 wifi/eth 节点），`qemu-wifi` 准入也仅覆盖
   Core2 / StickS3 / 通用 ESP32-S3，`qemu-esp32lx6` 的其余机型直接 409 `qemu_wifi_not_supported`。
   该固件声明的功能是 Wi-Fi 服务端（`network_required=true`），所以同 guest 数据面只能 `NOT RUN`。
3. 串口侧确有一条应用级异常：`STA disconnect failed! 0x3001: ESP_ERR_WIFI_NOT_INIT`（10.4 s），
   即 guest 的 Wi-Fi 协议栈未初始化。它可能来自固件自身初始化顺序，也可能来自本机型缺 radio 模型，
   本记录**未能区分**，按“未定位”处理，不作为模拟器缺陷证据。

结论覆盖层级：`virtual-device validation`（启动/运行/外设侧）＋`code-level verification`（准入与就绪判定代码）。
失败分类 `failure_attribution` 四个桶（emulator_or_transport / firmware / unknown / evidence_collection）全为空，
与本次“无模拟器归因证据”的结论一致；已查重 `m5agent/m5stack-esp-emulator` 现有/历史 issue，
无同一问题（#221 Atom-Lite LX6 是 WDT abort 重启、#224 是 eFuse MAC 全 0，均已关闭且现象不同），故未开新单、也未追加无关评论。

## 关键证据

- 固件：`Serv_M5AtomLitev1.43.bin`，1,258,736 B，SHA-256
  `3f7cc345195a019170c6d6021503141c702736b70d466eb43c913a5d167ba3fb`；合成后 4 MiB 镜像 SHA-256
  `ccbf21b600fe1c526771bb55549382750f175c3557e4911983e82befbd323454`，qemu-esptool 回读逐字节相等。
- 静态：bootloader `0x1000` 有效（3 段、`entry 0x4008059c`、`flash_size_code=2` = 4 MB）；分区表有效，
  `nvs 0x9000/20480`、`otadata 0xE000`、`app0 0x10000/1310720`、`app1 0x150000`、`spiffs 0x290000`、
  `coredump 0x3F0000/65536`，结束于 `0x400000` 与 4 MiB 容量一致；`app0` 有效、`app1` 为空槽（0xff）。
- 运行：60.145 s、13 次采样全部 `running`；`qom-diff` 仅 5 项变化且均为外设前进计数——
  `onboard_io/led-frames` 1→40467、`led-rgb` 12850→3276800、`output-transitions` 1→40467、
  `rmt-classic/tx-completions` 1→40470、`tx-symbols` 24→971304，即应用主循环与 SK6812/RMT 输出持续工作。
- flash：`changed_bytes=3199`、86 段，全部落在 `0x9000`–`0xAA00` 区间内（NVS 分区 `0x9000..0xDFFF`），
  属正常 NVS 写入；未触碰 app 分区。
- 串口（1179 B 后不再增长，节选）：

  ```text
  rst:0x1 (POWERON_RESET),boot:0x12 (SPI_FAST_FLASH_BOOT)
  mode:DIO, clock div:2
  load:0x3fff0030,len:4640
  load:0x40078000,len:15660
  load:0x40080400,len:3164
  entry 0x4008059c
  [   107][E][esp32-hal-cpu.c:143] addApbChangeCallback(): duplicate func=0x400edf54 arg=0x3ffbdcc0
  E (243) gpio: gpio_pullup_en(85): GPIO number error (input-only pad has no internal PU)
  [ 10395][E][STA.cpp:540] disconnect(): STA disconnect failed! 0x3001: ESP_ERR_WIFI_NOT_INIT
  ```

  以上均为 guest 自身调用 IDF/Arduino HAL 产生的日志（非法 GPIO 号、重复注册 APB 回调），
  同固件在同版本 Arduino/IDF 真机上会打印相同内容，不构成模型异常证据。
- 准入与判定代码：`platform/tools/device_service.py:958` 起 `parse_qemu_wifi_execution`，非
  Core2/StickS3/ESP32-S3 时抛 `qemu_wifi_not_supported`（:976）；审查服务
  `service/app.py:3976` 的 `ready_markers` 仅来自任务 network 配置，`:4702` 起无屏分支要求
  `serial_runtime_ready`（含 marker），`:5140` 在 `boot_status != PASS` 时置 `E_SIM_APP_READY_PARTIAL`。

## 文件

- `report.md`：完整归因路径、证据分层与未覆盖项
- `run.json`：结构化记录
- `evidence/summary.json`：脱敏后的执行计划、串口、QOM/flash 差异与观察摘要
- `patches/`：不适用（本次未改代码）
- `code/`：不适用（无新增可重建工程）

## 未覆盖项

- 真机复现：`NOT RUN`（无 Atom Lite 实机档期；本条不影响“非模拟器启动缺陷”的结论）。
- 独立重跑第二次虚拟设备会话：`NOT RUN`（只读归因既有任务证据，未新建会话）。
- 交互输入验证：`NOT RUN`（`interactions.json` 0 次接受/0 次变化；无 framebuffer 时画面变化无法作为功能证据）。
- 网络数据面：`NOT RUN`（设备无 NIC，准入不支持；不得表述为 FAIL 或“网络不通”）。
- 串口 `ESP_ERR_WIFI_NOT_INIT` 的成因（固件初始化顺序 vs 缺 radio 模型）：未定位，需人工确认。
- IR 及其余未选外设路径：沿用设备档案的 `partial` 边界，未验证。
