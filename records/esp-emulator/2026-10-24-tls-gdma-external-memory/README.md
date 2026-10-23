# ESP32-S3 GDMA 外部内存与 TLS Host Allowlist

- 日期：`2026-10-24`
- 结果：`PASS`
- 工作类型：`code_change`
- 问题来源：P0 网络 TLS/Host allowlist 阻塞
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`f0f7065b7ba42ba914a74b6d80ceb2c88c8e52eb`
- 基线版本：`dd705e8b8dfdb3bab927e9f4d1a7561a684466bc`
- 环境：macOS Apple Silicon；QEMU ESP32-S3；UIFlow2 StickS3 固件

## 结论

修复了 ESP32-S3 GDMA 在正常内部 DRAM 路径返回 `MEMTX_ERROR` 时无法读取
外部内存的问题。UIFlow2 `ssl.SSLContext` 不再卡死，stock firmware 已完成：

- WiFi 关联和 DHCP；
- 测试 CA 写入 VFS 并加载；
- TLS 握手；
- 允许 Host 返回 HTTP 200；
- 拒绝 Host 返回 HTTP 403；
- pcap、请求决策和串口 marker 联合取证。

补丁为 `0027-esp32s3-gdma-external-memory.patch`。修复后完整 UIFlow2 外设
矩阵为 `67/67` 用例、`274/274` 检查，全部 `attempts=1`、
`retry_used=false`。

## 关键证据

- TLS Host allowlist：`PASS`；
- 允许请求：`allowed.lab.test`、decision `allow`、status `200`；
- 拒绝请求：`denied.lab.test`、decision `deny`、status `403`；
- TLS TCP flow 和 DHCP 均在 pcap 中出现；
- 平台测试：`223/223` PASS；
- QEMU patch reverse/forward apply check：PASS；
- 完整 UIFlow2 矩阵：67/67、274/274 PASS，全部首轮无重试；
- Linux namespace TLS：`NOT RUN`；
- 物理硬件：`NOT RUN`。

## 文件

- `report.md`：根因、修复、复现过程和验证
- `run.json`：机器可读结果
- `evidence/verification.summary.json`：脱敏聚合证据

## 未覆盖项

- Linux namespace 下的 TLS/VFS/网关回归；
- 任意公网 destination allowlist、可控 resolver 和 DHCP renewal；
- 真机 TLS、RF、功耗、声学和电气行为；
- 本修复是数据面兼容路径，不等于完整 ESP32-S3 AES/GDMA 时序模型。
