# M5GFX #442 评审：StopWatch 启动时 Type-C USB 选择

## 条目

- PR：[m5stack/M5GFX#442](https://github.com/m5stack/M5GFX/pull/442)，
  标题 *Fix StopWatch Type-C USB selection at startup*，英文，正文 2 行。
- 作者：GitHub `hlym123`；提交作者 `luoweiyuan <luoweiyuan@m5stack.com>`。
- 状态：2026-11-24T09:44Z 创建，OPEN，评审前 comments / reviews 均为 0，无此前 m5agent 回复。
- head `cc6d5ff74783f7b001725a6f758ef11ffa7231aa`，base `92bd25c890bb05ea057064401401843e9c9f4f25`
  （= 当前 develop tip），MERGEABLE，3 文件 +45 / −5。
- 关联硬件：M5Stack StopWatch C152（ESP32-S3R8、M5PM1 + M5IOE1、CO5300 466×466、CH442E 复用器）。

## 结论

差异本身成立：它改的是 M5IOE1 GPIO1 / `PYB_MUX_CTR` 这一个引脚，位与顺序都对，
在虚拟 StopWatch 上冷启动后 GPIO1 稳定为推挽低电平，显示与触摸的电源/复位序列不受影响。
没有发现阻塞合并的缺陷。

但提交说明里“驱动为高会把 USB 切到后部连接器并断开内置 Type-C 数据线”这句话，
在目前唯一公开的 StopWatch 原理图（C152-SCH `VA_20251201`）上得不到支持，需要作者给出
V1.1 版的依据；同时这次改动让后部扩展口的默认功能从 USB 变成 UART0，且固件不再有任何
板级路径把它切回 USB，这一点应确认是有意为之。

证据等级：**virtual-device validation**（冷启动寄存器状态 + 首帧）+
**code-level verification**（位映射、顺序、影响面）+ **host-level test**（34/34）。
真机（Type-C 实际枚举）与热复位保留锁存路径均 **NOT RUN**。

## 差异

```
src/board_detect/m5/pmic_ops.hpp:94-108   (PR head)
-    ops::i2c_write8(1, 0x23, 0x00), ops::i2c_bit_off(1, 0x13, 0x9D),
-    ops::i2c_bit_on(1, 0x03, 0x9D), ops::i2c_bit_on(1, 0x05, 0x99),
+    ops::i2c_write8(1, 0x23, 0x00),
+    ops::i2c_bit_off(1, 0x05, 0x01), ops::i2c_bit_off(1, 0x13, 0x9D),
+    ops::i2c_bit_on(1, 0x03, 0x9D), ops::i2c_bit_on(1, 0x05, 0x98),
```

`test/board_detect/fixtures/s3.txt:187` 与 `test/board_detect/ops_host.cpp`
（新增 `test_stopwatch_typec_usb_default`，写出计数 12→13）同步更新。

## 核对 1：位与引脚

- M5IOE1 寄存器语义：`0x03` = `GPIO_M_L`（1 = 输出）、`0x05` = `GPIO_O_L`（输出锁存）、
  `0x13` = `GPIO_DRV_L`（0 = 推挽，1 = 开漏，复位值 0xFF）。
  依据：M5Unified `src/utility/M5IOE1_Class.inl:12-28` 常量；
  `IO_Expander_Datasheet_EN.pdf` 第 6 页寄存器表（M8..M1 / O8..O1 / DRV8..DRV1）。
- 引脚到位：`M5IOE1_Class::gpio1 = 0`，`_regForPin(reg_low, pin) = reg_low + (pin >> 3)`、
  `_bitForPin(pin) = 1 << (pin & 7)`（`M5IOE1_Class.hpp:19-31, 92-93`），
  所以 GPIO1 / PYG1 就是低位寄存器 bit 0。
- 板上网络：PYG1 → `PYB_MUX_CTR` → U26 CH442E 的 IN（原理图第 4 页 PYB_IIC / Ext.Port&CH442E）。
  旧代码 `0x05 |= 0x99` 同时置高 GPIO1/4/5/8，其中 GPIO1 就是 MUX_CTR；新代码把它排除，
  改成 `0x98` 并在前面显式清 bit0，目标位正确。

## 核对 2：顺序与保留锁存

- 新顺序在使能输出之前先写锁存低：`0x05 bit0 ← 0` → `0x13`（推挽）→ `0x03`（输出）→ `0x05 ← 0x98`。
  对“上次固件留下 push-pull 高 + 输出使能”的热复位场景，这是能把引脚尽早拉低的写法；
  若是先使能输出再写锁存，会先把 MUX_CTR 短暂驱动为高。
- 仍存在无法消除的窗口：芯片复位到 M5GFX 进入 `stopwatch_power_on` 之间（本次虚拟设备约 250 ms，
  含 ROM / 二级 bootloader / app 初始化），IOE1 未被复位时引脚保持上一次的电平。
  这段窗口本 PR 覆盖不到，属于设计取舍，不是缺陷。
- fixture 与断言一致：`6:1,5,0,1`（清 bit0）排在 `6:1,19,0,157`（0x13 清 0x9D）之前，
  新增测试对 0x00/0xFF 三种初值组合都断言“任何 0x03/0x05/0x13 写入后 bit0 为 0”，
  并要求其他 G2/G6/G7 位保持不变。

## 核对 3：影响面

- 全树只有 `pmic_ops.hpp` 写 M5IOE1；M5GFX 里没有第二处 `MUX_CTR` 写入。
- M5Unified 中 `M5IOE1_Class::gpio1` 的写入只属于 CoreMatrix（TF 卡电源）与 CoreP4X（音频电源），
  不属于 StopWatch；StopWatch 路径没有别的地方改这个位。
- 官方 `M5StopWatch-UserDemo` 的 `main/hal/hal_ioe.cpp:32` 也把
  `M5IOE1_PIN_1` 注释为 “CH442E MUX CONTROL”，并在 `:76` 写 0；本 PR 的低电平默认与官方
  App 固件一致，这是支持该改动的独立旁证。
- 行为变化：改后 GPIO1 永久推挽低，后部 J5/J6 扩展口按公开原理图注记默认走 UART0；
  由于没有专门的 API 把它切回 USB，应用只能自己通过 `M5.getIOExpander(0)` 或 I2C 直接写。
  原先“后部口默认 USB”的能力事实上消失，需要在提交说明里写明。

## 运行证据（虚拟设备）

构建：ESP-IDF v6.1，target esp32s3，16 MB flash + 8 MB octal PSRAM，M5GFX 组件分别指向
PR head 与 develop tip 的两个只读副本；应用只做三件事：`M5GFX::init()`、读 0x03/0x05/0x13、
把数值打到串口并画到屏幕。完整构建参数与固件哈希见 `evidence/environment.txt`。

| 构建 | 板型识别 | 初始化后寄存器 | GPIO1 | 首帧 |
| --- | --- | --- | --- | --- |
| develop `92bd25c` | `board_M5StopWatch`，468×468 | `mode=0x9D out=0x99 drv=0x00` | **1** | 正常 |
| PR `cc6d5ff` | `board_M5StopWatch`，468×468 | `mode=0x9D out=0x98 drv=0x00` | **0** | 正常 |

- PR 构建的 `IOE1_SAMPLE_0..2`（间隔 1 s）与 `IOE1_STABLE` 全部是 `out=0x98`，
  说明初始化后没有别的路径把它改回高。
- 两次构建的 `0x03` 都是 `0x9D`、`0x13` 都是 `0x00`，即 GPIO1/3/4/5/8 仍然被设为输出，
  GPIO1 为推挽低；TP_RST/OLED_RST 的 10 ms/8 ms 复位脉冲仍照旧执行，首帧渲染正常
  （`evidence/frame-pr.png`、`evidence/frame-develop.png`），没有显示/触摸回归迹象。
- 热复位路径（先人为把 GPIO1 拉高再 `esp_restart()`）没有跑通：虚拟设备在
  `rst:0xc (RTC_SW_CPU_RST)` 之后不再继续 boot（ROM 行之后没有再打印二级 bootloader），
  该会话停在 6518 字节串口输出，属模型限制，因此保留锁存场景 **NOT RUN**。

Host 测试：PR 树上 `sh test/board_detect/run.sh` → `C++ test programs: 34 passed`
（含新增 `test_stopwatch_typec_usb_default`），见 `evidence/host-tests-pr.txt`。

## 与提交说明不一致的地方（待作者确认）

公开原理图 C152-SCH `VA_20251201`（docs.m5stack.com StopWatch 页面唯一链接）第 4 页：

- U26 CH442E 的公共端 DB(4)/DC(6) 接 `MUX_IO_1/MUX_IO_2`，即后部 J5/J6 扩展口；
  四个选择端接 `G43_U0TXD`/`G44_U0RXD` 与 `USB_P`/`USB_N`。
- 图注原文：“PYB_MUX_CTR selects U0TXD/U0RXD when low, and USB_P/USB_N when high”。
- 第 3 页 TYPEC 区 J1 的 D+/D− 直接接同一对 `USB_P/USB_N`，不经过复用器。

按这张图，G1 为高只是把 USB 并到后部扩展口，并不会“断开内置 Type-C 数据线”；
G1 为低则后部口是 UART0。作者描述的 V1.1 若确实重画了复用器（公共端改到 SoC USB、
两个选择端分别接 Type-C 与后部口），需要指到那一版原理图/ECO，说明才可追溯。
两种版本共用同一份固件，这一点也需要在提交说明里交代。

## 未覆盖项

- **真机 Type-C 枚举**：NOT RUN。本机没有可观察 Type-C 数据通路的 StopWatch，未在实机上验证
  “G1 低 → Type-C 可枚举 / G1 高 → 不可枚举”。
- **热复位保留锁存**：NOT RUN，原因见上（虚拟设备 `esp_restart()` 后不再 boot）。
- **USB 复用本身**：虚拟 StopWatch 没有 USB PHY/复用器模型，只能观察 IOE1 寄存器状态，
  不能观察后部口或 Type-C 上的实际链路。
- **V1.1 硬件**：没有该版原理图，无法核对提交说明中的电气结论。

## 风险与回滚

- 回滚方式：还原 `pmic_ops.hpp` 的三行与对应 fixture/断言即可，无持久化状态改动。
- 旧固件留下的 push-pull 高状态在升级后第一次启动时仍可能维持到 `M5.begin()` 为止；
  升级后的后续启动不受影响。

## 引用

- PR head 源码：`https://github.com/m5stack/M5GFX/blob/cc6d5ff74783f7b001725a6f758ef11ffa7231aa/src/board_detect/m5/pmic_ops.hpp#L94-L108`
- 原理图：`https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1242/C152-SCH_Stopwatch_PRJ_Main_VA_20251201_2026_04_24_17_46_22.pdf`
  （第 3、4 页；副本与 SHA256 见 `evidence/`）
- M5IOE1 数据手册：`https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1210/IO_Expander_Datasheet_EN.pdf`（第 6 页）
- 官方 App 固件：`https://github.com/m5stack/M5StopWatch-UserDemo/blob/main/main/hal/hal_ioe.cpp`
