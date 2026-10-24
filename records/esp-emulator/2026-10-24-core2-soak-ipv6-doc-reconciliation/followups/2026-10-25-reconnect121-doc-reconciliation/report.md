# ESP Emulator 当前工作整理与 Core2 121 轮 reconnect 报告

## 背景

项目文档此前已经过度分散：动态计数、当前结论、在途工作和历史失败在不同页面
重复出现。部分页面仍在描述已经完成的限容两小时 soak，也有页面继续把服务重启
视为所有活动 session 一律失败，未反映已验证的 QEMU/QMP re-attach。

Core2 121 轮 reconnect 也暴露出两个 harness 问题：

- 第一次运行完成 29 轮并开始第 30 轮，固定 `180s` 预算终止了仍在推进的 guest；
- 第二次运行完成 `121/121` 功能检查，但 reconnect-only 路径没有 hold loop，
  QEMU accelerator 采样为空，导致 `bounded_tcg_cache` 假失败。

两次失败都不是 guest、NimBLE 或 BT controller 故障。

## 代码与文档改动

- README、current status、Backlog、workstreams、validation ledger、代码地图、
  Device Service 契约、Core2 专题和设备生成档案按单一事实源重整；
- readiness 预算集中到 `ble_runtime_limits.py`，由 runner 和 Device Service
  共用；
- runner 在 session 首次 running 时采样 live QEMU accelerator，不再依赖 hold；
- 原始失败 evidence 保留，新的 PASS 明确 supersede 关系；
- 项目快照由 catalog/profile/evidence/Backlog 重新生成。

## 执行

使用已推送的代码 commit 启动隔离 Device Service，并以固定 firmware、ELF 和
QEMU 执行一个 `core2-native-hci` / `qemu-unified` lease：

```text
attempts=1
ble_reconnect_cycles=121
ble_reconnect_delay_seconds=2
ready_timeout_seconds requested/effective=180/1028
accelerator=tcg,thread=single,tb-size=128
```

runner 在首 lease 前冻结 firmware、ELF、QEMU 和四个工具文件哈希，结束后重新
计算；drift 为空。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build/contract | PASS | 355/355 platform tests、19/19 docs、Node 2/2、三个 CI run |
| transport | PASS | Device Service API、HCI/HLI、Bumble GATT、pcap |
| device_response | PASS | WiFi/DHCP/HTTP、公网 DNS/HTTP、NUS GATT |
| data_behavior | PASS | 121 个完整 scan/connect/NUS/disconnect cycle |
| visual | PASS（virtual） | 3710-byte frame，SHA256 与既有基线一致 |
| physical | NOT RUN | 无真机、RF、功耗或电气测量 |

121 轮关键计数：

```text
HLI posts/consumed=3405/3405
C2H events/ACLs=2316/1089
HLI errors=0
HLI/meta/TX queues=0/0/0
dropped=0
last-error=0
peer-closed=0
panic=0
QOM nodes=34
pcap bytes=12670
```

## 验证边界

- PASS 只覆盖该 firmware SHA、Core2 native-HCI profile、单 lease 和 121 轮窗口；
- 尚未完成另外两个独立 lease，不能宣称 `3/3` 可复现；
- 不证明物理 cache/PSRAM 时序、bit-exact controller/baseband、RF 或真机；
- 服务 session 最终为 stopped，QEMU 进程已回收。

## 风险与回滚

无物理设备写入或其他不可逆操作。回退顺序：

1. `fa38050` 撤销 reconnect accelerator 采样修复；
2. `884885c` 撤销 workload-aware readiness 预算；
3. `74b45b3`/`d9008a3` 回退文档和 evidence 对账。
