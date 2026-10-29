# ESP Emulator external ESP-NOW guest controller key-state

- 日期：`2026-10-29`
- 结果：`PASS`（限定单 peer virtual-device controller key-state / rotation）
  / `PARTIAL`（`RUNTIME-06` 总体）
- 工作类型：`code_change`
- 问题来源：`RUNTIME-06` guest `set_pmk`/`add_peer` key-state 和 key rotation
- Base：[m5stack-esp-emulator@1a90d3e6](https://github.com/m5agent/m5stack-esp-emulator/commit/1a90d3e6b50a6906a52081611240b289335ff9b0)
- 结果提交：[m5stack-esp-emulator@2f048c9f](https://github.com/m5agent/m5stack-esp-emulator/commit/2f048c9fc4b6479d1c264ce79d780ca3f1b94427)
- Snapshot 收尾：[m5stack-esp-emulator@96ee9f33](https://github.com/m5agent/m5stack-esp-emulator/commit/96ee9f33a55a565f45a72315d29a91993f69cd46)
- 环境：macOS arm64；QEMU virtual device；stock UIFlow2 `v2.5.3`

## 结论

`0080` 将 classic ESP32 与 ESP32-S3 WiFi crypto key store 映射到 controller
MMIO。external bridge 未配置 runtime-env PMK/LMK 时，只有 stock guest
通过 `set_pmk`/`add_peer` 写满 16-byte extended key 且 valid bit 置位后，
模型才启用 encrypted 路径。

StopWatch↔StickS3 与 Core2↔StopWatch 均在不传 PMK/LMK 的情况下完成双向
payload 交付。不同 guest LMK 负控两端 `rx_packets=0`；delete/re-add/modify
后切换到新共享 LMK，post-resume 双向交付恢复。该结果关闭单 peer stock
guest key-state 和 rotation。

全部为 **virtual-device validation**。`RUNTIME-06` 仍为 `PARTIAL`：
multi-peer key routing/每 peer replay window、3+ peer fabric、PN wrap、
loss/retry、channel/rate、RF 和真机为 `NOT RUN`。

## 关键证据

- QEMU SHA256：`d2f25608dce3d4b4ff8951b1b89a778d52a57286bfb460f7959ddec696e48796`
- `0080` patch SHA256：`c827a3e6e76f591b319379342e099a5cd4ffd086029fb514cb99c61a72e2babc`
- runner SHA256：`23791688c70ca6c1c7c3ac171d021bb8c1c9b82d38ecad2602d92da6ae06472a`
- guest key：extended slot `24`、valid mask `0x01000000`、16-byte LMK
- S3 encrypted payload：`57/58`；classic mixed payload：`15/44`
- wrong guest LMK：四方向 `EXPECTED_DROP`、guest RX `0`
- rotation：两个设备对 pre-sync / re-add / post-resume 全 PASS
- platform tests：`1494 OK + 1 skipped`
- GitHub CI：[40814876612](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40814876612)
- 主仓证据：[guest key-state](https://github.com/m5agent/m5stack-esp-emulator/blob/96ee9f33a55a565f45a72315d29a91993f69cd46/docs/evidence/2026-10-29-espnow-guest-key-state/README.md)

## 文件

- `report.md`：根因、MMIO 模型、执行和边界
- `run.json`：机器可读记录
- `evidence/summary.json`：脱敏 machine summary
- `evidence/patch-check.txt`：patch apply/current/reverse 验证
- `patches/0001-esp32-espnow-guest-key-state.patch`：`0080` 原样 patch
- `patches/README.md`：patch 和 preimage 校验说明

## 未覆盖项

- multi-peer key routing、每 peer replay window、3+ guest fabric；
- PN wrap、loss/retry 和更完整 key lifecycle；
- channel/rate、bit-exact controller；
- RF、antenna、电气、timing 和 physical hardware。
