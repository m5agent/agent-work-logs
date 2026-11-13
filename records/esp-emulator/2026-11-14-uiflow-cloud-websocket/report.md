# UIFlow2 WebSocket 诊断报告

## 背景与目标

用户报告 UIFlow2 已获得配对码，但串口持续出现接收失败及 TCP FIN 错误。本次需要区分虚拟网络传输、云端设备绑定和固件心跳处理，避免把“获得配对码”“HTTP 升级成功”误写成“WebREPL 可用”。

源码 base 为 `ffa621cdcf8422005b7fdf66afdee1be7c5fbba7`。修复已进入 [`main @ a5990e720a8c79310456bf5868141f4cfd50afe8`](https://github.com/m5agent/m5stack-esp-emulator/commit/a5990e720a8c79310456bf5868141f4cfd50afe8)，[对应 CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/43468922515)成功。同路径候选验证和部署后 195 秒功能复验均已完成，Pages 更新另行验收。身份拒绝、控制 PONG 缺失、前端 304 构造错误分别判断；前两项不能因界面修复而记为已解决。

## 固定执行身份

两次 CoreS3 guest 对照使用相同原版固件和运行时：

| 项目 | SHA-256 |
| --- | --- |
| 原版 UIFlow2 BIN | `5847a2bcae33d6bb8942de1c3ae92295a8441b6a3424c78e444fc748c9508ded` |
| 规范化 Flash 基础镜像 | `480ca4a24c1c1b56deef1218f8533bf5b00c9e33a98f3b3f705e2569b53051c0` |
| 原生运行时 | `5ce7d9f5ce397ce87935626c0284955714e0ed286fcce0cd91ca47f4f326040c` |

身份对照只改变隔离的网卡/eFuse 身份配置，没有修改原版 BIN 或补造网络响应。实际身份值不公开。NVS 与会话配置、原始证据在私有归档保留，公开摘要只给出原始文件哈希、相对时间与协议结果。

## 假设与证据

### 1. 默认身份的立即断开来自云端业务拒绝

[默认身份摘要](evidence/default-baseline-redacted-summary.json)覆盖约 67.983 秒：

- MQTT 实际收到非空配对码回复。
- 20 次 WebSocket 请求均完成有效 HTTP 101 升级，响应 Accept 与该连接请求一致。
- 服务器返回 `mac_not_found` 1 次、`mac_not_bound` 19 次，随后 20 次均由服务器先发 TCP FIN。
- 串口接收错误 20 次；没有文本或控制心跳往返。

两个固定业务错误分别对应 `mac does not exist` 和 `mac has not been bound to a deviceId`。这里传输层已经到达有效 WebSocket 会话，失败发生在云端设备身份处理阶段。先获得配对码并不保证该身份已绑定到云端设备。

既有 8 份会话证据中的 31 次完成握手也呈现相同模式：29 次未绑定、2 次不存在。私下对照表明 WS 查询身份、MQTT 主题身份和会话 eFuse 身份一致；没有发现这三处身份分叉。公开版本不保留身份值。

### 2. 授权身份暴露了独立的控制 PONG 超时

[授权身份摘要](evidence/authorized-identity-redacted-summary.json)覆盖约 153.092 秒：

- 1 次有效握手，实际收到与请求身份匹配的 `deviceConnected`；这里仅报告已观测到设备注册响应。
- 关闭前完成 5 次 guest 文本 `PING` → 服务器文本 `PONG` 往返。
- guest 共发送 4 次 WebSocket 控制 PING（opcode 9），没有收到控制 PONG（opcode 10）。
- 第一次控制 PING 约在捕获开始后 32.068 秒，guest 首次 FIN 约在 153.047 秒，相差约 120.979 秒。
- 串口精确标记 `Error, no PONG received for more than 120 seconds after PING` 出现 1 次。

整个抓包中可数到 6 次文本 PING 和 6 次文本 PONG，但最后一次 PONG 在 guest 首次 FIN 之后到达，因此仅把前 5 次计为关闭前有效往返。不能将原始帧计数写成 6 次存活心跳成功。

这次运行并没有证明长期稳定。它证明授权身份消除了立即业务拒绝，同时发现了另一种约 120 秒控制心跳超时。文本 PONG 和 WebSocket 控制 PONG 是不同消息，不能相互替代。

### 3. 主机独立对照不经过模拟器

[主机诊断摘要](evidence/host-control-ping-redacted-summary.json)来自同一云端服务、同一授权身份的单个主机原生 TCP/WebSocket 连接。发送了 masked 空控制 PING、masked 非空控制 PING 和文本 PING。在配置的 12 秒观察窗口内，收到设备注册响应及 1 次文本 PONG，但没有控制 PONG。

首次对照独立于 guest/QEMU，支持“控制 PONG 缺失并非仅由模拟器路径造成”的判断。它不是物理硬件验证，也没有审计云端服务内部实现。首次主机探针只记录 HTTP 101 状态，没有核验 Accept，因此保留为有限诊断。

[独立的第二次主机运行](evidence/host-control-ping-v2-redacted-summary.json)补做了 Accept 与请求的一致性校验，结果为 true；在同样配置的 12 秒窗口、相同发送语义下，仍只收到 1 次文本 PONG、0 次控制 PONG。第二次结果不覆盖第一次，也不构成长期 guest 或物理硬件通过。

## 观察模块的改动范围

实现独立、有资源上限的抓包观察模块，将 MQTT 配对码获取与 WebREPL 状态分开。它只在完整请求来源与有效握手校验后采信服务器消息，使用真实 TCP 字节重组，支持乱序、相同内容重传、WebSocket 消息分片和控制帧。

公开输出仅包含固定枚举、计数和布尔值。HTTP 101 只能产生“握手已观测”；双向实际 PING/PONG 才能产生“心跳往返已观测”。两种已知 MAC 错误映射为身份拒绝，其他业务错误映射为通用服务器错误。未回复控制 PING 只计数，不在等待刚开始时自动判故障。

资源边界为最多 8 MiB 捕获、64 个方向 TCP 流、每流 64 KiB。缺字节、冲突重传、恶意长度和超限会明确返回不可观察；活动文件末尾的未完成记录被标为 partial。TCP 序列号回绕采用保守的 unavailable 结果，本模块不是通用 TCP 分析器。

24 项单元测试覆盖上述协议与隐私边界。[10 份真实抓包复核](evidence/observer-ten-captures-redacted-summary.json)验证了观察器的分类。它们验证的是观察逻辑；下述持久身份与候选 v2 浏览器运行另行验证服务集成，不能混作同一层证据。

## 持久身份的独立后续执行

[后续执行摘要](evidence/persistent-identity-redacted-summary.json)记录了 3 个真实 guest 的顺序启动，其中包含一次服务重启；三次实际网络身份保持一致，且 WS、MQTT、eFuse 身份逐次匹配。原版固件 SHA 与参考运行一致。此结果证明候选的身份持久化行为，不代表该身份已获云端绑定；三次 WebREPL 仍如实显示未绑定。

在已有 guest 活跃时，两种重复身份创建尝试都返回 409，幂等恢复没有增加活跃数。两次前置观察限制也保留：一次客户端在服务就绪前被拒绝、没有创建 guest；另一次冲突检查到达时前一 guest 已停止，因而发生了正确的顺序复用，随后恢复该会话并补做活跃冲突检查。这些情况不能删除或改写成首次尝试通过。

[Core2 的独立原版固件验证](evidence/core2-persistent-identity-redacted-summary.json)进一步确认实际 MQTT 身份与 eFuse 一致、收到配对码并完成停止/Flash 释放。其原 BIN SHA-256 为 `57868df3d1bb0cbd03fdca3eac0db8a9c6578a70195e4479822147b29ef691ae`，运行时 SHA 与本记录固定值一致。该原版 Core2 固件没有发起 WS，状态为 `not_observed`，不能借用 CoreS3 结果宣称其 WebREPL 已通过。

上述身份修复证据是独立 follow-up；最终源码已进入 main。首次浏览器长窗口运行的客体事实与当时的 UI 验收限制另列如下。

## 首次浏览器候选运行与验收纠正

[首次浏览器复核](evidence/browser-first-review-redacted-summary.json)属于浏览器调用原生 Device Service 的路径，不是浏览器 WASM 或线上 Pages 验收。195 秒窗口中的客体证据有效：实际登记、7 次关闭前文本心跳往返、6 次控制 PING、0 次控制 PONG，且观察到登记后断开与重连。[同会话 ZIP 的独立复算](evidence/browser-first-guest-redacted-summary.json)直接确认串口 120 秒 PONG 超时标记出现 1 次。

但截图中有 `Failed to fetch` 错误提示，运行状态标签与仍运行的 guest 不一致。因此首次 UI 验收为 PARTIAL，不能因网络或 DOM 子项通过而判整体 PASS。独立核对发现 API serial 内容与 ZIP serial.log 完全一致，均含 1 次 `no PONG`。最初使用的正则没有匹配这条实际措辞，因此布尔值漏报；这不是串口字段内容丢失，不能用初始判定否定 ZIP 中真实存在的超时。

初始摘要在保存更正前原字节副本之前被修改，无法提供原始未复核文件的哈希。目前已将[初始已发出的判断](evidence/browser-initial-verdict-reconstructed-summary.json)明确标为从原 stdout 重建，并另附[独立复核纠正记录](evidence/browser-review-correction-summary.json)；原始 guest ZIP、时间线与截图仍独立保留。当前报告不把重建 receipt 标成 raw，也不假造其原文件身份。修正后的浏览器重跑作为独立候选 v2 追加如下，保留当时 UI 验收失败的事实。

## 前端 304 响应问题的独立诊断

[浏览器诊断摘要](evidence/browser-304-diagnostic-redacted-summary.json)记录了一次配置为 30 秒的实际 guest 观察过程：浏览器出现 910 次 fetch 失败、910 次错误状态事件及 1009 次错误横幅事件，而 HTTP 错误响应数为 0，guest 本身仍正常运行。

受控浏览器试验将问题缩小到 COI service worker 对 304 响应的重建：原 worker 使用非空 body 构建不应带 body 的响应时，四种 cache/redirect 组合全部失败；不经过 worker 和使用 null body 适配器的两组对照，各自四种组合都正常得到 304。该前端问题与云端控制 PONG 缺失是不同故障。

这组结果支持响应构造问题的诊断，但不能把合成控制试验记为完整用户路径修复通过。owned worker 适配已完成候选 v2 的真实浏览器复验并进入 main；首次 UI PARTIAL 和短窗口复现 FAIL 保持不变。

## 候选 v2：同路径 UI 复验通过，云端连接故障保留

[独立的第二次 195 秒浏览器运行](evidence/browser-candidate-v2-redacted-summary.json)使用同一原版 BIN 与原生运行时，保持“浏览器 → 原生 Device Service → 原版 guest”的路径。运行中有 5859 次 frame 304 正常返回，API 网络失败、API HTTP 错误、错误横幅和运行状态错误均为 0。截图与运行态一致，真实配对、登记和身份匹配均已观察；因此该候选的 UI/身份验收为 PASS。

[同会话 ZIP 的独立复算](evidence/browser-candidate-v2-guest-redacted-summary.json)仍显示 7 次文本心跳往返、6 次控制 PING、0 次控制 PONG，以及 1 次串口 no-PONG 标记。采样中约 156.07 秒断开、160.08 秒重连。因此持续连接仍为 FAIL，整体仍为 PARTIAL；不能把页面修复说成已修复云端 PONG。

原始 ZIP 的 10 个 manifest 项校验通过，owned guest 停止并释放 Flash、进程回收、浏览器关闭均已完成。停止阶段的 1 次主动取消与运行期间的失败分开统计。首次 195 秒 UI PARTIAL、短窗口 910 次 fetch 失败及其纠正链均另存，未被新 PASS 覆盖。

[13 项真实 Chromium 控制](evidence/coi-final-browser-controls-redacted-summary.json)还验证了原 worker 的负对照、owned worker 的四种条件请求组合，以及既有 Service Worker 注册更新。该组属于 host-only 浏览器控制，不替代 guest 验收。

[主机验证收据](evidence/final-host-validation-summary.json)记录 Python 2217 项（8 项 skip）、50 项文档合同、Node contracts 和四个项目验证器通过。收据中 8 个产品源码哈希已独立与不可变候选提交 `a5990e720a8c79310456bf5868141f4cfd50afe8` 的 Git blob 比对一致。首次全量 Python 检查中的过期 OpenAPI inventory hash 失败保留，修正后重新跑完完整套件。

[源码交付收据](evidence/source-delivery-redacted-summary.json)分别记录候选分支与 main 的成功 CI，均绑定同一提交。[独立视觉复核](evidence/candidate-ui-independent-visual-summary.json)确认保留截图中设备画面、运行状态和云端观测一致；原图与配对码不公开。

## 部署后独立功能复验

[部署后同原版 BIN 的 195 秒运行](evidence/browser-postdelivery-redacted-summary.json)绑定 main 提交、实际源码字节、原生运行时、原 BIN 与规范化执行镜像。34/34 项验收通过，UI/身份为 PASS；取证前 5855 次 frame 304 正常返回，[整会话后检查](evidence/browser-postdelivery-postcheck-redacted-summary.json)计数为 5856。运行期间 API 网络失败、HTTP 错误、错误横幅、运行状态错误和页面脚本错误均为 0。停止后 1 次请求主动取消另行统计。

云端持续连接仍为 FAIL。此次有 2 次有效握手、身份业务拒绝 0 次、7 次关闭前文本心跳往返、6 次控制 PING、控制 PONG 0 次。浏览器采样约 156.08 秒观察到断开、160.08 秒观察到重连。[原 ZIP 独立复算](evidence/browser-postdelivery-guest-redacted-summary.json)确认 1 次 guest 先发 FIN，没有服务器先发 FIN；第一控制 PING 到 FIN 相隔 120.063614 秒，精确串口 120 秒超时标记出现 1 次。浏览器和 PCAP 的相对时间起点不同，不能直接相减。

实际收到配对码，登记身份匹配；两类状态在界面分别展示，远程执行仍标为未验证。证据在停止前获取，ZIP 内 10 个 manifest 项完整性校验通过。已有历史全部保留，新增 owned 历史亦保留；guest 已停止、Flash 及 lease 释放、客体进程回收、浏览器关闭。公开记录只保留功能证据和安全清理布尔值，不包含内部部署配置。

该复验与候选 v2 运行是两份独立证据；两个 UI PASS 都没有改变云端控制 PONG 缺失的结论。Pages 浏览器 WASM 发布验证尚未并入本记录。

## 当前验收状态

| 层级/目标 | 状态 | 依据 |
| --- | --- | --- |
| 同原版固件、同运行时对照 | PASS | 两份参考执行摘要中的一致 SHA-256 |
| guest 网络真实收发 | PASS | MQTT 回复、有效 HTTP 101、WS 帧和 TCP 关闭方向 |
| 默认身份 WebREPL 就绪 | FAIL | 云端业务拒绝与 20 次服务器 FIN |
| 授权身份初始注册、文本往返 | PASS（有界） | 匹配的登记回复；参考运行关闭前 5 次文本往返 |
| 授权身份持续连接稳定性 | FAIL | 参考、候选与部署后执行均有控制 PONG 超时；后两次均断开后重连 |
| 主机控制 PONG 对照 | PARTIAL | 两次独立 12 秒诊断均无控制 PONG；第二次 Accept 校验通过 |
| 观察器与集成状态展示 | PASS（限定范围） | 24 项测试、10 份抓包复核及候选/部署后实际浏览器状态 |
| 持久身份与重复身份准入 | PASS（限定范围） | 3 次 CoreS3 guest 身份一致、2 个活跃冲突 409；Core2 实际 MQTT/eFuse 一致 |
| 候选 v2 同路径 UI/身份 | PASS（限定范围） | 195 秒、5859 次 frame 304、运行期错误 0；持续连接仍 FAIL |
| 前端 304 修复 | PASS（限定范围） | 13 项 Chromium 控制及候选/部署后实际 guest 浏览器路径 |
| 源码 main 与 CI | PASS | 固定提交与对应成功 CI；不是独立功能结果 |
| 部署后同路径 UI/身份复验 | PASS（限定范围） | 195 秒、34/34 检查，运行期错误 0；云端持续连接仍 FAIL |
| Pages 更新 | PENDING | 后续独立发布验收，未借用本地原生服务结果 |
| 远程 REPL、物理硬件、浏览器 WASM | NOT RUN | 未在本组证据中执行 |

历史结果单独保留：首次 195 秒浏览器 UI 为 PARTIAL，短窗口 fetch 复现为 FAIL，第一次主机探针仅核验 HTTP 状态，初始串口超时正则漏检亦保留纠正链。后续 PASS 不覆盖这些记录。已完成执行中的 guest 停止、Flash 释放和浏览器清理均由各自终态或清理证据绑定，不能用取证时仍运行的 ZIP manifest 代替。

## 复现、边界与回滚

见[复现说明](code/README.md)。摘要生成脚本只读取私有证据，不联网、不创建 guest、不更改设备身份；原始字节仍由原始 SHA-256 绑定。公开读者需要自行取得合法固件、自己的授权身份及同路径执行证据才能重做在线对照。

修复已进入 main，部署后功能复验已追加独立证据；Pages 发布仍待后续独立记录，不能覆盖参考失败。本记录只公开功能和源码证据，不包含本机服务配置、部署路径或运维收据。没有发送 Burner 审核结果。

## 协议与源码参考

[RFC 6455 §5.5.2–5.5.3](https://www.rfc-editor.org/rfc/rfc6455#section-5.5.2)规定，未进入关闭流程的连接收到控制 Ping 后应回复携带相同载荷的控制 Pong。文本内容为 `PONG` 的数据消息不替代控制 Pong。

[固定候选源码](https://github.com/m5agent/m5stack-esp-emulator/tree/a5990e720a8c79310456bf5868141f4cfd50afe8)；[观察模块](https://github.com/m5agent/m5stack-esp-emulator/blob/a5990e720a8c79310456bf5868141f4cfd50afe8/platform/tools/uiflow_cloud_status.py)；[持久身份](https://github.com/m5agent/m5stack-esp-emulator/blob/a5990e720a8c79310456bf5868141f4cfd50afe8/platform/tools/device_service_identity.py)；[owned COI worker](https://github.com/m5agent/m5stack-esp-emulator/blob/a5990e720a8c79310456bf5868141f4cfd50afe8/platform/web/public-coi-serviceworker.js)。
