# Report

## 问题与目标

`0081` 已经验证三 guest shared-LMK fabric，但每个 guest 实际只用最高
priority 的一个完整 guest key。目标是根据 stock key-store 中的 peer
metadata 为不同 destination/source peer 选择不同 LMK，并加入错配负控。

## Controller 证据

匹配 UIFlow2 ELF 的 stock `wDev_Insert_KeyEntry`：

1. 从 peer address pointer 复制 6 bytes 到 descriptor `+3`；
2. 把 key index/type 写入 descriptor 前三个 bytes；
3. 调用 `hal_crypto_set_key_entry`；
4. hal 把 peer MAC 写入 controller key entry 的前 6 bytes，LMK 从 `+8`
   开始。

ESP32-S3 的 `hal_crypto_set_key_entry` 位于 `0x42182fc0`，classic ESP32
位于 `0x402e2178`。stock UIFlow2 三 guest 场景把两个 peer 写入 extended
slots `23`、`24`。

## 改动

`0082-esp32-espnow-per-peer-key-routing.patch`：

1. 保存每个 slot 的 8-byte key metadata；
2. slot ready 条件要求 valid bit、metadata 和 16-byte LMK 全部完成；
3. fabric TX 用 receiver peer 查找 LMK；
4. fabric RX 用 authenticated frame 的 transmitter peer 查找 LMK；
5. 每个 guest key slot 维护独立 TX PN；
6. key metadata/LMK replacement 和 cleanup 清理 mapping/Pn state。

runner 新增 `fabric-per-peer-key` 和
`fabric-per-peer-key-negative`。negative 只将 B 对 A 的 key 改成 B-C 的
key，并严格比较 expected link、source match 和 payload match 三个矩阵。

## 执行

最终 QEMU：
`9c36bb527f441b65acc16aff09728ae66e98ea19957a42fbc8bc087d52c9e5e0`。

| 场景 | A | B | C | 结果 |
| --- | --- | --- | --- | --- |
| shared LMK | B `205`, C `225` | A `210`, C `225` | A `56`, B `56` | PASS |
| pairwise LMK | B `213`, C `225` | A `211`, C `225` | A `56`, B `56` | PASS |
| cross-wire | B `0`, C `226` | A `0`, C `226` | A `45`, B `46` | expected PASS |

cross-wire 中 broker 仍转发六个 directed path，说明负控作用在 key
selection/MIC，而不是 broker 断链。A/B `source_matches` 对错误 peer 也为
`0`，trace 分别有 `470/472` 次 peer-key/CCMP failure，C 为 `0`。

shared-LMK 与 direct `guest-key` 回归均 PASS。四条 lane 共 11 个
session，全部 `purge=0`、terminal `stopped`、runtime PID gone、
history retained。

## 检查

- ESP-NOW contracts：`47/47 PASS`；
- full platform：`1506` tests，`OK (skipped=1)`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  PASS；
- compileall、new-contract Ruff 和 `git diff --check`：PASS；
- patch forward/current-source/reverse：PASS；
- CI `40819478506`：`platform-contracts` 与
  `network-namespace-policy` 均 PASS

## 兼容性与回滚

direct guest-key 仍使用最高 priority 完整 key；只有 fabric 模式按 peer
metadata routing。回滚 `0082` 和两个 pairwise scenario 即可恢复 `0081`
shared-LMK fabric。

## 未覆盖

- PN wrap 和更完整 key lifecycle；
- loss/retry、channel/rate；
- bit-exact controller；
- RF、antenna、电气、timing 和 physical hardware。
