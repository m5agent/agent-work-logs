# 追加证据：M5Unified#367 把 Tab5 LCD_RST 由驱动高电平改为上拉输入

- 采集/核对时间：2026-11-16（UTC）
- 来源评论：<https://github.com/m5stack/M5GFX/issues/418#issuecomment-6915523306>
  （huntson，2026-11-16T11:46:32Z）
- 性质：只读源码核对 + 引用报告者实测数据；未修改 M5GFX/M5Unified，未推送上游

## 1. 报告者本轮新增数据

同一台 Tab5（ST7121 面板、touch FW 01）、同一 60 轮循环、背光 255、自家 UI，每轮
3600 次读取，全部强制读（不再用 `with_coord` 门控）：每轮先读 `0x0010`，再无条件读
`0x0009` 与 `0x0014` 起 70 B，三次事务。

| 构建 | 含 valid 位的帧 | `with_coord`=1 / =0 | `0x0010`/`0x0009`/`0x0014` 失败 | `adv_info` |
| --- | --- | --- | --- | --- |
| develop：M5GFX `b48dce04` + M5Unified `e9a8e89` | 0 | 0 / 0 | 0 / 0 / 0 | 3600/3600 为 `0x00` |
| pinned：M5GFX `d91077b9` + M5Unified `8530f53` | 92，出现在 46/60 轮 | 92 / 0 | 0 / 0 / 0 | 3600/3600 为 `0x08` |

拆分（stock 驱动、带门控 `getTouchRaw()`）：

| M5GFX | M5Unified | 60 轮中出现帧的轮数 |
| --- | --- | --- |
| `b48dce04` | `8530f53` | 45 |
| `d91077b9` | `e9a8e89` | 无法编译：develop M5Unified 需要 develop M5GFX 的 board-detect API |
| `b48dce04` | `e9a8e89` | 0 |

按 M5Unified first-parent merge 二分（每侧用当期 M5GFX develop），再把 M5GFX 固定在
`bd331321` 复验过渡点：

| M5Unified | 60 轮中出现帧的轮数 |
| --- | --- |
| `a5285020`（#366 的 merge） | 44 |
| `24dad4ff`（#367 的 merge） | 0 |

## 2. #367 的真实 diff

`24dad4ff183907a0270889f1945966b072f3c28d` 只改一个文件、三个字节，全部在 Tab5 /
Tab5X 的 PI4IOE5V6408（0x43）初始化块里：

```diff
@@ src/utility/Power_Class.inl
   0x05, 0b01110000,   // OUT_SET
-  0x03, 0b01110011,   // IO_DIR
+  0x03, 0b01100011,   // IO_DIR (LCD_RST input)
   0x07, 0b00001000,   // OUT_H_IM
-  0x0D, 0b00000100,   // PULL_SEL
-  0x0B, 0b00000100,   // PULL_EN
+  0x0D, 0b00010100,   // PULL_SEL (LCD_RST pull-up)
+  0x0B, 0b00010100,   // PULL_EN (LCD_RST pull-up enabled)
```

两版行号：

- pinned `8530f5377d782e4a25a6c482de2e71c3f75ca8eb`
  `src/utility/Power_Class.cpp:141-155`，写入在 `:173`
  <https://github.com/m5stack/M5Unified/blob/8530f5377d782e4a25a6c482de2e71c3f75ca8eb/src/utility/Power_Class.cpp#L141-L155>
- develop `e9a8e8985e4c8e45b207d576b9405a419dbcd177`
  `src/utility/Power_Class.inl:556-570`，写入在 `:588`
  <https://github.com/m5stack/M5Unified/blob/e9a8e8985e4c8e45b207d576b9405a419dbcd177/src/utility/Power_Class.inl#L556-L570>

## 3. 位解码：只动了 P4 = LCD_RST

寄存器数组自带按位注释，bit7..bit0 依次是 HP_DET、CAM_RST、TP_RST、LCD_RST、NC、
EXT5V_EN、SPK_EN、RF_PTH_L_INT_H_EXT。驱动语义由类自身声明（两版实现相同）：

- `setDirection(pin, true)` → `bitOn(0x03, bit)`，注释为 `// Output, set 1`、文件头
  `// false input, true output`（`PI4IOE5V6408_Class.inl:25-34`）；
- `setPullMode(pin, pull_up)` → `0x0D` 置位（选上拉）+ `0x0B` 置位（使能）
  （`PI4IOE5V6408_Class.inl:36-52`）。

| 寄存器 | pinned | develop | 位变化 | 对 P4/LCD_RST 的影响 |
| --- | --- | --- | --- | --- |
| `0x05` OUT_SET | `0x70` | `0x70` | 无 | 输出锁存仍为 1，但输入模式下无效 |
| `0x03` IO_DIR | `0x73` | `0x63` | bit4 1→0 | 推挽输出高 → 输入 |
| `0x0D` PULL_SEL | `0x04` | `0x14` | bit4 0→1 | 选上拉 |
| `0x0B` PULL_EN | `0x04` | `0x14` | bit4 0→1 | 使能上拉 |

其余引脚不变：P6 CAM_RST、P5 TP_RST、P1 SPK_EN、P0 RF_PTH 两版都是推挽输出且
OUT_SET 为 1；P2 EXT5V_EN 两版都是带上拉的输入；P3、P7 为输入。因此**唯一差异是
LCD_RST：从被扩展器推挽驱动为高，变为释放给扩展器内部上拉；TP_RST 没有变**。

板级网络侧：M5Stack 官方 Tab5 原理图第 1 页 U6（PI4IOE5V6408，ADDR 接地 = 0x43，
网格 4A-B）同时引出 `LCD_RST`、`TP_RST`、`CAM_RST`、`SPK_EN`、`EXT5V_EN`、`HP_DET`
与 `RF_PTH_L_INT_H_EXT`；`LCD_RST` 与 `TP_RST` 都进入显示/触控 FPC J3。本次核对没有
逐引脚追查该网络上是否存在外部上拉，也没有示波器测量。

## 4. 为什么该差异能解释拆分/二分结果

M5GFX 的 Tab5 路径不控制这条 reset：

- 触摸描述符只传 SDA/SCL/INT（`esp32p4_construct.inl:120-128`），没有 reset 引脚；
- 面板描述符没有 `pin_rst`，`Panel_Device::init/rst_control` 在 `pin_rst < 0` 时直接
  返回（`Panel_Device.inl:363-397`）；
- `Panel_DSI::init()` 只在 `getResetDelayBeforeDpi()` 非 0 时发 `CMD_SWRESET`，ST7121
  未覆盖该值，所以连软件复位都不发（`Panel_DSI.inl:125-142`、`Panel_ST7121.hpp`）；
- `Touch_ST7123` 只读寄存器，不写配置、不复位芯片。

因此在这套库里，能改变 LCD_RST 的只有 M5Unified 的扩展器初始化；报告者观察到的
M5Unified 侧差异与该引脚一一对应，不是巧合，也不是解析层差异。

## 5. 需要修正的前一轮表述

1. 上一轮写的“PI4IOE 初始化字节在两版完全相同”只适用于 #402 语境下的 0x44 块；
   对 Tab5 的 0x43 块不成立，而 #367 正是这里的差异。
2. `with_coord` 常置 1 曾被解读为“与协议 §6.6 的确认不一致”。在有 #367 的构建上
   `adv_info` 为 `0x00`（3600/3600），说明正常初始化时读表确实会清该位；`0x08` 是控制器
   启动状态异常的症状，不是协议确认失效。它和鬼点在同一批构建上 1:1 共变，指向同一个
   初始化差异同时决定两者。

## 6. 机制假设（均未证明）

- **A：状态在初始化时被锁存。** TDDI 的触控核与显示复位共享上电/复位域（或共享同一
  内部复位释放时序），LCD_RST 被强驱动与仅上拉会让复位释放的边沿/电平不同，触控报表
  状态机因此停在“`with_coord` 常置、扫描恢复时吐边缘钳位弱点”的状态。运行期改引脚
  状态不会改变，只有重新上电/复位才会。
- **B：持续电气差异。** 强驱动与上拉在反灌、漏电、边沿或电平平坦度上不同，运行期释放
  引脚即可改变控制器行为。背光亮度与鬼点率相关（255 稳态最多、0+黑屏为 0）说明模拟
  前端基线受显示电流影响，但该相关性无法区分 A/B。

判别实验：运行期改写 0x43 三个字节（不重启），看 `adv_info` 与鬼点是否立即变化；再在
运行期给 LCD_RST 一个低脉冲（驱动低约 10 ms 后释放为上拉），看是否能清掉 `0x08`。

## 7. 建议报告者执行的下一步（按性价比）

1. **运行期回切**：在出鬼点的 pinned 固件里，`M5.begin()` 之后写
   `0x03=0x63, 0x0D=0x14, 0x0B=0x14`，读 `adv_info` 并跑 60 轮；再写回
   `0x03=0x73, 0x0D=0x04, 0x0B=0x04` 复跑。同一 boot 内可逆，直接区分 A/B。
2. **0x43 寄存器快照**：sketch 与自家固件在 `M5.begin()` 后各读一次
   `0x03/0x05/0x07/0x0B/0x0D/0x0F`。若字节相同而芯片状态不同，则“缺 #367 仍为 0”
   的差异在自家 boot 的其它环节（面板初始化顺序/时序），不在扩展器配置。
3. **#367 构建上的 boot 鬼点**：4.6–6.0 s 那批尚未在该构建上复跑，可验证 #367 是否
   同时消除它们。
4. 运行期复位脉冲（见上），用于区分“复位不完整”与“复位正常但模拟基线错误”。
5. 真实手指原始报表（尤其贴近 x=0 / x=719），标定 area/intensity 规则。

## 8. 给上游的新问题

1. #367 的 commit message 说“weak pull-up for resetting the LCD should be addressed”，
   但合并的三个字节做的是相反的事：不再驱动该线，改为依赖上拉。哪种状态才是 Tab5
   预期的？是否存在需要强驱动状态的硬件版本？合并说明里提到的“Capture LCD reset
   mode”（`_tab5_lcd_rst_pullup`）在 M5Unified develop 中并不存在，代码对
   `board_M5Tab5` 与 `board_M5Tab5X` 一律使用上拉形式。
2. 该面板的 LCD_RST 是否同时复位触控核（TDDI）？是否有最小复位低电平/释放斜率要求？
   若“复位释放不完整”会让报表状态机停在 `with_coord` 常置并在扫描恢复时输出边缘钳位
   弱点，两个异常就能由同一原因解释。

## 9. 边界

- 证据等级：`code-level verification`（三字节 diff、位解码、Tab5 路径无其它 reset 写入）
  + 报告者硬件测量；本机物理 Tab5 `NOT RUN`。
- 虚拟设备 `NOT RUN`：Device Service 已把 Tab5 列为 supported/creatable，但其告警仍写明
  “Tab5 ST7123 touch is currently a firmware GDB mailbox rather than an I2C chip model”，
  且没有 PI4IOE5V6408 / reset 网络模型，无法产生 `adv_info` 状态或复位线效应。
- 未测：LCD_RST 的示波器波形/电平、外部上拉是否存在、运行期回切与复位脉冲、boot 鬼点
  在 #367 构建上的复跑、第二台单元、温度与轻触数据、真实手指原始报表。
