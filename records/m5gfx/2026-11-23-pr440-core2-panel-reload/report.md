# M5GFX #440 review report

## 1. 背景与现象

Issue #438（svengrun）：Core2 + ILI9342E，每次 EN/RST 复位后约一半次数黑屏，且严格交替。
固件继续运行，背光正常；RDDPM（0Ah）读回 `0x10`（Sleep In、display off），下一次复位
又正常。原因是 `M5.begin()` 在 panel 仍在执行“Sleep Out 状态下硬件复位后的寄存器
reload（datasheet 最长 120 ms）”时就把 init 序列发了出去；panel 会应答命令远早于 reload
结束，所以“探测到按键有响应”不等于 ready。

m5agent 已在 issue #438 做过 code-level 归因，确认 `identify_panel_variant()` 的 120 ms
是上限不是等待，init 在复位释放后约 10 ms 就发出。本 PR 是作者 ainyan03 的实现。

## 2. PR 改了什么

9 files，+114 / -8（`evidence/pr440.diff`）：

1. 新复位标志 `reset_panel_reload`（`board_detect.hpp:166-174`），只加在
   `desc_core2` / `desc_tough` 的 `i2c_reset(1, 10, …)` 上（`esp32_d0wdq6.inl:60,75`）。
   `prepare.inl:367-370` 限制它只能用于 `reset_kind_t::i2c_regs`，且不能与
   `reset_hold_when_skipped` 组合。
2. 复位前观测（`esp32_d0wdq6.inl:495-503`）：把 `read_byte()` 从 `read_parameter()` 中
   拆出，新增 `panel_sleep_in()`（`board_registry.inl:140-148`），直接读 RDDPM(0Ah) 并用
   `(v & 0x18) == 0x08` 判定 Sleep In；读回 0 不当作 Sleep In。只在
   `!reload.reset_seen` 且 variant 已知时记录。
3. 状态与 deadline（`prepare.inl:22-40, 260-261, 515, 539-552`）：一个 inline 函数内
   static（全程序一份）保存 `reset_seen / sleep_in / pending / ready_ms`；
   `panel_reload_ms = 122`。复位 assert 时置 `reset_seen`；释放后若 `!sleep_in` 则
   `ready_ms = millis() + 122`、`pending = true`，并清 `sleep_in`。
4. 等待（`detection_integration.inl:226-239`）：`wait_panel_ready()` 清 `sleep_in`，
   `pending` 时算 `left = ready_ms - millis()`，只对 `0 < left <= 122` 等待；
   `M5GFX.cpp:925`（fixed-board）与 `:1039`（detected + adopted）在
   `_init_adopted_panel()` 之前调用，也就是在 panel init list 之前。

## 3. 代码级核对结论

- 与 #438 的根因吻合：EN 复位不会复位 panel，M5.begin() 里的复位前读数确实是“panel
  之前在显示”的有效判据；显示中复位 → 等 122 ms → init 不再落进 reload。
- 本来就 Sleep In 的启动（冷启动、上次已经黑屏）跳过等待，保留原有时长；这正好让
  “隔次”两半都成立：黑屏后的下一次本来就会成功，显示中的下一次现在也被保护。
- 一旦尝试过该复位就不再采信后续 RDDPM 读数，避免把正在 reload 的 panel 误判为
  Sleep In；失败重试不会绕过保护。
- 122 ms 取自 datasheet 120 ms + millis 截断余量；作者实测阈值是 ~7 ms，取 120 ms 属于
  保守余量，代价是显示中复位多 ~90 ms，PR 正文已明示。不是缺陷。
- 等待发生在检测与 NVS 之后，时间已计入 122 ms，不会与其它耗时叠加。

## 4. 验证

### 4.1 host 测试（本机复跑）

`test/board_detect/run.sh`：34 个 C++ 测试程序全部通过，包含新增的
`core_panel_sleep_in()`（`test/board_detect/esp32_families.cpp:122-146`），覆盖
RDDPM=16/56/0、reset_seen=true/false 与读数次数（3/2）。
证据：`evidence/host-tests.txt`。

### 4.2 上游 CI

40 项全 pass：Arduino esp32 2.0.17 / 3.1.3 / 3.3.13 / 4.0.0，C3/C5/C6/H2/P4 目标，
ESP-IDF 5.1.6 / 5.4.3 / 6.0.2，以及 catalog / host / translation-unit 等。
证据：`evidence/ci-status.txt`。

### 4.3 虚拟设备（本机 Device Service，Core2）

构建：PR head 与 base 43a8719 各用 `examples/Test/build_test`（ESP-IDF v6.1，target esp32）
构建；只把 example 的 `main.cpp` 换成测量 harness（串口 marker + 小图），库源码未改
（`evidence/harness-main.diff`）。合并成 0x0 flash 镜像后经 Device Service 的
`core2` profile（`qemu-esp32lx6` / `m5core2`，ILI9342C-E 320x240，simulated，screenshot）
启动。详细命令与 sha256 见 `evidence/build-info.txt`。

结果：

| 构建 | 串口 | 画面 | init 耗时 |
| --- | --- | --- | --- |
| PR 81642ae | `Autodetect M5StackCore2`，`board=2`，`ok=1` | 蓝底 + 绿块 + "PR440" | 328333 µs |
| base 43a8719 | 同上 | 同上，sha256 与 PR 完全相同 | 328330 µs |

PR 固件里 `nm` 能看到 `m5gfx::wait_panel_ready()` 与 `panel_reload()::state`，base 没有，
确认新代码被编入。

但这两次耗时只差 3 µs，说明 122 ms 等待在这个模型上**没有触发**。原因（`environment.txt`）：
QEMU 的 ILI9342 sink 没有 RDDPM 读路径，SPI 读恒为 `0x7f`（串口里
`DDh:7f CBh:7f ID4:7f7f`），复位后的 `identify_panel_variant(...,120,...)` 必定跑满
120 ms，把 122 ms deadline 先行耗尽；模型也没有寄存器 reload 窗口与 reset→Sleep In 转换。
因此这次虚拟设备验证只能证明 **Core2 检测/初始化/显示路径不回归**，不能证明 #438 的黑屏
被修复，也不能观察到新增等待。README 与回复都按此口径写。

## 5. 需要作者确认/可改进的点（非阻塞）

1. `init_without_reset()` 的表述。PR 正文写“does not reset the panel and does not wait”，
   但 `run_detection_session()` 在 `attempt + 2 == max_attempts` 时会强制
   `allow_reset = true`（`detect_types.hpp:171`）；M5GFX::begin() 的 max_attempts=5，
   所以第 4/5 次尝试仍可能复位并等待。`M5GFX.h:304-305` 已经写明这个提升，建议正文
   同步一下措辞，代码本身无需改。
2. 等待逻辑没有自动化覆盖。新增测试只验证 RDDPM 分类；`apply_reset()` 设置 deadline、
   `wait_panel_ready()` 的 122 ms 等待与 Sleep In 跳过都没有带假时钟的 host 测试。
   建议补一个可控制 `io::millis()/delay_ms()` 的用例，断言 deadline 与跳过分支
   （现有 host harness 已有 `host_probes`，扩展成本不高）。这是测试覆盖建议，不是缺陷。
3. 122 ms 常量相对作者实测 ~7 ms 阈值偏保守；PR 已说明 ~90 ms 的启动代价，属可接受权衡，
   只需维护者确认是否要按 panel variant 收窄。

## 6. 未覆盖项与风险

- hardware validation：`NOT RUN`。本机无 Core2/Tough；#438 复现与四个板型的测量表来自
  作者（PR 正文），不是本机测量。
- virtual-device validation 不能覆盖修复本身（模型缺口见上）；只覆盖不回归。
- `extras/board_spec` 的 `npm test` / `npm run check`：本机无 node/npm，未跑；上游 CI 覆盖。
- 未做 EN/RST 重复启动、Sleep In 起始、触摸/SD/背光回归；每构建只跑 1 次上电。
- 未验证 Core2 v1.1（AXP2101）与 Tough 的实机行为；代码上它们共用同一 descriptor 与
  `observe_core_panel()`，但仍需硬件确认。

## 7. 回滚

若合并后出现 Core2/Tough 启动时间或显示回归，回退本 PR 即可：改动集中在
`reset_panel_reload` 标志、`panel_reload` 状态和 `wait_panel_ready()` 调用，无持久化格式
或对外 API 变化。
