# 身份能力协商跟进报告

## 问题与修改

此前前端只检查 cloud 启动能力。连接旧版 Device Service 时，页面仍可能接受指定身份，但旧服务会忽略 `device_identity`；创建控制器只核 session/device，没有证明实际用了请求的身份。因此，页面的“持久身份”提示和实际执行可能不一致。

候选添加设备级 `device_identity` 能力：schema 版本、支持的 key/mac selector、支持的 runtime 与 cloud 默认身份策略。前端依据该能力显示身份入口；留空时显式请求设备对应的持久 key。创建收据必须匹配规范化 MAC 或持久 key，并具有有效的解析后 MAC。缺失或不匹配的收据不能进入运行态；已经取得的 owned 会话仍保留用于取证和清理，幂等恢复与失败清理不会另造新会话。旧服务不靠版本字符串猜测，而由实际能力缺失阻止分配。

## 固定输入

| 项目 | 身份 |
| --- | --- |
| 当前整合候选（仅文档后继） | `70ef503fc2fb8b2c787fa9065e2952f525c40099` |
| 整合候选（主机验证） | `014841a8fe082cf8aaaa57de898e0ac0f665aedf` |
| 执行源码（既有 guest 验证） | `3a4408e4a1f26c0c8ad3ff07dae1ac8149a50384` |
| 基线源码 | `a5990e720a8c79310456bf5868141f4cfd50afe8` |
| 真实旧 HTTP 服务源码 | `4a5d28e6d4764ec78c0621aed0e0527080597486`（API 1.61） |
| CoreS3 原版 BIN | `5847a2bcae33d6bb8942de1c3ae92295a8441b6a3424c78e444fc748c9508ded` |
| 标准化执行 Flash | `480ca4a24c1c1b56deef1218f8533bf5b00c9e33a98f3b3f705e2569b53051c0` |
| 原生运行时 | `5ce7d9f5ce397ce87935626c0284955714e0ed286fcce0cd91ca47f4f326040c` |
| 站点 manifest | `c9a3b79f45fdfeac7a4a8eb1eda1b521bea7a35a9da5538b1e35f52199cb0ca8` |

浏览器连接原生 Device Service，不是 browser-WASM，也不是物理硬件。第三轮由明确选择的 desktop Chrome 执行；历史 browser.version 与执行文件 SHA 未采集，不能根据后来安装的版本补推。这一复现限制由独立 provenance 摘要保留。

## 已执行验证

真实旧服务目录有 cloud 能力但没有身份能力。实际新 client/controller 通过 HTTP 分别尝试指定 MAC 和持久 key，两者均在 session POST 前拒绝：POST 0、guest 0，清理完成。该负控验证兼容性准入，不是固件启动通过。

指定身份第三轮完整用户路径有 36/36 检查通过。原版 BIN 字节、真实运行时、HTTP 创建请求与收据、eFuse 身份、MQTT code 和 WebSocket query 均已核对。102 个样本覆盖约 202 秒，自首次握手后观察至少 195 秒；初始 UI 样本处于 flashing，随后 101 个 running，未出现错误 banner 或脚本异常。运行期 frame 304 成功 5847 次，API HTTP/网络错误 0；准备期未认证 401 单独保留 1 次，清理期错误 0。

同 ZIP 的 10 个 manifest 成员均完成大小与 SHA 核验，抓包与报告使用同一 SHA。解析到 7 次关闭前有效文本心跳，控制 PING 6 次、PONG 0 次。首连接由 guest 先发 FIN，距首控制 PING 为 120.057725 秒；串口出现一次精确 120 秒 PONG 超时标记。轮询约 156.08 秒看到断连、160.10 秒看到第二次握手。身份和 UI 的 PASS 不覆盖持续云连接的 FAIL。

取得同会话证据 ZIP 后停止 guest，Flash、lease 与进程释放，浏览器退出；此前终态历史保留。独立视觉复核确认真实开发界面、配对码、running 状态和分离的云诊断同时可见。原截图仅保留私有哈希，不公开配对码。

## 失败与修正保留

1. 首轮在隔离页面重载期间过早操作连接面板，输入超时，没有创建 guest。该轮 FAIL/guest NOT RUN 保留；修复测试入口等待初始化完成后，两次独立无 guest 浏览器预检通过。
2. 第二轮真实 guest 完成观察，但旧网络 oracle 混入准备期未认证 401，因此原 harness FAIL 保留。回顾审计发现运行窗口无 HTTP 错误，清理后有一次 frame 409；没有把这个旧摘要改为 PASS。
3. 第三轮先固定阶段边界与 15 项主机负控，再完整重跑。全程原始网络事件保留；Start 前进入运行范围，直到截图和 ZIP 采集完成。运行期和跨阶段迟到的 401/500 仍失败，只有实际 owned stop 后的 frame 409 单独归入清理。该轮 UI/身份 PASS、总体 PARTIAL、云持续 FAIL。

默认 key 分支使用同一固定源码/站点/运行时/原 BIN，独立完成 45 秒实际 UI 验证：27/27 项通过，1176 次 frame 304，运行 HTTP/网络错误 0。空白输入实际发送设备默认 key；收据为 persistent-fixture 且 key 精确匹配，解析身份与 eFuse、Ethernet 帧和 13 条 WebSocket query 一致，跨两次独立创建保持同一身份。MQTT 配对码收到，云端以 mac_not_bound 拒绝 13 次，页面分别显示这两个事实。云绑定未通过，短观察不声称长期稳定。

默认分支第一次运行仍保留 FAIL：1172 个 requestfailed 与 1172 个真实 304 一一对应，页面 JavaScript、UI 和运行 HTTP 没有失败。随后 16 项纯主机对照覆盖两个固定浏览器、CDP 开关、allHeaders 开关和相同 worker 开关：后测的 bundled Chromium 156.0.8078.4 对每个成功 304 发出 ERR_ABORTED，desktop Chrome 157.0.8103.52 没有该事件。该对照是主机观察行为诊断，不能代替真实 guest 验收，也不能反推第一次未采集的浏览器版本。第二次另行使用记录版本与执行文件 SHA 的 desktop Chrome，严格网络门槛未放宽，实际 default-key 用户路径通过。浏览器执行文件前后 SHA 均为 `5441ca699b9eff7763f2f10765e2e8409a4b05f38917826b5247f6f6bb3b0c6b`。

默认分支证据 ZIP 10 个成员全部核验，取证时 guest 仍运行。此前 3 条终态历史保留，新增 owned 会话停止并释放 Flash/lease；guest 与浏览器进程均清理。整个候选验证结束后，专用执行环境停止，原证据与历史保留。

## 检查、边界与回滚

16 项受影响 Python 检查、22 项文档检查、Node contracts、27 项实际 host 浏览器检查、四项验证器与范围检查通过。当时的 `3a4408e4` 候选完整 Python suite 按运行资源隔离要求中断，没有完成全套；这一历史状态保留。

后续最终整合候选 `014841a8fe082cf8aaaa57de898e0ac0f665aedf` 的完整平台 suite 已执行 2235 项、跳过 8 项并通过。前一轮 `8266dfb2a99cfdcf9fdfab95f612c924cd9180e9` 的两项 API 清单和文档状态契约失败保留；修正仅涉及清单版本、契约 digest 与明确的审查日期，两轮之间没有产品行为变化。Node contracts、四项生成契约验证器和本地 scope 检查在前一源码完成通过，最终源码另由分支 CI [43492311926](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/43492311926) 的 `platform-contracts` 与 `network-namespace-policy` 两项 job 完成通过。CI 的 PR scope 步骤在该分支 workflow 中跳过，不用它代替已记录的本地 scope 检查。这些均是主机检查，不替代既有 guest 结果或交付后复验。后继当前候选 `70ef503fc2fb8b2c787fa9065e2952f525c40099` 只改动 18 个 `docs/` 文件，补入原生矩阵证据与当前状态；Git 差分已独立核对，没有实现、fixture 或 producer 变化。本记录保留 suite 的真实执行源码，不把它改写为在文档后继上重跑。随后该最终提交的分支 CI [43494608853](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/43494608853) 两项 job 通过，main 已从固定基线快进到 `70ef503fc2fb8b2c787fa9065e2952f525c40099`；最初读回时 main 独立 CI 43496500912 仍排队，这份历史摘要保留；后续完成读回确认 `platform-contracts` 与 `network-namespace-policy` 两项 job 全部 success，见独立 `main-ci-completed-summary.json`。其中 PR scope 步骤跳过，仍以已有本地 scope 检查为依据。

本跟进未改变原版固件或云端服务，也不证明账号已绑定、远程代码执行或物理特性。主分支已完成整合；最终源码用户路径复验见下节，Pages仍待独立证据。源码可在兼容回退时退回固定基线；临时执行状态和原证据应保留，不以删除历史完成回滚。未提交 Burner。

## 最终源码的独立用户路径复验

最终 `70ef503fc2fb8b2c787fa9065e2952f525c40099`、相同 `c9a3b79f…` 站点、
相同 `5ce7d9f5…` Xtensa runtime 与原版 `5847a2bc…` CoreS3 BIN 另行完成真实浏览器启动。
明确固定 Chrome 157.0.8103.52，执行文件前后 SHA 均为
`5441ca699b9eff7763f2f10765e2e8409a4b05f38917826b5247f6f6bb3b0c6b`。

这次30/30项验收通过。102个样本的guest均处于running，UI第一个样本仍显示flashing，
随后101个均running，无错误banner。561次UI状态观察均无可见错误，脚本异常0；
首次观测握手到最后样本为196.8秒。运行期5870次frame304，HTTP与网络失败均为0，
准备期认证401与清理期409均为0；这与早期第三轮5847次、准备期401一次的证据分别记录。

实际POST/收据、eFuse、网卡和WebSocket身份一致，收到配对码并登记，身份拒绝0。
同一ZIP仍记录7次有效文本心跳、6次控制PING、0次控制PONG，以及串口一次PONG超时。
两次握手之间有一次guest断连；最后连接快照的心跳计数1不能当作两连接总数7。
因此UI/身份与清理PASS，云持续连接FAIL；没有远程REPL执行通过的结论。

在停止前取得仍处于running的同会话ZIP，随后释放guest、Flash、lease和浏览器，
保留此前历史。UIFlow Develop界面、配对码与分离的WebREPL诊断已视觉复核；含身份和
配对码的截图不公开。原始摘要与独立审计均以SHA引用，旧执行和失败证据不修改。

独立协议复算确认258个packet、两次有效101升级、guest先发FIN，首控制PING至FIN
为120.047286秒；浏览器相对时钟在156.6秒观测断开、160.6秒观测第二次握手。
两种时间原点不混算。最终ZIP有10个清单成员且没有Flash，因此只独立核原BIN与
标准化FF补齐哈希，不声称postrun APP分区读回。实际网卡argv和eFuse backing挂接由
live helper检查，未留raw argv供停止后独立重算；收据、eFuse内容、Ethernet和WebSocket
身份对应则可从保留证据复核。上述可复算边界见
[独立协议审计](evidence/final-main-cloud-protocol-independent-summary.json)。
