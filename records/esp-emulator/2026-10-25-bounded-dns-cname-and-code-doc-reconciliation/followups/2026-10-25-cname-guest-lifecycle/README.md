# ESP Emulator firmware guest CNAME lifecycle

- 日期：`2026-10-25`
- 结果：`PASS`（virtual-device validation）；physical RF/hardware
  `NOT RUN`
- 工作类型：`code_change`
- 源码版本：
  `https://github.com/m5agent/m5stack-esp-emulator/commit/c2083ecddb553eaddbf69fabeb6abbb1218b22dc`
- Base commit：`8710e41bf00d592ad0a5a7b9e5a3d5f32a333f9d`
- 环境：macOS arm64 构建 probe；Ubuntu 25.04 arm64 privileged Docker
  container 执行 QEMU/Device Service；Python 3.13

## 结论

`NET-07` 已关闭。三个独立 Device Service lease 均使用同一 stock StickS3
UIFlow2 probe、`qemu-wifi/uiflow2-sticks3-wifi`、controlled DNS 和 Linux
private namespace。

每轮同一个 guest：

- 解析 `alias.cname.test`，resolver 返回 CNAME 到
  `origin.cname.test` 和 terminal A；
- 使用 terminal 的 QEMU SLiRP host alias 完成 allowed HTTP/1.0 200；
- 对未允许名称得到 NXDOMAIN；
- 对未允许端口得到连接拒绝；
- 在同一 session evidence ZIP 中留下 DNS/HTTP fixture log、pcap 和
  namespace cleanup；
- stop 后 QEMU reap、DNS close、HTTP close 和 namespace cleanup 全部成立。

三次运行的 probe、QEMU、runner、Device Service 与 sandbox hash 完全一致。

## 关键证据

- API contract：`1.31.0`；
- 三次 lease 时长：`17.817s`、`17.744s`、`17.937s`；
- probe SHA256：
  `53170651ccabc8fb16b5cf993d348693c12bcc643a6f0c60bf7a479d8a456c73`；
- QEMU SHA256：
  `f024f034d20bd5b8e2c224ce69deed70984b0514f8a310d221b388b74c179ecb`；
- 19/19 aggregate checks PASS；
- 两次 pre-guest 启动失败保留为诊断，均不是固件失败；
- 平台测试 `427/427 PASS`；Node `2/2`；CI
  `40153868339` 两个 job PASS。

## 文件

- `report.md`：根因、改动、执行、证据和边界
- `run.json`：机器可读结果
- `evidence/verification.summary.json`：脱敏 3× lease 与 CI 摘要

## 未覆盖项

- public DNS、DNSSEC 或 rebinding resistance；
- 任意公网域名解析；
- 物理 RF、功耗或电气行为；
- physical hardware validation。
