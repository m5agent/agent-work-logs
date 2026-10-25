# ESP Emulator Core2 equal-deadline timer fix and current-state refresh report

## 背景

前一份记录把最小 Core2 flash/IPC probe 的剩余问题描述为
interrupt-WDT/timer delivery 尚未定位。后续 IRQ-ring 采样捕获到相等
deadline 窗口，因此需要固化业务补丁，并重新整理 README、当前状态、
Backlog、代码地图、验证台账、运行时缺口登记和历史调查，使文档不再停留在
“timer 根因未知”的旧阶段。

## 结论

旧 `update_ccompare()` 对 deadline 使用无符号减法。若 timer ISR 在最后的相等
cycle 写入 `CCOMPARE == CCOUNT`，结果是 `2^32` ticks，而不是下一 cycle。
Core2 的 timer interrupt 因而不到来，guest idle/tick 任务停摆，interrupt-WDT
随后复位两核。

业务补丁只改变这一种情况：

```c
uint32_t delta = env->sregs[CCOMPARE + i] - env->sregs[CCOUNT];
dcc = delta ? delta : 1;
```

其他 delta 的解释不变，也没有增加 catch-up。ring/trace 继续只作为默认关闭的
诊断代码保留，没有混入业务补丁。

## 改动范围

- 新增 `0034-xtensa-ccompare-equal-deadline.patch`；
- flash/IPC runner 默认校验已知 image/ELF SHA256，错误样本 fail closed；
- runner 默认观察窗口从 `4 s` 改为 `15 s`，并把已进入 `READ_START` 但未在
  窗口内完成的样本标为 `INCOMPLETE`，避免误判为固件失败；
- README、项目状态、Backlog、交接、工作流、QEMU 矩阵、代码地图、运行缺口、
  历史调查、验证台账和生成快照统一到当前事实；
- 文档契约检查新增 patch、runner、pre/post evidence、legacy reset PC `0` 和
  black-frame 边界。

## 执行

```bash
git apply --check \
  patches/qemu-m5stack-peripherals/0034-xtensa-ccompare-equal-deadline.patch

python3 tests/firmware/core2_flash_ipc/run_test.py \
  --image .work/core2-flash-ipc-16m-final.bin \
  --elf .work/core2-flash-ipc-build/core2_flash_ipc.elf \
  --attempts 3

PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'

python3 platform/tools/project_snapshot.py --check
```

补丁以 QEMU source commit
`da100c909249926b9f4458f18e4f2d216d08f51a` 为 base，在干净归档的 source
上执行 forward 和 reverse check。runner 与平台测试通过真实仓库代码；QEMU
guest 通过 Device Service 创建独立 lease。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | patch clean-base forward/reverse check、compileall、Ruff `E9/F` |
| flash | `PASS` | Device Service 为每次 attempt 创建独立 session/Flash copy |
| transport | `PASS` | 串口 `MAIN/READY/READ_START/WORKER_PASS/PASS` markers 与 evidence ZIP |
| device_response | `PASS` | 修复版最小 probe `40/40` 完成 1000 次 CPU1 partition reads |
| data_behavior | `PASS` | `CCOMPARE == CCOUNT` 不再被算成 `2^32` ticks；trace 开关与两种 icount 对照通过 |
| documentation contract | `PASS` | 平台 `500/500`、snapshot/coverage/catalog/profile、diff check |
| delivery | `PASS` | product commit `c3193b9`；CI `40218210901` 的两个 job 均成功 |
| legacy UIFlow | `FAIL` | TG0/TG1 watchdog reset、reset PC `0`、同一 black frame |
| visual_or_physical | `NOT RUN` | 无物理 timer/cache/PSRAM、RF、电气或真机验证 |

## 验证边界

该 PASS 只适用固定 image/ELF、Core2 QEMU、runner 默认 runtime、四批
artifact-bound pre/post 证据和一次新版 runner regression。它不证明 PSRAM/cache
物理时序，也不证明其他 Core2 固件自动兼容。

legacy UIFlow 是独立失败：`TG0WDT_SYS_RESET`/`TG1WDT_SYS_RESET` 可能来自
watchdog feed/clear、服务任务饥饿、启动期长同步路径或 flash/IPC/DPORT 顺序。
当前没有证据把 minimal probe 的 timer 修复直接复用于 legacy 固件。

## 风险与回滚

没有真机烧录或不可逆设备状态。回滚 product commit `c3193b9` 会同时移除 timer
修复、runner 门禁和文档刷新；更小的回滚点是只回退 `0034` patch 并重新构建，
但会让 minimal probe interrupt-WDT 复现。legacy firmware 与物理硬件结论不会因
该回滚发生变化。
