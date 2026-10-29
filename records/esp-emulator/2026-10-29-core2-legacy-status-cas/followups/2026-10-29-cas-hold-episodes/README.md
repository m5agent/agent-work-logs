# Core2 legacy CAS hold intervals

- 日期：`2026-10-29`
- 结果：`PARTIAL`
- 工作类型：`virtual_device_diagnostic`
- 问题来源：`RUNTIME-03`
- 源码版本：`m5stack-esp-emulator@23a081ea5615bec2c36f3ef95237433bbb6b9a07`
- 合并版本：`12df2b9b40aa6160237fb00366b727dd7e4c9a32`
- PR：[#37](https://github.com/m5agent/m5stack-esp-emulator/pull/37)

## 结论

`0086` 在既有 freeze-only handoff trace 中增加了按 CPU/lock 聚合的
contended-CAS episode。首次实现读取 virtual clock 时触发 `Bad icount read`
并终止 VM；最终版本跳过不安全状态，不改变 guest 指令、CAS 结果、中断、
watchdog 或默认调度。

同一 public `UIFlow_Core2 v1.15.4` normalized Flash 在两个独立 10 秒
exact-time freeze 中显示：

- normal-WDT：`238` 个 episode，累计 `9.316534114 s`，最长 `631 ms`
- WDT-off：`253` 个 episode，累计 `7.825981502 s`，最长 `581 ms`
- 主锁 `0x3ffbf2cc` 对应 `xTaskQueueMutex` 的 BIN/control-flow 映射
- normal-WDT 的 `xTaskQueueMutex` 等待：`162` 个 episode、`6.743534018 s`
- failed-CAS slice yield 只把等待转移到 queue mux，没有改变 reset 边界

因此当前瓶颈是多轮失败 CAS 形成的长持有/等待区间，而不是 RDSR WIP/BUSY
或孤立单次碰撞。`RUNTIME-03` 仍为 `OPEN`：normal-WDT stage-1 reset、
startup UI、setup/REPL、非空应用帧和 matching ELF/MAP 命名均未闭环。

## 关键证据

- QEMU：`0a63c37f62752a3020988bb6b087b5eb11f4a6af323255f978ccb7012cb8be73`
- patch reverse apply：`PASS`
- PR #37 CI：`4/4 PASS`
- merge commit main CI：`2/2 PASS`
  (`https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40860945564`)
- platform：`1559 tests OK, 10 skipped`
- 物理硬件/RF/电气：`NOT RUN`

## 文件

- `report.md`：CAS episode 方法、映射和负向控制
- `run.json`：结构化记录
- `evidence/summary.json`：仓库机器摘要
- `patches/0001-esp32-legacy-cas-episode-profile.patch`：`0086` patch

## 未覆盖项

没有 matching legacy ELF/MAP，不能把 BIN-bound lock holder 命名为具体函数；
没有证明 Xtensa atomics 语义错误；没有在 physical hardware 上复现或排除
host-vCPU 调度与 guest 长临界区之间的最终归因。
