# 本轮工作与证据边界

日期：`2026-11-05`。公开源码仓库：[m5stack-esp-emulator](https://github.com/m5agent/m5stack-esp-emulator)。
基线 `73ed554fba02a2397dad81e39e12b5b4b92d0500`。最终集成 SHA、PR、合并 SHA、CI 与公开记录 SHA 由根代理填写；
本草稿不得被解读为最终集成或 17 项全部关闭。总体 `PARTIAL`。

## 目标与方法

用户要求逐一处理新问题，并释放约 200 GiB 工程数据中的非重要部分。
调查按原固件、实际分区、真实 driver/controller 路径和精确运行身份推进；
功能结论依赖 guest 输入、串口、帧、Flash readback 或控制器数据。
未用延长等待、削弱 marker、host 假值或旧固件 PASS 替代原验收。

下表是执行结果及收口候选。fresh native runtime 的新设备矩阵、旧固件对照与
独立后续均已绑定；最终完整平台、CI、远端交付仍待完成。

| Issue | 范围 | 当前局部状态 | 结论与条件 |
| --- | --- | --- | --- |
| [#172](https://github.com/m5agent/m5stack-esp-emulator/issues/172) | classic ESP32 eFuse package 5/6 admission | PASS | Bounded classic/S3 field encoding, actual eFuse driver and package values restored; targeted guest evidence retained. |
| [#173](https://github.com/m5agent/m5stack-esp-emulator/issues/173) | Four missing console image builders | PASS | Generic source composer restores buildability; classic console guests pass, AtomS3 Lite observation repaired under #187. |
| [#174](https://github.com/m5agent/m5stack-esp-emulator/issues/174) | Actual VFS layout and stock preservation | PASS | Derive VFS from each base partition table; verify unchanged non-VFS bytes and stock-file readback. |
| [#175](https://github.com/m5agent/m5stack-esp-emulator/issues/175) | ED2208 partial window and AUTO refresh | PASS | 0x83 inclusive windows and 0x17 A5/A7 AUTO refresh pass on frozen fresh native runtime; latest full matrix and previous official SD regression retained. |
| [#176](https://github.com/m5agent/m5stack-esp-emulator/issues/176) | AXP2101 charging status semantics | PASS | AXP2101 REG01 charger/current direction states pass on frozen fresh native runtime for latest and previous official firmware. |
| [#177](https://github.com/m5agent/m5stack-esp-emulator/issues/177) | SHA-bound official driver behavior expectations | PASS | StickS3 BMI270 axes and PaperColor undetermined-charge behavior follow exact new firmware/source; old bindings retained. |
| [#178](https://github.com/m5agent/m5stack-esp-emulator/issues/178) | Classic ESP32 esptool transport | PASS | Stock guest stub, actual ROM banner and UART transport; complete Flash byte readback; Core2 draw-completion fence followed preserved first frame failure. |
| [#179](https://github.com/m5agent/m5stack-esp-emulator/issues/179) | AtomS3 panel variant | PASS | Explicit ST7735 profile passes latest and previous official firmware on frozen fresh native runtime; original GC9107 profile preserved. |
| [#180](https://github.com/m5agent/m5stack-esp-emulator/issues/180) | PaperColor false pre-REPL diagnosis and EPD output | PASS | Real UART0 observes original main and key marker; 0x17 controller refresh makes the original black-pixel assertion pass. ER warning remains non-blocking. |
| [#181](https://github.com/m5agent/m5stack-esp-emulator/issues/181) | Dial Python console observation | PASS | Real UART0 dupterm exposes original guest markers; original display/input case passes. |
| [#182](https://github.com/m5agent/m5stack-esp-emulator/issues/182) | NanoC6 latest startup fixture | PASS | Actual VFS/stock resources restore latest NanoC6 startup; fresh native device matrix passes and previous/Nesso controls remain retained. |
| [#183](https://github.com/m5agent/m5stack-esp-emulator/issues/183) | Basic v2.7 BtnB report | PASS | Fresh full-matrix run reproduced missing BtnB after A redraw. Add a real guest redraw-completion fence between inputs, retaining the 450 ms key pulse. Independent A/B/C input and final 18-board run pass. Earlier standalone PASS and fresh FAIL are retained. |
| [#184](https://github.com/m5agent/m5stack-esp-emulator/issues/184) | StickC family frame/fixture contract | PASS | Four declared frame oracles now match their checked-in fixture and actual guest input; original frame results retained. |
| [#185](https://github.com/m5agent/m5stack-esp-emulator/issues/185) | Executed runtime provenance and native recipe | PASS | Bind receipts to live local worker/runtime execution; clean native replay/build and actual RTC cases pass; unavailable old runtime is NOT RUN. |
| [#186](https://github.com/m5agent/m5stack-esp-emulator/issues/186) | CoreS3 ADC calibration admission | PASS | Add one explicit latest app binding; same 17 virtual calibration fields and unchanged numeric oracle. Angle/Light pass; existing Buzzer failure retained. |
| [#187](https://github.com/m5agent/m5stack-esp-emulator/issues/187) | AtomS3 Lite Python console observation | PASS | Original guest already drove RMT RGB; UART0 observation restores all markers and same-VM friendly/raw REPL executes board 137. |
| [#188](https://github.com/m5agent/m5stack-esp-emulator/issues/188) | Tab5 latest official image packing/ELF | PARTIAL | Composition preserves exact official app; stale ELF rejected and seed copied. Independent official esp-emu 0.51 observes latest main waiting for DSI PHY PLL lock, with advancing timers; latest Python/UI/touch not proven. Keep open. |

## 修复和执行证据

**镜像与测试契约。** classic/S3 eFuse 字段分开且有边界检查，console 使用通用
镜像组合入口。VFS 从实际分区表派生，保留 stock 文件并独立回读，VFS 外字节
保持不变。首次 AtomS3 Lite 仍无 stdout 的 FAIL 保留，后续 UART 观测修复是独立执行。
StickC 四款图像契约对齐真实 guest；新固件的 BMI270 轴和充电状态使用明确 SHA
绑定，未把新期望转授给旧/未知固件。

**classic ESP32 下载。** 保留 ROM-only 协议失败。stock esptool guest stub 路径
读取了实际 ROM banner 和 UART 回应，并在退出 stub、启动应用前完整比较 Flash。
Core2 首次 Flash 已完全一致但采样到半次重绘，仍记 FAIL；随后使用 guest 绘制完成
marker 才采样的独立运行通过。不是用后一个 PASS 改写前一个执行。

**Basic 按键。** 早先 standalone 同最新固件 A/B/C PASS 只保留为历史对照。
冻结 fresh native 的首轮设备矩阵在 A/C 有 marker、B 缺失时记 17 PASS / 1 FAIL。
修复让下一次输入等待 guest 真实重绘完成，保持原 450 ms pulse；A/B/C 的实际
keydown→keyup ACK 间隔分别为 0.456461/0.453950/0.451503 秒。独立 Basic 和新的
18 板全矩阵均通过，不把这一观察器同步修复写成按键 controller 修改。

**S3 的观测和 EPD。** 原 AtomS3 Lite 没有串口 marker，但同 guest 的 RMT 已完成
两帧、RGB 为 `2113632`，证明不能仅凭静默判 pre-REPL 挂死。通过真实 UART0
`os.dupterm` 暴露原程序后，Dial 和 AtomS3 Lite 原程序通过。AtomS3 Lite 同一 VM
还完成 Ctrl-C、friendly/raw REPL 和 `M5.getBoard()` 返回 `137`。
PaperColor 原程序和按键已执行，但局部 EPD 更新需要 `0x83` 窗口及 `0x17` AUTO
A5/A7 提交；修后保持原 `(270,160)=000000` 断言通过，最新/此前官方三设备共六次
局部回归通过。`0x10200C` 属 Xtensa External Register debug-control SET 空间；
警告在完整通过的 PaperColor 执行中仍出现，不能归因为 PM1/I2C/面板启动死锁。

**runtime 与 ADC。** runtime receipt 绑定实际运行的本地 worker 可执行文件和二次
身份核对；首次身份未验证的功能观察保持 PARTIAL。独立源码重放、逐层正反 apply
及 clean compile 通过，依赖只读复用，QEMU 对象重新构建。最初缺少 enum header 的
构建 FAIL 和 host-specific Node locator 导致的 Unit suite FAIL 保留；它们不等于
固件功能失败。旧 pre-Unit runtime 没有所需模型，记 `NOT RUN` 而非 guest FAIL。

ADC 只追加一个精确最新应用绑定，IDF 数值 oracle 和 17 个虚拟校准字段保持不变。
Angle 的三点输入 `0/1250/2500 mV` 经原驱动得到 `0/1.232/2.427 V` 与
`0/1232000/2427000 uV`，Light 及其他 IO 回归按原断言运行。11 项 IO PASS 不能
掩盖 Buzzer 的既有自然 timer-zero FAIL；其错误与原基线同类，不归为本次新增回归。
这仍是虚拟 ADC 行为，不是物理电压精度或 eFuse 安全测量。

**冻结全矩阵及 host 门禁。** 新 18 板设备矩阵 18/18 PASS，首次 Basic FAIL
仍单列。首轮 68 项外设矩阵为 67 PASS / Core2 Mic 1 FAIL：guest 已成功记录，但
采样 (4,4) 为黑。独立后续在真实 `CORE2_MIC_DRAW_COMPLETE ok` 后采样，保持原
阈值，非零 PCM 6352、peak 253、result marker 与 (4,4) 绿色均通过；原完整矩阵不
改写为 68 PASS。旧 PMIC/EPD 2 例、旧 AtomS3 1 例在同冻结 Xtensa runtime 通过。
NanoC6 使用其实际 RISC-V backend 身份，不授予 Xtensa 的 hash。
最终设备组回读时，Dial 的 retained mutable Flash 与执行前 composition receipt
不同；摘要分别保存初始组合和运行后哈希。其它带 receipt 的最终设备镜像一致。
不把运行后内容回填成原始输入，也不推定此次差异的具体写入来源。

Unit host 首轮 298 项有六个 stock whitelist 失败。修后精确核对 stock 加 intentional
source overlay、回读 base SHA，并加入三个合成负控；301 total = 300 passed +
1 skipped。Node 首次缺依赖保留，匹配已有锁定依赖后 30 scripts 全部通过。
coverage/catalog/profile、112-layer bootstrap check 与 compileall PASS。最终平台 v3
的状态页长度超过 450 行两行，作为静态文档 FAIL 保留；压缩换行后的 v4 待根代理填写。最终完整
平台与 CI 独立待填，不把 host 检查当成新 guest 证据。

**Tab5。** 原 adapter 在正确 `0xaa0000` 注入后又按旧 `0x610000` 注入，
改坏 `1,557,304` 个应用字节，造成 Factory partition 拒绝。修复后实际分区、
stock 资源和整个 factory app 均保留；固件与应用完整身份见 JSON。
新官方应用期望的 ELF 与旧模拟器 ELF 不匹配，现已在启动 guest 前拒绝旧符号。
高地址 VFS 在当前 8 MiB ROM download 边界前明确拒绝，host-image 仍执行 ROM/
bootloader，不绕过应用校验。旧 merged image 的 UI/触摸和 RS-485 独立通过；
最新未改应用虽不再出现 Factory 拒绝，仍无 Python/UI/touch marker。后续使用
独立官方 esp-emu 0.51，不加载旧 ELF，六段实际 IRAM dump 与目标 BIN 一致；两核
PC 前的真实指令为 WFI。主任务保存栈与实际 BIN 显示反复读取 DSI host+0xb0 bit0，
实际 host 为 0x500a0000，PHY_STATUS 两次为零，PWR_UP=1、PHY_RSTZ=0xf。
计数器、interrupt 与任务 delay deadline 继续增长，证据指向 DSI PHY PLL lock 等待。
只读 DSI 负控未写 ready 位、PC 或应用字节；最新 Python/UI/touch 仍 NOT PROVEN。
限定 artifact 搜索没有找到 descriptor 匹配的官方 ELF，同版本或源码标签不当成相同
应用；公开 IDF 的对应轮询仅作与实际字节一致的源码参考。#188 保持 open。

早期 Tab5 诊断沿用了共享的**虚拟** eFuse seed；后端普通退出会写回，因事前没有
内容 hash，只能确认 mtime 被刷新，不能声称第一次字节未变。没有执行显式烧写命令。
runner 现先复制为自有 runtime 文件；修后正/负控验证输入 seed 的 hash 和 mtime
均未改变。该事件及边界保留在结构化摘要中。

## 存储清理的范围与可恢复性

盘点显示约 204 GiB 位于工程目录，主项目约 188 GiB，其中 ignored 运行数据约
181.76 GiB。App 支持数据与缓存仅约 0.55 GiB，不能把工程产物误称为聊天数据库。

1. 先保存逐文件路径、大小、mtime、inode、来源和所需 SHA，确认 gitignored、
   不跟随目录 symlink、没有 active 进程打开，并排除当前任务、源码、固件、ELF、
   日志、帧、summary/evidence 和配置。仅删除 41,400 个可再生成文件：490 个
   Flash cache 与 40,910 个纯 `.obj/.o/.d`；计 11,570,143,232 allocated bytes。
2. 对旧不可变 firmware/artifact store 验证实际 SHA 相同、同 filesystem 且写入采用
   atomic replacement，再将 1,014 个重复路径硬链去重；保留路径与 metadata。
   估计减少 15,568,494,592 allocated bytes，559 个 canonical 文件再次 hash 通过，
   所有目标与 source 同 inode，metadata hash 不变。
3. 后续对互不相交的 inode 集再消除 918 个重复 inode，930 条路径保留，新增
   12,793,475,072 allocated bytes；每个 inode 只计一次，各批 `du` 降幅与估计一致。
   额外 1,826 份 JSON metadata 不变，516 个存活内容 inode 再 hash 通过。
   macOS 自动给 62 条路径/4 个 inode 加 `com.apple.provenance` 的事件单列，不公开
   属性值，既有 xattr 未删除或覆盖；一个 hash 不一致的候选保留原样。
4. 最后一批按编译规则/已安装 package manifest 的 69 份证明，清理 24,762 个过期
   纯构建/下载缓存文件，回收 6,429,708,288 allocated bytes，`du` 实测相同，与此前
   删除路径交集为零。214,306 份保留文件的 SHA/size/mode/mtime/inode 全部不变，
   69 份证明及所有目录保留；source/ELF/map/bin/evidence/config/vendor 和当前任务不动。
5. 最终合计 46,361,821,184 allocated bytes，约 43.178 GiB。早期可用空间约
   45.4→70.45 GiB；追加批 `df` 净增加 12,501,004,288 B，但并行构建/测试和
   APFS 行为会影响该值，因此与 eliminated-inode/`du` 计数分开报告。最后一批 `df`
   净增 6,431,539,200 B 同样单列，不替代其 6,429,708,288 B 精确清理计数。

Flash cache 可由保留的原固件按同一填充规则再生成；对象缓存由保留源码/config
重编译。硬链可再复制为独立文件，不改变内容。没有删除模糊用途的 exports、工作
镜像、会话、配置、当前 runtime 或被系统打开的浏览器资源，也没有整目录清空。
原始清理清单只保留本地，公开摘要不披露宿主路径、端点或设备标识。

## 复现入口和交付门禁

在最终发布的源码 commit 上准备对应官方固件、固定 runtime、ROM、eFuse 和依赖，
逐项使用以下 checked-in 入口。先核对 evidence JSON 中精确身份；不要用另一 runtime
或另一 image 的同名结果替代。

```sh
PYTHONPATH=platform/tools python3 tests/uiflow2/run_device_matrix.py --device DEVICE --out-dir OUT_DIR
PYTHONPATH=platform/tools python3 tests/uiflow2/run_peripheral_matrix.py --case CASE --out-dir OUT_DIR
PYTHONPATH=platform/tools python3 tests/uiflow2/tab5_ui_test/make_image.py --base BASE.bin --out DERIVED.bin
```

Unit batch 使用专用 Device Service 会话，先 evidence ZIP 后 stop，保留 history。
本记录没有把这些 native/service 结果拼接成 browser-WASM PASS。

最终本地平台：**2020 PASS + 1 skip**（2021 total，155.584s）；Unit：300 PASS+1skip；Node：30组PASS。catalog/profile/coverage、snapshot、bootstrap112和compileall均PASS。CI与远端交付已在[独立交付摘要](evidence/delivery-summary.json)完成。
已执行的冻结设备矩阵、首轮外设及独立后续、三个 validator 和 Unit/Node 结果
见分组摘要；源码集成提交 `3f24fa6b5a056991c37018cedb41c42d6df19b1e`；最终head `87330d6afe6df2c66db4611be1b4c963e04d8173`、merge `ea6a553b702c636b10692665c475341b178cb662`，PR189已合并。
最终 issue 回复须先发布记录，并使用公开记录的完整 commit SHA permalink。
#188 未满足官方应用的 UI/touch 验收，不应随其余候选关闭。

## 回滚与未覆盖

代码回滚使用最终公开集成 commit 的标准 revert，当前未执行回滚。不要用重写
source/history 或重新格式化已有 VFS 作为回滚。清理缓存须按保留来源重建，
本记录不含原固件/ROM、原始 Flash、私有日志或大型二进制。

物理硬件、RF、声学、光学、电气、机械/存储时序及 browser-WASM 功能复验
`NOT RUN`；同一 firmware/runtime/controller 路径的 PASS 不外推到其他设备。

## 最终交付后续

PR189已合并，16项issue关闭、188保持OPEN。精确head4/4与merge2/2 CI通过；source tree完全一致，本地main仅快进且干净。首次Linux CI负控使用真实macOS系统库的失败保留，修后Unit304 total=303 PASS+1skip；两个head-run均实际执行新版12项provenance和3项VFS负控。详见[CI修复](evidence/ci-followup-summary.json)与[交付身份](evidence/delivery-summary.json)。
