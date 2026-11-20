# Atom Lite「Wifi_Rig_CW(Client)」`E_SIM_APP_READY_PARTIAL` 归因报告

- 任务：`job-a4dc24b70d32`，lane=`SIM_PARTIAL`，status=`manual_review`，error_code=`E_SIM_APP_READY_PARTIAL`
- 固件：`Wifi_Rig_CW(Client) For AtomLite` 1.431，version_id=`2123848540738240513`，
  `Clie_M5AtomLitev1.43.bin`，2,079,024 B，SHA-256 `9e317f1c…8c87b`
- 设备：Atom-Lite（SKU `C008`，ESP32-PICO-D4，4 MiB flash，0 PSRAM，无 LCD）
- 目标：判断该次“启动失败”是否可归因到 esp-emulator / QEMU 模型；仅在可归因时提交 issue
- 方式：对既有审查任务证据做只读归因；未改代码、未 push 模拟器仓库、未关闭 issue

## 1. 现象

审查服务把任务收口为 `manual_review / SIM_PARTIAL / E_SIM_APP_READY_PARTIAL`，结论文案为：
「虚拟设备已启动并采集证据，但首帧已出现但应用级 readiness 未完全确认；交互输入未产生足够的功能性
画面变化；描述声明的网络功能未获得同一虚拟设备上的数据面 PASS」。

`emulator-failure.json` 本身并不指向某类模拟器故障：

```json
{"category":"unresolved","phase":"guest_observation","source":"review_observation",
 "source_code":"E_SIM_APP_READY_PARTIAL","device_id":"atom-lite","runtime":"qemu",
 "guest":null,"firmware_conclusion":"NOT EVALUATED"}
```

即：失败阶段被标记为“guest 观察/就绪判定”，而不是 boot、镜像解析或 QEMU 执行阶段；
`firmware_conclusion` 仍为 `NOT EVALUATED`，说明不是固件被判 FAIL。

## 2. 假设与实际结论

| 假设 | 判定 | 依据 |
| --- | --- | --- |
| QEMU 断言 / 后端崩溃 | 排除 | 60.136 s 内 13 次采样全部 `running`；`crash-diagnostics` 为 `no_evidence`，`panic_count=0`、无 WDT、无重启请求，`runtime_stderr` 仅 24 B |
| 启动竞态（booting→running 过快/过慢） | 排除 | 事件序列 `flashing→booting→running` 中 booting→running 仅 112 ms，之后稳定运行 60 s；观察窗口内无状态回退 |
| 镜像 / 分区解析失败 | 排除 | bootloader 有效（3 段、`entry 0x4008059c`）；分区表有效，结束于 `0x400000`；`app0` 有效且镜像结束 `0x1FB900`；qemu-esptool 回读逐字节相等 |
| flash 容量/PSRAM 契约不匹配 | 排除 | `flash_size_code=2`=4 MB 与机型一致；`runtime_memory.effective_psram_mib=0`、`policy=qemu-no-psram`，与 Atom-Lite 无 PSRAM 的硬件事实一致 |
| 外设模型缺失导致启动失败 | 排除 | `/machine` 有 `onboard_io` 与 `rmt-classic` 子节点，且 60 s 内 `led-frames` 0→187、`tx-symbols` 0→4488，说明应用确实在驱动 SK6812/RMT |
| 固件自身崩溃 | 排除 | 串口无 `Guru Meditation`/backtrace/abort；只有 Arduino HAL 的 E 级日志；flash 差异全部在 NVS |
| 审查就绪判定口径（无屏设备） | **成立（主因）** | `features.screenshot=false`、`frame_bytes=0`、`frame_scope=serial_only`，且任务无 `ready_markers`；无屏分支 `boot_status` 结构上必为 `PARTIAL` |
| 交互输入未执行 | **成立（次因）** | `interactions.json` `accepted=0`、`changed=0`、`status=NOT RUN`；观察 `input_probe_timing=not_run`。没有注入过输入，谈不上“输入未产生变化” |
| 网络数据面不可验证（能力边界） | **成立（范围限制）** | 设备目录 `features.network=false`、`native_sta.reason=board_not_advertised`；`/machine` 无 wifi 节点；`qemu-wifi` 准入不含 `qemu-esp32lx6` 的 Atom-Lite |

## 3. 启动链路证据（virtual-device validation）

串口 1,872 B，一次 `POWERON_RESET`，随后：

```text
ets Jul 29 2019 12:21:46
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
...
[254563][E][STA.cpp:417] connect(): STA clear config failed! 0x3006: ESP_ERR_WIFI_STATE
```

解读：

- `entry 0x4008059c` 与静态分析得到的 bootloader `entry_addr=0x4008059c` 一致，二级 bootloader 正常跳转。
- `[105]…[249]` 段为 Arduino HAL / LEDC / GPIO 初始化日志，属 guest 自身代码路径。
  `gpio_pullup_en(85)` 是固件用非法 GPIO 号调用 HAL：ESP32 只有 0–39，真机同版本 core 会打印同一行，
  属固件侧无害瑕疵，不构成模型异常。
- `0x3006 ESP_ERR_WIFI_STATE` 从 t≈134.5 s 起每 30 s 出现一次，共 5 次；伴随 `sta is connecting,
  cannot set config`。含义是 STA 仍处 connecting 时应用重入 `WiFi.begin()`，与本机型“无 radio、无法关联”
  的环境一致；`endPacket` 的 `118`（ENOTCONN）同源。
- 全程无 panic、无看门狗、无复位循环；串口在 60 s 窗口内多次增长（末次 1,872 B），应用主循环在跑。

`qom-diff`（60 s 窗口）只有 5 项变化，全部是外设前进计数，没有出现模型状态跳变或错误位：

```text
onboard_io/children/led-frames/value            0 -> 187
onboard_io/children/output-transitions/value    0 -> 187
rmt-classic/children/tx-completions/value       0 -> 187
rmt-classic/children/tx-last-tick-hz/value      0 -> 10000000
rmt-classic/children/tx-symbols/value           0 -> 4488
```

flash 差异 4,587 B / 114 段，最小值 `0x9000`、最大结束 `0xB4FE`，全部落在 NVS 分区
（`0x9000..0xDFFF`）内；`app0` 未被改写，排除自擦写或分区越界。

## 4. 主因：无屏设备的 readiness 判定（code-level verification）

审查服务对 `boot_status` 的判定（`auto-firmware-review @ 9e62882`，`service/app.py`）：

```python
4702: serial_runtime_ready = bool(
4703:     serial_text
4704:     and ready_markers
4705:     and all(marker in serial_text for marker in ready_markers)
4706: )
4707: boot_status = "PASS" if (
4708:     (
4709:         features.get("screenshot")
4710:         and ready_after_execution
4711:         and frame.startswith(b"\x89PNG\r\n\x1a\n")
4712:     )
4713:     or (not features.get("screenshot") and serial_runtime_ready)
4714: ) else "PARTIAL"
```

`ready_markers` 只来自任务 network 配置（`service/app.py:3976-3981`）：

```python
3976: ready_markers = [
3977:     str(m) for m in (job_network.get("ready_markers") or [])
3978:     if str(m).strip()
3979: ][:16]
```

本次任务 `review_policy.validation={}`，无 `ready_markers`；`features.screenshot=false`。于是
`serial_runtime_ready=False` → `boot_status="PARTIAL"` → `service/app.py:5138-5140`：

```python
5138: if boot_status != "PASS":
5139:     reasons.append("首帧已出现但应用级 readiness 未完全确认")
5140:     error_code = "E_SIM_APP_READY_PARTIAL"
```

这一分支对照料设备不成立：Atom-Lite 无 LCD，`session.json` 记 `display=null`、
`display_available=false`、`last_frame_available=false`，`frame.png` 为 0 字节，`frame_scope=serial_only`。
因此：

- 文案「首帧已出现」与该分支实际证据（0 字节帧）矛盾，是通用兜底文案误用于无屏设备；
- 真正缺的是“无屏设备如何证明应用就绪”的验收口径（串口 marker 清单/结构化就绪断言），
  不是模拟器没有产生首帧。

同一段落里 `input` 分支的文案（`service/app.py:5141` 起）在探针为空时会落到
「交互输入未产生足够的功能性画面变化」，而 `interactions.json` 明确 `status=NOT RUN`、`accepted=0`，
即没有执行过任何输入。这同样属审查侧表述与证据不一致。

## 5. 网络：能力边界，不是缺陷

- 设备侧：`/machine` 子节点为 `esp32.i2s0/1`、`onboard_io`、`peripheral`、`peripheral-anon`、
  `rmt-classic`、`soc`、`unattached`，**没有 wifi/eth 节点**；`review.execution.features.network=false`，
  `native_sta_admission={status: unavailable, reason: board_not_advertised}`。
- 准入侧（`m5stack-esp-emulator @ 55e5763ea`，`platform/tools/device_service.py`）：

  ```python
  958: def parse_qemu_wifi_execution(
  962:     if spec.id == "core2":        nic = "misc.esp32_wifi"
  966:     elif spec.id == "sticks3":    nic = "misc.esp32s3.wifi"
  970:     elif spec.backend == "qemu-esp32s3": nic = "misc.esp32s3.wifi"
  974:     else:
  975:         raise ServiceError(
  976:             "qemu_wifi_not_supported",
  977:             ("qemu-wifi is supported for Core2, StickS3 and generic "
  978:              "ESP32-S3 observe profiles"), 409)
  ```

- 设备档案（`platform/qemu/profiles.json` 的 `atom-lite` 条目）声明 `display=null`、
  `input=["gpio-button"]`、`peripherals=["gpio-button","rgb-led","ir-tx-rx"]`，**不含网络能力**。

结论：Atom-Lite 在虚拟设备上不具备 STA 数据面，设备目录对此外显为 `false`/`board_not_advertised`，
是**声明的能力边界**而非“谎报能力”或运行期缺陷。它使“联网固件的数据面”只能记 `NOT RUN`，
但不改变本次 `E_SIM_APP_READY_PARTIAL` 的成因（成因在就绪判定口径）。是否给 LX6 Atom-Lite 补
`misc.esp32_wifi` 数据面属产品取舍，需要人工决策后再立项，不应以 bug 单形式混入本次归因。

## 6. 为什么没有开 issue

判定规则：只有能把失败归因到模拟器（模型/外设缺失导致启动失败、QEMU 断言、启动竞态、镜像/分区解析）
才开单，且先查重。

查重结果（`gh issue list -R m5agent/m5stack-esp-emulator --search`，open + closed）：

| 编号 | 状态 | 标题要点 | 与本次关系 |
| --- | --- | --- | --- |
| #221 | CLOSED | `[LX6][Atom-Lite/Atom-Matrix]` 官方厂测固件启动期 IDLE task WDT 并 abort 重启 | 本次无 WDT、无 abort、无重启，现象不同 |
| #224 | CLOSED | eFuse MAC 全 0，联网固件停在启动阶段 | 本次已 provision fixture 身份并正常启动，现象不同 |
| #204 | CLOSED | `[WiFi][StickS3]` 缺 802.11 monitor/raw-frame data plane | S3 安全固件功能面，非 LX6 STA 关联；本次也不属 monitor 缺口 |
| #226 / #216 / #188 | OPEN | P4 USB 断言 / C6 崩溃循环 / Tab5 分区不可启动 | 机型与失败形态均不同 |
| #178 / #225 / #228 / #229 / #230 / #234 / #235 | CLOSED | classic 烧录链路、LX6 DPORT、镜像有效性、板型探测等 | 均为其他阶段或机型，已修复或独立 |

因此：无同题单可补充证据，本次也无模拟器缺陷可开新单。按“已有同问题才评论、可归因才开单”的约束，
本次对 `m5stack-esp-emulator` **不产生任何写操作**（未开 issue、未评论、未改代码、未 push）。

## 7. 复现方式（不含内部端点）

1. 取同一源 BIN：`Clie_M5AtomLitev1.43.bin`，2,079,024 B，SHA-256 `9e317f1c…8c87b`；
   经审查服务合成为 4 MiB 整片镜像（装入前 `f50290c5…18705`）。
2. 以 `device_id=atom-lite`、`runtime=qemu` 创建整机会话，qemu-esptool 烧录并回读校验。
3. 观察 ≥60 s：串口应出现 `entry 0x4008059c`、Arduino HAL 日志、`0x3006` 重连循环；
   `/machine` QOM 的 `led-frames`/`tx-symbols` 应持续增长；无 panic、无重启。
4. 尝试 `runtime=qemu-wifi`：应按准入规则返回 `qemu_wifi_not_supported`（409），
   因为 Atom-Lite 不在 Core2 / StickS3 / 通用 S3 名单内。

## 8. 证据分层与未覆盖项

- `virtual-device validation`：启动/运行/外设活动/flash 回读/NVS 差异。
- `code-level verification`：`qemu-wifi` 准入名单、无屏 `boot_status` 判定、错误码落点；
  固定 `m5stack-esp-emulator @ 55e5763ea`、`auto-firmware-review @ 9e62882`。
- `NOT RUN`：真机复现；独立第二次虚拟机会话；交互输入（未生成探针）；网络数据面（无 NIC/未准入）；
  固件内容与功能结论（`NOT EVALUATED`）；SPIFFS 内容（`UNFORMATTED`，app 未使用）。
- 不作为结论依据：`session.json` 的 `serial_bytes=0`、`serial_channels[].bytes=0`、
  `last_device_state_available=false` 与同目录 `serial.log`（1,872 B）、`device-state.json`（`PASS`）
  不一致，属任务导出快照未刷新的元数据问题；与本次失败无因果关系，未据此开单。
