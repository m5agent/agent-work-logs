# Firmware guest CNAME lifecycle report

## 背景

上一里程碑只证明 controlled resolver 能编码 CNAME chain。`NET-07` 要求
进一步证明同一真实 guest 固件能跟随 CNAME terminal、使用取回的 address
完成 TCP/HTTP，并把 resolver、HTTP、pcap 和 cleanup 绑定到同一个
Device Service lease。

## 结论

该门禁通过。三个独立 `/api/v1` lease 都完成：

- WiFi association 和 DHCP；
- guest CNAME query；
- resolver CNAME chain + terminal A；
- allowed HTTP 200；
- denied name；
- denied port；
- evidence ZIP、pcap 与 namespace cleanup；
- session stop 后的 QEMU reap 和 fixture closure。

## 诊断与修复

第一次运行在 guest 启动前退出：

- 现象：serial 为 0，sandbox 返回 126；
- 根因：DNS hosts 已先规范化为 `tuple[ipaddress]`，`ControlledDns` 第二次
  规范化时只接受字符串/list；
- 修复：让 record normalization 接受 tuple 和 pre-normalized address，并
  保持 idempotent；
- 分类：服务启动失败，不是固件失败。

第二次运行仍在 guest 启动前退出：

- 现象：QEMU 报 machine ROM binary not found；
- 根因：Linux QEMU 被绑定到缺少 ESP32-S3 machine ROM 的 build `pc-bios`；
- 修复/运行约束：增加 `M5_QEMU_XTENSA_ROM_DIR` 与
  `M5_QEMU_RISCV32_ROM_DIR` 覆盖，并选择包含 machine ROM 的兼容目录；
- 分类：运行资产配置失败，不是固件失败。

第三次运行已完成 guest 全链路，但 evidence 聚合时发现 namespace wrapper
只有 5 秒终止预算，与 sandbox 自身 5 秒 QEMU reap 边界相同，导致 cleanup
字段尚未写入就可能被强杀。最终修复：

- namespaced session 的 wrapper termination grace 提升到 20 秒；
- `GET /network` 暴露 `isolation`、`dns_requests` 与
  `http_fixture_requests`；
- evidence ZIP 增加 `network/dns-requests.json`、
  `network/http-fixture.json` 和 `network/isolation.json`。

## 代码改动

- `network_sandbox.py`：DNS record normalization idempotent；
- `device_service.py`：CNAME/HTTP fixture checks、isolation/log evidence、
  namespace termination grace、ROM directory overrides；
- `cname_guest_lifecycle/`：stock UIFlow2 guest probe、Device Service runner、
  3-run summarizer、README 和 committed aggregate；
- OpenAPI/docs：`1.31.0`、new network evidence fields、关闭 `NET-07`。

## 执行

1. 在 macOS 上用 UIFlow2 VFS 依赖构建 stock StickS3 probe。
2. 在 privileged Ubuntu arm64 container 中安装兼容 QEMU runtime 依赖。
3. 启动真实 Device Service，上传 probe，并创建三个独立 session。
4. 每个 session 使用 controlled CNAME、allowlisted endpoint 和 Linux
   private namespace。
5. stop session，下载同一 lease 的 evidence ZIP。
6. 聚合三次运行并要求 artifact/tool hash、checks 和 cleanup 全部一致。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | probe 构建、compileall、OpenAPI YAML、文档契约 |
| transport | `PASS` | guest DNS CNAME、TCP HTTP、denied port |
| device_response | `PASS` | guest HTTP/1.0 200 + terminal marker |
| data_behavior | `PASS` | allowed/denied name、allowed/denied port、pcap 流 |
| visual_or_physical | `NOT RUN` | 无 RF、功耗、电气或物理硬件测试 |
| delivery | `PASS` | source commit + CI `40153868339` |

## 验证边界

本记录是 `virtual-device validation`。它不证明 public DNS/DNSSEC、
rebinding resistance、任意公网域名策略、RF/PHY、吞吐、功耗、电气行为或
physical hardware。

## 风险与回滚

本轮没有物理设备写操作。回滚 result commit 会恢复 `NET-07` 和较窄的
network evidence 契约；没有持久状态迁移。测试容器和 session 均在运行后
回收。
