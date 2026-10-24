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

平台测试 `305/305`，Node `2/2`，GitHub Actions CI
`40070863490` 两个 job 成功。

## 验证边界

- 真实进程是同一主机 loopback，不是跨主机网络；
- 临时 PKI 只验证协议与配置，不代表生产 CA 生命周期；
- TLS 证书在进程启动时加载，热轮换未实现；
- worker token/generation 凭据热轮换未实现；
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
跨主机网络、证书/worker 凭据热轮换、生产 CA 生命周期、多主机调度、
companion continuity 和真机仍未验证。
