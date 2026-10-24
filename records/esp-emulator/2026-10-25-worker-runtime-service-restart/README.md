# ESP Emulator Worker Runtime-service Restart Continuity

- 日期：`2026-10-25`
- 结果：`PASS`（virtual-device runtime restart scope）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`cd0308025309fcb6dfd373502e87890449a1f98c`
- 结果版本：`cd3adc70b815a61f216286250676e0ef7aa8a77d`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40141703399>
- 环境：macOS Apple Silicon；central/runtime Device Service；真实 StickS3 QEMU；WorkerAgent

## 结论

Worker claim job 并启动真实 StickS3 QEMU 后，只对 worker-local runtime
Device Service 发 `SIGKILL`；QEMU 子进程保持运行。`2.2s` 后同 port/state
启动新的 runtime service，并按以下证据重新接管同一 session：

- 同一 session ID；
- 同一 QEMU PID；
- PID start-time 内部校验；
- session-specific QMP socket ownership；
- `query-status=running`；
- `reattached_process=true`。

WorkerAgent 对已知 `session_id` 的 status/evidence/stop 做有界 transient
retry，但不盲重试 session create。原 job 最终：

```text
central job status       completed
result state             PASS
same lease               PASS
same worker identity     PASS
```

Evidence ZIP 来自重启后的 runtime service，包含 `manifest.json`、serial、
QEMU stdout/stderr；会话随后 stopped、PID released，QEMU process reaped。

## 关键证据

- 平台测试：`394/394 PASS`；
- 文档契约：`20/20 PASS`；
- Node SHA256/upload：`2/2 PASS`；
- runtime downtime：`2.2s`；
- same session / PID / start-time / QMP reattach：`PASS`；
- worker runtime retry/reconnect：`PASS`；
- evidence ZIP：`2,422 bytes`；
- evidence SHA256：
  `72a85a6cea32950e8c0cec044dabfe5022f4f60e6dcd7370a99f7f7b8430dd9c`；
- ZIP：`manifest.json`、`serial.log`、`serial1.log`、`qemu.stdout`、
  `qemu.stderr`；
- runtime session stopped、PID released、QEMU absent：`PASS`；
- token 未进入 worker log；
- GitHub Actions 两个 job 均 PASS。

源码 evidence：

<https://github.com/m5agent/m5stack-esp-emulator/blob/cd3adc70b815a61f216286250676e0ef7aa8a77d/tests/network/worker_runtime_restart/evidence-2026-10-25-runtime-restart-pass.json>

## 文件

- `report.md`：设计和验证；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：脱敏聚合证据。

## 未覆盖项

- session create 响应丢失后的 dedup 恢复；
- cross-host QEMU 进程迁移或 reattach；
- companion HTTP/BLE helper continuity；
- Tab5/network lane reattach；
- 生产多机 scheduler；
- physical hardware validation。
