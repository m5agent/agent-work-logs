# ESP Emulator Core2 flash-IPC diagnostic boundary report

## 背景

- 来源：
  [m5stack-esp-emulator](https://github.com/m5agent/m5stack-esp-emulator)
- 现象：legacy Core2 UIFlow 越过原 shared-I2C 错误后进入 interrupt-WDT 和
  黑帧，旧文档把 flash-cache/IPC/DPORT 交接描述为工作假设。
- 新任务：把新增的最小 Core2 flash/IPC 探针纳入代码与证据体系，并重新核对
  当前状态、Backlog、专题页和历史调查，防止旧假设继续漂移。

## 结论

最小 ESP-IDF probe 在 3 个独立 lease 中先于任何 partition read 触发
FreeRTOS 临界区 spinlock owner mismatch。CPU0 主任务执行
`xQueueSemaphoreTake()`，CPU1 worker 已打印 READY；随后 CPU0 退出临界区时
在 `spinlock_release()` 断言。三轮均无 `CORE2_FLASH_IPC_READ_START`。

该结果收窄了调查边界，但没有完成根因定位：

- PRID 值符合 ESP32 PRO/APP 的预期，不是“PRID 读成错误固定值”的简单证据；
- cross-core/DPORT trace 存在，不能归因于 trace 通道缺失；
- 旧 portable QEMU 也能在 `READ_START` 前失败，说明当前 trace build 不是
  唯一触发条件；
- 尚无实际 lock address、owner、`SCOMPARE1` 或 CAS 返回/写入证据，因此不能
  宣称 S32C1I 已实现错误；
- `RUNTIME-03`、legacy interrupt-WDT、黑帧和物理等价性继续开放。

## 改动范围

产品仓库新增：

- `tests/firmware/core2_flash_ipc/` ESP-IDF 5.5.4 复现工程；
- Device Service runner，按 first-boot 分段，避免 reboot 后第二次启动掩盖
  首次失败；
- 脱敏 evidence 和固定 artifact/QEMU hashes；
- 文档契约、退役说法和 stale-claim 回归。

同步更新：

- 根 README；
- 文档导航、工程交接、当前状态、Backlog、工作流；
- QEMU 适配矩阵、runtime model gap 登记、Core2 历史调查；
- 热门固件矩阵、代码地图和验证台账；
- 自动项目快照。

## 执行环境

- macOS arm64；
- Python 3.13；
- ESP-IDF 5.5.4，target `esp32`；
- 16 MiB merged image；
- Device Service `/api/v1`；
- QEMU virtual-device，非真机。

主要命令：

```bash
idf.py -C tests/firmware/core2_flash_ipc \
  -B .work/core2-flash-ipc-build build

python3 tests/firmware/core2_flash_ipc/run_test.py \
  --image .work/core2-flash-ipc-16m.bin \
  --elf .work/core2-flash-ipc-build/core2_flash_ipc.elf \
  --attempts 3

PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
```

## 证据

| 项目 | 结果 |
| --- | --- |
| 主诊断 QEMU | 3/3 first boot spinlock owner assertion before `READ_START` |
| 旧 portable QEMU control | 2/3 owner assertion + 1/3 interrupt-WDT；均无 `READ_START` |
| CPU0 / CPU1 PRID | `0xcdcd` / `0xabab` |
| 固件 image SHA256 | `7e786a27678285d60c006fcb25226b98212672b34ec8b3b844833b5050a18da3` |
| ELF SHA256 | `af6d765b5f17052d92bf582e9e3ab1ec05b12b3a43f61366f7da5f31eb5db648` |
| 主诊断 QEMU SHA256 | `a40455957b68453df63586829f5f843239572ebbd98edf7c84fab506f9b4fd23` |
| portable QEMU SHA256 | `4095fb1180f128f9d5fe8c240643dcc0fa99fca72981f6241b089667c0ca2fa8` |

符号化栈：

```text
panic_abort
<- esp_system_abort
<- __assert_func
<- spinlock_release
<- vPortExitCritical
<- xQueueSemaphoreTake
<- app_main
<- main_task
<- vPortTaskWrapper
```

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | ESP-IDF build、merged image、ELF、compileall、Ruff 和 JSON/parser checks |
| flash | `PASS` | 每个 Device Service lease 使用 session-isolated Flash copy 启动 |
| transport | `PASS` | 串口 marker、backtrace、QEMU stderr 和 evidence ZIP 同 session |
| device_response | `FAIL` | 目标是进入 `esp_partition_read()`，实际在 `READ_START` 前断言 |
| data_behavior | `FAIL` | 没有发生 partition read，也无 progress/worker PASS marker |
| visual_or_physical | `NOT RUN` | 无物理板、RF、电气或 cache/PSRAM timing |
| documentation contract | `PASS` | docs `40/40`、platform `500/500`、snapshot/coverage/catalog/profile |
| delivery | `PASS` | 产品 commit `e185b15`；CI run `40212483911` |

`device_response=FAIL` 表示最小探针的预期数据路径未完成，不等于 legacy
firmware 已被判定为固件缺陷。

## 验证边界

- 未跟踪单条 `S32C1I`；
- 未确定 owner mismatch 的具体锁和持有者；
- 未证明最小失败是 legacy UIFlow interrupt-WDT 的唯一或直接原因；
- 未执行 hardware validation；
- diagnostic trace build 的 replay patch 尚未进入正式 QEMU patch 序列；
- portable QEMU control 证明问题不依赖当前 trace build，但未解释 1/3
  interrupt-WDT 与 2/3 owner assertion 的差异。

## 风险与回滚

本提交没有烧录真机、修改生产配置或迁移持久数据。回滚
`e185b15b4a2d2bdbbe86f94e84de2217b40da55c` 可移除探针和文档纠偏；
该回滚不会修复或重新引入 QEMU 运行时行为，因为本轮没有提交行为修复。
