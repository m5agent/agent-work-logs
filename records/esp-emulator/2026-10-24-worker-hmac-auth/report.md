# Worker HMAC authentication 报告

## 背景

普通 Bearer token 能保护整个控制面，但不能证明请求来自一个具体的
worker generation。仅凭 JSON 中声明的 `worker_id/instance_id/generation`
不足以阻止同 token 客户端冒充其他 worker。

本轮增加 worker-specific HMAC，并让 queue lease/generation 校验与签名
identity 绑定。

## 协议

master token 不直接进入 worker 请求签名，而是派生：

```text
worker_key(worker) =
  HMAC-SHA256(master_token,
    "m5-worker-v1:<worker_id>:<instance_id>:<generation>")
```

每个受保护 POST：

```text
canonical =
  version
  method
  path
  unix_timestamp
  nonce
  sha256(body)

signature = hex(HMAC-SHA256(worker_key(worker), canonical))
```

请求携带：

```text
X-M5-Worker-Id
X-M5-Worker-Instance
X-M5-Worker-Generation
X-M5-Worker-Timestamp
X-M5-Worker-Nonce
X-M5-Worker-Signature
```

## 服务端验证

- 只对明确的 worker mutation path 启用；
- Bearer token 仍必须有效；
- 时间戳窗口 90 秒；
- nonce 24-128 lowercase hex，服务端 replay cache 有容量和 TTL 上限；
- body 在 JSON 解析前读取并缓存，签名和 JSON 使用同一字节串；
- 验证出的 identity 必须匹配 path 和 body；
- 队列 lease 继续校验 `lease_id + worker_id + instance_id + generation`。

## 验证

本地：

```text
platform tests                 296/296 PASS
worker auth tests              4/4 PASS
worker agent tests             3/3 PASS
authenticated live executor    1/1 PASS
runtime coverage               PASS
peripheral catalog             PASS
QEMU profiles                  PASS
OpenAPI YAML                   PASS
Ruff / py_compile              PASS
git diff --check               PASS
```

live：

```text
service started with API token
unsigned claim                 401
signed worker registration     201
signed worker heartbeat        200
signed claim                   200
signed job heartbeat           200
real StickS3 session           running
evidence ZIP                   6882 bytes
evidence SHA256                2df3fdc3...
signed job result              completed / PASS
agent exit                     0
```

GitHub Actions `40056937192`：

```text
platform-contracts        success
network-namespace-policy  success
Ran 296 tests
OK (skipped=2)
```

## 验证层级

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | compile 与平台测试 |
| transport | `PASS` | HTTP HMAC headers、body binding 和 real job |
| device_response | `PASS` | 真实 StickS3 QEMU 到达 running |
| data_behavior | `PASS` | unsigned 401、signed claim/heartbeat/result、evidence hash |
| visual_or_physical | `NOT RUN` | 未采集 UI 或物理测量 |
| review/delivery | `PASS` | OpenAPI、文档、CI 与归档 |

## 边界

- 仍是同主机 HTTP；没有 TLS/mTLS、跨主机证书或 credential rotation；
- HMAC 防止未授权 worker mutation，不是恶意固件隔离；
- nonce cache 是进程内状态，服务重启后清空；timestamp window 仍限制重放；
- 外部 side-effect exactly-once 未完成；
- 不是多机 scheduler、companion continuity 或真机验证。

## 风险与回滚

如果未配置 API token，本地兼容模式不要求 HMAC；生产协议要求启用 token。
回滚源码提交
`303e10744f3826763e355ee2c49e7715fe58a254` 会恢复 Bearer-only worker
mutation，不修改 queue、QEMU worktree、firmware 或历史 evidence。
