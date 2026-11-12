## 现象

StackChan（`m5stackchan`）上两款同框架固件在首帧、动画 UI 正常跑约 39 s 后崩溃：

| 固件 | firmware_id | SHA-256 | 现象 |
| --- | --- | --- | --- |
| StackChan-UserDemo | 1897200000000002129 | `245bc9af0a5d…` | `Guru Meditation ... (Unhandled debug exception)`，`Debug exception reason: BREAK instr`，PC=`0x403783c0` |
| StackChan-GPT | 2118408999704035329 | `e680215dd185…` | `Guru Meditation ... (InstrFetchProhibited)`，PC=`0x00385cde`，A0=`0x80385cec` |

崩溃前两者都已稳定运行、有画面（320×240，非黑 76800 px，60 色），串口里 SRAM 余量稳定（`free sram: 173567` 连续 5 次不变），没有明显内存泄漏或断言。

## 证据：寄存器形态

StackChan-GPT 的 PC 与返回地址只差低 24 位：

```
PC : 0x00385cde
A0 : 0x80385cec      # 低 24 位 0x385cec ≈ PC 0x385cde
A2 : 0x00000001  A5 : 0x3c3d9a08  A9 : 0x00000001  A12: 0x00060720
```

这种“PC 高位丢失、与 A0 低 24 位对齐”的形态更像**返回地址/函数指针被截断或写坏**，而不是普通的空指针解引用。StackChan-UserDemo 则在 IRAM `0x403783c0` 执行到 BREAK（类似 abort/trap 路径）。

## 会话

- UserDemo：`c558fb72089144a3b598eef5cb1de95a`（串口 12480 B）
- GPT：`6751b8b0be144dc1b07de70f17e2c20b`（串口 13017 B）

## 影响

- StackChan 上跑满 40 s 就崩，长稳和动画/舵机类验收无法进行；同一设备上 M5Launcher/QChan 等固件可运行，说明不是整机不可用。
- 两个不同固件在同一时间尺度崩溃，指向共同的运行时/内存路径（StackChan 使用 8 MiB PSRAM），而不是单一固件逻辑。

## 期望 / 验收

1. 定位崩溃前的第一处内存异常：建议检查 PSRAM（OPI/QSPI 模式与 cache 路径）、函数指针表读取、以及 39 s 附近触发的周期任务（舵机/动画/OTA 检查）。
2. 验收：两款固件都能连续运行 ≥300 s 且 UI 动画正常；同机其它 StackChan 固件与 UIFlow2 用例不退化。
3. 若确认是固件自身缺陷，请附真机对照证据。

## 边界

- virtual-device；不涉及真机舵机、功耗、射频与机械行为。
