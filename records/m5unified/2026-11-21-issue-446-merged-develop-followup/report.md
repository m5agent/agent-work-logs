# M5Unified #446 后续报告：合并后 develop 的 PCF8563 定时器保留行为

## 1. 背景与目标

- 来源：https://github.com/m5stack/M5Unified/issues/446 （作者 atgcgcta，日文，OPEN）。
- 2026-11-20 m5agent 已在该 issue 发布一条日文回复：定位到 `PCF8563_Class::begin()` 写
  `Timer_control (0x0E) = 0x03` 清掉 TE，并在虚拟 M5Dial 上复现、验证去掉该写后可保留。
- 2026-11-21T10:18:05Z 作者 ainyan03 新增评论：修复 #447 已在 CoreInk 实机复现并合并到
  develop，列出四点后续行为，并请求“如有可用装置，告知 develop 版在该装置上的动作”；同时
  说明尚未做实际电源断与 RTC 起床的重复验证。
- 本次目标：只回答这条新增请求，确认合并后 develop 的寄存器行为，并如实说明本环境能覆盖到
  哪一层；不重复上一轮已经给出的 issue 根因说明。

## 2. 代码核对（合并后）

合并 commit `dae3b5d04e6ad5f91ac72a89da09d427a0e20543` 是 #447 的 merge commit。
`git diff --stat 4a0ebfd74ec5f2fd0087fd025e7d4c36b6261e6a dae3b5d` 无输出，
GitHub compare 也返回 `files: []`，因此**合并后的代码树与已评审的 PR head `4a0ebfd` 完全相同**。

相关路径（`dae3b5d`）：

- `src/utility/rtc/PCF8563_Class.inl:18-30`：`begin()` 先空白写 `0x00`，再读 `0x0E`；
  `timer_control & 0x80` 为真时保持原字节，否则写 `0x03`。
- `src/utility/rtc/PCF8563_Class.inl:272-276`：`clearIRQ()` 仅 `bitOff(0x01, 0x0C)`，
  清 TF/AF，不触碰 `0x0E`。
- `src/utility/rtc/PCF8563_Class.inl:148-190`：`setTimerIRQ()` 的 `stop_timer()` 写
  `0x0E = 0x03` 并清 TIE；`setTimerIRQ(0)` 走该停止路径。
- `src/utility/rtc/PCF8563_Class.inl:278-292`：`disableIRQ()` 关闭 alarm 后写
  `0x0E = 0x03`，再写 `0x01 = 0x00`。
- `src/M5Unified.inl:2890-2902`：`M5.begin()` 先 `Rtc.begin()`，随后仅在
  `cfg.disable_rtc_irq == true` 时调用 `Rtc.disableIRQ()`。
- `src/M5Unified.hpp:160-164`：注释明确说明 `false` 时定时器跨重启保留、`clearIRQ()`
  不停止、需用 `setTimerIRQ(0)` 或 `disableIRQ()` 停止。

以上与作者评论中的四点描述一致；本次用运行证据复核，而不是只做代码阅读。

## 3. 验证方法与环境

### 3.1 证据路径选择

- 本机 Device Service 的 profile 列表中没有 `coreink`；`dial`（M5Dial / QEMU）是唯一带
  PCF8563 模型的 profile。硬件测试中心也没有可用的 CoreInk / PCF8563 板卡。
- 因此 hardware validation 不可用，选择 **virtual-device validation**：在 `dial` 虚拟设备上
  执行同一 `PCF8563_Class` 驱动路径，读取 `0x0E` / `0x01` / `0x0F`。
- 该模型只实现 PCF8563 的时间寄存器（`0x02-0x08`），没有倒计时、TF、INT 逻辑；因此本次
  只能证明寄存器保留与停止语义，不能证明定时器实际触发。

### 3.2 构建

| 项目 | 版本 |
|---|---|
| M5Unified | `dae3b5d04e6ad5f91ac72a89da09d427a0e20543`（develop, #447 merged） |
| 对照 PR head | `4a0ebfd74ec5f2fd0087fd025e7d4c36b6261e6a`（同树） |
| M5GFX | `28d47949bdc84f30881623476f555398e2194313`（0.3.0） |
| ESP-IDF | `7101770dc6db2667b3c477cc31365dd1acd6db4e`（v6.0.2） |
| 目标 | esp32s3，8 MB flash，无 PSRAM；`IDF_COMPONENT_MANAGER=0` |

命令：

```bash
idf.py set-target esp32s3
idf.py build
idf.py merge-bin
```

产物：merged BIN 503424 bytes，SHA256 `b57aa03c257ea0ddaa8d1d64c04be651b87ee1150dcd6612ecde9a39af913757`；
Device Service 归一化 firmware SHA256 `af556600a1126b5fa71a9d41388d522fe4ba1b57388f8a4352e50370b5f0e12c`。

### 3.3 探针阶段

`code/pcf8563-446-follow/main/main.cpp`，启动时先用 `m5gfx::i2c` 预置 PCF8563：

```
0x01 = 0x01   # TIE=1, TF/AF=0
0x0F = 2      # 2 秒倒计时
0x0E = 0x82   # TE=1, TD=1 Hz
```

然后：

1. `M5.begin(cfg)`，`cfg.disable_rtc_irq = false`；读 `0x0E/0x01/0x0F`。
2. `M5.Rtc.clearIRQ()`；再读。
3. `M5.Rtc.begin(&M5.In_I2C)`（模拟再次 begin）；再读。
4. `M5.Rtc.setTimerIRQ(0)`；再读。
5. `M5.Rtc.setTimerIRQ(3000)` → `M5.Rtc.disableIRQ()`；再读。
6. 重新直写 `0x82`，执行 `Rtc.begin()` + `disableIRQ()`（默认 `disable_rtc_irq=true`
   在 `M5.begin()` 中做的同一对调用）；再读。

## 4. 结果

| 阶段 | `0x0E` | `0x01` | `0x0F` | TE | TD | TIE |
|---|---|---|---|---|---|---|
| PRE_ARM | 0x82 | 0x01 | 0x02 | 1 | 1 Hz | 1 |
| POST_BEGIN_FALSE | 0x82 | 0x01 | 0x02 | 1 | 1 Hz | 1 |
| AFTER_CLEAR_IRQ | 0x82 | 0x01 | 0x02 | 1 | 1 Hz | 1 |
| AFTER_REBEGIN_AFTER_CLEAR | 0x82 | 0x01 | 0x02 | 1 | 1 Hz | 1 |
| AFTER_SETTIMER0 | 0x03 | 0x08 | 0x02 | 0 | 1/60 Hz | 0 |
| AFTER_ARM_LIB (3000 ms) | 0x82 | 0x09 | 0x03 | 1 | 1 Hz | 1 |
| AFTER_DISABLE_IRQ | 0x03 | 0x00 | 0x03 | 0 | 1/60 Hz | 0 |
| BEFORE_DEFAULT_REBEGIN | 0x82 | 0x01 | 0x02 | 1 | 1 Hz | 1 |
| AFTER_DEFAULT_REBEGIN | 0x82 | 0x01 | 0x02 | 1 | 1 Hz | 1 |
| AFTER_DEFAULT_PATH | 0x03 | 0x00 | 0x02 | 0 | 1/60 Hz | 0 |

结论：

- 作者所述四点全部在寄存器层面复现：`false` 保留、`clearIRQ()` 不停止、两个停止入口都落到
  `0x03`、默认 `true` 仍停止。
- `clearIRQ()` 后 `0x01` 仍为 `0x01`，说明只清了 TF/AF，TIE 与 `0x0E` 未动。
- `CNT (0x0F)` 在运行阶段保持 `0x02`/`0x03` 不递减，`TF` 也从未置位：这是 QEMU 模型缺
  倒计时逻辑，不能据此判断定时器是否实际计时。

## 5. 证据等级与边界

- 证据等级：**virtual-device validation**（M5Dial / QEMU / PCF8563 register model）。
- hardware validation：**NOT RUN**；本机与 Device Service 均无 CoreInk 实机或 profile。
- 定时器继续计数、TF 置位、INT 引脚触发：**NOT RUN**。
- 实际电源断→RTC 起床的重复周期，含 `M5.Power.timerSleep(seconds)`：**NOT RUN**；
  `timerSleep()` 的代码路径是在 deep sleep 前调用 `setTimerIRQ()`，但本环境无法执行完整的
  断电/上电周期。
- 其他 PCF8563 板卡的初始化差异：**NOT RUN**；本次只覆盖同一 `PCF8563_Class` 驱动路径。
- 合并 commit 与已评审 PR head 同树，因此上一轮 A/B 的寄存器结论可沿用；本轮是独立重跑，
  不是复用旧日志。

## 6. 对外回复（1 条，日文）

见 `evidence/review-comment.txt`（发布后补入）。回复只包含：

- 合并后 develop 的寄存器复测结论；
- 证据等级、同树事实、记录 permalink；
- NOT RUN 项（实际触发与电源断/起床）。

未关闭 issue、未 push、未修改上游仓库。

## 7. 复现命令

```bash
export IDF_PATH=<esp-idf v6.0.2>
export IDF_COMPONENT_MANAGER=0
export M5GFX_PATH=<M5GFX @ 28d4794>
cd code/pcf8563-446-follow
idf.py set-target esp32s3 build merge-bin
DEVICE_SERVICE_API=<Device Service /api/v1> \
  python3 run_on_device_service.py --image build/merged-binary.bin --out run
```
