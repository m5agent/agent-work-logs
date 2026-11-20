# Atom Lite「Wifi_Rig_CW(Server) 1.431」`E_SIM_APP_READY_PARTIAL` 归因报告

- 日期：`2026-11-21`
- 审查任务：`job-c5d046d3dd9f`（lane=`SIM_PARTIAL`、status=`manual_review`、error_code=`E_SIM_APP_READY_PARTIAL`）
- 设备档案：`atom-lite`（Atom Lite / SKU C008 / ESP32-PICO-D4 / 4 MB flash / 无 PSRAM / 无显示屏 / USER 按键）
- 运行时：Device Service 原生 QEMU，machine `m5atomlite`，`runtime=qemu`
- 源码基线：`m5agent/m5stack-esp-emulator @ 55e5763ea`；审查服务 `auto-firmware-review @ 9e62882`

## 1. 背景与现象

固件 `Wifi_Rig_CW(Server) For AtomLite` 版本 `1.431`（`Serv_M5AtomLitev1.43.bin`，1,258,736 B，
SHA-256 `3f7cc345195a019170c6d6021503141c702736b70d466eb43c913a5d167ba3fb`）由审查服务下载、
合成 4 MiB 虚拟 flash 后在 Atom Lite 虚拟设备上运行。规则检查、静态检查、虚拟烧录、60 s 运行观察
均为 PASS，但 `boot_and_ui` 为 `PARTIAL`（`ready=false`、`frame_bytes=0`），最终以
`E_SIM_APP_READY_PARTIAL` 进入人工复核。任务结论文字写“首帧已出现”，但该任务实际没有任何帧：
`frame_scope=serial_only`、`last_frame_available=false`、`frame.png` 为 0 B。

需要回答的问题：这次“启动失败”是不是 esp-emulator / QEMU 模型的问题，是否值得开 issue。

## 2. 判定路径

### 2.1 失败阶段：guest 观测/应用就绪，不是启动

`emulator-failure.json` 给出 `phase=guest_observation`、`source=review_observation`、
`category=unresolved`、`guest=null`、`firmware_conclusion=NOT EVALUATED`，并且
`failure_attribution` 的 `emulator_or_transport` / `firmware` / `unknown` / `evidence_collection`
四个桶全部为空。也就是说审查链路自身没有采集到任何可归因的模拟器或固件失败信号。

### 2.2 排除 QEMU 断言 / 崩溃 / 重启循环

- 会话事件：`created → flashing → booting → running`，`booting→running` 用时 0.18 s，
  60.145 s 观察期内 13 次采样均为 `running`，会话 `stop_reason=null`、`error=null`。
- `crash-diagnostics`：`panic=null`、`panic_count=0`、`task_watchdog_reports=0`、
  `repeated_resets=false`、`reboot_requests=0`、`core_dump=not_observed`，
  `backend_illegal_instruction=false`。
- QEMU stderr 仅 24 B：`Adding SPI flash device`；stdout 0 B。没有断言、没有后端错误、没有非法指令。

### 2.3 排除镜像/分区解析与 flash 契约

- bootloader（`0x1000`）有效：3 段、`entry_addr=0x4008059c`、`flash_size_code=2`（4 MB），
  串口 `load:` 三行与该段表逐项吻合。
- 分区表有效，且 `nvs 0x9000/20480`、`otadata 0xE000/8192`、`app0 0x10000/1310720`、
  `app1 0x150000/1310720`、`spiffs 0x290000/1441792`、`coredump 0x3F0000/65536` 结束于 `0x400000`，
  与设备 4 MiB 完全一致；`bootloader_flash_contract.partitions_fit=true`。
- `app0` 有效（6 段、`image_end=1258700`），`app1` 为 0xFF 空槽，属工厂镜像正常形态；
  `static-effective.json` 的 `findings` 为空。
- 虚拟烧录：`byte_compare=equal`，回读 SHA 与镜像 SHA 一致；esptool stub 握手与 13 类 opcode 均有应答。
- flash 差异 3199 B / 86 段全部位于 `0x9000`–`0xAA00`，落在 NVS 分区（`0x9000..0xDFFF`）内，
  未触碰任何 app 区，属正常 NVS 持久化。

### 2.4 排除模型卡死：应用在持续运行

`qom-diff` 只报告 5 项变化，全部是外设前进计数而非异常：

| 节点 | before | after |
| --- | --- | --- |
| `onboard_io/children/led-frames` | 1 | 40467 |
| `onboard_io/children/led-rgb` | 12850 | 3276800 |
| `onboard_io/children/output-transitions` | 1 | 40467 |
| `rmt-classic/children/tx-completions` | 1 | 40470 |
| `rmt-classic/children/tx-symbols` | 24 | 971304 |

60 s 内近 4 万帧 SK6812 输出、97 万 RMT symbol 说明 guest 主循环与 RMT/GPIO 模型都在工作。
串口在 10.4 s 后不再输出，但这是固件静默，不是 guest 停止：QOM 计数持续增长。

### 2.5 真正的两个结构性缺口

**（a）无屏设备的就绪判定没有可用口径。** Atom Lite 档案 `display=null`，会话
`display_available=false`、`last_frame_available=false`，观察 `frame_scope=serial_only`，
`frame.png` 0 B。审查服务 `service/app.py:4707` 的 `boot_status` 只有在
`screenshot && ready_after_execution && PNG` 或 `!screenshot && serial_runtime_ready` 时才 PASS；
后者要求 `ready_markers` 非空（`:4702`、`:4704`），而 `ready_markers` 只来自任务 network 配置
（`:3976`），本任务 `review_policy.validation={}` → 无 marker → `boot_status` 恒为 `PARTIAL`
→ `:5140` 置 `E_SIM_APP_READY_PARTIAL`。这是判定口径的结构性结果，对任何无屏、无 marker 任务都成立，
与固件和模型表现无关。同理 `:5141` 的文案“首帧已出现但应用级 readiness 未完全确认”在
`frame_bytes=0` 时属误导性表述。

**（b）Atom Lite 没有 Wi-Fi 数据面。** 该固件声明功能是 Wi-Fi 服务端（`network_required=true`），
但设备能力为 `network=false`、`network_capture=false`、`network_status=not-supported`，
`native_sta={status: unavailable, reason: board_not_advertised}`，`network.data_plane=NOT RUN`。
两条独立证据：

- QOM `/machine` 子节点只有 `onboard_io`、`rmt-classic`、`soc`、peripheral 容器等，没有 wifi/eth 节点；
  设备档案 `peripherals` 只有 `gpio-button`、`rgb-led`、`ir-tx-rx`，也没有 `native_network` 字段。
- 准入代码 `platform/tools/device_service.py:958` `parse_qemu_wifi_execution` 只对 `core2`
  （classic `misc.esp32_wifi`）、`sticks3`、`qemu-esp32s3` 放行，其余后端在 `:976` 抛
  `qemu_wifi_not_supported`；Atom Lite 的 `qemu-esp32lx6` 不在其中。这是一条有明确报错文案的
  既定支持边界，不是本次运行才出现的异常。

### 2.6 固件侧唯一异常：Wi-Fi 栈未初始化

串口末尾 `[ 10395][E][STA.cpp:540] disconnect(): STA disconnect failed! 0x3001: ESP_ERR_WIFI_NOT_INIT`
说明 guest 调 `disconnect()` 时 Wi-Fi 协议栈尚未初始化。可能成因有二：固件自身 init 顺序/未调用
`WiFi.mode()`，或本机型没有 radio 模型导致 `esp_wifi_init()` 未成功。现有证据无法区分
（无 Wi-Fi 寄存器访问 trace、无匹配 ELF、无源码），按“未定位”记录，**不作为模拟器缺陷证据**。
串口另有两类 guest 侧日志——`addApbChangeCallback(): duplicate`（7 次）与
`gpio_pullup_en(85): GPIO number error`——都由固件调用 Arduino/IDF HAL 产生，
同版本真机会打印相同内容，不反映模型行为。

## 3. 为什么不开 issue

1. 启动阶段有直接的“无缺陷”证据：正常加载、无 panic/WDT/断言、60 s 运行、外设计数持续前进。
2. 收口错误码来自审查侧的 readiness 判定路径（无屏、无 marker），不是模拟器行为。
3. 网络缺口是有明确报错文案的既定支持范围（仅 Core2/StickS3/通用 S3），属能力边界而非回归；
   把“Wi-Fi 不可验证”写成 bug 会与文档声明冲突，也会把 `NOT RUN` 误表述为 `FAIL`。
4. 查重结果：`m5agent/m5stack-esp-emulator` 现有 4 个 open issue（#226 Tab5 USB、#223 StackChan
   崩溃、#216 Nesso N1、#188 Tab5 分区）与本例无关；历史 #221（Atom-Lite/Atom-Matrix 厂测固件
   IDLE WDT abort 重启）与 #224（eFuse MAC 全 0）现象不同且均已关闭；无同一问题的 open issue，
   也没有值得追加本条证据的同题单。

因此本次不开新 issue、不追加评论、不改代码、不 push 模拟器仓库。

## 4. 归因表

| 候选归属 | 判定 | 依据 |
| --- | --- | --- |
| QEMU 断言/后端错误 | 排除 | qemu.stderr 24 B、无 panic、无 illegal instruction |
| 启动竞态 | 排除 | `booting→running` 0.18 s，60 s 稳定 running |
| 镜像/分区解析 | 排除 | bootloader/分区表/app0 均有效，分区终点 = 4 MiB |
| flash 容量契约 | 排除 | `partitions_fit=true`，回读逐字节相等 |
| 模型/外设卡死 | 排除 | RMT/led 计数 60 s 内持续增长 |
| 缺 Wi-Fi 数据面 | 成立（能力边界） | QOM 无 NIC、档案无 network、准入仅 Core2/S3 |
| 无屏就绪判定口径 | 成立（审查侧） | `boot_status` 依赖 frame 或 ready_markers，二者皆无 |
| 固件 Wi-Fi 未初始化 | 未定位 | 0x3001 现象明确，成因无法区分 |

## 5. 建议（审查服务侧，非本次改动范围）

1. 无屏设备的就绪判定应显式区分“无 framebuffer”与“应用未就绪”，避免在 `frame_bytes=0` 时输出
   “首帧已出现”这类与证据矛盾的文案；`E_SIM_APP_READY_PARTIAL` 建议附上具体缺口字段。
2. 对 `network_required=true` 的任务，应在派发阶段就检查目标设备是否公布同 guest 数据面，
   不支持的机型直接给出“能力不覆盖”的结论，而不是以就绪 PARTIAL 收口。
3. 若产品上需要覆盖 Atom Lite 这类经典 ESP32 网络固件，需评估是否把 `misc.esp32_wifi`
   扩到 `m5atomlite`（当前仅 Core2 走通），这属于能力建设而非缺陷修复。

## 6. 未覆盖项与风险

- 真机复现：`NOT RUN`。不影响“启动阶段无模拟器缺陷”的结论，但真机上该固件的 Wi-Fi 行为未验证。
- 独立二次虚拟会话：`NOT RUN`（只读归因既有证据，避免额外占用设备）。
- 交互输入：`NOT RUN`（`interactions.json` 接受 0、变化 0；无 framebuffer 时画面变化不能作为功能断言）。
- 网络数据面、AP 配网、软热点：`NOT RUN`（设备无 NIC，不得表述为失败）。
- 串口静默后的应用状态只能由 QOM 外设计数间接证明，未做 GDB/符号级确认（无匹配 ELF）。
- 回滚：本次为只读归因，未改动任何代码或服务配置，无需回滚。
