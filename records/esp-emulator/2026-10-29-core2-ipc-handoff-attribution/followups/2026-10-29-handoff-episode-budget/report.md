# ESP Emulator Core2 flash handoff episode budget 报告

## 背景

- 来源：`RUNTIME-03`，PR
  [#42](https://github.com/m5agent/m5stack-esp-emulator/pull/42)。
- 前序：bounded stack 已把 CPU0 定位到 `spi_flash_op_block_func`，但
  BIN-bound PC trace 在 deterministic `-icount` 下会以
  `Bad icount read` 终止。
- 目标：修复诊断边界，计算 reset 前每次 flash handoff 的虚拟时间预算。

## 结论

- 工具缺陷：匹配 PC 的 helper 在 no-I/O TB 中调用
  `qemu_clock_get_ns(QEMU_CLOCK_VIRTUAL)`。
- 修复：`translator_io_start()` 在 helper 前结束 TB，helper 增加
  `can_do_io` fail-safe。
- guest 影响：无；watchdog、peripheral、CAS、icount 和默认路径不变。
- 启动结论：两次 normal-WDT 均在 reset 前发生约 `12.6k` 个正常
  handoff，CPU0 累计等待约 57% reset 预算，单次最大 `<6.8 ms`。
- 判断：拒绝单个长 handshake deadlock；下一步优化累计 handoff 频率或
  单周期成本。

## 改动范围

- `target/xtensa/translate.c`：匹配 trace PC 时调用
  `translator_io_start(&dc->base)`。
- `target/xtensa/op_helper.c`：no-I/O 状态安全返回。
- `run_pc_trace.py`：支持显式 expected firmware SHA，并输出 phase
  count/total/mean/p50/p95/max。

## 执行

环境：

- public `UIFlow_Core2 v1.15.4`；
- `runtime=qemu-wifi`；
- deterministic `-icount shift=5`；
- normal WDT；
- 默认关闭的 contended-CAS fair-yield 仅用于匹配当前 RUNTIME-03 lane；
- 50 秒 wall-time 窗口。

pre-fix 控制在约 `2.351 s` virtual time 触发 `Bad icount read`。fixed
QEMU 两次均到达 reset。

## 结果

| run | reset | handoffs | block wait | mean | p50 | p95 | max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `17.249519230 s` | `12,645` | `9.851852864 s` | `779.110 us` | `782.400 us` | `813.312 us` | `6.655552 ms` |
| 2 | `17.253553502 s` | `12,693` | `9.828771008 s` | `774.345 us` | `781.824 us` | `804.704 us` | `6.781792 ms` |

两次 block wait 分别占 reset 预算 `57.1%` 和 `57.0%`。连同下一次 block
前的间隔，覆盖约 `86.4%` 预算。episode 频率约 `733-736/s`。

两次 serial 都记录 `TG0WDT_SYS_RESET`，没有 BOARD/APIKEY 或 REPL；frame
SHA 均为 `57580743a08a3f4ebdf57240cbcc997002ef63b7234531f946127f1495973f43`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | QEMU incremental build 与 patch reverse-check |
| transport | PASS | 真实 Device Service `/api/v1`、QEMU、串口和 frame |
| device_response | PASS | 两次 exact PC setter trace 与 WDT reset |
| data_behavior | PARTIAL | handoff 预算已量化，legacy 启动仍失败 |
| visual_or_physical | NOT RUN | 黑帧且无物理硬件/电气/光学证据 |

平台回归为 `1562 tests OK, 10 skipped`；runtime coverage、peripheral
catalog、QEMU profiles、project snapshot 和 `git diff --check` 均 PASS。
PR #42 两个检查 run 均 PASS，并 merge 到
`37480e9fc7a3f53db0fa8dbbdc9438d37ef1d5af`。

## 验证边界

- 结果来自 deterministic virtual time，不是墙钟性能或物理 Flash 时间。
- PC 地址是 BIN-bound；函数名只是 source-shape，不是 exact legacy ELF。
- WDT 未关闭或延长。
- 不能由 handoff 数量推断真实硬件 cache miss 数或 SPI 电气行为。

## 风险与回滚

trace 默认关闭。反向应用 `0089` 可恢复旧 PC helper；生产默认路径不受
影响。所有 QEMU session 使用 snapshot，未烧录硬件或修改设备持久状态。
