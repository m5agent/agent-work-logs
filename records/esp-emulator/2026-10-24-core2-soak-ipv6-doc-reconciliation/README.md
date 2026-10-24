# ESP Emulator Core2 soak、同 guest IPv6 与当前文档重整

- 日期：`2026-10-24`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：用户维护请求（无公开 Issue）
- 源码版本：`m5agent/m5stack-esp-emulator @ d5dff977cf8078117c1505b38884f7901ed3c881`
- 环境：macOS 测试主机、补丁构建的 QEMU Xtensa、UIFlow2 StickS3 测试构建；不涉及物理硬件

## 结论

Core2 的 7200 秒 artifact-bound active-BLE WiFi/公网/GATT 功能门禁已通过：
启动 firmware/ELF/QEMU 哈希在首 lease 前绑定，运行期无资产漂移，
frame/QOM、网络、NUS GATT、pcap、HLI health 和 session 清理均成立。
同一轮 QEMU host RSS 从 `744160 KiB` 增至 `1202176 KiB`，增长
`458016 KiB`，原因尚未归因，因此只记功能 PASS，内存趋势保持 `REVIEW`。

另外，原厂 StickS3 UIFlow2 虽包含 `AF_INET6`，但没有创建 IPv6
link-local，直接运行会 `EHOSTUNREACH`。使用保留在源码仓库中的 test-only
patch 开启 IPv6 autoconfig 并在 `IP_EVENT_STA_GOT_IP` 后创建 link-local
后，同一 guest 完成 `fec0::2:18095` 的 IPv6 TCP/HTTP，pcap 记录
site-local 双向流。该结果不等于原厂固件默认支持 IPv6；controlled AAAA、
denied-port 和 Linux namespace cleanup 仍未执行。

## 关键证据

- 平台契约与文档测试：`343/343 PASS`。
- Node SHA256/upload 单测：`2/2 PASS`。
- `runtime_coverage`、`peripheral_catalog`、`qemu_profiles`、
  `project_snapshot` 和 `git diff --check`：全部 `PASS`。
- GitHub Actions run `40107211782`：`network-namespace-policy` 和
  `platform-contracts` 两个 job 均 `PASS`。
- IPv6 test-build patch 对 UIFlow2 base checkout 通过 `git apply --check`。
- 同 guest IPv6 TCP/HTTP：HTTP/1.0 200、fixture `/ipv6` 请求和
  `fec0::2:18095` pcap 流同时成立。
- Core2 artifact-bound soak：HLI `45/45`、events `36`、ACLs `9`，
  errors/queue/dropped/peer-close/panic 均为 `0`。

## 文件

- `report.md`：改动、执行、验证层级和边界。
- `run.json`：机器可读记录。
- `evidence/summary.json`：从源码仓库 evidence 派生的脱敏摘要。
- `patches/`：不适用；test-only UIFlow2 patch 已提交到源码仓库。
- `code/`：不适用；可重建探针位于源码仓库 `tests/network/ipv6_end_to_end/`。

## 未覆盖项

- Core2 host RSS 增长原因未定位，不能声明内存有界。
- 未执行超过 120 轮 reconnect、长时吞吐或 process-stop/teardown 竞态。
- 未执行同 guest controlled AAAA、denied-port 和 Linux namespace cleanup。
- 未执行物理硬件、RF、功耗或电气验证。
