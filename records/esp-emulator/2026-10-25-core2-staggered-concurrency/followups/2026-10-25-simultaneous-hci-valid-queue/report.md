# ESP Emulator Core2 simultaneous HCI delivery 报告

## 背景

上一记录关闭了 Core2 `qemu-unified/core2-native-hci` 在 `30s` 启动错峰后的
双 lease 稳态并发，但保留了两个问题：

- shared host HTTP port collision；
- no-stagger cold start 的第二个 guest `ble_hs_hci_process_ack`
  `LoadProhibited`。

HTTP fixture 已在上一记录改为 per-session QEMU `guestfwd`。本 follow-up
继续处理 no-stagger 路径，并同步整理代码、设备 catalog、当前状态、
Backlog、验证台账和生成文档。

## 根因与判断

### 已修正的 HLI 调度竞态

旧实现允许 `esp32_native_hci_schedule_hli()` 在 guest scheduler/meta queue
尚未有效时安排工作项。一次扩展运行 `4x120s` 的结果为 `3 PASS / 1 FAIL`：

```text
hli-posts=45
hli-consumed=45
hli-errors=3
peak_data.ble_hs_hci_process_ack-panic
```

所有 HCI packet 最终仍被消费，说明错误发生在投递调度路径而非 H4 framing。
`0007` 增加：

```c
!s->hli_valid
```

只有最近一次 `observe_hli()` 成功观察到有效 guest queue 时才允许调度。
该 gate 不修改或清除 counter。

同一固件、ELF、QEMU 和工具哈希下，新实现首批四 lease 为 `4/4 PASS`，
每次 HLI `45/45`、`hli-errors=0`。

### 尚未定位的 cold-start guest panic

独立四 lease 复核没有复现 HLI counter 错误，但首个并发批的一个 guest
仍出现：

```text
LoadProhibited at 0x402630cc
symbol: ble_hs_hci_process_ack
peer GATT stalled before discovery
```

另一个 guest 正常完成并进入 `120s` hold。runner 将 aggregate 结果写为
`FAIL`，未用后续 attempt 覆盖首轮失败。

因此本记录不把“首批 4/4 PASS”写成 cold-start closed。当前判断是：

1. observed-invalid HLI scheduling 已修复；
2. no-stagger 仍有独立的 guest ACK/controller 生命周期竞态；
3. 该竞态需要继续结合 guest ELF、QEMU HLI/API boundary 和 host BLE peer
   时序定位。

## 改动范围

- `ble_probe.py`：新增有界 `--gatt-request-timeout`；
- Device Service：extended exchange 的 GATT request 和 notification timeout
  均为 `30s`；
- QEMU `0007`：HLI delivery 要求最近观察到的 guest queue valid；
- 测试：覆盖 extended timeout 参数、QEMU/patch 边界、四份 mixed evidence
  和文档口径；
- catalog：新增 `concurrency_validation` 字段，由 generator 输出到设备 JSON、
  `firmware.json` 和设备 README；
- `project_snapshot.py`：只在整个 Markdown table cell 由反引号包裹时移除
  code fence，避免 Backlog 末尾 inline code 被吞掉；
- README、项目状态、工程交接、工作流、Backlog、验证台账、Core2 专题和
  测试索引统一为同一结论。

## 执行环境

```text
host: macOS Apple Silicon
python: 3.13
node: 20
accelerator: tcg,thread=single,tb-size=128
runtime: qemu-unified
profile: core2-native-hci
firmware: 5ed4fcfad22c50d10d9a1af48bdb8e7b7e125a6fa278d3f8e30e53bd03aa43db
elf: 5bec056bb775bcc94bc020e4fa411def097ea17b108dcd597d9cdab3c347db49
```

QEMU hashes：

- timeout-only build：
  `80d3c50d1cc1d24a9686492bcb064891d43b7058c4e829ba2dc5879fbfee8881`
- valid-queue-gate build：
  `d69dcfa1ebb48cd8ed32361648226a96b036f93f1262f72811e6e1d30ec655c9`

## 验证

### 代码与静态检查

```text
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
462 tests PASS

PYTHONPATH=platform/tools python3 platform/tests/test_docs_consistency.py
36 tests PASS

PYTHONPATH=platform/tools python3 platform/tests/test_qemu_profiles.py
19 tests PASS

node --test platform/tests/test_sha256.mjs \
  platform/tests/test_firmware_upload.mjs
2 tests PASS
```

coverage/catalog/profile/snapshot、Ruff `E9/F`、compileall、QEMU patch
reverse-check 和 `git diff --check` 均 `PASS`。

GitHub Actions `40170434652` 的 `platform-contracts` 与
`network-namespace-policy` 两个 job 均 `PASS`。

### 无错峰并发

| 运行 | 结果 | 说明 |
| --- | --- | --- |
| timeout-only 2 lease | `2/2 PASS` | GATT timeout `30s` |
| timeout-only 4 lease | `3/4 FAIL` | 失败轮 `hli-errors=3` |
| valid-queue gate 4 lease | `4/4 PASS` | 每轮 HLI `45/45`、errors 0 |
| independent confirmation | `1/2 FAIL` | guest LoadProhibited；runner 停止 |

每轮通过 lease 均包含 WiFi、公网 DNS/HTTP、external NUS GATT、active BLE、
30+ 次 `1 MiB` PSRAM sweep、frame/QOM、pcap、bounded TCG、evidence 和
cleanup。

## 验证边界

- 所有结果都是 `virtual-device validation`；
- 不证明 physical PSRAM/cache timing 或容量性能；
- 不证明 bit-exact Espressif BT controller/baseband；
- 不证明 RF、功耗、电气、机械或光学；
- 不证明 no-stagger cold start 已稳定；
- 当前 QEMU hook/build 只对绑定 firmware、ELF 和 QEMU SHA 成立。

## 风险与回滚

`0007` 是一行调度前置条件，不删除 packet、不修改 health threshold。
若后续验证发现 valid queue 观察本身会成为长时间 stall，可回滚 `0007`，
并把 HLI scheduling 问题保留为独立 blocker；GATT timeout 改动可单独保留。

代码回滚对应源码提交 `2177925` 或 patch reverse apply；文档和 catalog
口径随 `8243850` 一起回滚。
