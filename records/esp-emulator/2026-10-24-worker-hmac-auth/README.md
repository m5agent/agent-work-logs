# ESP Emulator worker HMAC authentication

- 日期：`2026-10-24`
- 结果：`PASS`（worker-only mutation 与真实 authenticated job）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`d200bada9e72593db21cdfb191cdb59e488439a4`
- 结果版本：`303e10744f3826763e355ee2c49e7715fe58a254`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40056937192>
- 环境：macOS Apple Silicon；真实 StickS3 QEMU；启用 API token 的 Device Service

## 结论

worker-only mutation 现在有独立于普通 Bearer token 的身份绑定：

```text
worker_key = HMAC-SHA256(
  master-token,
  worker-id + instance-id + generation
)

signature = HMAC-SHA256(
  worker_key,
  version + method + path + timestamp + nonce + body-sha256
)
```

受保护操作：

- `/jobs/claim`
- `/jobs/{id}/heartbeat`
- `/jobs/{id}/result`
- `/workers/{id}/heartbeat|drain|stop|results`

要求：

- timestamp 在 90 秒窗口内；
- nonce 只使用一次，服务端有 bounded replay cache；
- 签名 identity 必须同时匹配 path worker ID 和 JSON body；
- generation 改变会改变 worker key，旧 generation 不能冒充新 worker；
- unsigned/body-tampered/replayed 请求被拒绝。

## 关键证据

- 平台测试：`296/296 PASS`；
- worker auth：`4/4 PASS`；
- worker agent：`3/3 PASS`；
- authenticated live executor：`1/1 PASS`；
- unsigned claim HTTP `401`；
- 签名后真实 job：`completed / PASS / attempts=1`；
- evidence ZIP：`6882 bytes`；
- evidence SHA256：
  `2df3fdc392b3f3b2e15f736465d766936ebd0fc5c1ec5d30e355c583ac3eec67`；
- GitHub Actions：`Ran 296 tests`、`OK (skipped=2)`，两个 job 均成功；
- OpenAPI `1.19.0` 记录 worker auth header/path/时间窗。

## 文件

- `report.md`：签名协议、服务端验证、真实 job 和边界；
- `run.json`：结构化记录；
- `evidence/verification.summary.json`：脱敏聚合证据。

源码证据：
<https://github.com/m5agent/m5stack-esp-emulator/blob/303e10744f3826763e355ee2c49e7715fe58a254/tests/network/worker_executor/evidence-2026-10-24-executor-auth-pass.json>

## 未覆盖项

- 跨主机 TLS/mTLS；
- worker credential rotation 和 key revocation；
- 外部 side-effect exactly-once；
- companion HTTP/BLE/evidence continuity；
- 跨主机 QEMU re-attach；
- 生产多机调度；
- 物理硬件验证。
