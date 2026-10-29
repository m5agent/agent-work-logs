# ESP Emulator lease-bound worker evidence

- 日期：`2026-10-29`
- 结果：`PASS`（真实 HTTP WorkerAgent/control-plane）
- 工作类型：`code_change`
- 问题来源：`NET-04` / `SVC-01` evidence persistence and response-loss recovery
- Base：`69902baf7b1f8fde5487628d0bb8217e69bc8e6d`
- 实现提交：`139e5cbf13014b6167de706d7f227188c1c5e8f4`
- 合并提交：`621b58e678e034c4b4bd54342ea709657fbbed2d`
- 环境：macOS arm64；Device Service API `1.50.0`；无 QEMU guest

## 结论

认证 worker 的 evidence ZIP 现在在 result 上报前上传到中央 store。记录由
job、live lease、worker instance 和 generation 派生；ZIP 以 SHA256 内容寻址。
同一 lease 同 bytes 的 response-loss retry 返回原 evidence ID，不同 bytes
返回 409。metadata/content 跨 control-plane restart 可读，result 只接受同一
evidence ID + SHA256。

真实 HTTP fixture 使用约 2 MiB ZIP；第一次上传已成功但客户端故意丢弃响应，
WorkerAgent 自动重注册并重试。服务重启后 metadata 与 ZIP bytes/hash 一致；
不同 bytes、错误 result evidence ID 均 fail closed。17/17 checks PASS。

## 关键证据

- OpenAPI `1.50.0` SHA256：
  `b59304036447986a3009cbd29180dd2af6f9dc331613d2c13e171e866da98319`
- evidence store SHA256：
  `0a9b29e76691e19c06fec0508e6c7386cdca7e1435e2f120e1f486b04cb6950e`
- WorkerAgent SHA256：
  `4972116d9c2a33ba6e7878247f927cad09e6f6240d111b23d84e16e2521cb4df`
- evidence ZIP：`2,097,444` bytes，SHA256
  `bf04ac516325cbf9c5b81345fdadc316a1ccc065dbd060fc821bdbdfb5025c43`
- metadata/blob mode：`0600`
- 平台：`1535 OK + 10 skipped`
- Node contracts、OpenAPI/YAML、runtime coverage、catalog、QEMU profiles、
  project snapshot、compileall、scope check 和 `git diff --check`：PASS
- [PR #23](https://github.com/m5agent/m5stack-esp-emulator/pull/23) 与合并后
  [CI `40834148271`](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40834148271)
  双 job PASS。

## 文件

- `report.md`：实现、兼容性、执行和边界
- `run.json`：机器可读记录
- `evidence/summary.json`：脱敏 machine summary

## 未覆盖项

- physical cross-host execution；
- 共享文件系统之外的 queue/session/evidence 复制或对象存储；
- QEMU guest/controller 内部状态；
- worker 未拥有的外部 side effect；
- physical hardware。
