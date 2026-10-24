# 对外记录

本目录只放**对仓库外的人有价值**的记录：公开仓库的 Issue 处理、PR/MR 评审、公开库的硬件或构建
验证、可复现的缺陷分析。这些内容会同时发布到内部 GitLab 和公开 GitHub。

内网运维、环境配置、权限盘点、服务部署这类只对内部有意义的内容放在 [internal/](../internal/)，
**只发布到内部 GitLab**。

## 何时不该放这里

- 只是配置本机或内网服务的操作记录；
- 涉及内网端点、账号、权限、设备标识的排查；
- 只有同事才需要看的环境说明。

判断标准：如果这条记录对一个只看公开仓库的外部读者毫无价值，它就不该出现在这里。

## 记录索引

| 日期 | 对象 | 主题 | 结果 | 记录 |
| --- | --- | --- | --- | --- |
| 2026-10-25 | `esp-emulator` | Worker central control-plane restart 与同 lease/evidence continuity | `PASS`（virtual-device：central 2.2s 重启、重注册、原 identity/generation/lease、terminal PASS、evidence ZIP、runtime/QEMU cleanup；runtime restart/cross-host/claim dedup 与真机 NOT RUN） | [查看](esp-emulator/2026-10-25-worker-control-plane-restart-continuity/) |
| 2026-10-25 | `esp-emulator` | HMAC-authenticated worker multicast discovery | `PASS`（virtual control-plane：无硬编码 control URL 注册、错误/旧 token 拒绝、SIGHUP 后新 token 重新发现、无 QEMU/session；NAT/跨子网/跨主机真机 NOT RUN） | [查看](esp-emulator/2026-10-25-authenticated-worker-discovery/) |
| 2026-10-25 | `esp-emulator` | SHA-bound UI/headless/network-first 固件审查预期 | `PASS`（virtual-device：OpenAI BIN+NVS fixture 完成 guest marker、network PASS、DNS/TCP443/37-packet pcap；387/387、20/20、CI PASS；真实 key/云服务/RF/真机 NOT RUN） | [查看](esp-emulator/2026-10-25-sha-bound-review-expectations/) |
| 2026-10-25 | `esp-emulator` | 代码、文档与当前工作/待办收口 | `PASS`（docs/contracts：377/377、20/20、snapshot/catalog/coverage、CI PASS；IPv4/IPv6 与 WPA2 边界纠偏；真机与完整矩阵 NOT RUN） | [查看](esp-emulator/2026-10-25-code-doc-current-state-consolidation/) |
| 2026-10-25 | `esp-emulator` | ESP32-S3 WPA2-PSK 正确/错误密码数据面 | `PASS`（virtual-device：RSN/M1-M4/CCMP、正确密码 DHCP+DNS+TCP443、错误密码 deauth/无 DHCP、15/15 定向矩阵、CI PASS；WPA3/group multicast/物理硬件 NOT RUN） | [查看](esp-emulator/2026-10-25-s3-wpa2-psk-data-plane/) |
| 2026-10-25 | `esp-emulator` | Worker-local StickS3 QEMU across network namespaces | `PASS`（virtual-device：18/18 checks、真实 QEMU、artifact/firmware/evidence/QEMU reap/namespace cleanup；physical cross-host/reattach/companion continuity/真机 NOT RUN） | [查看](esp-emulator/2026-10-24-http-worker-executor/followups/2026-10-25-control-runtime-plane-split/followups/2026-10-25-worker-local-qemu/) |
| 2026-10-25 | `esp-emulator` | Session-isolated FAT32+MBR SD fixture 与 CrossPoint closure | `PASS`（virtual-device：3 PASS / 1 PARTIAL / 0 FAIL；CrossPoint 主菜单、storage restore/evidence PASS；物理硬件 NOT RUN） | [查看](esp-emulator/2026-10-24-user-firmware-six-device-matrix/followups/2026-10-25-refreshed-four-functional/followups/2026-10-25-sd-mbr-fixture/) |
| 2026-10-25 | `esp-emulator` | 四个当前公开固件的 Device Service 功能重跑 | `PARTIAL`（virtual-device：2 PASS / 2 PARTIAL / 0 FAIL；CrossPoint SD fixture gap；物理硬件 NOT RUN） | [查看](esp-emulator/2026-10-24-user-firmware-six-device-matrix/followups/2026-10-25-refreshed-four-functional/) |
| 2026-10-25 | `esp-emulator` | Core2 三 lease 121 轮、guest IPv6 namespace 与当前 Backlog 重整 | `PASS`（virtual-device + docs/contracts；物理 cache/PSRAM、bit-exact controller、吞吐/teardown 与真机 NOT RUN） | [查看](esp-emulator/2026-10-24-core2-soak-ipv6-doc-reconciliation/followups/2026-10-25-three-lease-ipv6-current-state/) |
| 2026-10-25 | `esp-emulator` | 当前工作/文档总整理与 Core2 单 lease 121 轮 reconnect | `PASS`（virtual-device + docs；3/3、物理与真机 NOT RUN） | [查看](esp-emulator/2026-10-24-core2-soak-ipv6-doc-reconciliation/followups/2026-10-25-reconnect121-doc-reconciliation/) |
| 2026-10-24 | `m5stack-schematics-text` | AI Pyramid `llm-llm` deb 平台路径修正与全量链接审计 | `PASS` / PR #2 待审核 | [查看](m5stack-schematics-text/2026-10-24-ai-pyramid-llm-deb-link/) |
