# 报告：M5GFX #436 追加排查（217 ms 的归属）

## 1. 来源与现象

- 条目：<https://github.com/m5stack/M5GFX/issues/436>
- 最新评论：GOB52，2026-11-20 05:30Z，issuecomment-7031378374。
- 现象：ToughC5 上手指移动期间 `M5.update()` 偶发数十 ms 停顿，最大约 217 ms（试作、
  案 B 已应用）。作者已在试作的状态下给出驱动内的分段最大值，并判断「时间在驱动之外」，
  但明确说明外侧与内侧不是同一次调用，因此该判断仍是推测。

## 2. 作者提供的数据（外部实测，非本仓库复测）

| 项目 | 值 |
| --- | --- |
| 指未接触时 `M5.update()` 最大 | develop `44324f3`：约 293 ms（移动时）；试作：约 217 ms（移动时） |
| 指移动时 `endTransaction()` | 202〜207 µs，失败 0 次 |
| 指移动时 `readBytes()`（第 2 次，2 点 10 字节） | 876 µs，失败 0 次 |
| retry | 4 周 |
| `getTouchRaw()` 整体 | 1,667 µs |
| 同一区间从 `Panel_Device::getTouchRaw()` 看 `_touch->getTouchRaw()` | 最大 21〜27 ms |

作者同时说明：43,498 µs 是 develop 在手指未接触时的最大值，不是手指移动时的值。

## 3. 代码级核对

### 3.1 一次 `M5.update()` 只读一次触摸

- `M5Unified.inl:2927`：`M5Unified::update()` 在 `Touch.isEnabled()` 时调用
  `Touch.update(ms)`。
- `Touch_Class.inl:26`：`Touch_Class::update()` 调用一次
  `_gfx->getTouchRaw(_touch_raw, TOUCH_MAX_POINTS)`；触摸按键的后续处理只读缓存点，
  不再调用 `getTouchRaw()`。

因此一次 217 ms 的 `M5.update()` 中，`getTouchRaw()` 至多一次。

### 3.2 ToughC5 的 wrapper 不会插入 display transaction

- `esp32c5_construct.inl:25-31`：`touch_toughc5` 只设置 port/pins/freq/range，未设置
  `bus_shared`。
- `construct_common.inl:252`：`i2c_touch_desc_t` 的默认 `bus_shared(false)`。
- `Panel_Device.inl:531-535`：`need_transaction = getStartCount() &&
  _touch->config().bus_shared`；为 false 时只执行 `_touch->getTouchRaw()`。

因此 `Panel_Device::getTouchRaw()` 与驱动之间没有额外等待点，外侧与内侧的差只能是
调用开销或测量本身。

### 3.3 结论

- 217 ms 不能由一次 `getTouchRaw()`（≤1,667 µs）解释，作者的分段数据也排除了
  「25 ms × retry」。
- 但外侧 21〜27 ms 与内侧 1,667 µs 也无法在同一次调用中同时成立。
- 因此「驱动之外」目前不能作为结论；需要同轮、同调用的配对数据，以及
  `M5.update()` 各段（Touch / PM1 按键 / 其他）的耗时。

## 4. 下一步（已在 issue 中提出）

1. 同一次运行内，按调用 index 记录：`M5.update()` 总时长、`Panel_Device::getTouchRaw()`
   总时长、`_touch->getTouchRaw()` 总时长、该次 `getStartCount()`、`Touch.getCount()`、
   retry 次数、每次 `endTransaction()` 的返回值。
2. 记录所有 >5 ms 的调用，而不只是最大值；定位 217 ms 对应的 index。
3. 拆分 `M5.update()` 内部区段。ToughC5 的 PM1 按键读取通过 M5Unified 的 `In_I2C`
   使用同一个 LP I2C 端口（`Power_Class.inl:4269` 起、`M5PM1_Class.hpp:17` 默认
   `&In_I2C`），Touch 之外也值得单独计时。
4. 提供测量 sketch，确认 `M5.update()` 前后的处理与计时区间切法。

## 5. 影响与边界

- 本条不改变案 B 的方向与既有 review 结论；PR 可以不等 217 ms 的定位。
- 本记录不包含任何实机或虚拟设备结果；C5 的硬件与虚拟 profile 均不可用。
- 作者数据仅作为外部证据引用，未在本仓库复现。
