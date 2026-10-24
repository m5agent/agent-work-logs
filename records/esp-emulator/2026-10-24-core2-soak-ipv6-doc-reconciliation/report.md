# ESP Emulator Core2 soak、同 guest IPv6 与当前文档重整报告

## 背景

- 来源：用户要求完整整理当前代码与文档，说明已经完成的工作和剩余待办，并指出
  部分页面仍停留在较早的验证状态。
- 现象：Core2 两小时 soak 仍被多个入口描述为“在途”；UIFlow2 guest IPv6
  状态只有 host resolver/egress 证据；在途 IPv6 探针尚未进入文档契约。
- 目标：把新 evidence 纳入代码、自动生成物、状态页、Backlog、工作流台账、
  验证账本和文档一致性测试，同时保留未验证边界。

## 结论

- 状态：`PARTIAL`。
- Core2：artifact-bound `7200s` active-BLE WiFi/公网/GATT 功能门禁
  `PASS`；QEMU host RSS 增长 `REVIEW`。
- IPv6：专用 UIFlow2 测试构建在同一 StickS3 guest 中完成 IPv6 TCP/HTTP
  `PASS`；原厂 UIFlow2 未创建 link-local，controlled AAAA/denied-port
  `NOT RUN`。
- 文档：状态、Backlog、工作流、验证账本、代码地图、设备 catalog/profile
  和自动快照已按同一组 evidence 重整。

## 关键判断

### IPv6 固件配置边界

原厂 StickS3 UIFlow2 暴露 `AF_INET6`，但 board 配置未启用
`CONFIG_LWIP_IPV6_AUTOCONFIG`，并且应用没有调用
`esp_netif_create_ip6_linklocal()`。直接 socket connect 返回
`EHOSTUNREACH`，这是固件接口配置缺失，不是 QEMU egress/NAT 失败。

test-only patch：

- 在 StickS3 board config 启用 LWIP IPv6 和 autoconfig；
- 在 `IP_EVENT_STA_GOT_IP` 后创建 link-local；
- 不修改原厂源码 checkout；构建后 source diff 已恢复；
- patch 对 UIFlow2 base checkout 通过 `git apply --check`。

### Core2 长稳与资源增长

hash-freeze runner 在第一个 lease 前记录 firmware、ELF 和 QEMU SHA256，
结束时拒绝资产漂移。两小时运行中 frame/QOM、WiFi、公网 DNS/HTTP、外部
NUS GATT、pcap、HLI health 和 session 清理全部通过。

但 runner 采样的是 QEMU host 进程 RSS，数值从 `744160 KiB` 单调增加到
`1202176 KiB`。当前 evidence 只能证明功能保持，没有证明内存有界；原因需要
在后续独立实验中区分 TCG translation cache、QEMU heap、capture/evidence
路径或宿主 allocator 行为。

## 改动范围

- `platform/tools/network_sandbox.py`：controlled DNS/HTTP 的 IPv6 bind。
- `platform/tools/network_egress.py`：SLiRP IPv6 host alias 到 loopback 的
  精确映射。
- `platform/tools/pcap_summary.py`：`fec0::/10` 标记为 `site-local`，不再
  误标 global。
- `tests/network/ipv6_end_to_end/`：test-build patch、guest probe、runner、
  redacted evidence 和复现说明。
- Core2 catalog/profile/status/Backlog/workstreams/ledger 与自动快照同步。
- 文档一致性测试绑定新 evidence 的真实字段，并禁止旧“在途/RSS 有界”口径回归。

## 执行

- 环境：macOS 测试主机；UIFlow2 独立 build directory；补丁构建的
  `qemu-system-xtensa`。
- 平台测试：

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check
```

- Node：

```bash
npm test
npm run test:units
```

- IPv6 direct probe：

```bash
PYTHONPATH=.work/py python3 tests/network/ipv6_end_to_end/run_test.py \
  --qemu <patched-qemu> \
  --rom-dir <qemu-pc-bios> \
  --base-image <sticks3-test-build-merged.bin> \
  --out-dir <evidence-dir>
```

- 结果：平台 `343/343 PASS`；Node `2/2 PASS`；静态检查全绿；IPv6 guest
  TCP/HTTP `PASS`。GitHub Actions run `40107211782` 的
  `network-namespace-policy` 与 `platform-contracts` 均成功。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | UIFlow2 app build、Python compile、Node 和平台契约测试 |
| flash | `PASS` | 8 MiB merged test image 启动并进入 UIFlow2 guest |
| transport | `PASS` | IPv6 TCP、HTTP、pcap；Core2 WiFi/BLE HCI data path |
| device_response | `PASS` | HTTP 200、fixture `/ipv6`、外部 NUS GATT 与 HLI counters |
| data_behavior | `PASS` | 两小时 frame/network/GATT 稳定性；资产哈希无漂移 |
| visual_or_physical | `NOT RUN` | 无物理显示、RF、功耗或电气测量 |
| delivery | `PASS` | 源码 commit `d5dff977cf8078117c1505b38884f7901ed3c881` 已推送 |

## 验证边界

- 原厂 UIFlow2 不创建 IPv6 link-local，不能把测试构建写成原厂默认能力。
- 未运行 controlled AAAA、denied-port 或 Linux namespace cleanup。
- Core2 RSS 增长原因未定位；功能 PASS 不等于内存有界。
- 未运行超过 120 轮 reconnect、吞吐、teardown 竞态或物理硬件。

## 风险与回滚

- test-only patch 只用于测试构建，构建后源码已恢复；生产源码没有保留开关。
- 所有网络测试使用临时端口与进程，失败路径会停止 QEMU/HTTP fixture。
- 源码回滚点为 `ad6e96e69757eafd13993f0d45484c42d4476182`；可 revert
  `d5dff977cf8078117c1505b38884f7901ed3c881`。
