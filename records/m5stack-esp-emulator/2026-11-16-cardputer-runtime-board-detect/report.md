# 完整报告：Cardputer 运行时板型探测与两日审核归因

## 1. 范围与方法

时间窗口：`2026-11-14 00:00` 至 `2026-11-16 09:20 +08:00`（UTC
`2026-11-13T16:00` 至 `2026-11-16T01:20`）。

对象：审查服务在此期间创建的 42 条任务，其中
`done/SIM_VERIFIED` 12 条、`failed/FAIL` 3 条、`manual_review/SIM_PARTIAL` 27 条。

方法：只读读取每条任务的 `review-report.json`、`analysis.json`、`execution-plan.json`、
`session.json`、`wait.json`、`observation.json`、`serial.log`、`frame.png`、
`interactions.json`、`device-state.json`、`qom-diff.json`、`flash-diff.json`、
`network.json`（如有）；对 Tab5 的取帧错误额外用同一固件创建只读会话复现 409 的
响应体；对 Dial 参考既有归因记录
`records/firmware-review-service/2026-11-15-vinylm5dial-dial-no-frame-attribution`。
未修改模拟器代码、未 push、未关闭任何 issue。

## 2. 归因总表

| 归因 | 任务数 | 代表任务/固件 | 处理 |
| --- | --- | --- | --- |
| 模拟器：Cardputer 运行时板型探测回退 136 | 4 | Tiny Journal、MacroCard、Frequency、CapLab | 新开 #230 |
| 模拟器：M5Apps ROM EXTMEM occupy | 1 | M5Apps 2.7 | 既有 #229 |
| 模拟器：Tab5 板型探测缺 ST7123/GT911 | 1 | carPlay-Tab5 1.0.0 | 既有 #227 |
| 未定位：Tab5 模型缺口（崩溃循环） | 1 | M5TabOS 0.9.1 | 记录，未开单 |
| 审查服务：DEVICE_MAP 缺设备码 | 4 | ATOM_S3 ×2、PAPER_S3、PAPER_DIY | 建议补映射 |
| 审查服务：Tab5 取帧要求匹配 ELF | 5 | 98TAB5 ×3、GRUVPAKT T8、Evil-M5Tab5 | 建议 ELF/串口回退 |
| 审查服务：网络验证路径未启用 | 2 | obdM5-Stopwatch、NVS Manager-Cardputer | 建议启用/明确 NOT APPLICABLE |
| 审查服务：StickC-Plus2 静态判定误放行 | 1 | OnePork Stick2 Port | 既有 #228 |
| 审查服务：app-only 启动上下文缺失 | 1 | GroovePuter-Cardputer | 建议补 boot context |
| 外部夹具缺失 | 4 | ZILLASTICK ×3（CC1101 RF Pack）、vinylM5Dial（Unit AudioPlayer） | 不计模拟器缺陷 |
| 输入/声明解析或应用交互面 | 3 | alpha-buddy、AD Arcade、OnePork-Cardputer | 不计模拟器缺陷 |
| 合计 | 27 | | |

`SIM_VERIFIED` 12 条与静态 `FAIL` 3 条不在本表逐条展开；静态 FAIL 的具体原因见
`analysis.json` 与审查报告。

## 3. Cardputer / Cardputer-ADV 运行时板型回退（新开 #230）

### 3.1 现象

4 个独立固件在 `M5Cardputer::begin()` 之后打印同一行：

```text
[error] Keyboard: Unsupported board type: 136
```

| 固件 | 版本 | 设备 | 源 BIN SHA-256 | 任务 |
| --- | --- | --- | --- | --- |
| Tiny Journal | 2026.11.14 | Cardputer | `b02460c9af14e499fe12c3018ff72740bbbeaaf362e7c51697d09e480824d707` | `job-9a0f60dda4ff` |
| MacroCard | 1.0.0 | Cardputer | `f1732ab34f26b2341ed554aa2d0e8f996c014087c7e5dd2b651799bcfcde555b` | `job-f5223ad43b5a` |
| Frequency and Noise Generator | 1.0 | Cardputer-ADV | `2ac8d0133c8bd75c8c3345e3aadca6f4d605b149f0a38549c93b1225286c1d32` | `job-df141384a2fd` |
| CapLab | 1.5.1 | Cardputer-ADV | `f02a6c47fd436f619f4394aa3b4b3df7c79fb5168636a357e2c8e584b0423c4f` | `job-931f111cfb84` |

4 条任务的帧均为 174 B、240×135、全黑；观察 60.1–60.2 s、13 次采样；
`session.json` 保持 `running`，无 panic/assert/crash marker。MacroCard 在板型错误后还打印
LittleFS 损坏、SD 挂载失败、TinyUSB 初始化失败与 NVS key 缺失，但同样没有首帧。

### 3.2 根因链

1. M5Stack Arduino 板定义 `m5stack_cardputer` 的 `build.board` 为
   `M5STACK_CARDPUTER`，`build.defines` 为空；没有 `BOARD_ID`。M5Unified 只有在
   `BOARD_ID > 0` 时固定板型，否则使用 M5GFX 运行时探测。
2. M5GFX 的 `cardputer_family_detector` 首先调用 `probe_spi_id()`，探测 ST7789V2
   命令 `0x04`，掩码 `0xFB`，期望值 `0x81`。
3. 该探测由 `soft_spi_read32()` 用 GPIO 位翻转实现：SCLK=36、MOSI=35、DC=34、CS=37；
   3-wire 模式下 MOSI 兼作读数据线。
4. esp-emu 的 Cardputer 机器把 `M5SpiPanel` 只挂到 ESP32-S3 GP-SPI 的
   `0x60024000`/`0x60025000` 上，CS=37、DC=34，`read-id=0x00000081`；面板 ID 只通过
   GP-SPI 数据寄存器的读路径返回。
5. GPIO 位翻转的 SCLK/MOSI 没有进入面板模型；`esp32_gpio_add_out_listener()` 只用于
   CS 门控，没有用于命令/数据解码。探测读回 0，`probe_spi_id()` 失败。
6. Cardputer 家族探测器在第一步返回 false，后续无显示板探测给出 136（StampS3）；
   M5Cardputer 的 `Keyboard_Class::begin()` 进入 `else` 分支并打印 136；M5Unified 以
   displayless StampS3 配置构造，ST7789 未初始化，应用绘制不产生帧。

### 3.3 为什么不是固件问题

- 4 个固件来自不同作者/仓库，都是 Cardputer 应用；
- 串口没有 panic/assert，bootloader 与 app 已进入；
- 同机型上固定板型的 M5Launcher 审查通过，官方 UIFlow2 验收也通过；
- 板型枚举 136 对应 StampS3，而 Cardputer 应用不可能在真机 StampS3 上工作。

本次没有在真机复跑 4 个 BIN；真机预期返回 14/24 来自 M5GFX 探测器设计，不是实测结论。

### 3.4 复现与期望

通过 esp-emu 0.50.0 的 `m5cardputer` / `m5cardputeradv` machine，或 Device Service 的
`cardputer` / `cardputer-adv` 设备，运行 8 MiB 镜像；观察串口板型行与 60 s 全黑帧。
期望 `M5.getBoard()` 返回 14/24，串口不再出现 `Unsupported board type`，并出现非黑首帧。
建议为 GPIO 位翻转路径增加 3-wire RDDID 响应器，或以 Tiny Journal/CapLab 建立回归。

## 4. Tab5 的 409 与 ELF 取帧约束（服务侧）

5 条 Tab5 `E_SIM_OBSERVATION_INCOMPLETE` 的 `observation.json` 都是
`elapsed_seconds=0`、`samples=0`、`error="HTTP Error 409: Conflict"`。同一固件重新创建
只读会话后，409 的响应体是：

```json
{"error": {"code": "screenshot_requires_matching_elf",
 "message": "Tab5 screenshot capture requires an ELF matching this ..."}}
```

即 Tab5 的 framebuffer 取帧要求与固件匹配的 ELF，而审查链路只持有 BIN。该 409 被
`observe_session()` 当作致命错误，导致 0 采样；这不是应用崩溃或面板模型缺陷。

- CarPlay-Tab5：另有 #227 的 ST7123/GT911 板型探测 assert，属于真实模拟器缺口；
- 98TAB5 ×3、GRUVPAKT T8、Evil-M5Tab5：仅能确认取帧被 ELF 约束阻断；串口分别止于
  `esp_core_dump_flash: Init core dump to flash`（4113 B）或更早，未出现 panic/restart；
  应用是否完成显示初始化仍为 `NOT RUN`。

建议：为 Tab5 审查提供匹配 ELF，或允许串口/面板状态作为降级证据，并把 409 从
`E_SIM_OBSERVATION_INCOMPLETE` 区分为 `E_EVIDENCE_UNAVAILABLE`。不建议把它开成模拟器
issue。

### 4.1 M5TabOS 的 `E_SIM_MODEL_GAP`

窗口末尾新增的 M5TabOS 0.9.1（Tab5，`job-bdb3209e5d3a`，源 SHA-256
`08aa10d0caeaf7835cd2f93ee66a8d2042ce15bd6e52350df6b96c70ec8bbe3e`）在
`SPI SRAM memory test OK` 后进入 `esp_core_dump_flash`，随后
`rst:0xc (SW_CPU_RESET)` 重启；串口 30,546 B 内 6 次重启，无 panic 文本。审查以
`E_SIM_MODEL_GAP` 收口，Tab5 的外设覆盖本来不完整，当前无法区分是固件缺陷还是
ST7123/CSI/USB/SDIO/C6 伴生芯片等模型缺口。该条登记为未定位模型缺口，未新开 issue。

## 5. 设备映射与服务配置

4 条任务在 QEMU 启动前停在 `E_NO_SIM_PROFILE`：

| 设备码 | 模拟器已有档案 | 审查服务 `DEVICE_MAP` |
| --- | --- | --- |
| `ATOM_S3` | `atoms3`（可创建，有显示/截图） | 缺失 |
| `PAPER_S3` | `papers3`（可创建，有显示/截图） | 缺失 |
| `PAPER_DIY` | `paperdiy`（可创建，有显示/截图） | 缺失 |

这不是“模拟器没有机型”，而是审查服务查表缺项。建议补
`ATOM_S3 → atoms3`、`PAPER_S3 → papers3`、`PAPER_DIY → paperdiy`，并加一条目录/映射
一致性测试。正在运行的审查服务副本与仓库源码都缺这三项。

## 6. 网络与静态判定

- obdM5（Stopwatch）与 NVS Manager（Cardputer）均为 `E_NETWORK_PARTIAL`：
  - Stopwatch / Cardputer 的 `execution_plan()` 只在有 `uiflow2-sticks3-wifi` 档案时选择
    同 guest 网络路径；Stopwatch 的通用网络档案不会被使用，结果 `network.status=NOT RUN`；
  - Cardputer 设备档案的 `features.network=false`，本身没有网络能力。
  两者都先表现为审查链路的 `NOT RUN`，不能归因模拟器模型缺陷。
- OnePork Stick2 的串口为 `rst:0x1 ... invalid header: 0x04202040` 循环，属于合并镜像
  bootloader 偏移/静态判定问题（#228）；会话仍被创建并以 `E_NO_FRAME` 收口。
- GroovePuter 为 app-only 输入，Cardputer 没有已验证的 app-only 启动上下文
  （`E_APP_ONLY_UNSUPPORTED_DEVICE`）；需要补 boot context 或明确拒绝。

## 7. 外部夹具与输入/声明

- ZILLASTICK 3 条任务的首帧为 “Initializing / Probing CC1101...”，应用在等待外部
  Pingequa RF Pack S3 的 CC1101；A/B 注入不改变画面。该 DUT 需要外部 RF 板，虚拟设备
  没有对应夹具，不能据此判定按键模型损坏。
- vinylM5Dial 的应用停在显示初始化之前，既有归因记录已用同机 UIFlow2 对照证明 Dial
  显示链路可用；应用日志走 USB CDC，会话未接该通道，卡点无法收敛到单个外设。
- AD Arcade 的 `touch_claim_required=true` 来自描述里的 “tap to flap”；StickC-Plus2
  没有触摸屏，`touch_status=NOT RUN` 使整体 `PARTIAL`。这是声明解析误报。
- alpha-buddy 的 key_b 有画面变化、key_a 无；OnePork-Cardputer 的 key_a 有变化、key_b 无。
  两键都被当作 required，`button_status=PARTIAL`；现有证据不足以区分应用只使用单键还是
  按键模型缺陷。

## 8. 未开单清单与理由

| 现象 | 未开单理由 |
| --- | --- |
| `E_NO_SIM_PROFILE` ×4 | 模拟器已有档案；审查服务映射缺项 |
| Tab5 409 ×5 | `screenshot_requires_matching_elf`；BIN-only 取证链路问题 |
| `E_NETWORK_PARTIAL` ×2 | 审查规划未启用对应网络路径 / 设备无网络能力 |
| OnePork Stick2 | 既有 #228 覆盖；静态判定误放行 |
| GroovePuter app-only | 审查服务启动上下文缺失 |
| M5TabOS Tab5 崩溃循环 | 无单一模型证据；Tab5 外设覆盖多处 partial |
| ZILLASTICK / vinylM5Dial | 外部夹具/Unit 未接入；无具体模型缺陷证据 |
| AD Arcade / alpha-buddy / OnePork-Cardputer | 声明解析或应用交互面；无模型缺陷证据 |

## 9. 影响面与后续

- #230 的影响面是依赖 M5GFX 运行时板型探测的 Cardputer / Cardputer-ADV Arduino 固件；
  固定板型（`BOARD_ID`）或 UIFlow2 路径不受影响。
- 审查服务侧最优先：补 3 个设备码映射；把 Tab5 的 ELF 取帧失败与观察失败分开；
  修正 “tap” 触发触摸声明的解析。
- 若要闭环 ZILLASTICK / vinylM5Dial，需要为对应 DUT 提供 CC1101 RF Pack 与
  Unit AudioPlayer 夹具，或明确把这类外部依赖标为 `NOT RUN`。
- M5TabOS 需要先补 Tab5 的 USB Serial/JTAG 或 panic 通道，才能把崩溃定到单个外设。

## 10. 未覆盖项

- 4 个 Cardputer BIN 的真机启动/显示/键盘：`NOT RUN`。
- Tab5 非 CarPlay 固件的带 ELF 取帧与真机首帧：`NOT RUN`。
- CC1101 RF Pack、Unit AudioPlayer、SD、音频、USB、BLE：`NOT RUN`。
- 审查服务修复与部署：`NOT RUN`（本轮只归因）。
