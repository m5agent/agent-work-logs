# 原版固件与原生模拟器的补充验证报告

## 目标与身份

本轮继续排查经典 ESP32 的时钟/输入以及 ESP32-C6 的串口、身份和板级行为。目标是让原版固件通过真实控制器路径运行，并把固件故障、模型缺口和观察器故障分开。应用镜像没有为了通过测试而修改；专用探针使用独立固件身份。

已执行的 Xtensa 产物为 `5ce7d9f5ce397ce87935626c0284955714e0ed286fcce0cd91ca47f4f326040c`，由固定上游 `40edccac415693c5130f91c01d84176ae6008566` 加 150 个补丁构建，重新编译 1,235 个对象。已执行的 C6 产物为 `8df537142dd8e8231f7d201772176f6460fdbe46a80b812e7796d213373b8b8d`，固定上游 `febae182e132e4055529be423a818225ebddaa3a` 加 24 个补丁，重新编译 1,273 个对象。两者均没有诊断插桩。源码、补丁、ROM 和构建收据分别绑定，见[早期运行时摘要](evidence/runtime-pins-summary.json)。后续 25 补丁的 C6 `80d92a6c…` 构建和验收在下文另列，未替换旧结果。

JIGGLER 的执行服务为 `1be1e1464a49e7e36d849a4610cac6eacfc91ac4`，四条经典显示/输入控制为 `a8c9b222c6af0081fd48bc7facafa7cd12b6e5c3`，C6 正式路径和串口页面为 `10c826b832b78c9bc42e9f788bd3e595584978ae`。新增 80d 原版/页面运行使用 `4a5d28e6d4764ec78c0621aed0e0527080597486`。后续文档或测试提交不追认为这些 guest 的执行源码。

## 经典 ESP32：复位域、有界自适应与原版按键

原 JIGGLER 曾遇到缺失的 DPORT 时钟回读、CCOUNT 变频不连续、面板识别和 BR/EDR 定时器行为问题。旧自适应范围下，同一原 BIN 在按键路径于虚拟 155.641 秒触发 IDLE0 任务看门狗；无应用按键的独立对照也于 185.957 秒触发。首次超时的完整事件链仍未定位，不能将后续通过扩大为所有时钟配置正确。

补丁 0201 接通 RWBT MAC / 低功耗独立复位域。复位后残留状态由控制器 qtest 复现并验证，正常 CPU-only 和独立 baseband 复位边界保留。补丁 0202 为经典 ESP32 的有界自适应调用设置 `max-shift=5`，范围为 0–5；到达上限后虚拟时间可落后于主机。普通未指定上限的通用调用仍有原来的 0–10 范围。默认固定步长保持 5。回放组合在打开文件前拒绝，迁移的已有字段格式保留，范围校验有独立控制。

同一原版 JIGGLER 1.0 BIN，SHA-256 `c5ce5ad2e1a1f33bf99bbc1e29574562e1f2dbe661b9aca554c052cdb6b6e401`，经 C 下压/释放进入主界面。通过生产输入接口发送 B 100 ms、A 100 ms、B 2000 ms，分别观察鼠标未就绪、暂停和设置页。两轮有界自适应在新鲜主界面计时基准后的虚拟时钟下界分别为 300.377564 / 300.308091 秒，设置页后的下界为 280.820599 / 277.567543 秒。默认固定轮设置页后的下界为 15.866 秒。这些值表示至少经过的虚拟时间，不是精确 elapsed。三轮均一次上电、无看门狗或 panic，两个原应用分区不变。

计时使用既有虚拟微秒读数与固件主动锁存的 LACT shadow，目标画面之后再等待一次新的 shadow 更新建立起点；以两种读数的保守间隔中较小者形成下界。它不是物理时钟测量。Core2 和 Plus2 的固定/有界自适应四组合另有实际显示与输入后重绘证据。完整参数和复现入口见[固定源码说明](https://github.com/m5agent/m5stack-esp-emulator/blob/bb9475b163b108bb807959628b5bb7cb0e65768f/tests/firmware/stickc_plus2_bt_lp_clock/README.md)及[原版摘要](evidence/jiggler-bounded-adaptive-summary.json)。

## NanoC6：完整 USB 输出与两个独立串口通道

C6 的 USB Serial-JTAG 固定端点模型补齐 TX/RX、IRQ、host/pad gate，以及 SOF 与 IN 完成调度。模型中的 8/64 微秒是调度参数，不是 USB 物理总线测量。随后同一 `8df53714…` 产物暴露了执行前提缺口：直接运行原 Honeypot 180 秒仍只有 461 字节 ROM/PHY 输出；两个只读诊断运行分别得到 151 和 153 字节应用输出。这些失败与受观察器影响的结果均保留。

独立单变量对照仅加入已有 StickS3 USB capture 使用的 `-accel tcg,thread=single -icount shift=5,align=off,sleep=off`，同原 BIN 在 90 秒内完成全部输出。生产修复把该策略限定在**实际追加第三 USB chardev 的 plain NanoC6 qemu 分支**。HCI、统一 console、Nesso、Wi-Fi 和替代 console-index 保留既有策略，没有按固件哈希特判。

正式 Device Service 在 `10c826b8…` 直接运行原 Honeypot 180.008 秒，没有 wrapper、HMP、按键或应用修改。console 为 461 字节，USB 为同样前缀加完整 153 字节、四个 CRLF 的应用输出；后缀 SHA-256 为 `957653a047aacb4f6c16b22209ba72edc5e5ae941ff7fd744992c3c297d9f3c6`。两个通道各有一次 ROM banner、未观察到 fatal，两个应用区字节不变。每个通道分别读取，不把两份 ROM banner 相加误判重启。

18 次分块 API 响应与最终 ZIP 中各自日志逐字节一致；三个页面的 13 次响应也与同一 ZIP 核对。Public、Sessions、Observatory 均执行 `console → usb-serial-jtag → console`，USB 显示完整应用输出，切回 console 保留独立偏移且不混流。九张最终截图通过独立目视复核，仅公开哈希。

第一次 Public 和 Sessions 已通过，Observatory 虽正确显示输出，外部观察器读取响应体时失败，记录为 `INFRA_FAILED`。随后仅对 Observatory 在**同一持续运行 guest**上重做，采用只读 response clone 观察，产品源码和 guest 均不变。两次页面观察分开记录。ZIP 先于停止保存，最终 guest、Flash、租约和自有服务均清理。[串口证据](evidence/serial-channel-ui-summary.json)及[固定复现步骤](https://github.com/m5agent/m5stack-esp-emulator/blob/f33b96ad021adcc7bd9a3d1c0e7e87f4a84c32d7/tests/firmware/esp32c6_usb_serial_jtag/serial-channel-ui/README.md)

配置输出和通道隔离通过，Honeypot 完整应用仍为 `PARTIAL`。原日志保留 PHY 校准不匹配和 PLL 校准超时诊断；没有验证 AP 关联、HTTP、蜜罐网络行为或 RF。

## C6 共享中断修正前的限定结果

同一 8df 产物和生产服务路径的五个控制探针包括 Arduino 的精确 257 字节 TX / 197 字节 RX 与确认响应、原 UIFlow2 USB REPL、TSF 六项控制，以及两份隔离身份/复位稳定性检查。802.15.4 extended-address 数据通路仍为预期失败，不能因 eFuse 身份通过而授予 Zigbee 完整支持。

原 Meshtastic 的先前“B 键应改变画面”预期失败保留。独立同 BIN 运行中，A 1.2 秒打开 Home Action，短 A 移动选择，观察 45.431 秒，无 fatal。原 Bruce 观察 150.347 秒，触摸后画面改变，明确请求一次复位后文件系统重新挂载、画面有效；两次 ROM 启动分别对应上电与这次请求复位，不是“只有一次启动”。这两项为限定界面路径，不是完整无线应用验收。

这些结果属于**共享中断修复之前的 8df 运行时**。PI4IOE 的默认参考、掩码、锁存及共享 pad 语义另有修正 0023；新产物的独立定向结果见下一节，最终矩阵另有验收门。旧 PASS 不自动转授。CPU GPIO 中断分发、BMI 待决中断和物理 open-drain 电气行为也没有因此获得验证。[C6 原始失败、控制与限定结果](evidence/c6-pre-shared-irq-runtime-summary.json)

## 0023 新产物与独立页面复验

共享中断修正后的新 C6 产物为 `80d92a6c6c68137a7813b8b7c519725aac350258078d9b244098eaabf82f63bf`，固定配方 `60f13e41933a6664b8be2720d1feef7451dcc0c3`，25 个补丁、52 个源码 postimage，重新编译 1,273 个 QEMU 对象。已有静态依赖库复用单独记录，没有把旧 QEMU 对象当作 fresh 构建。新收据和原版执行绑定见[80d 摘要](evidence/c6-final-v3-runtime-summary.json)。

0023 按官方接线合并 GPIO3 上的触摸和 0x43 PI4IOE 待决源，0x44 不驱动该线。外部输入从默认值转为相反值时锁存，mask 只控制输出；读 0x13 清该源，读 0x0f 不清。配置写不合成新的输入事件或状态，但会正确改变已有 pending 的输出 gate。17 项真实 HP I2C0/FIFO 和 pad 观察在旧模型有 9 项缺口，新产物全部通过；actual-C 控制单列。方向切换时保留旧 latch 是明确模型选择，CPU ISR 分发、BMI 中断和 FT6336 精确脉冲时序仍未实现。

新产物原 Mesh 观察 150.382 秒，A 1.2 秒进入 LoRa region 菜单，短 A 从 Back 移到 US，自然休眠后 B 唤醒保留选择。原 Bruce 观察 150.393 秒，触摸从 WiFi 切到 Clock，一次请求复位后重新挂载并回到 WiFi 页；对应一次 Mesh 上电和两次 Bruce ROM 启动，无 fatal。原 Honeypot 独立观察 180.011 秒，保持完整 461+153 字节和原应用区不变。五个 USB/TSF/身份探针及 Nesso peripherals / LoRa 两项控制回归另有同产物证据，均不授予无线数据面或物理 RF 支持。

对 Mesh 的静态归因同时作了纠偏：[精确原 BIN 反汇编](evidence/mesh-exact-bin-button-summary.json)确认函数 `0x4202a75c` 直接轮询 0x0f，并分别处理 A、B；它不等于较旧公开 fork 的 0x13 状态门控、仅 A 路径。不能把那个 fork 的假设性释放故障归给原 BIN。8df 的 B 改变画面预期失败及其独立 Home Action 观察保持历史，80d 的实际菜单按新帧记录。

新运行时的第一次 UI 借用到达原 180 秒会话时，所有者已停止服务，首个 GET 连接拒绝，浏览器未启动；该项为 `INFRA_FAILED / 页面 NOT RUN`。随后建立**新的独立原版会话**，以浏览器完成回执与有界窗口协调所有者。90.012 秒内完整输出持续有效，三页在同一 guest 上一次完成，18 次 API 和 13 次页面响应逐字节匹配该会话最终 ZIP，九张新截图独立目视通过。没有按键/HMP/产品源码修改或变更 API 请求；浏览器先关闭，再由所有者导 ZIP、停止并清理。[新页面摘要](evidence/serial-final-v3-ui-summary.json)与旧 8df 页面结果分别绑定，不能相互替代。

## 当前公开固件的文件身份

按公开目录的 current / PUBLIC / PUBLISHED 记录重新下载并计算文件哈希，三份 BIN 均与先前原始文件相同：

| 固件 | 当前版本 | 文件字节数 | SHA-256 |
| --- | --- | ---: | --- |
| StackChan-UserDemo | V1.6.0 | 12,783,789 | `245bc9af0a5dff0388017073d7f571fdd03268a0df71bc62c8de7567f8e32866` |
| StackChan-GPT | 1.8.11 | 12,857,054 | `e680215dd1858dfcff5daff312ef13d1467ee72b77d9cb4a0caba2fd23e7cdc0` |
| Meshtastic RFID Demo | 2.7.21 Landscape PN532/PN532Killer | 2,028,592 | `1ea35725b85cf66745724daaaf8005ba1dcac522b2b10005671b7f7cf2cf86c8` |

UserDemo 在目录中标为 OFFICIAL，GPT / RFID 为该公开目录中的 COMMUNITY 项目。前两项旧文件名 URL 返回 404，已有下载器按公开版本记录回退到对应公开文件；最终文件哈希已核验。只凭版本名没有作判断。这次核对没有新建 guest，也不改变 #223 原 BIN 的稳定性失败、#216 RFID 的原始失败，或新源码重建对照与原 BIN 的区别。[公开来源与下载摘要](evidence/current-artifact-summary.json)

## 平台检查与 CI 失败保留

在 `10c826b832b78c9bc42e9f788bd3e595584978ae` 上，本机完整平台测试运行 2,177 项、8 项跳过，205.603 秒，退出码 0。相同提交的首次 Linux CI [43442928989](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/43442928989)仍失败：三个生成 C harness 触发 GCC misleading-indentation 诊断。

修正原提交为 `69aac24140c5cdda8bdfc4b20552dea289fea740`，集成为 `b33fc45c436ce3cfdab2cfc34983d8a6b64304ba`；两者 diff 字节相同，仅展开三个测试文件中的控制流写法，没有修改控制器。后续精确源码 `bb9475b163b108bb807959628b5bb7cb0e65768f` 的 [CI 43444553975](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/43444553975)已独立回读为 completed / success，两个 job 均成功。两轮 CI 和本机测试分别保留。[检查摘要](evidence/host-and-ci-summary.json)

后续精确执行源码 `4a5d28e6d4764ec78c0621aed0e0527080597486` 的本机全平台为 2,178 项、8 项跳过、209.054 秒，四项 validator 通过；[CI 43446583704](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/43446583704)已完成 success。该次 CI 原响应 SHA 与精简摘要已核对。[4a 检查证据](evidence/host-and-ci-4a5d-summary.json)独立追加。宿主检查不是 guest 或部署验收，执行源码与交付源码的区别仍保留。

## 复现与最终交付

三个配方文件已从公开 GitHub 回读并与本地固定 Git blob 逐字节比对：新 C6 [60f13 的 bootstrap-c6-runtime.py](https://github.com/m5agent/m5stack-esp-emulator/blob/60f13e41933a6664b8be2720d1feef7451dcc0c3/scripts/bootstrap-c6-runtime.py)、旧 C6 [3dcc 的同名配方](https://github.com/m5agent/m5stack-esp-emulator/blob/3dcc0dad339b7d453bc81996dbdff6737229d33a/scripts/bootstrap-c6-runtime.py)，以及 Xtensa [6a8 的 bootstrap-unit-runtime.py](https://github.com/m5agent/m5stack-esp-emulator/blob/6a8bf4a57a8b96d744b92966f4dc2a8d71976893/scripts/bootstrap-unit-runtime.py)。文档引用切到字节相同的集成提交，原始执行/配方 SHA 保留；[链接等值与回读摘要](evidence/source-link-equivalence-summary.json)记录证据。

从上述固定源码获取补丁顺序和构建配方，在独立源码/构建目录生成对应 `xtensa-softmmu` 或 `riscv32-softmmu` 目标，核对全体补丁、postimage、ROM 和构建收据。重新构建可能产生新的二进制哈希；必须按新身份记录，不冒用既有产物 SHA。

原版行为通过独立 Device Service 上传相同 BIN，创建目标设备的 `qemu` 会话，核对实际进程的二进制与启动参数。按各摘要里的输入、虚拟时间或 host 观察窗口执行；分离各通道日志，收集输出/帧/输入回执，在停止前导出 ZIP，再以 `purge=0` 停止并核资源释放。C6 控制探针的固定入口见[USB fixture](https://github.com/m5agent/m5stack-esp-emulator/blob/6f9d3afaa5f1710ee2229d3d2b2c28a97660a45d/tests/firmware/esp32c6_usb_serial_jtag/README.md)。这些步骤不包含 Burner 提交。

最终运行以精确源码 [4a5d28e6d4764ec78c0621aed0e0527080597486](https://github.com/m5agent/m5stack-esp-emulator/commit/4a5d28e6d4764ec78c0621aed0e0527080597486)和 Xtensa `5ce7d9f…` / C6 `80d92a6c…` 执行了一轮 69 项联合矩阵：69/69 PASS、每项一次、无重试、无显式负载 worker，964.7 秒后清场。这是环境常规负载验证，不是高负载覆盖或物理性能测量。[矩阵摘要](evidence/ambient-matrix-summary.json)保存每项固件、输入、输出、运行时与 ROM 哈希。

main 的 [CI 43453074487](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/43453074487)已成功。两个获授权的常驻服务已部署上述精确版本。独立只读保留性审计核对源码、配方、ROM、备份、依赖和浏览器资源；两组历史由 29→36 和 42→46，旧记录完整保留。配置、状态位置和当前鉴权检查通过；没有部署前令牌内容哈希，不能宣称令牌字节相等。

九个部署后用例均为本轮独立首轮，没有复用旧 cloud 行。八个配对路径从各自 ZIP 的真实 PCAP 重新解析非空云端回包，程序页面用例核对实际本地程序输出。九份完整 ZIP 串口分别检查一次启动和无 fatal；ROM banner 与 reset-reason 行不相加误判两次启动。实际 runtime 收据、九张截图和独立人工复核均绑定同一会话。post9 ZIP 不含 Flash，因此 post9 的应用字节比较明确为 NOT RUN，不能继承下述两份 dry-run 的结果。

原 Cardputer ADV MP3 Player v1.0.0 和 Core2 2048 Game v1.0 通过 saved_snapshot 再执行 dry-run，审核服务各为 `done / SIM_VERIFIED` 且无提交请求。另行从最终 ZIP 重算原应用区域不变、完整串口无故障；MP3 的实际单声道 48 kHz PCM 匹配 524 Hz 控制音，2048 的右、左、上、下各两次，共八次移动符合移动/合并及新块生成规则。原 helper 的 `execution_status=PASS, status=REVIEW, visual_review=PENDING` 原样保留；独立帧复核收据另列，不把自动结果与人工判断合并冒充原状态。没有提交 Burner，也没有把 PCM 结果当物理声学测量。

九个 post 用例与两个 dry-run 的 11 个独立会话均先导 ZIP、后停止，Flash、租约和捕获的 guest 进程已释放；两个服务均空闲。[完整交付摘要](evidence/post-delivery-summary.json)保存机器复算、人工复核、清场和实际文件哈希；[最终接受门](evidence/delivery-acceptance-summary.json)取代[历史门禁](evidence/pre-delivery-gates-history.json)作为当前状态。

工具失败没有从时间线抹除。原版审核首次在函数第一条 Pillow import 即失败，未请求审核队列、未创建 guest、未创建输出目录；随后仅启用已安装的依赖路径，helper 字节不变。只读保留性审计第一次误选宿主控制日志，被哈希门拒绝；第二次误把整数 active_sessions 当作列表，第三次审计完成。两次均未更改服务，也不属于产品或固件失败。全部失败收据和日志哈希均在交付摘要中单独保存。

57 项隔离宿主控制通过，但现场回滚和状态迁移为 NOT RUN。旧版本不支持新的 `max-shift` 参数，不能只替换二进制而沿用不兼容启动参数；备份存在与可核对，不等于执行过一次现场恢复。整体仍为 PARTIAL，因为 RFID、StackChan 等既有原版稳定性和完整无线数据面边界没有由本次通过覆盖。

公开层仅保留有界摘要、完整版本和文件哈希；不包含本机拓扑、内部端点、会话/设备唯一标识、原始图片、BIN、ROM、PCAP或整份第三方文档。所有结果均为 virtual-device validation；物理硬件、周期精确时序和浏览器 WASM 为 `NOT RUN`。

后续文档主线已更新到 [ffa621cdcf8422005b7fdf66afdee1be7c5fbba7](https://github.com/m5agent/m5stack-esp-emulator/commit/ffa621cdcf8422005b7fdf66afdee1be7c5fbba7)。从执行版本 4a 起只追加或更正文档与有界 JSON 证据，常驻服务仍固定在 4a；[差异核对](evidence/final-documentation-main-summary.json)没有把新文档 SHA 当作重新执行结果。
