# StickS3 原版配网保存快照执行报告

## 目标与基线

先前的原版回放直接调用 Device Service，已记录首次配网、复位后 STA 恢复和复用已配置 Flash 冷启动。本次检查常规 Firmware Review 保存快照入口能否正确调用同一个板级路径，并把终态数据面绑定到审核结果。服务源码基线 `1939e39885d3cffe74f01576182bfa28c6148dd2`。实际选用的冻结原生服务为 `597e03214dc5f442787cec52f1720567e4ed2a00`。本次涉及的服务实现与 API 文件均逐一与源码基线比对。Firmware Review 使用 `f0101b6bb0926a69ef2f8477ae81e991338391f5` 和 OpenAPI 0.27.0。

## 复现

1. 在 macOS ARM64 启动各自有独立状态目录的 Device Service 和 Firmware Review。给 StickS3 允许 `network.softap.provision`，预检设备能力声明 `sticks3-open-softap-provisioning`。若复测运行中 Flash 读取，再允许 `flash.read`。关闭审核服务的提交选项。
2. 从保存的原版 v0.2.4 应用和已经核验的同版工具链段配置 `app_vendor_boot_contexts`。启动前缀长 65,536 字节，bootloader、partition table 和 `boot_app0` 分别在 `0x0`、`0x8000`、`0xE000`。以原应用 SHA-256 为配置键，填写匹配的 `app_sha256`、`sha256`、`app_offset=65536`、`provenance` 和前缀 `path`。核对 [本次哈希](run.json)。
3. 对该固件的本地保存快照调用 `POST /api/reviews/{job_id}/retry`。

   ```json
   {"sourceMode":"saved_snapshot","useAgentReview":false,"validation":{"sticks3_provisioning_fixture":true}}
   ```

4. 比对实际启动进程的原生 QEMU SHA-256。只读观察单个活动租约，待门户完成后读取同一租约中的 Flash，待审核完成后读取该已停止租约的网络和证据 ZIP。比对报告、终态 API 及 ZIP 的固件、PCAP 摘要和释放状态。

初次本地测试配置漏填应用绑定、应用偏移和来源字段。前缀文件本身匹配，但受理返回 `E_APP_ONLY_BASE_MISMATCH`，未启动原生 QEMU。补齐配置后，原版应用的二进制与前缀均保持同一 SHA-256，审核进入虚拟设备验证。两次执行独立保留。

## 实测结果

| 验收层 | 状态 | 观察 |
| --- | --- | --- |
| 分段受理和虚拟烧录 | `PASS` | 原应用、启动上下文和 8 MiB 组合 Flash 均核验。原应用从 `0x10000` 启动。 |
| 串口、帧和观测 | `PASS` | 冷启动 ROM 串口标记和 1 张终态帧进入 ZIP。审核的虚拟观测为 60.027 秒。串口保留原版缺少 core-dump 分区提示。 |
| 热点与 STA 数据面 | `PASS` | 同一次租约先门户 DORA，随后 `GET /`、`POST /wifisave` 各实际返回 200，再执行站点 DORA 和来宾的 ARP 回复。 |
| Flash 持久写入 | `PASS` | 同会话读回的 NVS 相对冷镜像有 4,344 字节不同。应用区域与原版逐字节一致。 |
| 审核终态与清理 | `PARTIAL` | `manual_review / SIM_PARTIAL / E_NETWORK_PARTIAL`。本地配网 `PASS`。Unix peer 已释放，活动租约为零，可读终态证据，活动虚拟 Flash 已释放。 |
| 云端、物理设备、browser-WASM | `NOT RUN` | 这次是私有 Unix socketpair 夹具，宿主 IP 后端数量为 0，只覆盖这一个原固件和板型。 |

第二次执行的独立 PCAP 回读逐包匹配四步 DHCP 顺序，以 TCP 序号重组两份正文，校验实收 Content-Length、HTTP 200 与报告的正文 SHA-256，最后核对站点租约 ACK 之后由来宾发出的 ARP。终态 ZIP 全量 CRC 检查通过，ZIP 内 PCAP 与审核报告 SHA-256 相同。摘要移除服务端点、租约标识和设备地址。原始 ZIP 与已配置 Flash 留在私有取证区。

本次没有代码或常驻服务改动。复位和已配置 Flash 冷重载属于之前的直测。Burner 未提交。
