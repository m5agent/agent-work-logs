# Cross-Subnet NAT Worker Discovery Report

## 背景

当前 authenticated multicast discovery 只覆盖一个 multicast domain。
路由器和云网络通常不会转发 link-local multicast，所以 worker 不能把
“同一广播域内可用”推导为跨子网或 NAT 环境也可用。

本阶段保留 multicast 快路径，同时增加一个可路由的单播 seed 路径：
seed 返回与 control-plane announcer 相同的 HMAC-signed beacon，worker
验证后再使用其中声明的 control URL。seed 是不可信传输，不持有额外信任。

## 实现

### Worker discovery client

- 新增 `fetch_discovery_beacon()`；
- seed URL 仅允许 HTTP(S)，禁止 credentials、query 和 fragment；
- 请求超时为正值且最多 60 秒；
- 响应必须是 `application/json`，最大 4 KiB；
- 禁止 HTTP redirect；
- 校验 Content-Length、响应大小、UTF-8 JSON；
- 复用现有 beacon 字段、schema、group/port、issue/expiry、HMAC 和 clock
  skew 校验；
- 返回值明确标记 `transport=unicast-seed` 和脱敏来源 host。

### Standalone seed service

- 新增 `worker_discovery_seed.py`；
- 每次 HTTP GET 都重新读取 token file，因此 token rotation 后下一次请求
  即使用新 active token；
- 只返回签名 beacon，不含 token；
- 错误路径返回结构化 `503`，但不泄露 token 或文件内容；
- seed 默认路径为 `/worker-discovery/v1/beacon`。

### WorkerAgent

新增：

```text
--discover-control-seed-url
M5_WORKER_DISCOVERY_SEED_URL
```

它与 `--service-url`、`--discover-control` 互斥。HTTPS seed 可使用现有
`--ca-file` / credential generation 的 CA trust。发现后仍由 Bearer/HMAC
访问 control plane，TLS/mTLS 仍是单独的 transport identity 边界。

## 拓扑

```text
worker namespace             router namespace             control namespace
10.213.2.10/24   <->   10.213.2.1 / 10.213.1.1   <->   10.213.1.10/24
                         IPv4 forwarding + NAT
```

control namespace 同时运行：

- Device Service 和真实 Worker directory；
- active-token multicast announcer；
- unicast discovery seed。

worker namespace 中的 `WorkerAgent` 只获得 seed URL，不获得 control URL。

## 执行

每个独立 attempt：

1. 创建三个独立 network namespace 和两组 veth；
2. 配置两个不同 subnet、default routes、router IPv4 forwarding；
3. 在 router 安装 nftables masquerade；
4. 启动 Device Service；announcer 继续发送 multicast；
5. 启动 unicast seed service；
6. 尝试 multicast discovery，确认不跨 router 且 worker 不注册；
7. 使用 seed 发现 control URL，worker 注册、heartbeat、停止；
8. 随机错误 token 经 seed 获取 beacon，但签名验证失败且不注册；
9. SIGHUP rotation 到新 token；
10. 新 token worker 经同一 seed 注册；
11. 旧 token worker 被拒绝；
12. control-side seed access log 验证源地址为 router；
13. 停止 process、删除 namespaces，确认 nftables 和 worker lease cleanup。

runner 在首次运行前计算并记录：

- `run_test.py`
- `worker_agent.py`
- `worker_discovery.py`
- `worker_discovery_seed.py`
- `serve.py`

SHA256 在运行结束后复算，任一漂移都使 attempt FAIL。

## 证据

三个独立运行均为 `PASS`：

- cases：`3/3`；
- checks：`23/23`；
- control observed source：每轮只有 `10.213.1.1`，证明 masquerade；
- seed bootstrap worker：`returncode=0`、`state=stopped`；
- rotated worker：`returncode=0`、`state=stopped`；
- multicast/wrong-token/old-token worker：非零退出、无注册；
- namespaces：空；
- nftables：无测试 table；
- control/seed process：已退出；
- token：每个 attempt 均未出现在 beacon 或 captured log；
- tool hashes：运行前后无漂移。

平台级验证：

```text
platform unittest        442/442 PASS
docs consistency         29/29 PASS
Node SHA256/upload       2/2 PASS
runtime coverage         PASS
peripheral catalog       PASS
QEMU profiles            PASS
project snapshot         PASS
Ruff fatal checks        PASS
compileall               PASS
OpenAPI / CI YAML        PASS
git diff check           PASS
GitHub Actions           PASS
```

CI：
<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40159761453>

最初一次 CI artifact step 因尝试递归上传 root-only worker work directory
而 EACCES；功能步骤本身已经 PASS。随后将 artifact path 收窄到唯一脱敏
`evidence.json`，新提交 `667c356` 的两个 CI job 均 PASS。

## 验证边界

- 这是同一 Docker daemon 中的三个 Linux namespace，不是物理跨主机；
- 证明一个 reachable seed 可以跨路由和 masquerade，不证明不存在 seed 时的
  NAT hole punching 或任意网络 traversal；
- 未创建 QEMU session，未证明 cross-host executor、reattach 或 companion；
- 未验证生产 scheduler、quota、object storage、secret manager 和 audit；
- seed HMAC 只证明 beacon 内容真实性，不证明 confidentiality；
- 物理硬件、RF 和电气行为 `NOT RUN`。

## 风险与回滚

- seed 是无认证读取端点，只能公开已签名 metadata；不得返回 token、凭据或
  control-plane state；
- production seed 应置于 HTTPS 或受信私有网络；
- HMAC token rotation 与 seed/control 的原子发布仍需运维协调；
- redirect disabled，响应大小和 timeout 有界；
- 完整回滚使用 revert `d879103` 与 CI-only `667c356`，恢复显式 control URL
  或多播单一路径，不影响已有 worker API。
