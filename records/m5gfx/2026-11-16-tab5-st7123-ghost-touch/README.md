# Tab5 ST7123 停止轮询后的鬼触点（M5GFX #418 代码级核对）

- 日期：`2026-11-16`
- 结果：`REVIEW`（仅代码级；物理硬件与虚拟设备均 `NOT RUN`）
- 工作类型：`issue`
- 问题来源：[m5stack/M5GFX#418](https://github.com/m5stack/M5GFX/issues/418)
- GitHub 回复：[issuecomment-6904885353](https://github.com/m5stack/M5GFX/issues/418#issuecomment-6904885353)（英文，单条；issue 保持开启）
- 第二轮回复：[issuecomment-6908007729](https://github.com/m5stack/M5GFX/issues/418#issuecomment-6908007729)（2026-11-16，英文单条，未关闭 issue、未推送上游）
- 第五轮回复：[issuecomment-6915706899](https://github.com/m5stack/M5GFX/issues/418#issuecomment-6915706899)（2026-11-16，英文单条，未关闭 issue、未推送上游）
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

## 追加：翻转/脉冲/0x43 转储（2026-11-16，第六轮）

- 帧由 LCD_RST 的驱动电平连续门控（一轮内可停可起，无需复位）；`0x08` 是粘滞标记而非
  前置条件（B3/A2：已置位 + 上拉 = 0 帧）。
- 10 ms 低脉冲在 3 ms 后仍未清 `0x08`，`0x00` 出现在显示被打入 sleep in 的同一窗口，
  故“只有低脉冲能清”是过度归因。
- 一次 DCS `0x0A` 读可在 P4 仍驱动时停止 60 轮帧；M5GFX 自身不做 DCS 读，说明这是
  显示命令路径影响共享 TDDI 状态。
- `0x43` 两边字节相同，扩展器配置分支关闭；但转储时机应改到 `0x08` 首次置位那一轮。

新增证据：[evidence/followup-lcd-rst-flip.md](evidence/followup-lcd-rst-flip.md)。
第六轮回复：[issuecomment-6918168398](https://github.com/m5stack/M5GFX/issues/418#issuecomment-6918168398)
（英文，单条；issue 保持开启）。证据等级 `code-level verification` + 报告者测量；
物理与虚拟设备 `NOT RUN`。

## 追加：上拉态黑屏使零帧结果作废（2026-11-16，第七轮）

报告者更正：镜像 M5Unified#367 三字节后屏幕空白、真实按压 0 次按下 0 帧，改回驱动并重启
后画面恢复、6 次点击一次登记。故上拉态的所有零帧结果（mirror 电量/启动、develop、
早前 0/58、二分“好”步进）都只是“面板不工作”，不是鬼点修复；第六轮“帧由驱动电平门控”
与“`0x9C` 即醒着”的表述撤回，`0x08` 粘滞证据降级。DSI 读抑制也需重新区分“关显示”与
“停扫描”。已站得住的是：面板工作时确有鬼帧。下一步用画面 + 真手指门禁重跑，并在两种
面板上复核 #367 上拉态是否都黑（若都黑则为显示回归）。新增证据：
[evidence/followup-panel-liveness.md](evidence/followup-panel-liveness.md)。
证据等级 `hardware validation`（报告者观察）+ `code-level verification`；物理与虚拟设备
`NOT RUN`（Tab5 profile 无 0x43/reset 模型，触摸为 GDB 邮箱）。

第七轮回复：[issuecomment-6918409539](https://github.com/m5stack/M5GFX/issues/418#issuecomment-6918409539)
（英文，单条；issue 保持开启，未推送上游）。

## 追加：重启前按压为 0，报告延迟分支关闭（2026-11-16，第八轮）

报告者补充：上拉黑屏构建上，重启**前**的多次按压即为 0 次按下、0 帧（逐次日志开着），
重启后登记的 6 次是 24–31 s 后的新按压，不是补报。

- **报告延迟分支关闭**：不存在“上拉态缓存、驱动恢复后补报”；上拉行只能读作“没有坐标
  上报”。上一轮保留的 host-reporting-failure 分支撤回。
- **“扫描停”降级为“未证实”**：failed-read = 0 且 `with_coord` 未置位，只证明没有坐标
  上报；结合 A2/B3 的 I2C 应答与 `0x08` 保持，上拉态是“显示灭、数字核在应答、无坐标、
  扫描状态未证实”。
- **门禁两半独立**：未看屏 → `panel state unknown`；看屏无手指 → `touch path unknown`。

证据：[evidence/followup-pre-restart-presses.md](evidence/followup-pre-restart-presses.md)。
证据等级仍是 `hardware validation`（单台）+ 本记录 `code-level`；物理 Tab5 与虚拟设备
`NOT RUN`。

## 追加：真实触摸原始表与起始规则（2026-11-16，第九轮）

报告者给出 16 次真实按压的 first/peak area、intensity、held ms，并说明第 16 号的真实
首帧（area 35 / intensity 50）被 area-only 规则丢弃、下一帧才登记；规则改为
`area>=30 && intensity<25`。

- **area 条件只应在起始帧、且与强度同取**：本表 peak area 达 31/42（intensity 53/61），
  全程生效会丢真实帧；报告者已改为 start-only。
- **新规则在起始帧不可达**：门禁 intensity>=25 放行的点不可能同时 `<25`，故面积子句
  在起始路径永不触发，实际过滤器只有强度门禁（若作用于非起始帧，则只在抬指/衰减帧触发，
  等价于松开再按下）。
- **“余量 8”是表内数字**：更早 20 次按压 first-scan 下限 26、鬼点上限 22；以 26 为约束，
  门禁 25 的实侧余量 1、鬼侧 3；空带 23–25，24 为两侧各 2。
- **两列都是幸存者样本**：`first` 是“通过过滤的第一帧”，第 16 号即反例；低于门禁的值
  不会出现，实侧下限只有上界。
- **两次 x≈719 未登记存在歧义**：轨上且 intensity<25 的真实按压与鬼点签名相同，会被
  门禁静默拒绝，需记录被拒起始候选才能与“按到边框”区分。
- 轨道坐标（真实点距轨 ≥26，鬼点全在 0/719）分离度够，但当前不增加拒绝力，先记录不先加规则。

新增证据：[evidence/followup-real-touch-table.md](evidence/followup-real-touch-table.md)。
证据等级 `code-level verification`（表值算术核对）+ 报告者硬件测量；物理与虚拟设备
`NOT RUN`（`tab5_enabled: false`，ST7123 为固件 GDB 邮箱，无 `0x43`/reset 模型）。

第九轮回复：[issuecomment-6928659888](https://github.com/m5stack/M5GFX/issues/418#issuecomment-6928659888)
（英文，单条；issue 保持开启，未推送上游代码）。

## 追加：29 次按压与门禁锚点（2026-11-16，第十轮）

报告者追加 13 次轻触数据：真实首帧下限降到 24，鬼点上限仍 22，实际门禁为 23 而非 25；
`area>=30 && intensity<25` 子句本就 start-only，已删除。回复要点：24 锚在“首帧下限”，
而软门禁下真正的约束是 peak 下限（29 次全部 ≥36，鬼点 ≤22），故阈值可在 23–35 之间取；
24 只留 1–2 的余量，30 位于实测 peak 带中部、距鬼点上限 8。

第十轮回复：[issuecomment-6928827172](https://github.com/m5stack/M5GFX/issues/418#issuecomment-6928827172)
（英文，单条；issue 保持开启，未推送上游代码）。

## 追加：空闲 164 次 burst 与日志写停顿（2026-11-17，第十一轮）

报告的 329 分钟空闲运行里出现 164 次 burst（29.9 次/小时），形状是中列 x=358 或两端轨
x=0/719 上的 10 个极弱点（intensity 7–13、area 1–7/1–18），另有单点 (669,631)
area 32 / intensity 13；全部低于门禁 24，无一次成为按压。

- **恒定 x 来自控制器**：驱动逐 slot 用各自 `x_h/x_l` 组装 x，没有跨 slot 复制路径，
  撕裂读只会让各 slot 的 x 不同；故这些帧是控制器发出的整列/整表扫描结果，不是解析缺陷。
  29 次真实按压均为单点、x 35–693，与此不同类。
- **“10 点”是 10 个 slot 全部 valid**：`0x0009` 是最大触点数能力值，驱动一次读 70 B
  后逐 slot 输出；整表 valid 且字段极弱是扫描状态，不是 10 个触点。
- **门禁 24 无需改动**：新数据只把鬼点分布向下延伸（7–13），上限仍 22、真实下限仍 24；
  (669,631) 这类“面积像真、强度像鬼、且不在轨道”的点再次证明面积规则不能回到起始判据。
- **两次空闲统计不同口径**：29.9 次/小时与早前“约一小时 4 次”按 burst 计差 7.5 倍、
  按读取计约 15 倍；可分离的变量是屏幕/背光状态（作者实测 0→35/60）与写 flash 日志造成
  的轮询停顿。
- **计数工具可能制造触发条件**：写 flash 同时停 CPU 与 PSRAM，CPU 停顿正是作者已测的出鬼
  条件（上传 20 分钟 74 次；独立 sketch 0/60）。若空闲运行边计数边写 flash，它不满足
  “无轮询停顿”前提；需改 RAM 缓冲重跑，并记录每次 burst 前最后一次轮询的时间戳。
- **可选形状后备规则**：一次读内 ≥3 点共享完全相同的 x 不可能是真实接触，可在强度漂移时
  兜底；但 (669,631) 不在轨道，轨道规则仍会漏，故强度仍是主判据。

证据：[evidence/followup-idle-bursts.md](evidence/followup-idle-bursts.md)。
证据等级 `code-level verification`（slot 组装与 `0x0009` 语义）+ 报告者硬件测量（单台、
单面板、FW 01）；物理 Tab5 与虚拟设备均 `NOT RUN`。

第十一轮回复：[issuecomment-6937083296](https://github.com/m5stack/M5GFX/issues/418#issuecomment-6937083296)
（英文，单条；issue 保持开启，未推送上游代码，未关闭 issue）。

## 追加：无停顿空闲运行（30 min 零 flash 写 + 15 min 周期 flash 写，2026-11-17，第十二轮）

按第十一轮的要求重跑：45 min 无人触碰、grid view 横屏、背光 170/255、0 重绘；
A 段 30 min 完全不写 flash（日志留 RAM 后落盘，0 行丢失），B 段 15 min 每 8–12 s 做一次
未使用区域的 4 KB 擦除 / 1 KB 编程。寄存器 `0x0005`–`0x0009` = `02 d0 05 00 0a`
→ 720 × 1280、10 触点。

- **撤回上一轮的“停顿制造速率”**：A 段零 flash 写仍 30 次/小时，与 29.9 次/小时同量级；
  13/15 与 2/2 的 burst 不在停顿后 1 s 内，B 段 90 次 flash 操作后 0 次 burst。列形状
  是自由运行的，flash 与停顿不是它的触发条件。
- **停顿假设按形状分裂，且分裂完美**：两次轨 burst 恰是两次“停顿后”burst（停顿后
  81–95 ms），15 次列 burst 全自由运行；2 × 2 Fisher 双侧 p = 0.0147（事后假设，待确认）。
  34 次停顿里 2 次后随轨 burst（约 6%/停顿）。22.7 次/小时是两个来源之和：约 30 次/小时
  的列状态 + 约 0.4 次/小时的轨事件，不应再合并。
- **寄存器读回**：`02 d0` = 720，故 358 不是 720 的半宽（720/2 = 360，坐标中心 359.5），
  只在 1.5–2 个计数内接近中缝；716 的巧合就此排除。驱动从不使用 `0x0005`/`0x0006`
  做缩放或钳位（只用于全零存活判断），`_cfg.x_max` 默认 2047，故“358 是驱动默认坐标”
  也不成立。
- **自纠**：上一轮“驱动把每个 slot 都置 valid=1”的措辞不准确，驱动会跳过 valid=0 的
  slot；因此“最满一读 9 个 valid slot、slot 9 从未 valid”是芯片自己的上报。
- **两种形状是同一件事，且比“整列读出”更窄**：174 点只落在 0↔719、140↔578、179↔538
  与自镜像的 357–359 上，x 栅距 20 px（720/36，残差 ≤ 2），镜像轴 358.5–359.5 即中缝；
  y 不落在栅上（残差 −7…+9）也不按 slot 排序。即 x 是被扫描的列、y 是每点各自带出的，
  且同一列索引连同其镜像一起出现。可证伪：任一鬼帧出现三个非镜像对的 x 即推翻。
  17/17 burst 连续两读（24 ms）说明状态持续 ≥ 1 个轮询周期，进一步排除撕裂读。
- **后备规则覆盖 8/17，剩余 9 次不建议补规则**：漏掉的是一次一 x 只有 1 点的帧；用
  “两点之和 ≈ 718”能补，但与对称双指捏合不可区分，且强度门禁本就拦下全部 17 次。
  另否掉一个候选：x 的 20 px 栅距单独不区分——29 次真实按压中 8 次落在 20k−1 ± 1
  （随机期望 4.35，1.9σ）。
- **A、B 不应合并成速率**：B 段 2 次/15 min 对 A 段速率 P(≤2 | λ=7.5) ≈ 0.020，
  要么速率非平稳，要么 flash 反而压制；n=2 判不了，但 B 不是中性对照。
- **门禁不变**：新增 174 点全部 ≤ 16，鬼点上限仍 22，默认 24 的余量不变；本轮没有落在
  24–35 峰值带的按压，第十轮“24 vs 30”的论证原样成立。

证据：[evidence/followup-idle-free-running.md](evidence/followup-idle-free-running.md)，
复算脚本与输出为同目录 `idle-free-running-check.py` / `.txt`。
证据等级：报告者 `hardware validation`（单台、单面板、FW 01）；本记录为
`code-level verification`（develop b48dce04 与 pinned d91077b9 的驱动源码 + 其数字的算术）。
物理 Tab5 与虚拟设备均 `NOT RUN`（服务级 `tab5_enabled: false`，ST7123 触摸为固件
GDB 邮箱，无 0x43 扩展器与 reset 线模型）。
