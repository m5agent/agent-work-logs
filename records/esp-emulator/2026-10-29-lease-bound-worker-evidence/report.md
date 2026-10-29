# ESP Emulator lease-bound worker evidence 报告

## 背景

`NET-04` 已具备 durable claim、worker HMAC、lease fencing 和同机 restart
恢复，但 WorkerAgent 仍只把 evidence ZIP 留在 worker 本地，result 只记录
SHA256。control plane 因而无法确认 evidence 内容实际存在，也无法在 worker
离线后读取同一次运行的证据。

## 实现

Device Service API/OpenAPI 升至 `1.50.0`。

1. `POST /api/v1/evidence` 接收 authenticated worker 的 `application/zip`；
2. `X-M5-Job-Id`、`X-M5-Lease-Id`、`X-M5-Evidence-SHA256` 与 worker HMAC
   联合绑定 request；
3. evidence ID 由 job、lease、worker instance/generation 派生，内容以 ZIP
   SHA256 寻址；
4. 相同 lease/bytes 重试是幂等 replay；不同 bytes 返回
   `409 evidence_conflict`；
5. metadata/content 使用原子 `0600` 文件，默认保留 90 天，并进入
   `/storage` 与 `/storage/prune`；
6. WorkerAgent 在 result 前上传 evidence；terminal result 同时记录
   `evidence_id` 与 `evidence_sha256`；
7. 服务端只在 evidence 与该 live job/lease/generation 及 hash 一致时接受
   new pair。仅上报旧 SHA256 的 legacy caller 保持兼容，但不会获得中央
   evidence persistence 保证。

## 兼容性

claim、heartbeat、cancel 和旧 result 字段未改变。`evidence_id` 是可选扩展；
没有 central record 的旧 caller 仍可只上报 SHA256。没有 API token 的部署
不能上传 evidence，并返回 503。

## 失败控制与真实执行

真实 HTTP fixture 启动 Device Service 和 WorkerAgent：

- 第一次 evidence upload 已被服务端保存，但客户端响应被注入丢失；
- WorkerAgent 重注册并复用同一 bytes/SHA256；
- 服务端返回原 evidence ID，`idempotent_replay=true`；
- control-plane 重启后 metadata/content 仍可读取，bytes 与 hash 一致；
- 同 job/lease 改 bytes 返回 409；
- result 使用错误 evidence ID 返回 409，正确 ID/SHA 才完成 job；
- evidence ZIP、jobs queue 和 service log 未保留 token 或 raw evidence
  payload 于不允许的位置。

## 验证

- 真实 HTTP integration：17/17 checks PASS；
- platform：`1535 OK + 10 skipped`；
- targeted evidence store、worker queue、WorkerAgent、worker auth、Device
  Service HTTP、docs/OpenAPI tests：PASS；
- Node contracts、runtime coverage、peripheral catalog、QEMU profiles、
  project snapshot、compileall、scope check、`git diff --check`：PASS。
- PR #23 与合并后
  [CI `40834148271`](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40834148271)
  双 job PASS。

## 边界

本记录是 control-plane/data-plane HTTP 验证，不执行 QEMU guest。物理跨主机
executor、共享文件系统之外的对象存储复制、guest/controller 内部状态、
外部 side effect ownership 和 physical hardware 均未验证。

## 回滚

可 revert `139e5cbf`。恢复后旧 queue/result JSON 仍可读取；已创建的 evidence
目录不会被旧版本主动访问或迁移。
