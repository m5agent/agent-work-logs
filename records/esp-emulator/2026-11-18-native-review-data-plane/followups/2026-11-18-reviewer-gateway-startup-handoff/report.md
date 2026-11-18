# 来宾启动前后的网关交接边界

此前验证的网关恢复覆盖已启动的来宾。本轮将故障推到同原版 CardputerDict 保存快照审查的启动阶段。隔离 ARM64 Linux VM 没有外部网卡，具名网关连接的内部合成对端仅响应 SNTP 并读取 TLS ClientHello。保留无关的独立网关作为资源归属对照。

## 旧版与初版修订

| 固定设备服务与中断位置 | 实际结果 |
| --- | --- |
| 1.98.0，创建内层进程前终止外层 | 样本中没有来宾 QEMU，旧命名空间、两端 veth、NAT 表、可写 Flash 和一个租约仍在。 |
| 1.98.0，内层进程已存在但未写入启动回执 | 观察到外层退出后约 0.240 秒仍启动了属于原会话的 QEMU。后续资源回收完成，启动交接保护失败。 |
| 初版候选 `124774ec…`，内层 fork 后、启动交接提交前 | 未观察到 QEMU 迟到启动。旧资源在 61.310 秒后才自动回收。正常同原版 Retry 随后可用。 |
| 初版候选，创建内层进程前的 32 秒观察尝试 | 结束时仍未到 60 秒的 QMP 等待期限。该样本记录为不充分，用于保留时间线。 |

[旧版无来宾资源滞留](evidence/incumbent-pre-spawn-a1.verified.summary.json) · [旧版迟到来宾](evidence/incumbent-inner-before-receipt-a1.verified.summary.json) · [初版交接回执](evidence/candidate-post-fork-pre-commit-a1.verified.summary.json) · [32 秒尝试](evidence/candidate-pre-spawn-a1.bounded-window.summary.json)

## 最终候选

版本 3 启动记录使用每次启动独立的继承锁，内层进程必须完成启动提交后才能启动客体。外层在初始 QMP 等待期间退出时，设备服务随即让该启动事务结束。回收前核对原授权记录、锁已释放、内核资源与租约的匹配条件。缺少可核对的归属或记录冲突时，服务保留旧会话等待后续确认。

最终源提交 `a729e24b1e4724b783ab2d59eec689cfdfeb24b3`，OpenAPI 版本 1.99.0、SHA-256 `82758d20ff3d129ec57e2e1587bf699d683f44525f8dfa8befc05b433ed74325`。内层创建前中断的终态在 2.436 秒观测到，原会话从未启动 QEMU，旧网关、Flash 和租约释放，独立网关保留。普通保存快照 Retry 返回 HTTP 202，新同原版会话的传输通过，随后 Flash 释放且租约为零。[最终候选内层创建前回执](evidence/final-pre-spawn-a1.verified.summary.json)

已创建内层但尚未提交交接的对照，在外层退出后特意让同一个内层进程保持暂停约 2.7 秒。内核观察确认两者使用同一启动锁，交接管道的读端传给内层，写端仍由外层持有。内层暂停并持锁期间保留目标资源和租约；恢复内层后读取到未提交的交接，退出且未启动原会话的 QEMU。5.186 秒观测到网关、Flash 和租约清理。该时间包含人为暂停的时段。

两组标准 Retry 都返回 HTTP 202，实际创建新的同原版会话。合成对端证实来宾发出 SNTP 和 TLS ClientHello，两组均保留中断会话和重试会话的证据，随后释放新租约和 Flash，独立网关未受影响。综合发音审核仍为 `manual_review / E_CARDPUTER_PRONUNCIATION_PARTIAL`。Device Service 最终平台测试共 2,482 项，2,472 项通过、10 项跳过，验证器通过。[最终双场景回执](evidence/linux-named-gateway-handoff-release.summary.json)

另做一次交接已提交、尚未写入启动许可的对照。外层退出时，原内层暂停并持锁。恢复后原 QEMU 仍未启动，5.204 秒确认目标网关、Flash 和租约均释放，包含约 2.7 秒的刻意暂停。旧会话 ZIP 及原版身份通过核对，独立网关继续保持。此补充场景未另行执行 Retry。[提交后、许可前回执](evidence/final-post-commit-pre-permit-a1.verified.summary.json)

## 复现与限制

1. 使用冻结服务、Linux 运行时、原版卡片和存储种子。用隔离网关与只在本地运行的合成对端执行正常保存快照 Retry。
2. 单独构造内层创建前、已创建未提交两种中断边界。在故障前核对实际运行时和会话归属，终止仅属于实验的外层监督进程。在未提交分支，仍观察原内层进程被重新调度后的行为。保存中断后原租约、网关、实际 QEMU 存在性和证据清单。
3. 核对独立网关存续和目标网络资源回收，发起标准同原版 Retry 验证新会话。结束所属服务和 VM。合成对端只用于 SNTP 和 TLS ClientHello 流量观察，证书、真实公网和发音验收未执行。两种中断的内核网关资源均已完成配置，配置尚未完成时的故障另行验收。未提交 Burner。
