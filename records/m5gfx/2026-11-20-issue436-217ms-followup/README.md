# M5GFX #436 追加排查：217 ms 的归属（ToughC5 触摸）

- 日期：`2026-11-20`
- 结果：`REVIEW`（仅代码级梳理；hardware / virtual-device / build 均 `NOT RUN`）
- 工作类型：`issue`
- 条目：[m5stack/M5GFX#436](https://github.com/m5stack/M5GFX/issues/436)
  「LP_I2C ポートで ACK 終端の read の後に endTransaction() が 25 ms 待ち切る」，作者
  GOB52，日文，OPEN。最新评论 GOB52（2026-11-20 05:30Z，
  [issuecomment-7031378374](https://github.com/m5stack/M5GFX/issues/436#issuecomment-7031378374)）
- 源码：`m5stack/M5GFX` `develop` @ `44324f34748812ce557e0dea39fb173cf9a73952`；
  `m5stack/M5Unified` @ `6df015290976764e5e71beffe28abcd25dc54818`
- 环境：macOS arm64，只读公开源码。Device Service 的 36 个 profile 中没有 ESP32-C5
  （只有 C6 的 `nanoc6` / `nesso-n1`、P4 的 `tab5`），也没有 C5 实机

## 结论

作者补充数据后，上一轮「25 ms 等待按 retry 累积成 217 ms」的判断不成立：试作中
`endTransaction()` 为 202〜207 µs、失败 0 次，retry 4 周，`getTouchRaw()` 单次最大
1,667 µs；按最大值累 5 周也只有 8.3 ms。该判断已撤回。

但现有数据也不足以把 217 ms 归到「驱动之外」，有两点对不上：

- `M5.update()` 只调用一次 `Touch.update()`，后者只调用一次 `getTouchRaw()`
  （M5Unified `6df0152` 的 `src/M5Unified.inl:2927`、`src/utility/Touch_Class.inl:26`）。
  217 ms 的那次调用理应出现在「外侧最大 21〜27 ms」的采集里。
- ToughC5 的 touch 在新 board_detect 构造中 `bus_shared = false`
  （`src/board_detect/m5/esp32c5_construct.inl:25-31`，默认值见
  `construct_common.inl:252`），`Panel_Device::getTouchRaw()` 的
  `endTransaction()` / `beginTransaction()` 分支（`Panel_Device.inl:531-535`）不会执行。
  外侧与内侧之间实际上没有能插入 20 ms 的代码。

因此 217 ms 与 21〜27 ms 很可能不是同一次运行的同一次调用（不同 sketch/不同轮次，
或最大值保持漏掉了部分 return）。「另有原因」的方向合理，但目前仍是推测。下一步应在
同一次运行内按调用配对，并把 `M5.update()` 的区段拆开（Touch 之外，ToughC5 的 PM1
按键读取也走同一个 LP I2C）。

## 关键证据

- 作者试作值（ToughC5，属 hardware validation，不是本仓库复测）：`endTransaction()`
  202〜207 µs、失败 0；第二次 `readBytes()`（2 点 10 字节）876 µs、失败 0；retry 4 周；
  `getTouchRaw()` 整体 1,667 µs；同一区间外侧调用最大 21〜27 ms。手指移动期间
  `M5.update()` 最大值：develop 约 293 ms、试作约 217 ms。
- 单次 `M5.update()` 对触摸只读一次；217 ms 无法由一次 `getTouchRaw()`（≤1,667 µs）解释。
- ToughC5 touch 的 `bus_shared` 为 false，wrapper 不插入 display transaction。
- 结论：既有数字互相矛盾，先做同轮配对采集，再决定是否拆成独立 issue。

## 文件

- `report.md`：完整报告（代码路径、作者数据摘要、下一步、边界）
- `run.json`：结构化记录
- `evidence/code-facts.txt`：固定 commit 的源码位置与摘录
- `evidence/latest-comment-summary.md`：作者最新评论的数值摘要（含出处）

## 未覆盖项

- 217 ms 的原因：未定位。本记录是代码级梳理，不是实测。
- hardware validation：`NOT RUN`。没有 C5（ToughC5）实机。
- virtual-device validation：`NOT RUN`。Device Service 没有 C5 profile。
- build：`NOT RUN`。本机没有 C5 的 Arduino / ESP-IDF 工具链。
- C6 / P4 的 LP 端口：`NOT RUN`。
- 作者在 ToughC5 上的实测（217 ms、21〜27 ms、1,667 µs 等）均为作者数据，本仓库未复测。

## 已发布回复

- 待补充（发布后追加 URL）。
