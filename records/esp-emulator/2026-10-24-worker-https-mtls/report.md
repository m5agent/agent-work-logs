# ESP Emulator Worker HTTPS/mTLS Transport 报告

## 背景

现有 worker 已有 Bearer token、worker/generation 派生 HMAC、timestamp、
nonce replay cache 和 path/body identity binding，但控制面仍通过明文 HTTP
传输。`NET-04` / `SVC-01` 要求补齐跨主机 worker 的安全传输基础。

目标：

- Device Service 可用 PEM 证书和私钥启动 HTTPS；
- 可配置 client CA 并强制 mTLS；
- worker client 校验服务端证书，支持私有 CA 和客户端证书；
- 明文 HTTP 不得因为提供 TLS 参数而静默回退；
- 不降低已有 Bearer/HMAC 身份认证。

## 实现

- 新增 `platform/tools/transport_security.py`：
  - server/client TLS 1.2+ context；
  - server certificate chain/private key 加载；
  - optional client CA，设置 `CERT_REQUIRED`；
  - client 自定义 CA 和 mTLS 证书/私钥；
  - client certificate/key 必须成对提供。
- `serve.py` 新增 `--tls-cert`、`--tls-key`、`--tls-client-ca` 及对应
  `M5_SERVICE_TLS_*` 环境变量；
- `worker_agent.py` 新增 `--ca-file`、`--client-cert`、`--client-key`
  及对应 `M5_WORKER_TLS_*` 环境变量；
- HTTPS URL 使用正常 hostname 验证；TLS 参数用于 HTTP URL 时直接拒绝；
- TLS 建连、证书和断开错误统一转为 `WorkerAgentError`；
- 新增真实 HTTPS/mTLS 集成测试和可复现 run/test fixture。

## 执行

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'

python3 tests/network/worker_tls/run_test.py
```

真实进程 fixture：

1. 生成临时 CA、server cert 和 client cert；
2. 启动带 API token、server cert 与 client CA 的 Device Service；
3. 用验证服务端证书的 client 建立 TLS 1.3；
4. 无可信客户端证书的连接预期失败；
5. 带可信客户端证书的 worker client 通过；
6. 保持 Bearer + worker HMAC，unsigned claim 预期 `401`；
7. 运行 `worker_agent.py --once`，完成签名 worker 生命周期；
8. 向 TLS 端口发送明文 HTTP，预期失败。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | compileall、定向 syntax Ruff、CLI help |
| transport | `PASS` | 真实 loopback HTTPS，TLS 1.3 |
| authentication | `PASS` | 服务端证书验证、mTLS、Bearer + HMAC、unsigned `401` |
| worker lifecycle | `PASS` | 签名 register/heartbeat/claim/stop，agent exit 0 |
| data_plane | `NOT RUN` | 本轮未执行真实 QEMU job over mTLS |
| visual_or_physical | `NOT RUN` | 与本传输改动无关 |

初始传输里程碑的平台测试 `305/305`，Node `2/2`，GitHub Actions CI
`40070863490` 两个 job 成功。

## 验证边界

- 真实进程是同一主机 loopback，不是跨主机网络；
- 临时 PKI 只验证协议与配置，不代表生产 CA 生命周期；
- 在本记录最初 commit 中，TLS 证书和 worker token 只支持进程启动时加载；
  后续 rotation follow-up 已补 `SIGHUP` 文件重载；
- 本轮没有执行真实 QEMU job over mTLS；
- 不包含 RF、硬件或设备功能验证。

## 风险与回滚

未使用生产证书、真实凭据或外部服务，也没有执行硬件写操作。回滚可 revert
`ea6e4cb37460f6ce20fc2f18f03224c8724ae0cd`。回滚后恢复明文 HTTP/Bearer +
HMAC 的旧能力；不得把回滚状态用于跨主机不可信网络。

## Follow-up：真实 QEMU job over mTLS

源码版本：
`m5agent/m5stack-esp-emulator @ 865e4f810263f3f388beeee3aa577de27f99d0b1`。

该 follow-up 不再停在无 job 的 worker 生命周期：

1. 将 cached StickS3 源镜像补齐为完整 8 MiB flash；
2. 通过 mTLS 上传 artifact；
3. 通过 mTLS 调用 firmware compose；
4. 提交 capability-constrained durable job；
5. 带客户端证书和 worker/generation HMAC 的 agent claim job；
6. 启动真实 StickS3 QEMU session；
7. 下载 evidence ZIP，要求包含 manifest 和 serial；
8. 本地重新计算 evidence SHA256，并与 job result 对照；
9. 提交 `completed / PASS / attempts=1`，agent 退出码 0。

结果：

- TLS 1.3；
- firmware SHA256：
  `a5d027f6d2953edb9ece45cddea1490112d8e421ba563edc6e7c71cf7ac4f6ec`；
- evidence bytes：`6852`；
- evidence SHA256：
  `84cc4339184794536d36276e05be13d4e271274f6b8f5444bdd4831010f16065`；
- job terminal status：`completed`；
- result：`PASS`；
- attempts：`1`；
- platform tests：`305/305 PASS`；
- CI run `40071518376`：两个 job 均成功。

该 QEMU job 使用 `runtime=qemu`，没有声明 unified board/network/UI PASS。
在该 follow-up commit 上，跨主机网络、凭据 rotation、生产 CA 生命周期、
多主机调度、companion continuity 和真机仍未验证；rotation 由后续 follow-up
闭合，跨主机和零中断仍未覆盖。

## Follow-up：unified StickS3 job over mTLS

源码版本：
`m5agent/m5stack-esp-emulator @ 48ff20c416221e20f76873c07d7473329318eb5c`。

该门禁通过 mTLS 上传 unified StickS3 flash，创建
`qemu-unified/profile=uiflow2-sticks3-unified` durable job。带客户端证书
和 worker HMAC 的 agent 完成 claim、真实 QEMU unified session、evidence
下载和 terminal result。

从同一个 evidence ZIP 独立验证：

- `UNIFIED_STICKS3_BOOT/MAIN/READY`；
- WiFi connected、HTTP PASS；
- BLE ready、RX、ACK；
- network evidence `PASS` 且全部 checks 为 true；
- pcap `9570` bytes；
- PNG frame `2885` bytes；
- evidence ZIP `42949` bytes；
- evidence SHA256
  `87fb8d04f630833cbebcc2d0842a8dabe94b02a4f20c6c60a106341496a4f423`；
- job `completed / PASS / attempts=1`；
- firmware SHA256
  `43429d475fea7ce8dfd24fe34c373e8cd0cb9196b1f64a1f60f42957547580c9`。

平台测试 `305/305 PASS`，CI run `40071841654` 两个 job 成功。

该结果证明 retained unified StickS3 路径可与 mTLS worker 控制面组合；在该
commit 上不证明任意固件、跨主机拓扑、凭据 rotation、多主机 continuity 或
真机。凭据 rotation 由下一节 follow-up 闭合。

## Follow-up：TLS/token rotation 与轮换后真实 job

源码版本：
`m5agent/m5stack-esp-emulator @ b01e95b22c163c270d1ef632c1abb75cbdd4c527`。

该 follow-up 增加 token 文件、服务端动态 TLS context、worker 凭据快照和
`SIGHUP` reload：

- `serve.py` 为每个新 accept 的 socket 使用当前 TLS context；已有握手连接
  不被主动迁移；
- 服务端先加载并校验 token、server cert、client CA，再原子替换 live token
  与 verifier；
- worker 在每次请求前对 token 和 TLS context 做一致快照，避免并发 reload
  产生 token/signature 混代；
- token 文件限制为 UTF-8、1–4096 bytes、非空且无 NUL；
- token 与 `--api-token`/`--token` 的 CLI 参数互斥；
- 配置加载失败保留上一份安全配置。

真实进程执行顺序：

1. 用 A PKI 和 token A 启动服务端、worker；
2. 等 worker 完成注册；
3. `SIGSTOP` worker，原子替换为 B PKI/token；
4. 向服务和 worker 发送 `SIGHUP`，随后恢复 worker；
5. 用旧 CA 的身份发起 TLS health，握手失败；
6. 用新 CA 的身份发起 TLS health，得到 200；
7. 用新 TLS 身份携旧 token 和已注册 worker identity 生成合法 HMAC claim，
   服务端返回 401；
8. worker 记录 `worker credentials reloaded`，用新凭据继续 claim；
9. 上传完整 8 MiB StickS3 flash、compose、提交真实 `runtime=qemu` job；
10. 下载 evidence ZIP，独立核对 SHA256，job 终态 `completed/PASS`。

结果：

- 9 项 rotation checks 全部 `PASS`；
- firmware SHA256：
  `a5d027f6d2953edb9ece45cddea1490112d8e421ba563edc6e7c71cf7ac4f6ec`；
- evidence bytes / SHA256：`6853` /
  `51899986348661abefb82d042ea85f3007e54e33f2c366bd218573b2450761e8`；
- job：`completed / PASS / attempts=1`；
- 平台测试：`306/306 PASS`；
- Node：`2/2 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、compileall 和定向 Ruff
  均 `PASS`；
- GitHub Actions CI run `40072474174`：`platform-contracts` 与
  `network-namespace-policy` 均成功。

边界：

- 同主机 loopback，不是跨主机网络；
- 新 TLS context 只影响后续握手，已有 TLS 会话保留协商状态；
- 新 token 影响后续受保护请求，包括已有 keep-alive 连接；
- 在该 commit 上不证明轮换期间的 active-request draining；该缺口由下一节
  follow-up 闭合；
- 不包含生产 CA/secret-manager 生命周期、多主机 continuity、RF 或真机。

回滚：revert
`b01e95b22c163c270d1ef632c1abb75cbdd4c527`。回滚后恢复启动时加载
证书/token；不得把回滚状态用于需要凭据轮换的部署。

## Follow-up：活动请求 drain 后轮换

源码版本：
`m5agent/m5stack-esp-emulator @ e1c18f6eb46fc172f5e2048f5b233cb5ca596765`。

该 follow-up 在 `ServiceHTTPServer` 增加请求门禁：

- 每个请求进入和结束都更新 active count；
- `SIGHUP` 先进入 draining 状态，阻止新的 handler 进入；
- 已进入处理器的请求继续使用旧 token/TLS 完成；
- active count 清零后才执行配置加载与 token/TLS 提交；
- drain 默认等待 30 秒，可通过
  `--security-reload-drain-timeout` 或
  `M5_SECURITY_RELOAD_DRAIN_TIMEOUT` 调整；
- 超时或配置加载失败时不提交新配置，并立即恢复请求接纳；
- reload 期间新连接保留在 listener/backlog，不声明旧/新凭据重叠窗口。

真实进程验证：

1. 用旧 token 建立 `/api/v1/artifacts` 上传，只发送部分 body；
2. 原子替换 A/B PKI 与 token，向服务和 worker 发送 `SIGHUP`；
3. 服务输出 `security configuration drain started`，在上传未完成前不
   输出 reload 完成；
4. 发送剩余 body，旧 token 请求返回 `201`；
5. 服务随后 reload，旧 TLS 身份/旧 token 拒绝；
6. worker 用新凭据继续 claim，并完成真实 StickS3 QEMU job。

额外平台单元测试覆盖：

- active request 未完成时 reload callback 不执行；
- request 完成后 reload 执行，响应保持 200；
- drain 超时后 callback 不执行，旧配置保留并恢复接纳。

结果：

- activity-drain checks：`10/10 PASS`；
- firmware SHA256：
  `a5d027f6d2953edb9ece45cddea1490112d8e421ba563edc6e7c71cf7ac4f6ec`；
- evidence bytes / SHA256：`6850` /
  `c67f44265ecad925c8bd2069041fd4cfa65f9a3ac4dab2f1f03f2cb4403a1c0a`；
- job：`completed / PASS / attempts=1`；
- 平台测试：`308/308 PASS`；
- Node：`2/2 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、compileall 和定向 Ruff
  均 `PASS`；
- GitHub Actions CI run `40072991528`：`platform-contracts` 与
  `network-namespace-policy` 均成功。

边界：

- 同主机 loopback，不是跨主机网络；
- 新请求在 drain 窗口内等待，不保证无限 backlog 或大规模并发下无重试；
- 不提供旧/新 token 同时有效、双 CA 信任或客户端批量迁移；
- 不包含生产 CA/secret-manager 生命周期、多主机 continuity、RF 或真机。

回滚：revert
`e1c18f6eb46fc172f5e2048f5b233cb5ca596765`。回滚后 `SIGHUP` 仍会立即
切换配置，但不会等待活动请求完成。
