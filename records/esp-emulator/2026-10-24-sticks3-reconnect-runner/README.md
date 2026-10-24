# StickS3 自动 radio 断线与重连回归

- 日期：`2026-10-24`
- 结果：`PASS`（virtual-device radio loss/recovery）
- 工作类型：`code_and_validation`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`5b686a976e679af2638e5b65f83c75e143582977`
- 基线版本：`e27a7c95ea2838fd2790ed10f0b95035025bf06a`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40064309448>
- 环境：macOS Apple Silicon；Python 3；QEMU StickS3；Device Service；公开 UIFlow2 base

## 结论

新增一个命令即可复现的 StickS3 radio 断线/恢复 runner。它自动：

- 从公开 StickS3 base 和 matching unified app 重建镜像；
- 替换 reconnect probe 的 user filesystem；
- 启动 disposable Device Service；
- 在同一 `qemu-wifi` session 中等待第一次 DHCP 和 `/before` HTTP；
- 在 guest 断开后通过 QOM 设置 `radio-enabled=false`；
- 要求扫描为 0，再恢复 `radio-enabled=true`；
- 要求重新关联、第二次 DHCP、`/after` HTTP 200 和最终 guest PASS；
- 停止 session 后验证同一 pcap 包含两组 DORA 和两条受控 HTTP 流。

## 关键证据

- 16/16 checks PASS；
- QOM `radio-enabled=false → true`；
- scan `1 → 0 → 1`；
- DHCP message sequence：
  `DISCOVER/OFFER/REQUEST/ACK` 两次；
- `/before` 与 `/after` 都是 HTTP 200；
- pcap：9,586 bytes，SHA256
  `5b57d36ccf55dc6ef840f7fe28e41d56e7c9ece5f7bb2235e063f39eef979b9e`；
- 平台测试：299/299 PASS；
- GitHub Actions platform contracts + network namespace policy：PASS。

## 边界

- 这是 QEMU WiFi 模型和 guest IP 栈结果，不是物理 RF/AP；
- 不证明 WPA2/WPA3、hidden SSID、不同 DHCP server 或新 lease 地址；
- 不证明硬件时序、功耗或恶意固件沙箱；
- 物理硬件为 `NOT RUN`。

## 文件

- `report.md`：实现、执行和验证；
- `run.json`：结构化记录；
- `evidence/verification.summary.json`：本地与 CI 聚合；
- `patches/`、`code/`：不适用，runner 在源码仓库。
