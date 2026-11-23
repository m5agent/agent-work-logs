# 归因报告：ATEM HD8 EMULATOR 1.01 在 Atom Lite 上的 `E_SIM_APP_READY_PARTIAL`

## 1. 任务背景

| 字段 | 值 |
| --- | --- |
| 审查任务 | `job-64c19d0704ae` |
| lane / status | `SIM_PARTIAL` / `manual_review` |
| error_code | `E_SIM_APP_READY_PARTIAL` |
| 固件名 / 版本 | ATEM HD8 EMULATOR / 1.01 |
| M5Burner version id | `2124772926055989250` |
| BIN | `atem-emu-atom-0.5.0-stock.bin`，522,384 B |
| BIN SHA-256 | `86ad1b7f784e3a9965884f46e3114c03cfbd21aa9f9f4bf06b8578d4691c9758` |
| 合成镜像 SHA-256 | `3a59f6f97224f7c73bf1e803038f449135a5877af51e3f8e9a7115803b1e387e`（4 MiB） |
| 设备 | Atom Lite（`atom-lite`，SKU C008，ESP32-PICO-D4，4 MB flash，无 PSRAM、无 LCD） |
| 运行方式 | Device Service 原生 QEMU（`m5atomlite`，`qemu-esp32lx6`） |
| 审查服务版本 | `auto-firmware-review @ a938d9651af5dc9c94868bcede48f6a64712bcb9` |
| 模拟器版本 | `m5agent/m5stack-esp-emulator @ 55e5763ea` |

固件自述：模拟 Blackmagic Design ATEM Television Studio HD8 ISO，单键 cut / 长按切换 preview，
版本描述声明新增 DHCP server；BIN 内应用 banner 为 `atem-emu-atom 0.5.0`（IDF v4.4.4、
`arduino-lib-builder`、2023-04-20 构建）。

审查任务的最终结论为：「规则检查与静态检查通过；虚拟设备已启动并采集证据，但首帧已出现但应用级
readiness 未完全确认；交互输入未产生足够的功能性画面变化；描述声明的网络功能未获得同一虚拟设备上
的数据面 PASS（设备目录尚未公布同 guest STA 能力），需补充验证。」

## 2. 现象拆分与假设

任务要求判断失败阶段属于：模型/外设缺失、QEMU 断言、启动竞态、镜像/分区解析，还是固件自身崩溃。
逐项核对结果：

| 假设 | 判定 | 证据 |
| --- | --- | --- |
| QEMU 断言 / SIGABRT | 排除 | QEMU stderr 仅 `Adding SPI flash device`（24 B），stdout 0 B；`backend_observations=[]` |
| 启动竞态 / 反复复位 | 排除 | `reboot_requests=0`、`reset_reports` 仅 `0x1 POWERON_RESET`、`panic_count=0`、WDT 报告 0；13 次采样全 `running` |
| 镜像/分区解析失败 | 排除 | bootloader `0x1000` 有效（`entry 0x400805e4`、4 MB 契约）；分区表有效并止于 `0x400000`；`app0` 有效（5 段、`entry 0x40082f90`）；`app1` 空槽；qemu-esptool 回读与镜像逐字节相等 |
| 固件自身崩溃 / 卡死 | 排除 | 串口 2.0 s 打印应用 ready，之后稳定运行；`crash-diagnostics.status=no_evidence`、`kind=null` |
| 模型/外设缺失导致无法启动 | 排除 | guest 进入应用并驱动 RMT/SK6812；`led-frames 0→473`、`tx-symbols 0→11352`；无 ILI/非法指令 |
| 审查侧 readiness/输入判定口径 | **成立** | `wait.json={}` 说明未发起 readiness 探测；`boot_status` 结构性 `PARTIAL`；输入探针因无 PNG 帧从未执行 |
| 设备能力边界（无 NIC / W5500 外置） | **成立（能力边界，非缺陷）** | 设备目录 `network=false`、`native_sta=board_not_advertised`；guest 自报 `W5500 not found - check the PoE base` |
| 首启空白文件系统 | **已知现象** | `Corrupted dir pair {0x0,0x1}` → `mount failed (-84)`；issue #206 已登记 sparse 镜像首启空白 FS |

## 3. 关键证据链

### 3.1 启动与运行

- `events.json`：`flashing → booting → running`，`flash_prepared` 记录 `byte_compare=equal`、
  `rom_download_ready=true`、`session_isolated_copy=true`。
- `observation.json`：`elapsed_seconds=60.14795287499874`、13 次采样、`final_session_state=running`、
  `serial_next_offset=948`（后 55 s 串口无新增，符合常驻网络设备稳态）。
- `crash-diagnostics.json`：`panic=null`、`panic_count=0`、`task_watchdog_reports=0`、
  `core_dump.status=not_observed`、`backend_illegal_instruction=false`。

### 3.2 外设输出

`qom-diff.json` 只有 6 项变化，全部是单调前进的外设计数：

```json
{
  "onboard_io/children/led-frames/value": {"before": 0, "after": 473},
  "onboard_io/children/led-rgb/value": {"before": 0, "after": 24},
  "onboard_io/children/output-transitions/value": {"before": 0, "after": 473},
  "rmt-classic/children/tx-completions/value": {"before": 0, "after": 473},
  "rmt-classic/children/tx-last-tick-hz/value": {"before": 0, "after": 10000000},
  "rmt-classic/children/tx-symbols/value": {"before": 0, "after": 11352}
}
```

即 60 s 内 473 次 RMT/SK6812 帧（约 7.9 fps）。Atom Lite 的“显示”就是这 1 颗 RGB LED，
模型按无 LCD 契约工作，因此不属于「设备模型缺失」。

### 3.3 flash 写路径

- 入库分析：`spiffs 0x290000/1441792`，状态 `UNFORMATTED`（"appears erased or zero-filled"）。
- 会话前 flash SHA `3a59f6f9…`（等于合成镜像），会话后 `ba6ad62d…`；`changed_bytes=129`、13 段，
  分别位于 NVS（`0x9000..0x9059`）与 spiffs 超级块区（`0x290000..0x291034`）。
- 末态镜像 `0x290000`、`0x291000` 均可见 `littlefs` 魔数与合法的 block size(4096) / block count(352)，
  证明 guest 对空白分区执行了格式化，且模拟器 flash 写路径完整持久化。

### 3.4 readiness 判定为什么必然是 PARTIAL

审查服务 `a938d965` 的实际控制流：

1. `service/app.py:4017-4022`：`ready_markers` 只来自任务 network 配置或已保存 validation；
   本任务 `review_policy.validation={}`，因此 `ready_markers=[]`。
2. `:4021-4022`：仅当 `ready_markers` 非空才注入 `serial_markers`。
3. `:4041-4046`：`ready` 字典为空对象时**不调用** `POST /sessions/{id}/wait`；证据里
   `wait.json` 就是 `{}`（3 字节）。
4. `:4743-4754`：

   ```python
   serial_runtime_ready = bool(
       serial_text and ready_markers
       and all(marker in serial_text for marker in ready_markers)
   )
   boot_status = "PASS" if (
       (features.get("screenshot") and ready_after_execution and frame.startswith(b"\x89PNG\r\n\x1a\n"))
       or (not features.get("screenshot") and serial_runtime_ready)
   ) else "PARTIAL"
   ```

   本机型 `screenshot=false`，所以 `boot_status` 完全取决于 `serial_runtime_ready`；而它要求
   `ready_markers` 非空。marker 未配置 ⇒ 无论串口打印什么，`boot_status` 恒为 `PARTIAL`。
5. `:5179-5181`：`boot_status != "PASS"` 时追加固定文案「首帧已出现但应用级 readiness 未完全确认」并
   置 `E_SIM_APP_READY_PARTIAL`。该文案在 `frame_bytes=0`、`frame_scope=serial_only` 的任务里并不成立，
   属审查服务表述缺口。

串口里客观存在应用级就绪行 `00:00:02 ready: ATEM udp 0.0.0.0:9910, videohub 9990, web :80`，
若任务配置 `ready_markers=["ready:"]`（或更严格的复合 marker），该机型即可在串口维度判定就绪。

### 3.5 输入为什么是 NOT RUN 而不是失败

- `service/app.py:4312-4313` 与 `:4346-4347`：两处 `probe_input` 调用都带
  `frame.startswith(b"\x89PNG\r\n\x1a\n")` 条件。Atom Lite 无 framebuffer ⇒ `frame=b""` ⇒ 探针永不执行。
- 证据与代码一致：`interactions.json` 为 `{"results": [], "accepted": 0, "changed": 0, "status": "NOT RUN"}`，
  `observation.json` 的 `input_probe_timing="not_run"`。
- 附带口径问题：固件描述只说 “button to cut, hold button to switch preview”，没有 A/B 字样；
  `service/app.py:806-825` 在 `button_required` 为真且无显式按键时默认
  `required_buttons=["a","b"]`，而 Atom Lite 设备档案只有 1 个 USER 键（GPIO39）。即使将来补上
  framebuffer 或 QOM 断言，这套 a/b 默认值也会与单键板冲突，需要按设备控制表裁剪。

### 3.6 网络为什么不可验证

- 执行计划：`network_required=true`（分类 `Network & Communication`、描述提到 DHCP server），
  但计划 `features.network=false`、`network_status=not-supported`、`native_sta.status=unavailable`、
  `reason=board_not_advertised`；`network` 检查为 `NOT RUN`、`data_plane=NOT RUN`、`same_guest=false`。
- 固件自报 `ethernet: W5500 not found - check the PoE base`、`ethernet: 0.0.0.0, link down`。
  Atom Lite 本体没有以太网口，W5500 属于外置 PoE 底座；模拟器外设目录仅有
  `ethernet-sr9900a`（Cardputer Zero 的 Linux 后端），没有 W5500 SPI 模型。
- 因此这是「机型 + 附件不在虚拟设备范围内」的能力边界，不是模型缺陷，也不能写成「网络 FAIL」。

### 3.7 首启 LittleFS 报错

`Corrupted dir pair at {0x0, 0x1}` → `mount failed (-84)` 与 issue #206 记录的 sparse merged 镜像
首启空白 FS 行为一致；固件随即回退 `state: built-in standard HD8 ISO` 并继续启动，随后完成格式化。
该现象在真机用 M5Burner 首次烧录同款镜像时也可能出现，issue #206 明确写了「不一定是模拟器 bug」，
本次不重复开单。

## 4. 归因结论

**失败归属：审查服务判定/采集口径（主因）＋设备能力边界（次因），非模拟器缺陷。**

- 模拟器侧没有失败：flash 契约、启动、运行、外设计数、崩溃诊断全部通过或为 `no_evidence`。
- 触发 `E_SIM_APP_READY_PARTIAL` 的直接原因是：无 framebuffer 机型的 readiness 依赖任务
  `ready_markers`，本任务未配置；同时输入探针被 PNG 帧门控。两者叠加导致 `boot_status=PARTIAL`
  且输入 `NOT RUN`，并输出与证据矛盾的固定文案。
- 网络 `NOT RUN` 与 LittleFS 首启报错都属已知边界，不进入 `emulator_or_transport` 桶。

`failure_attribution` 四个桶全为空，与该结论一致。

## 5. 查重与 issue 决定

检索 `m5agent/m5stack-esp-emulator` 的 open/closed issue，关键词：`atom-lite`、`ATOM_LITE`、
`ready_markers`、`onboard_io`、`W5500`、`littlefs`、`ethernet`、`readiness`、`screenshot`。
最接近的三条均不同题：

| issue | 状态 | 为何不同 |
| --- | --- | --- |
| #221 Atom-Lite/Atom-Matrix 厂测固件 IDLE WDT abort 重启 | CLOSED | 本次 WDT=0、无重启、无 abort |
| #206 sparse merged 镜像首启空白 FS / 无 flash fixture | CLOSED | 记录的是已知首启行为与测试能力缺口，本次 LittleFS 报错正是该现象 |
| #224 所有设备 eFuse MAC 全 0 导致联网固件停启 | CLOSED | 本次 eFuse fixture 已 provisioned，guest 正常启动 |

**未开 issue、未追加评论**：按归因规则，只有能落到模拟器（模型/外设缺失、QEMU 断言、启动竞态、
镜像/分区解析）时才开单；本次主因在审查服务判定口径。

## 6. 建议的修复方向（均不在模拟器仓库）

1. 审查服务：对 `screenshot=false` 机型，若任务提供 `ready_markers`，应允许以串口 marker 判定
   `boot_status=PASS`；未提供时应在报告里明确写「未发起 readiness 探测」，而不是「首帧已出现」。
2. 审查服务：输入验证不应以 PNG 帧为唯一门控；无 framebuffer 机型可用 QOM（`pressed`、
   `input-level`、`led-frames`/`led-rgb` 变化）做功能断言。
3. 审查服务：`required_buttons` 默认值 `["a","b"]` 应按设备控制表裁剪（Atom Lite 只有 1 键）。
4. 审查任务配置：若要以串口就绪为准，应为该固件补 `ready_markers`（例如 `ready:`）后重跑；
   网络声明需明确标注为「依赖外置 PoE 底座、本机型不可验证」。

模拟器侧若要做能力增强（不在本记录范围）：为 Atom 系列 1×N LED 增加可断言的像素/颜色状态，
使“按键→画面变化”能在无 LCD 机型上被验证；这属于功能扩展，不是缺陷修复。

## 7. 影响面与回滚

- 本次为只读归因：未修改模拟器或审查服务代码，未新建会话，未修改任务状态、证据或报告字段，
  未 push 模拟器仓库，未关闭任何 issue。
- 回滚：不适用（无写入）。记录本身可整体删除，不影响任何被测系统。

## 8. 未覆盖项

- 真机复现：`NOT RUN`。
- 第二次虚拟设备会话（验证格式化后 LittleFS 可挂载）：`NOT RUN`。
- 输入注入（USER 单键 cut / 长按切换预览）：`NOT RUN`。
- 网络数据面（W5500 / DHCP / ATEM UDP / web）：`NOT RUN`。
- IR 与未选外设路径：`NOT RUN`（沿用设备档案 `partial` 边界）。
- 固件静态字符串中的 2 个私网 IPv4 字面量：`REVIEW`（仅计数，地址值不记录；是否预期由内容审查判断）。
