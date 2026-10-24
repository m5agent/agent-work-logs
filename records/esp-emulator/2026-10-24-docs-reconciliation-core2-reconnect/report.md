# ESP Emulator 代码文档重整与 Core2 同 guest 重连边界报告

## 背景

- 来源：用户要求定期完整整理代码和文档，并指出部分页面与后续工作脱节；
- 目标：把当前能力、契约、验证、Backlog 和历史页重新对齐，同时把当前 Core2
  reconnect 实验准确归类；
- 约束：不得把 virtual-device 结果描述成真机/RF，不得用一次 active-link hold
  代替连接生命周期验证。

## 结论

- 状态：`PARTIAL`；
- 文档、API 和验证入口已对账；
- 第一轮 Core2 GATT 与 active-BLE 120 秒 hold 的既有 PASS 不变；
- 同一 guest 第二轮连接为 `FAIL`，失败发生在 cycle 1 disconnect 后；
- 两套固件对照证明测试用途 `gap_advertise()` 不是唯一触发条件；
- 当前 blocker 是 disconnect/HCI command lifecycle，需要 H2C/C2H transaction
  trace 才能继续定位。

## 改动范围

- 统一 `README.md`、`project-status.md`、`project-backlog.md`、
  `workstreams.md`、`code-map.md`、`validation-ledger.md` 和 Core2 专题页的状态；
- Device Service contract 从 `1.20.0` 升到 `1.21.0`，记录同一 peer process 的
  `ble_reconnect_cycles` 与 `ble_reconnect_delay_seconds`；
- `ble_probe.py` 支持默认一轮及最多 10 轮完整 scan/connect/GATT/disconnect，
  异常退出时清理当前连接；
- `run_service_5x.py` 增加 `--ble-reconnect-cycles`；
- 增加 stock 与测试重广告两个 Core2 对照，并固化 FAIL evidence；
- 文档契约测试阻止把同 guest reconnect 写回 PASS。

## 执行

```bash
PYTHONPATH=platform/tools:.work/py \
python3 -m unittest discover -s platform/tests -p 'test_*.py'

python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check

node platform/tests/test_sha256.mjs
node platform/tests/test_firmware_upload.mjs

python3 -m compileall -q platform tests
```

GitHub Actions CI run `40066005133` 的 `platform-contracts` 与
`network-namespace-policy` 两个 job 均通过。

重连门禁通过真实 Device Service `/api/v1` 创建一条 `core2-native-hci` session，
外部 peer 请求两个完整 cycle。两个固件变体都记录 serial、peer、pcap、QOM 和
evidence ZIP hash。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | `compileall`、平台契约、catalog/profile/coverage 与 Node 测试 |
| transport | `PARTIAL` | cycle 1 H2C/C2H、NUS subscribe/write/notify PASS；disconnect 后 HCI reset |
| device_response | `PARTIAL` | 第一轮 guest RX 与 notification PASS；第二轮没有 advertisement |
| data_behavior | `FAIL` | 同一 guest 的第二次 scan/connect/GATT 未建立 |
| visual_or_physical | `NOT RUN` | 本任务不验证显示、RF、功耗、声学、光学或机械属性 |
| hardware | `NOT RUN` | 全部为 virtual-device validation |

## 关键 artifact

| Variant | 固件 SHA256 | cycle 1 | cycle 2 | 观察 |
| --- | --- | --- | --- | --- |
| stock advertising lifecycle | `b9c91c40e60867186717938e075da8b19271cc8e7a22323524be213beff81982` | `PASS` | `TIMEOUT` | 未调用测试重广告仍出现 `ack 12` reset |
| guest scheduled re-advertise | `62693f5377264da0dda2bd9aaa0dc34aec624b88c51f13e3aa863622e090a198` | `PASS` | `TIMEOUT` | `OSError(-12,)` 后出现 `ack 12` reset |

匹配 ELF SHA256：
`5bec056bb775bcc94bc020e4fa411def097ea17b108dcd597d9cdab3c347db49`。

QEMU SHA256：
`667ec84c9e53ce73b0e63c7be69284837ff00b77a9194577ef757c164e8e31a1`。

## 验证边界

- 这是一次 targeted reconnect gate，不是完整矩阵；
- 未证明 `ack 12` 的第一个来源是 NimBLE host、Bumble command reply 还是 QEMU
  HLI 事件顺序；
- active BLE 两分钟 hold 只证明一条连接不断开，不证明断开后重连；
- 没有物理设备、RF、功耗、声学、光学或机械证据。

## 风险与回滚

风险仅限于新增诊断参数和测试固件路径，默认 `ble_reconnect_cycles=1` 保持原
一轮行为。回滚可整体 revert 源码提交
`e686838e38dc8ec46daa6dbc2830322806ca7355`。未修改或擦除物理设备。
