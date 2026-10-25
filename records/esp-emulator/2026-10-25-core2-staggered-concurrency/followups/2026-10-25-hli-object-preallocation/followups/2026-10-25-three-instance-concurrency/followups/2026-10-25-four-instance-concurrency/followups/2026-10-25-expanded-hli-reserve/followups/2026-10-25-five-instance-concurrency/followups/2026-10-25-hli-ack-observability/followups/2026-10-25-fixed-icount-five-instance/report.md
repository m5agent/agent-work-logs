# Core2 fixed-icount five-instance cold start 报告

## 背景

`0010` ACK-state trace 已证明旧 `shift=auto` 五实例失败不是初始 stale ACK
pointer，也不是物理 PSRAM/cache 故障。Bumble 返回首条 Reset Complete 后，
guest 在 PSRAM 初始化窗口关闭中断，HLI 事件已经进入队列但无法及时消费。
多个 QEMU 同时争用宿主时，自适应 icount 又放大了 guest 可见等待，使
delivery 越过 NimBLE ACK 预算。历史零错峰结果为一批 `5/5 PASS`、独立批
`3/5 FAIL`。

目标是让同一 five-instance/120-second 门禁在零错峰冷启动下可重复通过，同时
不放宽外部 NUS GATT、HLI health、frame、QOM、网络或 PSRAM 断言。

## 改动

- `platform/tools/qemu_accel.py` 默认使用固定
  `icount shift=5,align=off,sleep=off`；`M5_CORE2_ICOUNT_SHIFT` 只接受
  `auto` 或 `0-10`，作为显式诊断覆盖。
- `run_service_5x.py` 从实际 QEMU 进程命令行采样 accelerator 和 icount，
  并新增 `deterministic_icount` 门禁。
- `unified_core2/main.py` 把测试 BLE server 初始化提前到 WiFi 和长 PSRAM
  workload 前；外部 NUS GATT 和 active-link 判定不变。
- 固定时钟下五实例中一次 1 MiB 全缓冲 sweep 约需 10 秒，sustained 下限
  从历史 `hold/5` 校准为 `hold/10`；120 秒仍要求至少 12 次连续 sweep。
- 新增测试锁定两批 evidence 的原始 SHA、tool hashes、HLI/PSRAM/网络/frame/
  QOM/pcap 字段，并覆盖固定默认值、环境覆盖和非法输入。

## 执行

环境为 macOS arm64、Python 3.13、Node.js 和已补丁的 Xtensa QEMU。

关键验证：

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check
node platform/tests/test_sha256.mjs
node platform/tests/test_firmware_upload.mjs
```

结果：平台测试 `487/487 PASS`，文档契约 `37/37 PASS`，Node `2/2 PASS`；
coverage、peripheral catalog、QEMU profile、snapshot、compileall、
Ruff `E9/F` 和 `git diff --check` 均 PASS。GitHub Actions run
`40193742174` 的两个 job 均 PASS。

## 五实例证据

两批 `qemu-unified/profile=core2-native-hci` 均使用五个独立 lease、
`stagger_seconds=0`、`hold_seconds=120` 和最大并发 5。

| 批次 | 结果 | evidence SHA-256 |
| --- | --- | --- |
| A | `5/5 PASS` | `87dd71664fe4a9a7035051572a934254505608ce28313b7d5f0ff45fa857670a` |
| B | `5/5 PASS` | `8f9a913af3af0b4c43326a363dec0d5766df10379f7bdd8f27d1bf6a48508e9f` |

两批使用相同 firmware/ELF/QEMU 和已冻结 tool hashes，运行期间没有输入资产
漂移。每个 lease 的 frame SHA 均为
`cd2f2033fa92dabd8a60dd4e81bbefd3656b855123e762aef5080188ddf5192f`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `NOT RUN` | 本轮复用已构建并冻结的 test image；没有把旧构建等同于新源码 clean rebuild |
| flash | `PASS` | 每个 lease 通过真实 Device Service firmware/session 路径启动 |
| transport | `PASS` | UART HCI-offload、外部 BLE NUS GATT 和每 session pcap |
| device_response | `PASS` | frame、31 节点 QOM、WiFi DHCP/HTTP、公网 DNS/HTTP |
| data_behavior | `PASS` | 每 lease 14–15 次 1 MiB PSRAM 全缓冲读回，HLI 45/45 |
| visual_or_physical | `NOT RUN` | 无物理屏幕、RF、功耗或电气测量 |

## 验证边界

固定 icount 是确定性的虚拟时间，不表示实时速度、物理 cache/PSRAM timing
或 bit-exact controller。结论只覆盖当前固件 SHA、ELF、QEMU build、
`core2-native-hci` hook ABI、五个同时冷启动的 lease 和 120 秒窗口。

大于五实例、持续吞吐、active-stop 之外 teardown、RF、安全启动和真机仍需
独立验证。

## 风险与回滚

改动仅影响 Core2 QEMU 启动参数、测试 workload 顺序和门禁阈值。需要诊断时
可通过 `M5_CORE2_ICOUNT_SHIFT=auto` 临时恢复旧虚拟时间模型，但该覆盖不用于
concurrency PASS。回滚提交 `39e6295` 可恢复旧实现；历史失败 evidence 不应
删除。
