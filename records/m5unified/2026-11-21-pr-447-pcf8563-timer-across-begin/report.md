# M5Unified PR #447 评审报告：PCF8563 `begin()` 保留运行中的定时器

## 1. 背景

- 来源：[m5stack/M5Unified#447](https://github.com/m5stack/M5Unified/pull/447)（作者 ainyan03，
  2026-11-21，英语，OPEN，0 条评论），Fixes #446。
- 现象（issue #446）：PCF8563 的周期定时器在 `M5.begin()` 后停止。原因是
  `PCF8563_Class::begin()` 每次写 `Timer_control (0x0E) = 0x03`，清掉 TE(bit7)，并把 TD
  改成 0b11（1/60 Hz）。`M5.begin()` 在检查 `cfg.disable_rtc_irq` 之前就调用了 `Rtc.begin()`，
  因此 `false` 也无法避免。
- PR 目标：让 `begin()` 在 TE=1 时保持 `0x0E` 不变；停止的定时器仍规范化为 `0x03`；并把
  `disableIRQ()` 的写入从 `0x00` 改为 `0x03`。

## 2. 改动审阅

PR head `4a0ebfd`，base `11bfd4b`，改动 2 个文件（+11/−3）：

`src/utility/rtc/PCF8563_Class.inl`：

```cpp
// begin() (line 22-29)
std::uint8_t timer_control = 0;
_init = writeRegister8(0x00, 0x00)
     && readRegister(0x0E, &timer_control, 1)
     && ((timer_control & 0x80) || writeRegister8(0x0E, 0x03));

// disableIRQ() (line 285-287)
ok = writeRegister8(0x0E, 0x03) && ok;   // was 0x00
```

`src/M5Unified.hpp` 只补充了 `disable_rtc_irq` 的注释，说明 `false` 时定时器跨重启保留，
`clearIRQ()` 不会停止它，需要用 `setTimerIRQ(0)` 或 `disableIRQ()`。

判断：

- 与 PCF8563 寄存器语义一致：TE=1 表示定时器使能，TD 是时钟选择；保留整个 `0x0E` 才能让
  跨复位的定时器继续按原周期运行。
- `begin()` 不触碰 `Control_status_2 (0x01)`，因此跨重启的 TIE 与 TF 状态也保持，符合
  “定时器继续工作”的目标。
- 停止的定时器仍写 `0x03`，保持原先“TD=1/60 Hz、TE=0”的初始化结果。
- `disableIRQ()` 写 `0x03` 与 `setTimerIRQ(0)` 的 `stop_timer()` 一致，没有引入新的寄存器值。
- RX8130 路径未改，行为不变。
- 兼容性变化仅限 PCF8563 + `cfg.disable_rtc_irq = false` + 重启前已 armed 的定时器；默认
  `true` 仍在 `M5.begin()` 内调用 `disableIRQ()` 停止定时器。PR 描述与注释都写明了这一点。
- 一个非阻塞观察：`begin()` 现在多了一次 `0x0E` 读，读失败会使 `begin()` 返回 false；此前
  该路径只需写成功。驱动本身依赖读时间寄存器，正常器件不受影响，因此不视为缺陷。

## 3. 验证方法

### 3.1 证据等级选择

本机无 CoreInk；硬件测试中心当前只有 matrix / corep4 / sticks3 / stopwatch 四类在线节点，
没有 PCF8563 板卡，因此 hardware validation 不可用。Device Service 的 `dial`（M5Dial）profile
带 QEMU PCF8563 模型，且 profile 注明 RTC 已验证；缺陷位于 `PCF8563_Class` 与 PCF8563
寄存器语义内，与具体板卡初始化无关，因此用 M5Dial 虚拟设备执行同一驱动路径。

- 证据等级：**virtual-device validation**（M5Dial / QEMU / PCF8563 register model）
- hardware validation：**NOT RUN**
- CoreInk 虚拟设备：**NOT RUN**（无该 profile）

QEMU 的 PCF8563 模型（`patches/qemu-m5stack-peripherals/0026-m5stack-rtc-virtual-clock.patch`）
只计算 0x02–0x08 的时间寄存器，没有倒计时/TF 逻辑，因此本记录只验证寄存器写入与读回，
不把“定时器实际触发”当作虚拟设备结论。

### 3.2 构建

同一份 sketch 分别链接：

- PR：M5Unified `4a0ebfd74ec5f2fd0087fd025e7d4c36b6261e6a`
- 对照：M5Unified `11bfd4bbb2705a36e7149a117c94f39511cee1bb`（develop）
- M5GFX `28d47949bdc84f30881623476f555398e2194313`（0.3.0）
- ESP-IDF `7101770dc6db2667b3c477cc31365dd1acd6db4e`（v6.0.2）
- `esp32s3`、8 MB flash、无 PSRAM；`IDF_COMPONENT_MANAGER=0`，M5Unified/M5GFX 均用本地固定
  checkout，避免 registry 版本混入。

命令：

```bash
idf.py set-target esp32s3
idf.py build
idf.py merge-bin
```

产物均为 503,936 bytes 的 merged BIN：

| 构建 | artifact SHA256 | 服务归一化 firmware SHA256 |
|---|---|---|
| PR | `e7d73710c2c4268ed37c5d6b5a0bea6dcefe8f5249d65d0d94e736badd6bc9a0` | `bfb48593519ecdda805470e94555516f2ee46262cd4e54f15a12cf452637976e` |
| develop | `0633d3edb461fb65ba1cb53adce96010250d03b052a0f173072071188f91cab1` | `59670dc528fe2e8f2b0d7477028382b8fdf89cb6f3ae33a058f246a17f5cd37b` |

### 3.3 复现工程与阶段

`code/pcf8563-pr447/main/main.cpp`。启动时用 `m5gfx::i2c` 直接写 PCF8563：

```
0x01 = 0x00        # 清 AF/TF
0x0F = 2           # 2 秒倒计时
0x0E = 0x82        # TE=1, TD=1 Hz
```

随后执行 `M5.begin(cfg)`（`internal_rtc = true`, `disable_rtc_irq = false`），再依次：

1. 读 `0x0E/0x01/0x0F`；轮询 TF（最多 8 s）。
2. 再次 `M5.Rtc.begin(&M5.In_I2C)`（`M5.begin()` 使用的同一调用）。
3. `M5.Rtc.setTimerIRQ(3000)` 后用同一调用再次 `begin()`，轮询 TF。
4. `M5.Rtc.disableIRQ()`。
5. 直接写 `0x0E = 0x00`（停止态），调用 `begin()`。
6. 模拟默认分支：`0x82` + `begin()` + `disableIRQ()`，轮询 TF。
7. `M5.Rtc.setTimerIRQ(0)`。
8. 直接写 `0x0E = 0x83`（TE=1、TD=1/60 Hz），调用 `begin()`。

每个阶段打印 `TC/C2/CNT` 与 TF 等待结果；完整串口日志见 `evidence/`。

## 4. 结果

十阶段 A/B（`TC` 为 `Timer_control 0x0E`）：

| 阶段 | develop `11bfd4b` | PR `4a0ebfd` |
|---|---|---|
| PRE_ARM（0x82） | 0x82 | 0x82 |
| POST_BEGIN（`M5.begin`, `disable_rtc_irq=false`） | **0x03** | **0x82** |
| AFTER_REBEGIN_RUNNING | 0x03 | 0x82 |
| AFTER_ARM_LIB（`setTimerIRQ(3000)`） | 0x82 | 0x82 |
| AFTER_REBEGIN_ARMED | 0x03 | 0x82 |
| AFTER_DISABLE_IRQ | 0x00 | 0x03 |
| BEFORE_REBEGIN_STOPPED（直写 0x00） | 0x00 | 0x00 |
| AFTER_REBEGIN_STOPPED | 0x03 | 0x03 |
| AFTER_DEFAULT_PATH（begin+disableIRQ） | 0x00 | 0x03 |
| AFTER_SETTIMER0 | 0x03 | 0x03 |
| AFTER_PRESERVE_TD60（0x83 → begin） | 0x03 | 0x83 |

TF 轮询在两次构建中均为 `within_ms=-1`：QEMU 模型没有倒计时逻辑，不能据此判断定时器是否运行；
该列不作为结论证据。

结论：PR 的四个行为点均复现——运行中的 TE/TD 跨 `begin()` 保留、停止态仍规范化、
`disableIRQ()` 写 `0x03`、`setTimerIRQ(0)` 行为不变；且默认 `disable_rtc_irq=true` 的组合
路径仍然停止定时器。PR 描述中的 CoreInk 实机定时器触发数据无法由本环境复核，保持为作者证据。

## 5. 验证边界

- 定时器在 `begin()` 后继续计数、TF 置位、INT 引脚触发：**NOT RUN**；QEMU PCF8563 模型缺
  倒计时/TF 逻辑（`patches/qemu-m5stack-peripherals/0026-...patch` 只实现时间寄存器）。
- CoreInk 或其他 PCF8563 板实机：**NOT RUN**；本机与硬件测试中心均无可用该型号。
- 真实 power-off / RTC wake-up 周期、INT 波形、功耗、长期漂移：**NOT RUN**。
- 其余 PCF8563 板卡的初始化差异：**NOT RUN**；本验证只覆盖同一 `PCF8563_Class` 驱动路径。

## 6. 风险与回滚

- 改动只影响 PCF8563 的 `begin()` 与 `disableIRQ()`；RX8130 与其他 RTC 路径不变。
- 行为变化需要同时满足 `cfg.disable_rtc_irq = false` 且重启前定时器已 armed；默认配置仍会
  在 `M5.begin()` 内停止定时器。
- 回滚方式：revert PR 的两个 commit，`begin()` 恢复为无条件写 `0x0E=0x03`，`disableIRQ()`
  恢复写 `0x00`。
- 未执行任何上游写操作；PR 保持 OPEN。

## 7. 已发布回复（英文，1 条）

见 `evidence/review-comment.txt`。评论只包含寄存器级结论、证据等级、A/B 结果与未覆盖项，
不关闭 PR、不 approve、不 push。

## 8. 复现命令

```bash
export IDF_PATH=<esp-idf v6.0.2>
export IDF_COMPONENT_MANAGER=0
export M5GFX_PATH=<M5GFX @ 28d4794>
cd code/pcf8563-pr447
idf.py set-target esp32s3 build merge-bin
python3 run_on_device_service.py --image build/merged-binary.bin --out run
```

`run_on_device_service.py` 通过 `DEVICE_SERVICE_API` 指定可达的 Device Service API。
