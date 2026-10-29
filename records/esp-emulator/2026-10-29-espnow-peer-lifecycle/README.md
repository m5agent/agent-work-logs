# ESP Emulator native ESP-NOW peer lifecycle

- 日期：`2026-10-29`
- 结果：`PASS`（限定 stock native guest encrypted peer add/delete/modify）/ `PARTIAL`（`RUNTIME-06` 总体）
- 工作类型：`code_change`
- 源码 Base：[m5stack-esp-emulator@cb689891](https://github.com/m5agent/m5stack-esp-emulator/commit/cb68989193768573238dc53afb026ef14ac7c229)
- 结果提交：[m5stack-esp-emulator@ccd23e41](https://github.com/m5agent/m5stack-esp-emulator/commit/ccd23e41dc941a65eca53f9962fdafda8aab7887)
- 环境：macOS arm64；QEMU virtual device；stock UIFlow2 `v2.5.3`；
  two independent Device Service sessions

## 结论

stock UIFlow2 `espnow.ESPNow` lifecycle runner 在两个设备对完成 encrypted
peer 生命周期：

- 初始 `add_peer(..., encrypt=True)` 后 `peer_count=[1,1]`；
- 双向 PRE barrier 后 `del_peer`，count 变为 `[0,0]`；
- 删除后 `get_peer` 和 `send` 均抛 `OSError`；
- 重新 `add_peer`、`mod_peer` 后 count 恢复 `[1,1]`；
- post-resume 双向 encrypted payload 重新交付。

StopWatch↔StickS3 与 Core2↔StopWatch 最终均 PASS。Core2 首轮的 runner
屏障竞态被保留为 failure control，并用“收到 PRE 后继续广播 1.5 秒再删除”
修正。

该结果关闭 stock native guest peer add/delete/modify 生命周期；guest
key-state 写入 QEMU bridge、key rotation、m5espnow wrapper、多 peer replay、
RF 和真机仍开放，因此 `RUNTIME-06` 保持 `PARTIAL`。

## 关键证据

- QEMU SHA256：`be7c376550829427b0fc72ada75f9d06e2246feaa64b2c222904d5a17a3c4076`
- runner SHA256：`7d1c4a9122cbb51316ccc91aecc3241449ec49b304cee62d3c0026ed4c4c23e4`
- StopWatch↔StickS3：双方 bridge TX/RX `16/16`，lifecycle 全项 PASS
- Core2↔StopWatch：Core2 TX/RX `51/35`、StopWatch `39/51`，lifecycle 全项 PASS
- 四个 session：`purge=0` 停止、runtime PID gone、history retained
- platform tests：`1479 OK + 1 skipped`
- generated checks：runtime coverage、peripheral catalog、QEMU profiles、
  project snapshot 全 PASS
- CI：[40810312221](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40810312221)
- 主仓证据：[ESP-NOW peer lifecycle](https://github.com/m5agent/m5stack-esp-emulator/blob/ccd23e41dc941a65eca53f9962fdafda8aab7887/docs/evidence/2026-10-29-espnow-peer-lifecycle/README.md)

## 文件

- `report.md`：API 依据、runner、failure control、边界和回滚
- `run.json`：机器可读记录
- `evidence/summary.json`：脱敏 machine summary
- `patches/`、`code/`：不适用；runner 已随主仓提交

## 未覆盖项

- guest key-state 写入 QEMU bridge、key rotation；
- `m5espnow.M5ESPNow` wrapper 同等生命周期；
- 多 peer/乱序 replay window、loss/retry；
- channel/rate、bit-exact controller、RF、电气、timing 和物理硬件。
