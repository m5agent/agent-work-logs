# ESP Emulator trusted-host unified companion continuity

- 日期：`2026-10-25`
- 结果：`PASS`（virtual-device same-host companion restart scope）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`61204890a1442ea6b88652fd5da53d678a8a826e`
- 结果版本：`3bd0f6655fc6495bd1653eac2f39c1139f1fed64`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40144639644>
- 环境：macOS Apple Silicon；central/runtime Device Service；真实 StickS3 QEMU；Bumble BLE peer；WorkerAgent

## 结论

Trusted-host `uiflow2-sticks3-unified` session 已达到以下同一 lease 连续性：

- BLE 初次 GATT 完成、HTTP generation 1 已持久化后，只 SIGKILL runtime
  Device Service；
- QEMU 保持同一 PID，新服务通过 PID/start-time/QMP ownership/running
  校验重新接管；
- HTTP fixture 在相同 profile port 恢复，并从 durable request log 进入
  generation 2；
- 存活 BLE peer 只有在 PID、精确 start-time 和完整 process command SHA256
  全部匹配时才被 adopt；
- 触发后同一 peer 完成 GATT cycle 2，同一 guest 对 HTTP generation 2
  再次请求并输出 `UNIFIED_STICKS3_HTTP_RECHECK_PASS`；
- Worker 使用有界 `evidence_delay_seconds` 等待最终数据面，再通过原 job /
  lease 采集 evidence；
- 最终 QEMU、BLE peer 和 HTTP fixture 均清理，无残留进程。

## 关键证据

- 统一 StickS3 镜像 SHA256：
  `04b008c60cf54d1e9fc52b8c9a1c2c4738a7ee046a64000779bebc8de9074c9d`；
- runtime downtimes：`2.2s`；
- same QEMU PID / session：PASS；
- recovery scope：`qemu-control-plane+companions`；
- HTTP generations：`[1, 2]`；
- BLE peer state：`running → adopted`；
- GATT cycle 2 和 guest HTTP recheck：PASS；
- network evidence：PASS；
- 26/26 checks PASS；
- 原 job/lease：`completed/PASS`；
- evidence ZIP：`42,247 bytes`；
- evidence ZIP SHA256：
  `8fe5e4c687e04db2d59bbdcddd75638dc82d4ff2c46674924945e04f588412ae`；
- ZIP 包含 `manifest.json`、`serial.log`、`ble-probe.log`、
  `http-fixture.json`、`network/evidence.json`、pcap、QEMU logs 和 PCM；
- QEMU/BLE companion 残留：无；
- platform tests `402/402`，docs `22/22`，Node `2/2`，CI 两个 job PASS。

源码 evidence：

<https://github.com/m5agent/m5stack-esp-emulator/blob/3bd0f6655fc6495bd1653eac2f39c1139f1fed64/tests/network/worker_runtime_restart/evidence-2026-10-25-runtime-companion-continuity-pass.json>

## 文件

- `report.md`：实现、执行、验证和边界；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：脱敏聚合证据；
- `patches/`：不适用，改动已包含在源码提交 `3bd0f66`；
- `code/`：不适用，复现入口在源码仓库测试目录。

## 未覆盖项

- namespace-managed、Tab5 和 cross-host companion recovery；
- cross-host QEMU migration/reattach；
- production multi-host scheduler；
- session-create response-loss recovery within this fixture；
- physical hardware、RF、功耗和电气行为。
