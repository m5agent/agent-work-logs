# Tab5 ST7123 停止轮询后的鬼触点（M5GFX #418 代码级核对）

- 日期：`2026-11-16`
- 结果：`REVIEW`（仅代码级；物理硬件与虚拟设备均 `NOT RUN`）
- 工作类型：`issue`
- 问题来源：[m5stack/M5GFX#418](https://github.com/m5stack/M5GFX/issues/418)
- GitHub 回复：[issuecomment-6904885353](https://github.com/m5stack/M5GFX/issues/418#issuecomment-6904885353)（英文，单条；issue 保持开启）
- 第二轮回复：[issuecomment-6908007729](https://github.com/m5stack/M5GFX/issues/418#issuecomment-6908007729)（2026-11-16，英文单条，未关闭 issue、未推送上游）
- 源码版本：M5GFX `28d47949bdc84f30881623476f555398e2194313`（0.3.0）；
  M5Unified `96576a14247ddc935149145aa6b51943464120f1`
- 环境：macOS 主机 + host C++ 解析复现；本机无 Tab5 硬件，本地 Tab5 模拟器无 ST7123
  控制器级模型；未运行物理或虚拟设备验证

## 结论

报告中的鬼触点是控制器 `valid=1` 的原始上报，M5GFX 会原样转发：`Touch_ST7123` 没有
面积/强度/时长过滤，且把报表中的 `intensity` 字节丢弃；M5Unified 首帧按下即
`touch_begin`。因此“1–2 次扫描的鬼点被当成一次点击”与代码一致。控制器为什么在轮询
间隙后产生这些帧，源码不能证明；作者“暂停期间持续轮询可消除鬼点”的实验指向芯片侧
行为，但本轮未复现。新触摸固件是否存在、是否应在驱动内加阈值，均未确认。

## 关键证据

- `getTouchRaw()` 三次独立读 `0x0010`/`0x0009`/`0x0014`，只把 area 写入 `size`：
  [Touch_ST7123.inl:132-148](https://github.com/m5stack/M5GFX/blob/28d47949bdc84f30881623476f555398e2194313/src/lgfx/v1/platforms/esp32p4/Touch_ST7123.inl#L132-L148)。
- `touch_point_t` 无 intensity 字段：`Touch.hpp:29-35`；面板层与 M5Unified 均无过滤。
- INT（GPIO 23）传入配置但驱动从不配置/读取；驱动不写任何寄存器、不复位芯片。
- 0.2.28 与 0.3.0 的 `getTouchRaw()` 函数体一致。
- host 解析：用作者给出的双边缘点数值，原逻辑返回 2 点；area≥30 且 intensity<25 规则
  返回 0；真实点（area 8 / intensity 45）保留；窄鬼点需 intensity 阈值才能拦住。
- ESPHome 从 `0x0010` 一次读 74 B 并说明读取会清 INT；espp 文档说明 `0x0009` 是最大
  同时触点数、ST7123 不应拨动 `TP_RST`。

## 文件

- [report.md](report.md)：代码事实、对照实现、三问边界和未覆盖项
- [run.json](run.json)：结构化状态与文件身份
- [code/parse_check.cpp](code/parse_check.cpp)：host 解析复现；编译方法见
  [code/README.md](code/README.md)
- [evidence/parse-check-output.txt](evidence/parse-check-output.txt)：本次运行输出
- [evidence/source-pins.json](evidence/source-pins.json)：固定 commit、文件 SHA256 与
  对照驱动说明

## 未覆盖项

物理 Tab5 复现、长时间/多温度测试、虚拟设备复现（无 ST7123 模型）、单事务读取与
INT 门控实验、驱动内强度阈值在真实触摸上的误拒率、触摸固件版本可用性均为 `NOT RUN`
或需要 M5Stack 确认。未修改 M5GFX/M5Unified，未推送代码，未关闭 issue。

## 追加：第二轮 INT 双帧、确认位与协议 §6.6（2026-11-16）

报告者补充了逐帧 INT 电平、两种读取模式的 burst 原始帧，以及 burst 结束后的
`adv_info`。结论有三点变化：

- **重复供给与跨帧撕裂被排除**：7 例有坐标的相邻帧之间 INT 均先高后低，5/7 字节不同；
  每次读取都是控制器的新帧，三次读的非原子性不是鬼点来源。
- **“`with_coord` 仍为 1 就说明确认不完整”的判据得到修正**：协议 §6.6c 规定读到最后
  一个坐标寄存器会同时清除 INT 与该位；两种读取模式都读到了 `0x0059`（10 触点 × 7 B），
  但该位 10/10 次仍为 `0x08`，而 INT 已被清除。两个确认信号不一致，指向固件未清该位
  或在采样前被下一帧重新置位，现有数据无法区分；不再把它当作“读取未生效”的证据。
- **鬼点几何由“同一行”修正为“两端钳位”**：两种模式都出现 `x=0` 与 `x=719` 的成对
  点，area 28–32、intensity 11–13；两端 y 差在 8–83 之间，同一行只在多数帧近似成立。

对过滤规则的建议：`area >= 30` 应保留 `intensity < 25` 的条件，否则实心按压可能被整帧
丢弃，在 M5Unified 里表现为松开后重新按下。

`with_coord` 长期为 1 还会让 `getTouchRaw()` 的门控在首次触摸后不再短路，每次调用固定
执行 `0x0010` + `0x0009` + 70 B 三次事务；效率影响，非正确性问题。

- 新增证据：[evidence/followup-int-trace.md](evidence/followup-int-trace.md)（作者原始帧、
  协议 §6.6 原文、确认地址核算、`0x0059` 推导）
- 证据等级仍为 `code-level verification` + 报告者测量；物理与虚拟设备均 `NOT RUN`
  （本地 Tab5 profile 的 ST7123 触摸仍是固件 GDB 邮箱，不是 I2C 寄存器模型）

## 追加：#367 三字节 LCD_RST 差异与 `with_coord` 结论收窄（2026-11-16）

报告者用强制读（跳过 `with_coord` 门控）证明 develop 的 0 帧不是门控造成的，并把差异
二分到 M5Unified#367（merge `24dad4ff`）。该 PR 只改三个字节：Tab5 的 PI4IOE5V6408
（0x43）把 P4/LCD_RST 从推挽输出高改为输入 + 内部上拉，`PULL_SEL/PULL_EN` 同步使能；
`TP_RST` 与其余引脚不变。

- 结论：M5GFX 的 Tab5 路径不控制这条 reset（触摸无 reset 引脚、面板无 `pin_rst`、
  DSI 路径不发 `SWRESET`、`Touch_ST7123` 只读），因此 M5Unified 扩展器初始化是唯一
  写入者，二分结果与引脚差异在机理上一致。
- 修正：有 #367 时 `adv_info` 为 `0x00`（3600/3600），说明读表确实清位；`0x08` 是
  控制器启动状态异常的症状，不是协议确认失效，上一轮“两个确认信号矛盾”收窄。
- “必要但不充分”：现有出鬼点构建都缺 #367，但缺 #367 的 sketch 也不出（`adv_info`
  同样 `0x00`），更像初始化边缘条件而非确定性逻辑差异。
- 机制仍未证明：初始化时锁存 vs 持续电气差异；判别实验是运行期改写 `0x43` 三字节
  （必要时加 LCD_RST 低脉冲）后观察 `adv_info` 与鬼点。
- 证据等级仍为 `code-level verification` + 报告者硬件测量；物理与虚拟设备均 `NOT RUN`
  （Tab5 profile 已 supported/creatable，但 ST7123 触摸仍是固件 GDB 邮箱，且无扩展器/
  reset 网络模型）。

新增证据：[evidence/followup-lcd-rst-367.md](evidence/followup-lcd-rst-367.md)。
