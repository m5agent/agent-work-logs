# ESP32-S3 GDMA 外部内存与 TLS Host Allowlist 报告

## 背景

上一轮 TLS/Host allowlist fixture 已完成 WiFi/DHCP，但 guest 停在
`ssl.SSLContext` 创建。QEMU 同时报告 `[AES] Error reading from GDMA buffer`。
由于所有更早期 AES 小块都能完成，问题需要继续追到 descriptor 的 payload
地址，而不是直接归因于 mbedTLS。

## 根因

QEMU 的 GDMA device 原先只初始化了内部 DRAM AddressSpace。AES descriptor
前几次指向内部 DRAM，能够正常读取；后续 16-byte payload 指向 ESP32-S3 的
外部内存/PSRAM 窗口时，`dma_memory_read()` 返回 `MEMTX_ERROR`，AES 不置
完成状态，固件重试并最终卡住 TLS context 创建。

`0027-esp32s3-gdma-external-memory.patch` 保留正常内部 DRAM 路径；当该路径
失败时，通过 QEMU SoC system AddressSpace 访问已建模的外部内存窗口。该
路径仍经过 SoC/cache/PSRAM 模型，不访问宿主进程任意内存。

## 复现与修复顺序

1. 初始 TLS fixture 停在无关的 `esp.random()` 探针；该探针不属于验收条件，
   移除后进入 TLS context 创建。
2. AES trace 显示小块读取初始成功，随后 descriptor payload 指向外部内存，
   `MEMTX_ERROR` 与 I/O 停滞同时出现。
3. 增加外部内存 fallback 后，`SSLContext` 成功创建，卡点前移到 CA 加载。
4. UIFlow2 的 SSL API 接受 PEM `cafile`；测试把生成 CA 写入 guest VFS 的
   `/flash/ca.pem` 后加载成功。
5. 测试证书 notBefore 固定为 Unix epoch，避免未完成 SNTP 的 guest 将
   host 当前时间生成的证书判为“validity starts in the future”。
6. pcap 断言从并不存在的 `dst_port` 字段改为解析 flow 的 `destination`
   端口；随后允许 200、拒绝 403、TLS flow 和 DHCP 全部通过。

## 改动

- 新增提交级 QEMU patch `0027`；
- TLS fixture 使用 PEM CA、VFS 文件和 `cafile` 加载；
- 测试 CA 使用固定的历史有效区间；
- 记录 TLS pass evidence，同时保留之前的 blocked evidence；
- 更新项目状态、Backlog、网络方案、代码地图和完整矩阵 evidence；
- 文档一致性检查确保 HISTORICAL blocker 不会重新成为当前状态。

## 验证

```text
platform tests                 223/223 PASS
runtime coverage               PASS
peripheral catalog             PASS
QEMU profiles                  PASS
TLS/Host allowlist fixture     PASS
UIFlow2 full matrix            67/67 cases, 274/274 checks PASS
attempts per case              1
retry_used                     false
QEMU patch apply checks        PASS
Linux namespace TLS            NOT RUN
physical hardware              NOT RUN
```

TLS 实测结果：

```text
allowed.lab.test  allow  200
denied.lab.test   deny   403
```

## 验证边界

- 记录的 TLS 运行使用 trusted-host isolation；
- Linux namespace 内尚未重复执行该 TLS fixture；
- Host allowlist 不是目标 IP/端口级通用 egress allowlist；
- 不证明公网 DNS/TLS 稳定性、证书固定、mutual TLS 或恶意固件安全；
- 不证明物理 RF、功耗、声光或电气行为；
- 完整外设矩阵证明当前共享 GDMA 改动没有破坏已覆盖设备路径，但不证明
  外部内存时序与真机 bit-exact。

## 风险与回滚

回滚源码提交 `f0f7065b7ba42ba914a74b6d80ceb2c88c8e52eb` 会恢复 TLS
context 阻塞，不应回滚。若仅需禁用外部内存 fallback，可移除 `0027` patch；
内部 DRAM 路径保持原行为。
