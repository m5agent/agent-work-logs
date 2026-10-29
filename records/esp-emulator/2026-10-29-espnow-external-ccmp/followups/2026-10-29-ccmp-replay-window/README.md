# ESP Emulator external CCMP 64-frame replay window

- 日期：`2026-10-29`
- 结果：`PASS`（限定单 peer authenticated reorder window）/ `PARTIAL`（`RUNTIME-06` 总体）
- 工作类型：`code_change`
- 上一里程碑：[CCMP replay rejection](../2026-10-29-ccmp-replay/)
- Base：[m5stack-esp-emulator@398509e9](https://github.com/m5agent/m5stack-esp-emulator/commit/398509e9492a1e95825e6d546f11462f6364b0e8)
- 结果提交：[m5stack-esp-emulator@1a90d3e6](https://github.com/m5agent/m5stack-esp-emulator/commit/1a90d3e6b50a6906a52081611240b289335ff9b0)
- 环境：macOS arm64；QEMU virtual device；stock UIFlow2 `v2.5.3`

## 结论

`0079` 将单 external encrypted peer 的严格 monotonic PN guard 升级为
64-frame authenticated bitmap。新 PN 向前推进窗口；window 内未见 older
PN 接受一次；duplicate 和窗口外 PN 丢弃。MIC 验证仍先于 replay state。

真实 UDP `ReorderProxy` 在两个方向均通信后暂存一帧，再交换前两帧。
receiver `replay_drops=0`，StopWatch↔StickS3 双向 payload 保持。
duplicate replay 负控仍各记录一次 drop，Core2 encrypted 回归 PASS。

该结果关闭单 peer bounded reordering，但 multi-peer window、PN wrap/
key rotation、guest key-state 写入 bridge、RF 和真机仍开放。

## 关键证据

- QEMU SHA256：`ef88746915960fe26a275cccfefcbb506cbc0f7d322747faad81a4a0916661cd`
- patch SHA256：`c4f40a614412db0b0c642f448820bb1acb8cf9bbe980df4e20e15d5c74556e0c`
- runner SHA256：`264f475e9c1d1725fde16112025219e8933e5fb7678b361e9f131692f1211708`
- ReorderProxy：双向各转发 `58` 帧、`reordered=true`、held frame released
- reorder receiver：replay drops `0`，peer payload `57/58`
- duplicate replay：StickS3 RX `59`、replay drop `1`
- Core2↔StopWatch encrypted 回归：`14/44`
- platform tests：`1487 OK + 1 skipped`
- CI：[40812108173](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40812108173)
- 主仓证据：[replay window](https://github.com/m5agent/m5stack-esp-emulator/blob/1a90d3e6b50a6906a52081611240b289335ff9b0/docs/evidence/2026-10-29-espnow-external-ccmp-window/README.md)

## 文件

- `report.md`：实现、reorder/duplicate 控制、边界和回滚
- `run.json`：机器可读记录
- `evidence/summary.json`：脱敏 machine summary
- `evidence/patch-check.txt`：patch 校验
- `patches/0001-esp32-espnow-external-ccmp-window.patch`：`0079` 原样 patch
- `patches/README.md`：preimage 与校验说明

## 未覆盖项

- multi-peer replay windows；
- PN wrap、key rotation；
- guest key-state 写入 QEMU bridge；
- loss/retry、channel/rate、bit-exact controller、RF 和物理硬件。
