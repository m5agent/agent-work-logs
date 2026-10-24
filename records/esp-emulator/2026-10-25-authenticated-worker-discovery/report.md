# ESP Emulator Authenticated Worker Discovery Report

## 背景

Remote worker 已具备注册目录、durable job queue、HTTPS/mTLS、worker HMAC、
token rotation、control/runtime plane split、worker-local QEMU 和
`--advertise-endpoint`，但 worker bootstrap 仍需人工提供 control URL。
`NET-04` / `SVC-01` 的下一项是自动发现，同时不能引入无认证 mDNS 或把 token
写进广播包。

## 设计

新增 IPv4 multicast discovery v1：

- Device Service 默认向 `239.255.77.77:8788` 周期广播；
- beacon 包含 service URL、group、port、issued/expires time 和 nonce；
- HMAC-SHA256 使用当前 active master token；
- worker 必须提供匹配 token，验证 HMAC、TTL、group/port 和 URL 后才使用；
- URL 禁止 credentials、query 和 fragment；
- packet 最大 4 KiB，TTL 最长 300 秒；
- beacon 不携带 token；
- announcer 从当前 Handler token 取值，因此只在 SIGHUP reload 成功后切换；
- worker 仍通过 Bearer/HMAC 执行后续请求，HTTPS/mTLS 仍独立验证 transport。

服务端 CLI：

```text
--worker-discovery-advertise-url
--worker-discovery-group
--worker-discovery-port
--worker-discovery-interval
--worker-discovery-ttl
```

Worker CLI：

```text
--discover-control
--discover-control-group
--discover-control-port
--discover-control-timeout
```

发现功能强制要求 active API token。未配置 token 或未显式 advertise URL 时
不会启动 beacon。

## 执行

本轮真实 fixture：

1. 启动带 token file 和 discovery advertise URL 的 Device Service；
2. announcer 周期发送 signed beacon；
3. 第一个 WorkerAgent 只给 token 和 multicast group/port，不给 service URL；
4. worker 自动发现、注册、heartbeat、无 job、停止；
5. 随机错误 token worker 发现失败且不注册；
6. token file 切到 B、服务 SIGHUP reload；
7. B worker 自动发现并注册；
8. A 旧 token worker 发现失败且不注册；
9. 查询 worker directory 和 sessions；
10. 停止 service，清理 token files。

结果：

```text
worker discovered control URL       PASS
worker registered/stopped           PASS
wrong token rejected/not registered PASS
rotation SIGHUP                     PASS
rotated worker discovered/registered PASS
old token rejected/not registered   PASS
token absent from service log       PASS
token absent from worker log        PASS
no device session created           PASS
```

Fixture 使用 17 个 checks，全部 PASS。GitHub Actions
`network-namespace-policy` 也执行了同一真实 discovery/rotation runner。

## 验证

```text
platform tests              391/391 PASS
documentation contracts     20/20 PASS
worker discovery unit       4/4 PASS
Node SHA256/upload          2/2 PASS
runtime coverage            PASS
peripheral catalog          PASS
QEMU profiles               PASS
project snapshot            PASS
Ruff fatal checks           PASS
compileall / diff check     PASS
GitHub Actions              PASS
```

CI：`40140611924`。

## 边界

- IPv4 multicast 只在同一 multicast domain 内工作；
- 不证明 NAT 或跨子网转发；
- 不创建 QEMU session，不替代 worker-local QEMU executor；
- 不证明跨主机进程 reattach、companion/BLE continuity 或生产 scheduler；
- HMAC 解决 beacon authenticity，不替代 HTTPS 证书校验；
- 物理硬件不适用/未验证。

## 风险与回滚

主要风险是发现域过宽或 token 泄漏。Beacon 不含 token；错误/旧 token 已拒绝；
服务只在配置 advertise URL 且存在 active token 时启用。Rollback
`658b2d494bbd40fcb798ed4349a6304d46c0d917` 到
`351eb16d49f1ffbef562810668f3248e1cfc7f52` 会恢复显式 control URL bootstrap，
不影响现有 worker API 或凭据。
