# Core2 会话直接解码 UART core dump

- 日期 `2026-11-17`
- 结果 `PASS`，限下述两份原生 Core2 来宾夹具和 UART 格式
- 工作类型 `code_change`
- 问题来源 固件审核所需的同会话崩溃与任务上下文
- 源码版本 Device Service `3748b02807cdcd22096e70b5f647c7385164ba08`
- 环境 Core2 原生 Xtensa QEMU、ESP-IDF v5.5.4，virtual-device validation

## 结论

普通 `/crash` API 和同会话 ZIP 自动校验 Core2 的 ELF32 CRC32 UART dump，并返回故障任务及保存的任务 PC、SP。真实 CPU1 中断 watchdog 和 abort 来宾分别读得 5、6 个上下文。匹配的应用 ELF 分别将故障任务的保存 PC 解析到 `trigger_fault` 和 `panic_abort`。

## 关键证据

- 两份新会话使用同一 QEMU 可执行文件和已有的两个固定探针 BIN。任务上下文在串口完成传输后读出。
- 普通 API 和 ZIP 内的完整诊断对象一致，ZIP CRC 与串口范围 SHA-256 均通过。缺少或替换 ELF 时保留已校验的上下文，省略任务符号。停止并重启独立服务后复读一致。
- 同一 ZIP 的离线官方解码对照确认两份 dump 的 CRC、SHA-256 和任务数，并将故障任务命名为 `fixture_fault`。[验证摘要](evidence/session-task-context-summary.json)

## 文件

- [完整报告](report.md)
- [结构化记录](run.json)
- [脱敏证据](evidence/session-task-context-summary.json)
- [复现工程与命令](https://github.com/m5agent/m5stack-esp-emulator/tree/3748b02807cdcd22096e70b5f647c7385164ba08/tests/firmware/crash_diagnostics)

源码与测试工程发布在 ESP Emulator。单独的补丁、原始设备产物和完整运行日志不随此记录归档。

## 未覆盖项

HTTP 任务名称、优先级、栈用量、现场任务调度和其他 dump 格式待验证。实机、浏览器、常驻部署与 Burner 均未执行。

[组合版本原生复验](evidence/combined-native-summary.json)
