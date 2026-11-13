# 身份能力协商与实际收据校验跟进

- 日期：2026-11-14（UTC+08:00）。
- 工作类型：代码修复、兼容性验证、virtual-device validation。
- 追加目标：既有 `records/esp-emulator/2026-11-14-uiflow-cloud-websocket` 记录；原有运行与失败证据保持不变。
- 当前结果：PARTIAL。旧服务兼容保护和指定身份的真实用户路径已通过；默认持久身份分支也已通过实际 UI 与身份验证；云端控制 PONG 缺失仍为 FAIL。
- 执行源码：`3a4408e4a1f26c0c8ad3ff07dae1ac8149a50384`，base `a5990e720a8c79310456bf5868141f4cfd50afe8`。主机验证候选 `014841a8fe082cf8aaaa57de898e0ac0f665aedf` 的完整平台检查 2235 项、跳过 8 项通过，分支 CI 两项 job 通过；当前候选 `70ef503fc2fb8b2c787fa9065e2952f525c40099` 仅追加文档与回归证据，已核对实现、fixture 和 producer 未变；该提交已快进合入 main，同提交分支 CI 两项 job 通过；main CI 的后续独立读回已确认两项 job 通过。最终源码的195秒用户路径已完成30/30验收，Pages仍由独立验收记录约束。

新版客户端仅在设备目录明确广告身份能力时提供指定身份和持久身份语义，并校验创建响应中的实际身份。连接真实旧版服务时，MAC 和持久 key 请求均在 POST 前被拒绝，没有创建 guest。

同一原版 CoreS3 固件的指定身份分支跨过 195 秒握手后观察窗口，36/36 项验收通过。运行阶段有 5847 次真实 frame 304，HTTP、网络、界面与脚本错误均为 0。实际 POST、eFuse 和 WebSocket 身份匹配，配对码收到且云端登记成功。仍观测到 7 次有效文本心跳、6 次控制 PING、0 次控制 PONG，以及一次 120 秒超时和重连；这不构成持续连接或远程 REPL 执行通过。

默认 key 的独立 45 秒运行有 27/27 项通过、1176 次 frame 304、运行期 HTTP/网络错误 0。实际 key 收据、eFuse、网卡和 WebSocket 身份一致，页面收到配对码但明确显示尚未绑定；不把未绑定状态包装成云连接通过。先前浏览器观测失败与后续 16 项主机对照均保留。

[最终 main CI](evidence/main-ci-completed-summary.json)、[主分支交付与 CI](evidence/main-integration-summary.json)、[最终候选主机检查](evidence/integration-full-platform-summary.json)、[分支 CI](evidence/integration-branch-ci-summary.json)、[默认身份用户路径](evidence/capability-default-browser-redacted-summary.json)、[默认分支同 ZIP 复算](evidence/capability-default-guest-redacted-summary.json)、[完整跟进报告](report.md)、[结构化记录](run.json)、[旧服务负控](evidence/capability-legacy-http-redacted-summary.json)、[最终指定身份用户路径](evidence/capability-authorized-browser-redacted-summary.json)、[同 ZIP 独立复算](evidence/capability-authorized-guest-redacted-summary.json)、[失败历史](evidence/capability-harness-failure-history-summary.json)、[复现说明](code/README.md)。

物理硬件和远程代码执行 NOT RUN；原始 BIN、ZIP、截图、串口、唯一身份及认证资料不公开。没有提交 Burner。

最终源码独立复验：同一原版 BIN、原生 runtime 和固定站点再次完成握手后195秒窗口。
30/30项验收、5870次真实frame304、运行HTTP/网络/UI错误0；配对码与云登记通过。
仍有7次文本心跳、6次控制PING、0次控制PONG、一次超时和重连，所以总体保持PARTIAL。
[最终源码功能摘要](evidence/final-main-cloud-functional-summary.json) 与
[UI时序独立复核](evidence/final-main-cloud-ui-independent-summary.json) 保留这次新执行，
不覆盖旧33文件及此前失败。

[最终协议独立审计](evidence/final-main-cloud-protocol-independent-summary.json)明确保留
“ZIP无Flash读回”和“raw NIC argv未留存”的证据边界，不把live helper布尔结论冒充离线重算。
