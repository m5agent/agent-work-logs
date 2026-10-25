# ESP Emulator corrected Core2 flash-IPC and interrupt-WDT boundary

- 日期：`2026-10-26`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 源码版本：
  [m5stack-esp-emulator @ 7bf311e](https://github.com/m5agent/m5stack-esp-emulator/commit/7bf311e67385552a6be5c2f610811421458e1e73)
- Base commit：`e185b15b4a2d2bdbbe86f94e84de2217b40da55c`
- 环境：macOS arm64；Python 3.13；ESP-IDF 5.5.4；Core2 QEMU
  virtual-device；物理硬件 `NOT RUN`

## 结论

上一份记录中的 Core2 spinlock owner mismatch 已撤销。原因是探针在
4096-byte CPU1 task stack 上又分配了 4096-byte 局部 read buffer；栈溢出覆盖了
同一内存区域的 FreeRTOS queue lock。PRID、S32C1I 和原子指令本身没有在该
失败中得到错误证据。

修正版把 read buffer 放到静态 aligned internal RAM，并每 50 次读取让出 CPU。
20 次 current/portable 首启动全部到达 `CORE2_FLASH_IPC_READ_START`：

- `14 PASS`：完成 1000 次 CPU1 4 KiB `esp_partition_read()`；
- `6 interrupt-WDT`：至少在读取 250 次后触发，CPU0/CPU1 PC 都在 idle
  `esp_cpu_wait_for_intr()`/`waiti`；
- `0 spinlock owner assertion`。

该结果证明普通 partition-read 数据面可以运行，并把剩余最小失败收敛到
long-synchronous flash workload 开始后的虚拟 timer/interrupt 交付或宿主调度。
它不证明 legacy UIFlow 黑帧/WDT 具有同一根因，也未覆盖物理时序。

## 关键证据

- 修正镜像 SHA256：`c2762e5f34d513e34a47739174fd452567f2f3ec87164a4d421a1a7141c68359`；
- ELF SHA256：`7636c3e5aa182621f9998e12938a2e037adf99689f7d1b7e5c154a7892aaf88b`；
- current QEMU `7226de8c…`：5 次为 `1 PASS / 4 interrupt-WDT`；
- portable QEMU `4095fb11…`：15 次为 `13 PASS / 2 interrupt-WDT`；
- WDT 栈：`esp_cpu_wait_for_intr -> esp_vApplicationIdleHook ->
  prvIdleTask -> vPortTaskWrapper`；
- 新增默认关闭的 `0033-esp32-s32c1i-trace.patch`，reverse-check PASS；
- 平台测试 `500/500`、文档领域契约 `40/40`，snapshot/coverage/catalog/
  profile、compileall、Ruff、JSON 与 diff check 均 PASS；CI
  `40213908086` 的两个 job 均 PASS。

## 文件

- `report.md`：纠偏、实验、证据和边界；
- `run.json`：机器可读结果；
- `evidence/core2-flash-ipc-wdt-summary.json`：current/portable 合并结果和
  旧镜像撤销量据。

## 未覆盖项

- 尚未解释为什么 virtual timer/interrupt 在 idle waiti 后停摆；
- 尚未证明与 legacy UIFlow 单一同因；
- 尚未完成 current/portable/accelerator 的全量同输入统计；
- 物理 timer、cache、PSRAM、RF、电气和真机均为 `NOT RUN`。
