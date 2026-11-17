# 保存快照审核的本地 STA 应用断言

早期审核只能依据捕获确认 STA 传输存在。同一 Cardputer ADV 固件在基线确实查询 DNS、收到 HTTP 200 并接受 UDP 响应，但报告只有被动传输 `OBSERVED`，没有应用层判据。本次给保存快照的 `validation.native_sta_operation` 增加显式应用断言。Reviewer 结合停机后的同会话串口、PCAP、受控夹具回执和实际固件摘要核对来宾结果。已定型的产品检查要求板级能力声明和隔离准入满足条件，再分配网络租约。

## 八次保存快照回放

Device Service 执行版本为 `9bbbcba8477039c8e35cf85b002c6b63a83cae86`。固定 Linux QEMU SHA256 为 `1733f511c4528cbd991e673069ecedf261b7043e8302553e050924089ce09bff`。运行使用独立容器，外层无网络、无宿主端口映射。正向使用保存快照重试，以已知固件核对 DNS A 和 NXDOMAIN、HTTP 200、二进制 UDP 往返以及正确响应后打印的完整串口行。保留 `purge=0` 停机证据并释放 Flash。 [固件代码、应用判据和可追溯运行边界](https://github.com/m5agent/m5stack-esp-emulator/tree/541871f6fb6f48a4bda9b8846a9fb3054074f207/tests/network/native_sta_peers)

| 保存快照用例 | 执行版本 | 应用层结果 |
| --- | --- | --- |
| Cardputer ADV 基线 | `ef813f5a` | 已观察到传输与按预期接受的来宾记录，旧 Reviewer 无应用断言 |
| Cardputer、Cardputer ADV、Core2 固定应用数据 | `f1805ec5` | 三板 `PASS`，来宾记录 `STA_FIXTURE_RESULT PASS` |
| Cardputer ADV 单字节错误响应 | `f1805ec5` | `FAIL`，捕获仍有双向数据，来宾记录 `STA_FIXTURE_RESULT NO_FIXTURE` |
| Cardputer ADV 缺少网络命名空间能力 | `f1805ec5` | `PARTIAL`，阶段为 `admission`。实际服务返回 HTTP 503 `network_isolation_unavailable`，网络租约分配数为零 |
| Cardputer ADV 固定响应与单字节错误响应复跑 | `ae60ffd0` | 分别为 `PASS` 和 `FAIL`，两次独立停机回读与 Reviewer 归档的来宾串口及 PCAP 字节一致 |

Core2 保存快照保留了测试用的历史网络计划。实际启动仍使用明确请求的固定隔离夹具，停机 ZIP 回读证实了实际策略。顶层传入 `network` 覆盖被 Reviewer 以 HTTP 409 拒绝。初次 Core2 回放已产出终态报告和 ZIP，取证脚本误从执行计划中查找网络对象而退出。后续从该同会话终态 ZIP 清单及独立日志核对实际策略与结论。 [八个执行身份及归档校验值](evidence/native-sta-saved-snapshot-summary.redacted.json)

## 发布与验证边界

Reviewer 主分支 `8e27a74412310b224b2e1395fd5760c3eeb274c4` 在执行过的 `ae60ffd00ba6aac36b8a89bc6b22f19934b2979d` 基础上增加文档、API 合约说明及测试。Reviewer 测试 220 项通过。模拟器文档和有界证据主分支 `541871f6fb6f48a4bda9b8846a9fb3054074f207` 的 51 项文档检查、生成校验及差异范围检查通过。远程 CI 在归档时等待完成。 [主分支有界结果](https://github.com/m5agent/m5stack-esp-emulator/blob/541871f6fb6f48a4bda9b8846a9fb3054074f207/tests/network/native_sta_peers/saved-sta-operation-summary.json)

具备网络执行条件的七次回放保留大范围网络 `PARTIAL` 与被动传输 `OBSERVED`。无画面固件的整单均为 `manual_review / E_NO_FRAME`。测试结束后活动租约为零。公网、任意应用协议、实机与 RF、浏览器 WASM、常驻部署和 Burner 提交均为 `NOT RUN`。一般任务继续使用现有审核路径，仅在保存快照显式提交该断言时启用固定夹具。
