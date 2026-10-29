# ESP Emulator external ESP-NOW CCMP replay rejection

- 日期：`2026-10-29`
- 结果：`PASS`（限定单 peer authenticated CCMP PN replay）/ `PARTIAL`（`RUNTIME-06` 总体）
- 工作类型：`code_change`
- 上一里程碑：[external ESP-NOW CCMP](../../README.md)
- Base：[m5stack-esp-emulator@82118424](https://github.com/m5agent/m5stack-esp-emulator/commit/82118424bca82266041015480ef32b5920c205da)
- 结果提交：[m5stack-esp-emulator@cb689891](https://github.com/m5agent/m5stack-esp-emulator/commit/cb68989193768573238dc53afb026ef14ac7c229)
- 环境：macOS arm64；QEMU virtual device；stock UIFlow2 `v2.5.3`；
  UDP replay proxy

## 结论

`0078` 为单个 encrypted external ESP-NOW peer 保存最后一个 MIC 成功的
CCMP PN。只有 authenticated frame 能推进状态；equal/older PN 在完整 RX
DMA 注入前丢弃。UDP replay proxy 在两个方向都已通信后只重复一帧；
StickS3 receiver 记录恰好一次 `CCMP PN replay` drop，正常 payload 仍为
唯一帧数量。

wrong-LMK 负控和 Core2↔StopWatch encrypted 回归保持 PASS。该结果关闭单
peer monotonic replay fixture，但 `RUNTIME-06` 仍为 `PARTIAL`：多 peer/
乱序 replay window、PN wrap/key rotation、guest key-state、peer lifecycle、
RF 和物理硬件未覆盖。

## 关键证据

- QEMU SHA256：`be7c376550829427b0fc72ada75f9d06e2246feaa64b2c222904d5a17a3c4076`
- `0078` patch SHA256：`b30c56272dba2fd6e4000ee8b12f82a08e57ccadf8bc8e0d0d42488b5baa1adc`
- runner SHA256：`9778e0d8a10e05e839c6f6aff542077ff8c7da5bb5e943aab71d427240992ac9`
- replay proxy：双向各转发 `58` 帧、`replay_sent=true`、无 proxy error
- receiver：TX `58` / RX `59`、replay drop `1`、正常 peer payload `58`
- wrong-LMK：双向 `40/40` bridge traffic、`0` peer payload、`EXPECTED_DROP`
- Core2↔StopWatch encrypted：`15/44` peer payload
- platform tests：`1475 OK + 1 skipped`
- generated checks：runtime coverage、peripheral catalog、QEMU profiles、
  project snapshot 全 PASS
- CI：[40809207085](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40809207085)
- 主仓证据：[CCMP replay](https://github.com/m5agent/m5stack-esp-emulator/blob/cb68989193768573238dc53afb026ef14ac7c229/docs/evidence/2026-10-29-espnow-external-ccmp-replay/README.md)

## 文件

- `report.md`：实现、运行控制、验证边界和回滚
- `run.json`：机器可读记录
- `evidence/summary.json`：脱敏 machine summary
- `evidence/patch-check.txt`：forward/current/reverse 验证
- `patches/0001-esp32-espnow-external-ccmp-replay.patch`：`0078` 原样 patch
- `patches/README.md`：preimage 与校验说明

## 未覆盖项

- 多 peer、乱序和固定 replay window；
- PN wrap、key rotation 和 guest key-state 传播；
- peer add/update/delete、loss/retry；
- channel/rate、bit-exact controller、RF、电气、timing 和物理硬件。
