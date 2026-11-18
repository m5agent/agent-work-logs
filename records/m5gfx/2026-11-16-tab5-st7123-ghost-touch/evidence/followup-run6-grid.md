# 第十九轮：65 s 网格、148 ms 定长前因与 1/7 转化率

- 来源评论：huntson，2026-11-18T01:38:17Z，
  [issuecomment-6966368918](https://github.com/m5stack/M5GFX/issues/418#issuecomment-6966368918)
- 回复：[issuecomment-6966482255](https://github.com/m5stack/M5GFX/issues/418#issuecomment-6966482255)
- 作者数据：单台单 boot 60.3 min（3616 s），无人值守、无按压；16 条带点读（11 双轨 + 3 同 x + 2 弱起始），
  256 条 keep-alive 全空；8 个双轨 episode 全部在 65 s 网格上，且前一次调用 147.1–149.6 ms。
- 本轮只做算术与口径核对，无新运行时数据；脚本与输出见
  [grid-check.py](grid-check.py) / [grid-check.txt](grid-check.txt)

## 结论

1. **前因是定长主机操作，不是总线等待**：8 次 147.1–149.6 ms（离散 1.7%，均值 148.5），
   锁等待已在测量口径外，其余四器件单次事务亚毫秒，排队数十次才会到 148 ms 且会随队列浮动。
2. **周期在主机侧**：15 个 episode 跨两个 boot 落在 9.35 s（mod 65）±15 ms，周期在主机时间上
   稳定到几 ppm；65536 ms 会在本 boot 漂 29.6 s，60 s 被 464.354→659.356 排除 → 65000 ms 或其组合。
3. **网格不只出双轨**：本轮 2349.353（前因 147.1 ms）后续依次是 n=4 双轨、n=6 x=719 列、
   两条 (710,y) 单点（y 相差 132）；上一 boot 的 x=0 列 2479.355/2544.351 也在网格上
   （9.355/9.351 mod 65）。两个 boot 唯一离网的是 x=358 列（11.06 s、676.42 s），同一固定列。
   故上一轮“形状选择性与总线矛盾”的论证只属于暂停域，不能外推到机制。
4. **转化率约 1/7**：本轮 8/56 个 9.35 s 节拍（14.3%），上一 boot 7/58（12.1%），
   且两 boot 命中的节拍编号不同（7,10,12,15,21,36,46,48 vs 11,21,22,26,29,38,39）。
   65000 mod 23 = 2 ms 会让每个节拍落在不同轮询相位；按“调用结束 = episode 起点 − gap”复算，
   八次结束落在 23 ms 周期的 8.2/15.5/20.8/9.6/12.4/19.1/18.8/21.3 ms，无偏好相位 → 14% 不是采样假象。
5. **状态晚于调用、且鬼点全是起始**：148 ms 调用本身无点，点由 21.9–22.7 ms 后（一个正常轮询间隔）
   的读给出；所有鬼点读在驱动口径里都是 weak start/ignored，没有一条是已接受接触的续帧
   （691 那次是三次独立 weak start）。所以规则形状应为“扰动窗口内不开新接触、已开的继续更新”。
6. **本轮是否是“短停顿”样本，取决于读在 148 ms 调用内的位置**：keep-alive 只有每 14 s 一次
   （256/3616），覆盖不了；芯片未读窗口是 22–170 ms，正好落在 63–79 ms（1/326）与 1.3–2.5 s（约 1/5）
   之间。故下一步要日志记录调用内触摸事务自身的起止，而不是只记调用总时长。

## 证据等级与局限

- 作者：计数/时序/普查为 `hardware validation`；`touch path unknown`、`panel state unknown`。
- 本记录：`code-level verification`，只对作者时间戳做模运算；无新运行时数据。
- 物理 Tab5：`NOT RUN`。虚拟设备：`NOT RUN`，2026-11-18 复查本机 Device Service `/api/v1/devices`
  仍 `tab5_enabled: false`；`tab5` 为 `supported`/`creatable`/`backend_ready`，但 `features.qom=false`、
  `device_state=false`，警告仍为 "Tab5 ST7123 touch is currently a firmware GDB mailbox rather than an I2C chip model"。
- 未覆盖：单台单 boot、无按压、未看屏；65 s 来源未定位（网格是对时间戳的算术，不是对操作的测量）；
  未泄漏节拍上是否也有慢调用未知；仅空闲域，暂停域触发、6/9 覆盖停顿个例、boot 132 的 205 ms 重绘未触及；
  无 INT、无电极图；给 M5Stack 的两个问题仍未答。

## 复算

```
python3 grid-check.py   # 输出见 grid-check.txt
```
