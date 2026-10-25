# ESP Emulator Core2 Staggered Concurrent Unified Leases

## 背景

现有 Core2 证据已经覆盖单 lease active-BLE、121 轮 reconnect、
artifact-bound `7200s`、QOM 8 MiB PSRAM/MMU、PSRAM sustained stress 和
active-stop/recovery。但 Backlog 仍把 long-run concurrency 标为未执行。

机器级并发不能只比较“两个命令都能单独 PASS”；至少需要证明：

1. 两个 session 的运行区间真实重叠；
2. 每个 session 有独立的 HTTP/BLE companion 归属；
3. 每个 session 在同一时间窗口内完成网络、controller、frame/QOM 和
   evidence；
4. 失败路径和资源冲突保留原始证据。

## 实验一：共享 HTTP 端口冲突

新增 runner `--concurrency/--stagger-seconds` 后，第一轮将两个
`core2-native-hci` session 同时提交。两者都在 host 绑定
loopback `18089` HTTP fixture：

- session A 正常完成；
- session B 在 create 阶段得到 `Address already in use`，没有 QEMU；
- aggregate 为 `1/2 FAIL`。

这说明原服务虽然允许两个 session，unified HTTP companion 却不是
per-session isolation。

## 修复：QEMU guestfwd HTTP

Core2 native-HCI 不再在宿主端口启动 `ThreadingHTTPServer`，而是给每个
QEMU user-net 配置：

```text
guestfwd=tcp:10.0.2.2:18089-cmd:<per-session helper>
```

helper 由 `unified_http_guestfwd.py` 实现：

- 每个 guest TCP connection 由 QEMU 启动一次独立 helper；
- 读取 HTTP request headers；
- 以文件锁把请求记录到该 session 自己的 `http-fixture.json`；
- 返回固定 body；
- 不监听共享 host port。

DeviceService 仍把 HTTP companion 记录为
`kind=qemu-guestfwd-command`，由 QEMU process ownership 管理；服务重启
reattach 时不会重复绑定宿主端口，而是把已 reattach 的 QEMU guestfwd
标记为 adopted。stop/failure 会标记 companion terminated。

## 实验二：无错峰冷启动

端口冲突消失后，两个 session 在同一毫秒附近同时创建。两轮都完成了
WiFi、公网 DNS/HTTP 和一个 HTTP 请求，但第二个 guest 在 BLE GATT
discovery 期间出现：

```text
Guru Meditation Error: Core 1 panic'ed (LoadProhibited)
PC: 0x402630cc
ble_hs_hci_process_ack
```

`l_ble_hs_hci_ack` 为 null，随后引起 reboot 和 `PC=0`。外部 Bumble peer
记录 GATT request timeout。该失败只发生在两个 guest 同时冷启动，属于
native-HCI concurrent cold-start 边界，不能被端口修复掩盖。

## 实验三：30 秒启动错峰

runner 用 `--stagger-seconds 30` 让第一个 guest 完成启动/HCI 初始化后，
再启动第二个 guest；二者之后继续保持并发。

最终结果：

| 项目 | 结果 |
| --- | --- |
| lease 数 | `2` |
| 最大并发 session | `2` |
| 启动错峰 | `30s` |
| 每 lease hold | `120s` |
| session 完成 | `2/2 PASS` |
| Wi-Fi/公网/HTTP | `PASS` |
| BLE GATT | `PASS` |
| PSRAM sweep | `31/32` 次，各 session |
| HLI health | `45/45`，无 error/queue/drop |
| frame/QOM | `PASS`，两 session SHA/节点数一致 |
| pcap/evidence/cleanup | `PASS` |

该结果证明 30 秒错峰后的双 lease 稳态并发，不证明无错峰冷启动。

## 验证

```text
platform unittest       460/460 PASS
docs consistency         35/35 PASS
concurrent fixture      19/19 PASS
Node SHA256/upload        2/2 PASS
runtime coverage         PASS
peripheral catalog       PASS
QEMU profiles            PASS
project snapshot         PASS
Ruff E9/F                PASS
compileall               PASS
git diff --check         PASS
GitHub Actions           PASS
```

CI：
<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40168564543>

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build/static | `PASS` | 460 项平台测试、profile/schema/docs checks |
| controller data plane | `PASS` | 两个 guest 各自 native HCI → Bumble GATT |
| virtual network | `PASS` | 各自 guestfwd HTTP、DHCP、public DNS/HTTP、pcap |
| storage/PSRAM | `PASS` | 每 session 30+ 次 `1 MiB` 全缓冲校验 |
| concurrent steady state | `PASS` | 最大并发 `2`，30 秒错峰 |
| simultaneous cold start | `FAIL` | 第二 guest `ble_hs_hci_process_ack` LoadProhibited |
| physical hardware | `NOT RUN` | 无物理设备或测量 |

## 边界

- 两个 QEMU 共享同一个 macOS host 和 service process，不是物理多机；
- guestfwd 是 controlled local HTTP endpoint，不是公网服务实现；
- public DNS/HTTP 通过 QEMU user-net，不证明 RF/PHY；
- native-HCI 仍是功能级 QEMU relay，不是 bit-exact ESP32 BT controller；
- PSRAM sweep 是虚拟 guest 数据面，不证明物理 cache/PSRAM timing；
- 30 秒错峰 pass 不能外推为任意同时启动、任意固件或任意并发数。

## 风险与回滚

- guestfwd helper 每个连接执行一次，需保留请求数/资源上限；
- generic unified profiles 仍使用原 in-process HTTP fixture，行为未改变；
- 回滚实现为 revert `e3c5d08`；
- 回滚后并发 Core2 会重新暴露共享 18089 冲突，文档必须同步撤回该能力。
