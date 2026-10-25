# ESP Emulator WebBurner part integrity

- 日期：`2026-10-25`
- 结果：`PASS`（static-manifest validation）
- 工作类型：`code_change`
- 源码仓库：<https://github.com/m5agent/m5stack-esp-emulator>
- 基线版本：`a9d60e12599b10ea2602b00e88dbf7742c800868`
- 结果版本：`10df26ece0b605a3a8bb36a3661b53494fdae9a0`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40151571675>
- 环境：macOS Apple Silicon；Python 3；无物理设备

## 结论

WebBurner `parts[]` 的可选完整性声明现在会在组合完整 Flash 前由 importer
流式复算：

- `size`；
- `sha256`；
- `sha1`；
- `md5`；
- 顶层字段或 `integrity` 对象内的等价声明。

3-segment 阳性样本的每个 segment 都记录
`status=verified`、算法集合 `[size,sha256,sha1,md5]` 和
`weak_digest=true`。SHA-256 mismatch、size mismatch、非法 digest、
顶层/`integrity` 冲突声明和未知 integrity 字段均被拒绝。

这不是发布者签名、证书或来源真实性验证。SHA-1/MD5 只用于兼容包格式和检测
意外损坏，不证明安全启动、Flash Encryption、boot、网络或真机行为。

## 关键证据

- 平台测试：`419/419 PASS`；
- 文档契约：`23/23 PASS`；
- WebBurner integrity runner：`PASS`；
- 阳性 segment：`3/3`；
- 负向用例：SHA-256 mismatch、size mismatch、非法 SHA-256、重复声明冲突；
- GitHub Actions `platform-contracts` 与 `network-namespace-policy`：`PASS`。

## 文件

- `report.md`：实现、验证、风险和边界；
- `run.json`：机器可读记录；
- `evidence/verification.summary.json`：脱敏验证摘要。

## 未覆盖项

- 发布者身份、数字签名、证书链和供应链真实性；
- secure boot、Flash Encryption、生产 key/eFuse；
- boot、网络、运行态外设和 malicious-firmware sandbox；
- 物理硬件验证。
