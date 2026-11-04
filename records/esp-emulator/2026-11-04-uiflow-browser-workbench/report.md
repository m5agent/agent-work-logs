# UIFlow浏览器工作台：实现、验证与边界

日期：2026-11-04。结果PARTIAL：限定工程验收PASS；模型/性能未建立项与未执行交付分开。
源码为[公开c3db提交](https://github.com/m5agent/m5stack-esp-emulator/commit/c3db057d2ee99c022a4116ae72d661c4d39888c6)，相对base b41eba70eb61f7ddc5c41e0b981341064f9d1d1f。
无物理设备操作；本文只授予声明的virtual-device与host验证层。

## 背景与最终行为

用户需要为全部19款浏览器可运行设备编辑和运行UIFlow源码，既有参考固件不能替代通用工作台。
每板使用自己的官方base和确定性boot/main，独立读回确认原文件及VFS外内容保留。
M5.begin与ready marker后返回真实UART REPL。网页提供粘贴/.py导入、实际stdout/stderr、
UTF-8/长源码/异常恢复、暂停继续、中断和硬复位后的新console执行。

UART owner、generation/session和console epoch隔离旧执行；运行中interrupt只发一个Ctrl-C，
同run并发/重复请求幂等，初始CR/Ctrl-C/Ctrl-C连接握手独立保留。
输入源码上限65,536 UTF-8字节，未读UART缓冲131,072字节，stdout/stderr各保留尾部
65,536 UTF-16 code units；协议控制字符在取得UART前拒绝。
这是文本raw-REPL/EOF协议，不声明任意二进制stdout透明传输。

固定来源WASM75含host poll真实EventNotifier唤醒：shared epoch变化只促使重新poll，
不伪造fd readiness，也不改guest clock/WDT/Flash。
11个S3工作台variant要求精确Flash/main/fixture/ready/0027补丁，divisor1、oneInsn，
未知固件和原fixed/classic维持原契约。49个实际R8 source-vector文件与最终c3db逐字相同；
这是内容绑定，不是补跑一次guest。

## 功能验收

V6 manifest e597ce3c4465f582928042d4a36be684454a9cb4f8910f80720ad027cf1da898，
WASM96ea9f91956aa80926182ed174ea426f3f4c84e96ca58754fa249063fdda5ca1。
R8于2026-11-04T06:54:09.317Z至07:20:47.704Z完成60/60，19editor/19buttons/
Card56/Stackbody/20fixed，共2,564检查、224raw-paste、38默认Run、200subject-trial。
最多两个独立VM功能并行，不能作性能测量。
[严格汇总](evidence/all19-acceptance-summary.json)按原compact bytes保留，
独立核对60个原report byte/SHA及exit0；原测试/固件/执行策略与实际输入输出逐case绑定。

41个普通按键subject各键盘/指针共82trial，Cardputer56键各两种方式共112trial，
StackChan三区键盘/指针共6trial。请求pulse保持250ms。
Card只使用公开driver callback/IRQ，未调用privateISR或手动poll FIFO；
Fn pointer subject有grave键盘伴随，不能写成56个纯鼠标chord。
PM1四板采用显式500ms click窗口和single-click IRQ配置，cfg49 2a→2d、cfg4a保持：
StopWatch/StickS3用固件公开driver，PaperColor/PaperMono明确用公开I2C RMW、无fallback。
Color缺driver.m5pm1已实证，Mono未探测helper import，状态UNKNOWN；
不能由同型号库名或alias I2C bus推导另一个BIN的API或物理pinmux。

每lane清场保持实际shape。editor/fixed/body所捕获的两阶段CDP与普通buttons/Card
仅before-context捕获分开；后者held-iframe外部CDP为NOT CAPTURED。
不把一个lane的正常退出或Worker围栏转授给另一lane。

[DOM摘要](evidence/dom-qa-summary.json)仅为V5无guest的CoreS3四宽度与两边界设备
各两宽度观察，PaperS3首observerFAIL保留；不授V6 guest或全设备布局。
[readiness摘要](evidence/readiness-summary.json)按19个原报告取positive finite首次
click-to-ready，max2功能并行含host contention，不作独占性能、跨板排名或before/after证明。

## 首次失败与限定后续

| 原问题 | 实际后续与仍保留的边界 |
| --- | --- |
| UART signed-array接收失败 | 修复真实UART字节路径，原FAIL与后续scope/SHA保留 |
| StopWatch全矩形/亮度观察器误判 | rotation0、brightness255；原生466圆形帧内170499点F800、外46657黑，SDK逻辑468仍独立，原FAIL不覆盖 |
| StopWatch默认PWR250ms无event | 合法公开PM1应用模式配置后固定250ms通过，不写成default模式PASS |
| PaperColor driver导入FAIL | R6发生在setup、零输入；Paper显式公开I2C路径独立通过，不是PWR路由FAIL |
| Cardputer双Ctrl-C抢finally | R3全部112输入通过但deinit被中断；受控拆包负正对照证明可再次打断finally，单Ctrl-C/同run幂等后严格516及R8通过；不声称原每byte时序已定因 |
| PaperColor颜色观察器误判 | 源Spectra palette/PIXMAN565得到B800，严格400x600全帧与fresh source/frame序列验证；旧F800假设FAIL保留 |
| StamPLC多指令reset PIF | 精确IRAM普通32位load指向已实现UNIT1_OP；精确策略通过，RUNTIME-07 OPEN |
| Cardputer多指令reset OOB | 原44项后失败保留；单独原策略/ACK诊断亦曾未复现，exact策略PASS不能关闭RUNTIME-08 |
| AtomS3Lite首次boot PIF | PC403864c3为普通对齐32位load到6002306c=INT_CLR，源callback返回0且已映射，实际transaction未捕获，RUNTIME-09 OPEN |
| 3cMatrix warm pre-Start观察器FAIL | 旧disposed shell被id-only条件误认，未启动第二guest，无效复制计时不计入warm；独立修正只改precondition/清旧timing，保留原15/26断言、start hooks和清场 |

上述原FAIL、artifact byte/SHA与受控实验身份在主摘要所引公开source evidence中保留。
Stam/Card/Atom故障阶段、固件和指令不同，没有共同C根因结论。
单个策略通过不证明未知镜像、全模型稳定性或物理等价。

## 冷启动与四组warm

此前两款原fixed镜像独立cold-only：Matrix109.458→54.775s，Plus90.687→39.144s。
是单次同Flash/icount shift5/divisor1对照，不是新默认镜像或全设备提速。
3c→75同时包括中间stack/link/UART变化，不能把差值完全归给0032或某一行C；
0030的host语义证明也不等于启动收益。

| 原镜像/runtime | cold-prime s | same-page warm s |
| --- | ---: | ---: |
| Matrix/75V1 | 53.491 | 76.480 |
| Plus/75V1 | 39.378 | 63.627 |
| Matrix/3c | 109.448 | 108.710 |
| Plus/3c | 96.703 | 111.456 |

四组独占guest槽、8phase/164原功能检查与正常清场通过，16个raw artifact已逐文件独立复核byte/SHA/status。
[warm摘要](evidence/warm-summary.json)逐字保留54276字节/cbcf7bb3…原JSON。
每组warm在同page/URL/timeOrigin上，正常Stop后公开CoreS3→target重建模型，再新VM/
Workers；观察到asset/compiled-Module memory命中。故包含模型重建和保留页背景效应，
不是纯cache或严格仅rerun证明；一次pair不是统计保证。75两组更慢，3c Matrix略快、
Plus更慢。新cold-prime不替换旧cold-only记录。
SDK六个正向控制通过；pthread cancellation仍NOT ESTABLISHED，v7 cancel NOT RUN；
浏览器正常guest cleanup不能证明SDK取消。

## 最终host与远端CI

首R1：Python1967项、155.239s，3文档FAIL/10skip，脚本fail-stop后8步骤NOT RUN。
三因分别为精确backticked07/08/09 ID、旧Oct30日期预期、Markdown-only freshness表误纳
DOM JSON行（223/224而coverage/inventory均613）；不是缺实际文件或代码inventory bug。
随后定点21项通过、snapshot write/check通过，完整R2才授最终host PASS。
[首轮FAIL](evidence/final-host-r1-failure-summary.json)与[最终host摘要](evidence/final-host-summary.json)分开保留。

R2 finalc3db九步骤均exit0：
Python1967项=1957PASS/10skip/0fail、154.528s；
Node28命令无SKIP、collector9、四validators和diff/scope通过。
环境Python3.12.14、Pillow13.0.0、littlefs-python0.19.0、Node22.14.0/npm10.9.2。
10skip为2个optional littlefs测试运行时、1个optional pinned compiler、
7个pinned UIFlow source checkout。包已安装，不能把test-runtime skip写成依赖包缺失。
完整skip测试名/原因、原报告和各step log byte/SHA均在独立host摘要，不复制大日志。
全历史scope为218新blob/9469208字节、新evidence671526字节，UTF8/JSON/隐私/预算检查通过。

[普通源码CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41796558326)的platform-contracts和network-namespace-policy均completed/success。
这不是regular Pages60guest job，也不是线上同路径或部署验证。

## 复验入口

在公开commit对应源码根目录使用记录中的Python/Node依赖版本，按源码package-lock安装Node依赖。
Python命令使用相对venv路径，避免本机路径：

~~~sh
PYTHONPATH=platform/tools .work/venv-platform/bin/python -m unittest discover -s platform/tests -p 'test_*.py' -v
npm run --prefix platform/tests test:contracts
.work/venv-platform/bin/python platform/tools/runtime_coverage.py --check
.work/venv-platform/bin/python platform/tools/peripheral_catalog.py --check
.work/venv-platform/bin/python platform/tools/qemu_profiles.py --check
.work/venv-platform/bin/python platform/tools/project_snapshot.py --check
~~~

guest导出/组合/逐lane命令与原FW/runtime/profile身份见公开源码的
[workbench入口](https://github.com/m5agent/m5stack-esp-emulator/blob/c3db057d2ee99c022a4116ae72d661c4d39888c6/tests/browser-qemu/uiflow_workbench/README.md)及[all19证据](https://github.com/m5agent/m5stack-esp-emulator/blob/c3db057d2ee99c022a4116ae72d661c4d39888c6/docs/evidence/2026-11-04-browser-uiflow-all19-acceptance/README.md)。
新输出不能覆盖原FAIL；选择agent-owned空闲端口，不占用已有服务。
源码级检查不代替guest；独占性能方法与max2功能方法分开。

## 风险、回滚与交付

未写物理Flash。源码、默认组合与profile可按逻辑提交回退，exact variant必须连同
Flash/main/fixture/ready/required-patch绑定一起回退，并保留原失败证据。
首次归档时PR尚未创建；交付后续见下节。main合并、Pages发布和在线同路径NOT RUN，等待授权。
物理RF/电气/功耗/声学/光学/机械、未知固件、未建模外围与长期稳定性无新增证明。
后续PR与发布结果应追加独立记录；本次未执行部署。

## PR #165 交付后续

2026-11-04T08:24:25Z：PR已创建，精确head为c3db，push/PR两轮普通CI四检查均通过。
[交付与边界记录](followups/2026-11-04-pr165-handoff/report.md)保留实际回读及此前功能证据的复用范围。
合并、Pages和在线验收仍未执行；首次归档状态保留在原固定提交。

## 合并与首次正式发布尝试

PR #165已按授权合并为23d38d8d，文件树与原c3db验证版本一致，普通main CI通过。
[发布检查点](followups/2026-11-04-pr165-merge-publish-attempt1/report.md)固定首次下载TLS失败及其后一次同源码恢复尝试。
截至该检查点，尝试2仍在正式构建中，尚未授予新站点或线上验收通过。
