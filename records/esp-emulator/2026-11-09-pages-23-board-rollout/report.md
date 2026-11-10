# Pages 下载回退与发布验证

正式站点原部署为 `5f15d1f824958829f7d62648a5efbfe5fcee2edb`，开放 19 款设备。用户批准发布包含初代 Cardputer、PaperS3、PaperDIY、CoreMatrix 和 #211 工作台状态与双 SHA 的主线版本。第一次正式任务从 `02c046679fd7c7dbb008afd3c4c29e3cfca517df` 启动，libffi 归档请求返回 HTTP 403。日志未记录响应头或响应正文，无法确认 403 的进一步原因。

`0ea7e36ae0dd769deb8bf83529756db5e9213e8e` 只修改发布工作流的归档传输。三个原锁定文件逐一验证大小和 SHA-256，构建器仍按各自源码锁独立复核。下载测试通过官方地址完成。模拟主地址返回正确大小但错误内容、鉴权 API 返回 403 时，验证拒绝坏文件并用匿名 API 取回同一归档。重跑的托管下载步骤通过，当前正在按原门禁构建和验收。

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| transport | PASS | 三个官方归档匹配 Xtensa 与 C61 锁，错误内容和 403 回退负控通过 |
| build | PARTIAL | 静态导出和发布契约 10 项通过，托管源构建未完成 |
| virtual-device validation | PASS | 独立导出上 StickC Plus 编辑器 63/63，通过应用显示、硬复位和五个 Worker 回收 |
| delivery | PARTIAL | 正式站点仍是 19 板旧部署，新任务已启动 |
| hardware validation | NOT RUN | 本次针对浏览器 WASM |

在源码树中以 `publish=true`、项目默认前缀和空服务地址触发 `public-site.yml`。本机复验采用 `build_public_site.py` 的正式导出和 `test_public_uiflow_guest.mjs`，选择 `M5_QEMU_DEVICE=stickc-plus` 及系统 Chrome。托管失败记录与本地通过各自绑定不同执行环境。回滚传输改动可撤销本次工作流提交；当前线上部署由 GitHub Actions 管理。

## 本地全量门禁及独立复验

本地同版全量串行门禁在 AtomS3 编辑器硬复位后失败。复位前执行代码、真实画面和旧控制台取消已通过。新 guest 在访问 SYSTIMER 0x60023008 时出现 Core 1 LoadStorePIFAddrError，未取得新启动就绪标记。同一固件和 WASM 的独立复验通过 63 项，回收全部 Worker。首次失败保留，本地全量结果不作为发布通过依据。 [复验摘要](evidence/local-atoms3-reset-summary.json)

## 新机型定向验证

同一独立导出上，初代 Cardputer、PaperS3、PaperDIY 的固定例程各通过 26 项，CoreMatrix 通过 28 项。另用未修改的 CoreMatrix 官方 UIFlow2 v2.5.4 镜像验证真实 C61 启动、USB REPL、矩阵显示和停止，五个 CDP Worker 目标全部退出。这些是本地定向结果。 [运行摘要](evidence/four-board-fixed-and-c61-stock-summary.json)

## 托管门禁失败

工作流 42597576699 成功构建并导出两套 WASM，CoreMatrix 原版通过。Atom Matrix 编辑器用例在正常 QMP 退出、四个 pthread 全部消失和 iframe 移除后，CDP 仍观察到一个引擎 Worker。72 个计划用例中首个失败，71 个未执行，部署跳过。失败层级为浏览器清场；复位后的真实代码执行已经通过。 [托管工作流](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42597576699) · [脱敏摘要](evidence/hosted-atom-matrix-worker-summary.json)

## 引擎关闭候选

针对两次托管端残留引擎 Worker，提交 f23ecfe8 改用引擎在释放回执、端口关闭和 owner 通知后调用 self.close()。初始化失败和异常仍保留强制回收兜底。验收继续要求独立 CDP 观察到目标实际消失。本地最终导出的 Atom Matrix 58/58 与 StickC Plus 63/63 均通过，两轮各五个 Worker 目标全部退出，兜底终止为零。此前并行诊断在 StickC Plus2 也有自关闭后目标残留的失败，故托管修复效果仍须由串行完整门禁证明。 [本地摘要](evidence/engine-self-close-summary.json) · [正式重跑](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42603482039)

## 第三轮托管门禁及本地触摸复验

工作流 42603482039 两套运行时、导出和 CoreMatrix 原版均通过。Atom Matrix 完成冷启动和复位前代码检查，QMP 硬复位进入新控制台周期。新客体串口到 bootloader 入口与 I²C 初始化报错后停滞，600 秒内未发出第二次就绪标记。I²C 是最后观察到的日志，尚不足以定位复位根因。失败清场有正常退出码和自关闭通知，Chrome CDP 仍记录一个引擎 Worker。正式部署跳过。 [托管重跑](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42603482039) · [运行摘要](evidence/hosted-self-close-reset-summary.json)

本地完整门禁另在 PaperS3 触摸失败。同镜像独立重跑复现，等待客体出现稳定轮询后，同样 250 毫秒输入得到实际按下、松开、坐标和清场通过。该验证为定向诊断，未代替正式全量门禁。 [PaperS3 摘要](evidence/local-papers3-touch-cadence-summary.json)

## 2026-11-10：Atom Matrix 同会话复位基线

在未改动的 f23ecfe8 浏览器运行时上，用 Chrome 157.0.8103.39、本地独立静态导出和同一固件执行标准编辑器用例，追加八次交替的运行中与空闲硬复位。九次均取得 QMP RESET、新控制台周期、新的 UIFlow 就绪标记和该周期独立的串口输出；共 102 项通过。额外八次从硬复位到新代码回显为 40.25–41.67 秒。正常退出码 0，五个 CDP Worker 目标均消失，强制回收为零。 [脱敏摘要](evidence/local-atom-matrix-reset-stress-summary.json)

本机结果保留原托管失败。托管失败曾于复位约 39.6 秒后额外创建一个嵌套 pthread，此现象未出现在本机九次复位中；尚无证据把它确定为固件复位或引擎目标残留的根因。正式 Pages 仍未更新；未运行真机。

## 2026-11-10：PaperS3 稳定轮询复验

实际客体的一组心跳相隔 1002 客体毫秒，在宿主侧仅相隔 475 毫秒。验证保留原 250 毫秒触摸长度，等待两个独立的客体和宿主心跳间隔均约 1 秒后再送输入。模型实际按住 253.97 毫秒，GT911 客体报告 (270,400) 按下与松开；10 项检查通过，6 个 CDP Worker 目标均退出。该改动只触及 PaperS3 测试前置观察，PaperDIY 不继承。 [脱敏摘要](evidence/local-papers3-fresh-polling-summary.json)

## 2026-11-10：调度和 Worker 修复候选

`0038` 给完全匹配的 Atom Matrix UIFlow 工作台镜像启用每核 10 µs 调度上限，让副核更早参与 Flash IPC 交接。相同浏览器、固件、WASM 和导出下的开关对照各通过 58 项；复位到新代码开始执行从 40.391 秒降至 28.972 秒。来宾时钟、看门狗和就绪判据保留。两个对照未重现托管 600 秒停滞，不能确定该极端失败的根因。 [开关对照摘要](evidence/atom-matrix-cap-ab-summary.json)

浏览器把引擎 Worker 的创建、监听和释放统一放到顶层页面，保留 iframe 的来源、同源、会话及单端口握手。正常退出后解除监听并让引擎自己关闭；仍以独立 CDP 清零为准。合并候选的 Atom Matrix 编辑器 58 项、按键 10 项通过，含新控制台周期、实际代码输出与正常回收；独立生产 Worker 版的 StickC Plus 编辑器 63 项通过，五个目标全部回收。Chrome 157 和 Chromium 156 的纯浏览器对照未复现残留，托管结果仍是必要验证。 [候选客体摘要](evidence/browser-candidate-guests-summary.json)

主线提交 `ec3deaaaae0c6d9af3f1adf8e6d86db88923b729` 的平台套件执行 2069 项，11 项跳过，其余通过；Node 契约、配置验证、快照和变更范围检查通过。已触发[正式工作流 42736158712](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42736158712)，仅在全部 72 个串行客体用例及官方 CoreMatrix 镜像等门禁通过后部署。触发后回读仍是旧的 19 板部署 7647968330；本记录不把运行中的工作流当成发布完成。

## 2026-11-10：正式门禁进度与上线验收预检

工作流 42736158712 已通过 Xtensa/C61 构建、导出、Canvas 控制与官方 CoreMatrix 固件用例。完整浏览器串行验收于 02:04:43 UTC 启动；02:06:57 UTC 仍运行，没有新的部署。新站点不能用旧部署的证据替代。

四款新机型使用已锁定的完整演示 BIN；另保留 #211 的原版 CoreS3 固件与两种 SHA。候选导出的真实文件选择器在独立 Chrome 中接受全部五个文件，文件名和大小匹配。本次预检未启动客体。正式验证会先将 HTTPS 清单与成功部署的产物逐字节比较，再由网页文件选择器加载，核对真实 guest 的串口、画面和清理。 [进度与预检摘要](evidence/hosted-progress-and-online-chooser-summary.json)

## 2026-11-10：本轮发布终态

[工作流 42736158712](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42736158712) 用时约 46 分 49 秒。串行构建 Xtensa/C61 WASM 分别耗时 17 分 10 秒和 15 分 28 秒；官方 CoreMatrix 固件通过，逐板浏览器门禁运行 11 分 37 秒后失败。72 例中 6 通过、1 失败、65 未运行。Atom Matrix 和 StickC Plus 编辑器均通过真实硬复位、新代码及独立 CDP 清场。

首个失败是 Cardputer-ADV 的第 108 个键盘验收动作，鼠标操作句号键。模型实际按住约 256.93 ms，两个控制器命令获确认，原厂 KeyboardI2C 回调返回 46，原厂公开状态 API 的按下及松开记录未观察到。QMP 正常退出，6 个 Worker 全部消失。缺少状态记录的具体原因仍待验证，失败保持，部署跳过。 [终态摘要](evidence/hosted-cardputer-adv-irq-failure-summary.json)

修复候选仅调整键盘验收采样：原厂回调先读公开状态并缓冲，再由主循环输出 UART。相同固件与 WASM、250 ms 输入、全部状态与清场断言保持。最终版 112 个动作、516 项检查通过，鼠标句号键的原厂回调、按下、松开均观测到，正常退出后 6 个 Worker 全部消失。旧脚本本机也曾全过，因此这不是托管根因定论。修复已推主线，启动[新一轮完整门禁](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42765369676)。 [限定结果](evidence/local-cardputer-adv-keyboard-buffered-summary.json)

## 2026-11-10：Canvas 前置控制失败

[工作流 42765369676](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42765369676) 的两套 WASM 和静态导出通过。合成 Canvas 前置检查只通过第一条异步谓词负控，随后 1000 ms 内未取得首份像素读回；没有发现错误像素或页面异常，也未记录浏览器内是哪一步延迟。本轮真实客体、发布和现网验收均未执行。 [独立证据](evidence/hosted-canvas-first-read-timeout-summary.json)

Canvas 候选先确认实际第 0 帧双区哈希，再进行原计时控制。对照人为延迟首次真实像素读回 1.2 秒：旧版复现托管超时，新版正常与同等延迟均通过五项，三个原有计时不变。正式工作流改为两个独立的 macOS 源构建作业，以同一次尝试的产物进入原完整串行门禁，不复用旧构建。 [候选摘要](evidence/canvas-setup-and-parallel-build-candidate-summary.json) · [后续正式工作流](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42770355747)

## 2026-11-10：并行构建版本的完整门禁终态

[工作流 42770355747](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42770355747) 完成两套源构建，Canvas 前置控制与 CoreMatrix 官方原版通过。串行完整门禁 72 例中 6 通过、1 失败、65 未运行；部署跳过。

第 77 个键盘动作是实际浏览器 L 键，模型按住 256.435 ms，按下和松开的 QMP 回复都返回。原厂固件的按下回调与公开状态为真均存在；随后近 30 个客体秒的心跳继续报告 L 按下，没有松开。这与前一轮句号键缺少两种状态不同，故不能归因于同一采样问题。正常 QMP 退出码为 0，五个 pthread 目标都已退出，收到了引擎自关闭通知，未触发强制回收。独立 Chrome CDP 仍在 120 秒期限结束时观测到一个引擎 Worker，构成第二项失败。未确定具体丢失位置及 Worker 残留原因。 [脱敏证据](evidence/hosted-cardputer-release-and-worker-residue-summary.json)

## 2026-11-10：PaperDIY 的独立 GPIO 按键

本地全量预检 45 例通过后，在第 46 例 PaperDIY 的首个 A 键失败；其编辑器硬复位已通过。未修改的独立复跑在同一输入失败。两轮实际 QMP 按下和松开间隔均约 251 ms，客体从就绪到第一条轮询心跳分别为 4,207 和 4,037 客体毫秒，原厂 M5 Button 没有报告按下。两轮均正常回收 Worker。

限定候选在首个输入前先取得两段连续、宿主和客体时间均约 1 秒的空闲轮询区间，原 250 ms 手势、两种真实输入、按下/松开断言均保留。原厂 A/B 的键盘和鼠标共四个手势通过，15 项检查通过，6 个 Worker 目标全部消失。此项是本地虚拟验证，不改变之前完整预检失败和 26 例未执行的记录。 [脱敏证据](evidence/local-paperdiy-gpio-polling-summary.json)

## 2026-11-10：托管 Cardputer ADV FIFO 对照

[诊断工作流 42775250168](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42775250168) 在独立 macOS runner 上使用与正式失败相同的固定固件和 WASM。普通版和启用 FIFO 追踪版均通过 112 个真实手势、516 项检查，6 个 Worker 目标全部退出。追踪实际覆盖 QMP 输入、QEMU 按键分发、TCA8418 读写和 GPIO11；SHIFT 观测到一次松开与先前上升沿 ISR 的清除写交错，GPIO11 保留实际下降沿，原厂固件随后读到 FIFO 松开。未复现此前 L 键松开缺失，不能用本轮通过覆盖正式失败。 [脱敏证据](evidence/hosted-cardputer-fifo-paired-diagnostic-summary.json)

## 2026-11-10：CoreMatrix 原版的托管清场复现

[诊断工作流 42776130682](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42776130682) 的 Canvas 通过。未改动 CoreMatrix 原版固件已启动，完成 USB、真实按键及九次点阵像素比对，QMP 退出码 0。内部六个 pthread 在退出时计数为零，已有引擎自关闭通知且无兜底。Chrome CDP 实际观察 7 个目标，其中 1 个残留，故本轮失败；原报告只有数量，无法辨认残留目标类型。后续七个用例跳过。 [脱敏证据](evidence/hosted-corematrix-stock-worker-residue-summary.json)

## 2026-11-10：同一托管 runner 的 Worker 退出对照

[诊断工作流 42775514548](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42775514548) 在同一 macOS runner 上，用同一 Cardputer ADV 固件和 WASM 对照三条退出路径。三组各通过六次实际键盘/鼠标手势，停止时探针仍在运行，QMP 退出均为 0。原版自行关闭本轮通过；确认跨过一个新的 Worker 任务再自行关闭的模式仍留下一个主 Worker，五个内部线程已消失。相同握手后由顶层 owner 回收的模式 6 个目标全部消失，未用异常兜底。该对照证明丢键不是残留的必要条件；单次候选通过不足以确认可靠性。 [脱敏证据](evidence/hosted-cardputer-worker-differential-summary.json)

## 2026-11-10：重复对照、候选与正式任务

[六轮对照 42776531090](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42776531090) 在同一 runner 上交替执行两种退出路径，各轮真实输入和客体退出均通过。握手后自行关闭 1/3 通过，两轮在 120 秒后仍有一个引擎；握手后由顶层回收 3/3 通过，兜底为零。 [重复摘要](evidence/hosted-cardputer-worker-repeated-summary.json)

候选 b4e280d5 的[独立托管验证](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42777412965) 全部通过：Atom Matrix 硬复位周期 0→1 并执行新代码，Chrome 6/0；Cardputer ADV 112 个实际动作，Chrome 6/0；CoreMatrix 原版 USB、按键和点阵，Chrome 5/0。各例确认一次正常 owner 回收，退出码 0、兜底 0。[常规 CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42777412610) 2070 项，11 项跳过，其余通过。 [候选摘要](evidence/hosted-worker-production-candidate-summary.json)

候选已推送主线，[正式任务 42777985298](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42777985298) 已开始重新构建。正式部署仍要求全量 72 例、Canvas 和原版 CoreMatrix 门禁，本段不作为已部署证据。

## 2026-11-10：本地剩余用例

本地早前完整预检仍是第 46 例失败。独立后续在相同本地导出以单客体执行剩下的 CoreMatrix 编辑器/按键 2 例，以及所有固定固件 24 例，均通过；其中四款新增机型有真实客体帧和独立 CDP 清零记录。这个分段诊断不改变早前完整运行结论，也不是正式发布。其 C61 WASM 使用实际本地摘要，不与托管构建混用。 [脱敏摘要](evidence/local-remaining-corematrix-and-fixed-summary.json)

## 2026-11-10：旧路径顺序复现及新版纸屏输入

[旧版顺序诊断](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42776981254) 的原版 CoreMatrix 和 StickC Plus 编辑器均未通过 CDP 清场；StickC Plus 可识别的残留是主引擎。顺序任务因此未运行 Cardputer FIFO，不能从这轮定位丢键。

正式候选 b4e280d5 独立本地导出上，PaperDIY 4 次 250 ms 级真实 GPIO 手势与 PaperS3 触摸坐标、松开均通过。两次正常 owner 回收，Chrome 各自 6 个目标全部消失。 [脱敏证据](evidence/old-ordered-worker-failure-and-candidate-paper-buttons-summary.json)
