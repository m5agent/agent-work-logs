# ESP Emulator M5ESPNow wrapper peer lifecycle

- 日期：`2026-10-29`
- 结果：`PASS`（限定 stock M5ESPNow wrapper encrypted peer add/delete/re-add）/ `PARTIAL`（`RUNTIME-06` 总体）
- 工作类型：`code_change`
- 上一里程碑：[native ESP-NOW peer lifecycle](../../README.md)
- Base：[m5stack-esp-emulator@ccd23e41](https://github.com/m5agent/m5stack-esp-emulator/commit/ccd23e41dc941a65eca53f9962fdafda8aab7887)
- 结果提交：[m5stack-esp-emulator@398509e9](https://github.com/m5agent/m5stack-esp-emulator/commit/398509e9492a1e95825e6d546f11462f6364b0e8)
- 环境：macOS arm64；QEMU virtual device；stock UIFlow2 `v2.5.3`

## 结论

`m5espnow.M5ESPNow` wrapper 在 StopWatch↔StickS3 与 Core2↔StopWatch 完成
external encrypted peer 生命周期：`set_add_peer`、peer list/count `[1,1]`、
bidirectional PRE barrier、`set_delete_peer`、peer list empty、
delete 后 `send_data` no-op、re-add、peer list 恢复和 post-resume 双向 payload。

wrapper 的删除后发送行为与 native API 不同：M5ESPNow 在 peer-id slot 为空时
静默跳过底层 `send`，不抛 `OSError`。本轮按 wrapper 实际语义分别验证，不把
native NOT_FOUND 结果套到 wrapper。

该结果关闭 stock M5ESPNow wrapper add/delete/re-add 生命周期；guest key-state
写入 QEMU bridge、key rotation、多 peer replay、RF 和真机仍开放。

## 关键证据

- QEMU SHA256：`be7c376550829427b0fc72ada75f9d06e2246feaa64b2c222904d5a17a3c4076`
- runner SHA256：`6cf511cd66e5f2a1580ee87c8ec63f50952428d22e8b428e427048859a294fd9`
- StopWatch↔StickS3：双方 bridge TX/RX `15/15`，wrapper lifecycle 全项 PASS
- Core2↔StopWatch：Core2 TX/RX `21/32`、StopWatch `33/21`，全项 PASS
- 四个 session：`purge=0`、runtime PID gone、history retained
- platform tests：`1481 OK + 1 skipped`
- generated checks：runtime coverage、peripheral catalog、QEMU profiles、
  project snapshot 全 PASS
- CI：[40811149946](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40811149946)
- 主仓证据：[M5ESPNow lifecycle](https://github.com/m5agent/m5stack-esp-emulator/blob/398509e9492a1e95825e6d546f11462f6364b0e8/docs/evidence/2026-10-29-espnow-m5espnow-lifecycle/README.md)

## 文件

- `report.md`：API、结果、边界和回滚
- `run.json`：机器可读记录
- `evidence/summary.json`：脱敏 machine summary
- `patches/`、`code/`：不适用；runner 已随主仓提交

## 未覆盖项

- guest key-state 写入 QEMU bridge、key rotation；
- 多 peer/乱序 replay window、loss/retry；
- channel/rate、bit-exact controller、RF、电气、timing 和物理硬件。
