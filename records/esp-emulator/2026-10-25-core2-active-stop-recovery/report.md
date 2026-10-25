# ESP Emulator Core2 active-stop 与连续恢复报告

## 背景

Core2 已通过 `core2-native-hci` 的 WiFi、公网 DNS/HTTP、外部 NUS GATT、
多轮重连、active-BLE 和限容 TCG 长稳。Backlog 仍保留 process-stop/
teardown 时序缺口：已有正常结束和 service restart 证据，但没有在 BLE/HTTP
companion 仍活跃时主动删除 session，再验证 PID、lease 和下一 session
恢复的连续门禁。

## 目标与约束

目标是在真实 Device Service 路径中：

1. 创建 ready 的 `core2-native-hci` session；
2. 在 BLE peer 仍处于 linger、HTTP fixture 仍运行时采集 frame/QOM/network/
   peer/pcap/resource evidence；
3. DELETE session；
4. 验证 companion terminate、QEMU/BLE PID 回收与 worker lease release；
5. 连续启动下一次 session，证明停止没有留下阻碍恢复的残留；
6. 冻结 firmware/ELF/QEMU/工具哈希，运行期不得漂移。

约束是 stock internal-controller app 必须来自 `build-M5STACK_Core2`，不能
使用 HCI-UART offload 镜像；结果只属于 virtual-device validation。

## 实现

新增 `run_service_teardown.py`：

- 上传 firmware 与匹配 ELF；
- 每个 attempt 使用独立 session、QEMU 进程和 BLE peer；
- 请求 `ble_linger_seconds=120`，并在 stop 前确认 BLE companion 状态为
  `running`、`peer-closed=0`；
- 获取 session-bound evidence ZIP、frame 与 QOM；
- 通过真实 `/api/v1/sessions/{id}` DELETE 停止；
- 读取最终 session、worker status，并检查 PID 不存在；
- 进入下一 attempt，形成连续 recovery 门禁。

该任务没有发现新的 production 代码缺陷；现有 stop/cleanup 路径在门禁下通过。
新增的是可重复测试、结构化证据和文档边界，而不是为测试伪造 cleanup 状态。

## 执行结果

| Attempt | STOP | Final state | Error | HTTP/BLE companion | BLE/QEMU PID | worker lease |
| --- | ---: | --- | --- | --- | --- | --- |
| 1 | 0.359s | stopped | none | terminated | reaped | 0 |
| 2 | 0.222s | stopped | none | terminated | reaped | 0 |
| 3 | 0.154s | stopped | none | terminated | reaped | 0 |

每个 attempt 在 stop 前均满足：

- `network=PASS`；
- WiFi DHCP/HTTP、公网 DNS/HTTP；
- 外部 BLE NUS discovery/subscribe/write/notify；
- HLI posts/consumed 平衡、`hli-errors=0`、空 HLI/meta queue；
- `peer-closed=0`、pcap 非空、evidence ZIP 完整；
- PNG frame 一致为 3710 bytes，QOM 34 nodes。

连续的下一次 session 均重新完成上述功能路径。

## 验证

```text
Core2 active-stop/recovery       3/3 PASS
platform contracts               411/411 PASS
documentation contracts          22/22 PASS
runtime coverage                 PASS
peripheral catalog               PASS
QEMU profiles                    PASS
project snapshot                 PASS
compileall                       PASS
selected Ruff E9/F               PASS
git diff --check                 PASS
GitHub Actions 40146597625       PASS
GitHub Actions 40146679013       PASS
```

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | QEMU/ELF/firmware 与工具哈希、compileall |
| transport | `PASS` | native HCI + HLI 到 Bumble |
| device_response | `PASS` | frame/QOM、WiFi/公网、NUS GATT |
| data_behavior | `PASS` | companion terminate、PID reap、lease release、连续新 session |
| visual_or_physical | `NOT RUN` | 无物理屏幕、RF、功耗或 cache/PSRAM 测量 |

## 未覆盖与风险

- 只验证 trusted-host 下的三个连续 active-stop session；
- 不覆盖 namespace-managed、Tab5 或 cross-host companion；
- 不覆盖 SIGHUP/drain 与 active QEMU 的组合、QMP 暂停态删除或 killed peer；
- 不证明 bit-exact controller/baseband、物理 cache/PSRAM、长时并发/吞吐；
- 不把 virtual-device 结果描述为物理硬件或 RF 结果。

## 回滚

回滚 `c36b790` 后再回滚
`3621301bef264447f79812530e157d3090826e5f`，可移除文档证据和新增 runner。
新 runner 只通过 Device Service API 操作虚拟设备，不包含数据库迁移、凭据或
不可逆硬件状态。
