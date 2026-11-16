# 追加证据：INT 双帧、with_coord 与协议 §6.6（第二轮）

- 采集者：报告者 huntson（Tab5 实机，触摸固件版本 01）
- 来源：[M5GFX#418 评论 6907904668](https://github.com/m5stack/M5GFX/issues/418#issuecomment-6907904668)，2026-11-16T05:09:14Z
- 用途：核对 m5agent 上一轮提出的“两帧 INT 电平”与“with_coord 是否被读取清除”两项判据
- 说明：以下数据均为报告者测量，本记录只做协议与主机侧核算，未复现

## 1. 作者测量摘要

| 项目 | 结果 |
| --- | --- |
| 有两点坐标的相邻两帧 | 7 例；两帧之间 INT 均先高后低，未出现持续低电平 |
| 两帧字节 | 5/7 不同；2 例相同，均为单事务读取模式 |
| INT 周期 | 约 8.7 ms 一帧；不读取时约 8.7 ms 自行回高；读取会更早清除 |
| 鬼触点 INT 低电平宽度 | 4.8–21 ms |
| burst 结束后的 `adv_info` | 10/10 次（两种读取模式）仍为 `0x08`，即 `with_coord=1` |

## 2. burst 原始帧（stock 三次读，INT 读前低、读后高）

```text
read @0.0ms   adv_info=08
  report 0: 80 00 02 4a 20 0d 00  valid=1 x=0   y=586 area=32 intensity=13
  report 1: 82 cf 01 f7 20 0d 00  valid=1 x=719 y=503 area=32 intensity=13
read @24.0ms  adv_info=08
  report 0: 80 00 02 7c 20 0d 00  valid=1 x=0   y=636 area=32 intensity=13
  report 1: 82 cf 02 74 20 0d 00  valid=1 x=719 y=628 area=32 intensity=13
reports 2-8: valid=0，两帧之间字节不变
```

单事务（`0x0010` 起 74 B）同一 burst：`(0,634) area=32 intensity=12` 与
`(719,619) area=28 intensity=11`。

解码后的共同特征：

- x 精确落在两端 `x=0` 与 `x=719`（Tab5 的 `x_max`），同一帧两点；
- area 28–32，intensity 11–13；
- 两端 y 差：83（第一帧）、8（第二帧）、15（单事务帧）；上一轮 97 例表中的成对样本
  差 2 和 3。即“同一行”只在多数帧近似成立，不是稳定不变量；
- 上一轮另一类鬼点是单点、area 1、intensity 10，说明鬼点至少有“边缘对”和“窄单点”
  两种形态，两者都靠 intensity 门限拦截。

## 3. 协议 §6.6 原文（Sitronix ST7123 TDDI Interface Protocol V01.11）

- 文档：<https://dl.espressif.com/AE/esp-iot-solution/ST7123+TDDI+Interface+Protocol+V01.11.pdf>
- 版本/日期：01.11，2023-12-25；22 页；PDF SHA256
  `40db033ce31fa5785dac1698b9271561382609150e6d3e7b1f5fcdb9f838efce`
- 位置：§6.6 Reporting table，p.18–19

> The touch controller will output INT pin to notify host that data in reporting table is
> updated. If host read any Reg addr. from 0x0010 to Reg addr. 0x0013, and if the bit
> "With Coord." and "With prox. raw." is 0, the touch controller will clear INT pin and
> update next data if they're ready. If the bit "With Coord." is 1, host must read the last
> Reg. addr. of the last supported coordinate and the touch controller will clear INT pin.

> c. With Coord.: If this bit is 1, it means coordinates are updated in this INT signal.
> If host read the last Reg. addr of the last supported coordinate, the touch controller
> will clear this bit.

## 4. 主机侧核对：两种读取模式都覆盖了“最后一个坐标寄存器”

- 每个触点 7 B：`0x0014 X_H`、`X_L`、`Y_H`、`Y_L`、`area`、`intensity`、`reserved`。
- `0x0009` 读到 10，`max_touch_points = 10`（`Touch_ST7123.hpp:49`），所以最后一个
  触点的最后一个寄存器是 `0x0014 + 10*7 - 1 = 0x0059`。
- stock 三次读：`_readParams(0x0014, ..., 7 * max_touches)` → `0x0014..0x0059`
  （`Touch_ST7123.inl:141`）。
- 单事务读：`0x0010` 起 74 B → `0x0010..0x0059`。
- 两种模式都读到 `0x0059`，按 §6.6 应当同时清除 INT 和 `With Coord`。

## 5. 推断与边界

1. **INT 双帧判据成立**：两帧之间 INT 先高后低，说明每次读取拿到的是新帧，没有重复
   供给，也没有三次读跨帧撕裂造成的伪点。字节相同的 2 例发生在单事务模式，属于同一
   静止伪影在相邻帧的重复上报，不是同一次读取被服务两次。
2. **`With Coord` 与 INT 两个确认信号不一致**：INT 被读取清除，而 `With Coord` 在
   10/10 次 burst 后仍为 1，与 §6.6c “读最后一个坐标寄存器即清除该位”不符。可能是
   固件未实现该清除，或在采样前已有下一帧把它重新置位。单凭现有数据无法区分。
3. **该不一致不影响“点是否有效”**：报告者在约 117,000 次 INT 高电平读取中没有读到
   有效点，说明控制器仍按帧清除各槽位的 valid 位；`with_coord` 残留不会让旧点被反复
   上报。
4. **对驱动的影响**：`getTouchRaw()` 用 `if (adv_info.with_coord)` 决定是否读表
   （`Touch_ST7123.inl:134`）。该位一旦长期为 1，门控在首次触摸后就不再短路，每次
   调用都会固定执行 `0x0010` + `0x0009` + 70 B 三次事务。这是效率问题，不是正确性
   问题，但在共享 I2C 总线上可以测量到。
5. **INT 低电平宽度不适合做判据**：读取会提前清除 INT，未读取时约一帧自行回高，宽度
   主要由主机何时服务该引脚决定，与触点持续时间没有稳定关系。

## 6. 未覆盖

- 真实手指的原始报表（尤其靠 `x=0` / `x=719` 边缘的按压）与 area/intensity 分布：`NOT RUN`
- 空闲 10 s 后 `0x0010` 是否回到 `0x00`（用于判定该位是“上一帧状态”还是“只置不清”）：`NOT RUN`
- 第二台 Tab5、不同温度、轻触/手套下的阈值误拒率：`NOT RUN`
- 触摸固件侧是否会在扫描恢复时产生边缘钳位坐标：需 M5Stack 确认
