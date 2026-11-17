# Core2 UART core dump 会话解码报告

固件审核需要把来宾的故障任务关联到同一次运行。旧版 `/crash` 记录 UART dump 的起止标记，由人工离线使用 ESP-IDF 工具完成任务解码。服务端保留的标记本身无法证明传输完整、CRC 正确或任务上下文存在。

Device Service 在 Core2 的原生 `qemu` 会话中从最新 512 KiB 串口窗口选取一份完整传输。传输顺序绑定到同窗口最近一次 panic，跨复位、重复边界或不一致的 ELF 前缀均无法得到结构化上下文。随后验证 ESP32 Xtensa ELF32 CRC32 容器、应用 ELF note 和任务寄存器 note。解析只使用有界数据，不启动外部调试器。任务 PC 符号来自已上传且匹配固件应用描述符的精确 ELF，仍需与 dump note 一致。原有 UART 标记和 panic PC、回溯语义保留。[代码](https://github.com/m5agent/m5stack-esp-emulator/commit/3748b02807cdcd22096e70b5f647c7385164ba08)

## 复现与证据

1. 使用 ESP-IDF v5.5.4 `735507283d5b2f9fb363a1901172dbd9e847945d` 编译 Core2 的默认 abort 探针及 `-DCRASH_PROBE_WATCHDOG=ON` 变体。使用各自 `flash_args` 输入，将应用、分区表和 bootloader 合成 16 MiB 镜像，保留应用 ELF。
2. 在独立的 Device Service 启动一个原生 Core2 会话，使用 QEMU SHA-256 `7d19fd18eb0adeddcf36070c1d3c0e81c028552dcd4f76195e3234cdc1e9c03a`。两个探针都在 CPU1 上发出 `CRASH_PROBE_ARMED`；等待 `CORE DUMP END`。
3. 分别用无 ELF、匹配 ELF、另一变体 ELF 查询 `GET /api/v1/sessions/{id}/crash`。取 `include=serial,logs,crash` ZIP，将 ZIP 的 `diagnostics/crash.json` 与匹配 ELF 返回的对象比较，再独立校验 ZIP 与其中串口取证范围。
4. 停止会话并释放 Flash，核对该进程结束和零活动租约。在同一独立状态目录重启服务，再读该停止会话。用现有 `decode_esp32_coredump.py` 读取同一份 ZIP 与合并镜像、匹配 ELF，核对任务数、dump CRC 和 SHA-256。[完整复现步骤](https://github.com/m5agent/m5stack-esp-emulator/blob/3748b02807cdcd22096e70b5f647c7385164ba08/tests/firmware/crash_diagnostics/README.md)

| 来宾 | 保存上下文 | CRC32 | 匹配 ELF 下故障任务保存的 PC |
| --- | ---: | --- | --- |
| CPU1 中断 WDT | 5 | `06a9b1f2` | `0x400d7d1b`，`trigger_fault` |
| CPU1 abort | 6 | `57f26c16` | `0x400851e0`，`panic_abort` |

独立的 Espressif 离线解码对同一份归档确认了上述任务数和 dump 字节身份。两个不同时间的新会话可能有不同的上下文地址、CRC 或 SHA-256，比较以各自的原始 ZIP 为准。汇总文件排除了本机环境标识和原始来宾内存，仅保留测试型号、工件摘要和受控探针的诊断输出。[最终同会话摘要](evidence/session-task-context-summary.json)

## 边界与回滚

HTTP 只提供已保存的任务上下文。任务名称、优先级和栈用量由保留的本地离线工具另取。实时 FreeRTOS 调度、RISC-V、其他板型或 dump 格式、物理硬件和浏览器均未作本项验收。恢复原 API 行为可回退上述源码提交，服务没有引入数据迁移。
