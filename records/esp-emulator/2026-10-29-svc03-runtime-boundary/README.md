# ESP Emulator SVC-03 runtime boundary and Core2 unified stability

- 日期：`2026-10-29`
- 结果：`PASS`（本里程碑）
- 工作类型：`code_change`
- 问题来源：`SVC-03`，Core2 unified service timing follow-up
- 源码版本：`m5agent/m5stack-esp-emulator@fa5610bd2f1e880f46fc2cbaf56d4c2ceb20617c`
- 合并版本：`20ae4413ed577159db98782a2f4419e504e5b76f`
- 环境：macOS Apple Silicon；Python 3.12；Device Service；QEMU virtual Core2

## 结论

完成 `SVC-03` 的第二个无状态边界：QEMU runtime memory policy、PSRAM
mismatch、私有 runtime env 集合和脱敏 helper 移入
`device_service_runtime.py`，`device_service.py` 保持 same-object
re-export。

同一里程碑修复了两个 unified service harness 假失败：profile QOM 注入不再
固定等待 20 秒，而是跟随 session readiness；Core2 unified profiles 默认
180 秒。外部 unified BLE peer 在订阅后等待 10 秒再写，并同步扩大 reconnect
预算。最终 firmware/ELF/QEMU 上三个独立 `/api/v1` lease 全部完成 frame、
QOM、WiFi、公网 HTTP、NUS notification、HLI、pcap、ZIP 和 cleanup。

## 关键证据

- full platform：`1581 OK + 1 skip`；
- Device Service matching tests：`142/142 PASS`；
- runtime helper boundary：`6/6 PASS`；
- Core2 native-HCI service：最终 QEMU 与旧对照 QEMU 各 `3/3 PASS`；
- 每个 lease：3,888-byte 同 SHA frame、32-node QOM、8 MiB effective PSRAM、
  HLI `45/45`、36 events/9 ACLs、零 errors/queues/drops；
- PR #46 CI 4/4 PASS；
- runtime coverage、peripheral catalog、QEMU profiles、snapshot、Ruff、
  compileall 和 diff check PASS。

## 文件

- `report.md`：根因、改动、执行、边界和回滚
- `run.json`：结构化记录
- `evidence/verification.summary.json`：测试、运行和交付摘要

## 未覆盖项

- `SVC-03` 仍在进行中；store、runtime adapter、evidence collector、
  lifecycle/history 和 HTTP facade 尚未拆分；
- 所有结果为 virtual-device validation；物理硬件、RF、天线、BLE 安全/配对、
  电气和物理 timing 为 `NOT RUN`；
- Core2 legacy UIFlow `RUNTIME-03` 仍为 `OPEN`。
