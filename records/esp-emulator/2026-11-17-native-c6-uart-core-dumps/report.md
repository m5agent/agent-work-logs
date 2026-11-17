# 原生 ESP32-C6 崩溃会话回执

## 变化

原服务对 C6 来宾只统计 UART 分隔符。扩展使用同会话 panic 的摘要比对 ESP-IDF 应用 note、验证芯片与 ELF machine，按对应容器格式核验 CRC32 或 SHA-256，再解析保存的任务 PC/SP。符号仍需完整应用 ELF SHA-256 与合并镜像一致。

## 复验

保留 Nesso N1 同一两份探针的合并 Flash、ELF 与原生 QEMU 哈希。旧服务只有分隔符结果，同样的固件在候选服务上生成两个独立会话的任务回执。新解析器也可以从旧归档原有转储字节读出各 3 个任务。两次新会话的 live API 与 evidence ZIP 一致，两个精确 ELF 均解析出 `panic_abort`，省略或交换 ELF 保留上下文且不给出符号。RISC-V GDB 独立读回任务数及崩溃 PC/SP。停止并重新启动独立服务仍能读回，Flash 和租约已释放。

首轮 CRC32 实际 ZIP 已取得，验证程序误用了串口范围字段而提前退出。修正验证程序后，两种格式、同件旧版本对照及两次 Core2 回归均通过。

[精确 SHA、旧版对照及结果](evidence/session-core-dump-summary.json) · [构建及 API 重放](https://github.com/m5agent/m5stack-esp-emulator/blob/7caf061ea74c5275910d3837e61786158cc263b5/tests/firmware/crash_diagnostics/riscv_c6/README.md)

## 边界和回滚

测试范围为原生 Nesso N1 与指定 ESP-IDF abort 探针，Core2 的旧格式另行回归。其他 RISC-V 堆栈展开、任务名称和优先级、Flash dump、浏览器和物理硬件未运行。回退源代码恢复原有 UART 标记行为，固件与运行时无须回退。记录仅包含派生诊断和摘要，原始 ZIP、路径与会话标识未归档。
