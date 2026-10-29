# ESP Emulator worker claim response-loss idempotency

- 日期：`2026-10-29`
- 结果：`PASS`（真实 HTTP control-plane / WorkerAgent）
- 工作类型：`code_change`
- 问题来源：`NET-04` / `SVC-01` claim-response-loss recovery
- Base：`6c72ea74ebfe4fd64770ced888012900d3bb2cde`
- 结果提交：`468eeebcd6e62e352761a19f552d5a102f8e3de3`
- 环境：macOS arm64；Device Service API `1.49.0`；无 QEMU guest

## 结论

durable queue claim 新增 identity-bound `claim_idempotency_key`。真实
`WorkerAgent` 的第一个 claim 已由服务端签发 lease，但成功响应在客户端被
故意丢弃；WorkerAgent 自动重注册并使用同一 key 重试，获得原 job/lease。

服务使用同一 state directory 重启后，同一 claim replay 仍返回原
job/lease；第二个 queued job 没有被误领。新 key 才能领取第二个 job。
相同 key 改 request 返回 409 conflict，lease 过期或 ownership 改变返回
409 stale。

`jobs.json` 只保存 worker identity + key 的 SHA256、request hash、job ID
和 lease ID，不保存 raw claim key，文件 mode 为 `0600`。

## 关键证据

- OpenAPI `1.49.0` SHA256：
  `9027209dd5659d5845759638eb9d4ff212b700b5d2d8525199ffb27a4d0a1490`
- worker queue SHA256：
  `dd1653043dfb9cb4c2975a08647f53ef87a3b89a45f02efb390ab9922bd54b4d`
- worker agent SHA256：
  `599f5273d717177a3432d8fab6169ee077fea9e2366676fba50ecfd33445a146`
- 真实 HTTP evidence：11/11 checks PASS；
- restart 前后 same job/lease；
- 平台：`1529 OK + 1 skipped`；
- runtime coverage、catalog、QEMU profiles、snapshot、compileall、Node：
  PASS。
- GitHub Actions
  [`40828778684`](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40828778684)
  双 job PASS。

## 文件

- `report.md`：根因、实现、兼容性、执行和边界
- `run.json`：机器可读记录
- `evidence/summary.json`：脱敏 machine summary

## 未覆盖项

- 物理跨主机 executor/reattach；
- 真正网络黑障/丢包矩阵；
- 跨主机 queue/session/evidence 持久存储；
- QEMU guest/controller 内部状态；
- worker 未拥有的外部 side effect；
- physical hardware。
