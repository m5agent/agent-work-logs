# ESP Emulator corrected Core2 flash-IPC and interrupt-WDT boundary report

## 背景

上一轮把两个独立 lease 中的 `spinlock_release()` owner mismatch 解释为
Core2 QEMU 跨核锁/CAS 候选缺陷。继续增加 S32C1I 参数追踪后，发现错误 owner
位于 CPU1 task stack 范围内。进一步核对 `Queue_t` layout 和 probe stack size
后确认：probe 对 4096-byte stack 使用 4096-byte 局部 buffer，必然溢出并覆盖
相邻 FreeRTOS queue。

本任务的目标是撤回该错误证据，修正 probe，并判断 partition read 能否在
QEMU 中正常执行。

## 结论

修正版 probe 使用静态 aligned buffer，并在每 50 次读取后 `vTaskDelay(1)`。
20 次 current/portable first boot 均进入 `READ_START`，14 次完成全部读取，
6 次在 flash 已读取至少 250 次后进入 interrupt-WDT。所有 WDT dump 中
CPU0/CPU1 PC 都位于 idle waiti，没有 spinlock assertion。

因此：

- partition-read/flash 数据面可以执行；
- 旧 spinlock mismatch 不是 QEMU 模型缺陷证据；
- 剩余最小复现是 flash workload 后的虚拟 timer/interrupt 停摆；
- legacy UIFlow 与最小 WDT 的单一因果关系尚未证明。

## 改动

- 将 probe read buffer 从 task stack 移到静态 internal RAM；
- 每 50 次读取让出 CPU，避免 probe 自身持续饿死 IDLE1；
- runner 按 first boot 分类 `PASS`、`INTERRUPT_WDT`、spinlock 和 other failure；
- 用 corrected evidence 替换旧 spinlock evidence；
- 文档、Backlog、runtime gap、QEMU matrix 和验证台账撤回旧结论；
- 新增默认关闭的 `0033-esp32-s32c1i-trace.patch`，保留通用 CAS 审计通道。

## 执行

```bash
idf.py -C tests/firmware/core2_flash_ipc \
  -B .work/core2-flash-ipc-build build

python3 tests/firmware/core2_flash_ipc/run_test.py \
  --image .work/core2-flash-ipc-16m-final.bin \
  --elf .work/core2-flash-ipc-build/core2_flash_ipc.elf \
  --attempts 5

git apply --reverse --check \
  patches/qemu-m5stack-peripherals/0033-esp32-s32c1i-trace.patch

PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
```

## 证据

当前 QEMU：

- 5 first boots；
- `1 PASS / 4 interrupt-WDT / 0 spinlock assert`；
- 5/5 到达 `READ_START`；
- PASS 轮完成 1000 次读取；WDT 轮 progress marker 为 5、5、11、14，
  每个 marker 代表 50 次读取。

旧 portable QEMU：

- 两个批次 5 + 10，共 15 first boots；
- `13 PASS / 2 interrupt-WDT / 0 spinlock assert`；
- 15/15 到达 `READ_START`。

合并：

- `14 PASS / 6 interrupt-WDT / 0 spinlock assert`；
- WDT 栈均为 `esp_cpu_wait_for_intr -> esp_vApplicationIdleHook ->
  prvIdleTask`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | ESP-IDF build/merge、S32C1I patch reverse-check |
| flash | `PASS` | 每个 Device Service session 使用独立 Flash copy |
| transport | `PASS` | 串口 marker、backtrace 和 evidence ZIP |
| device_response | `PARTIAL` | 14/20 完成 1000 次 partition reads |
| data_behavior | `PARTIAL` | 读取路径可执行；6/20 后段 interrupt-WDT |
| documentation contract | `PASS` | platform `500/500`、docs `40/40` 与生成校验 |
| visual_or_physical | `NOT RUN` | 无物理 timer/cache/PSRAM/电气验证 |

## 验证边界

当前 QEMU 与旧 portable runtime 的失败比例不同，但两者都能触发该失败类别。
需要继续做相同输入、相同 accelerator、更大样本和 timer/INTENABLE 状态对照，
才能判断当前构建是否存在额外回归或纯粹的宿主时序差异。

## 风险与回滚

没有真机烧录或不可逆状态。回滚 product commit `7bf311e` 会恢复旧 probe 和
错误结论，不建议；应以新的 follow-up 修正旧记录，而不是重写公开历史。
