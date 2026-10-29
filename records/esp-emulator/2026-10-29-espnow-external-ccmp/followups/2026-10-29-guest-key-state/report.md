# Report

## 问题与目标

前序 `0077`–`0079` 已证明 external ESP-NOW bridge 的真实 CCMP/MIC 和
单 peer replay window，但 encrypted 使用的 PMK/LMK 来自 trusted-local
runtime-env fixture。目标是把 stock guest `set_pmk`/`add_peer` 编程的
controller key-state 接到同一数据面，并验证错误 guest LMK 与 key rotation。

## 根因

匹配固件的 `mt_set_lmk -> ic_set_key -> hal_crypto_set_key_entry` 路径
最终写 WiFi crypto key store，而不是经过可观察的 DMA payload：

- classic ESP32：control `0x3ff73800`，key store `0x3ff74400`；
- ESP32-S3：control `0x60033800`，key store `0x60034400`；
- 每 entry `40` bytes，16-byte key data 从 entry `+8` 开始；
- stock guest 首选 extended slot `24`，valid mask 为 `0x01000000`。

此前模型既未接入这两个窗口，也没有在 bridge 使用 guest key。

## 改动

`0080-esp32-espnow-guest-key-state.patch`：

1. 为 WiFi controller 增加独立 control/key MemoryRegion；
2. 在 classic ESP32 与 ESP32-S3 SoC mapping 中接入两个窗口；
3. key data 必须完整写满 16 bytes 且 valid bit 已置位才 arm；
4. 新增 guest-key mode：bridge 没有 env PMK/LMK 时使用捕获的 active key；
5. key replacement、slot clear 和 cleanup 清 active key、PN 和 replay state；
6. trace 只输出 slot、mask、state，不输出 key bytes。

runner 新增 `guest-key`、`guest-key-wrong-lmk` 和
`guest-key-rotation`。guest-key 场景不设置
`M5SW_ESPNOW_PEER_PMK/LMK`。rotation 先完成初始共享 key 通信，
`del_peer` 清 key，re-add 后 `mod_peer` 切到新共享 LMK，再完成
post-resume 通信。

## 执行与证据

最终 QEMU binary：
`d2f25608dce3d4b4ff8951b1b89a778d52a57286bfb460f7959ddec696e48796`。

| 场景 | 设备对 | guest key ready | 结果 |
| --- | --- | ---: | --- |
| 正控 | StopWatch↔StickS3 | 1 + 1 | payload `57/58` PASS |
| 正控 | Core2↔StopWatch | 1 + 1 | payload `15/44` PASS |
| wrong guest LMK | StopWatch↔StickS3 | 1 + 1 | 两端 `EXPECTED_DROP`、RX `0` |
| wrong guest LMK | Core2↔StopWatch | 1 + 1 | 两端 `EXPECTED_DROP`、RX `0` |
| rotation | StopWatch↔StickS3 | 4 + 4 | pre/re-add/post PASS |
| rotation | Core2↔StopWatch | 4 + 4 | pre/re-add/post PASS |

十二个 session 均 terminal `stopped`、QEMU PID 消失、history retained，
并 `purge=0`。每个 key-ready 记录均先由 controller valid bit 和完整
16-byte data 触发。

## 检查

- patch：forward check、apply 后对当前 source `cmp`、reverse check PASS；
- platform：`1494` tests，`OK (skipped=1)`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  PASS；
- compileall、scoped Ruff `E9/F`、`git diff --check`：PASS；
- CI `40814876612`：`platform-contracts` 和
  `network-namespace-policy` 均 PASS。

## 兼容性与回滚

env-key fixture 路径保留，现有 `encrypted` / `wrong-lmk` / `wrong-pmk`
测试不改变；新 guest-key 场景不设置 key env。回滚 `0080` 和 runner
guest-key scenarios 即可恢复 `0079` 的单 peer fixture 行为。

## 未覆盖

- multi-peer key routing 和每 peer replay window；
- 3+ peer fabric、PN wrap、loss/retry 和完整 key lifecycle；
- channel/rate、bit-exact controller；
- RF、antenna、电气、timing 和 physical hardware。
