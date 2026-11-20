# 作者最新评论的数值摘要

- 出处：<https://github.com/m5stack/M5GFX/issues/436#issuecomment-7031378374>
- 作者：GOB52，2026-11-20 05:30Z，日文。
- 性质：作者在 ToughC5 上的实机测量（hardware validation）。以下为本仓库的摘要，
  不是原始日志；本仓库未复测。

## 217 ms 是试作（案 B）状态下的值

| 状态 | 手指移动期间 `M5.update()` 最大 |
| --- | --- |
| develop `44324f3` | 约 293 ms |
| 试作 | 约 217 ms |

作者同时更正：43,498 µs 是 develop 在手指未接触时的最大值，不是移动时的值。

## 试作 + 手指移动区间的驱动内最坏值

| 项目 | 最坏值 | 失败次数 |
| --- | --- | --- |
| `endTransaction()` | 202〜207 µs | 0 |
| `readBytes()`（第 2 次，2 点 10 字节） | 876 µs | 0 |
| retry | 4 周 | — |
| `getTouchRaw()` 整体 | 1,667 µs | — |

同一区间从 `Panel_Device::getTouchRaw()` 看 `_touch->getTouchRaw()` 的调用：最大 21〜27 ms。
作者明确说明，外侧慢调用与内侧记录没有按同一次调用配对，因此「另有原因」仍是推测。

## 差分计划

- 先完成上述配对测量，再把 217 ms 作为独立问题拆分。
- PR 在拆分调查结束后提交，并反映既有 review 观点（失败时清除 `last_read_acked`、
  哑读的意图、读指针前进 1 字节的注释等）。
