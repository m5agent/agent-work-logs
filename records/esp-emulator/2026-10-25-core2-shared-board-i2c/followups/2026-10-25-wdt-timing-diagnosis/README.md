# ESP Emulator Core2 legacy UIFlow WDT timing diagnosis

- 日期：`2026-10-25`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：shared I2C 修复后，同一 legacy UIFlow 仍触发 watchdog
- 源码版本：
  [`m5agent/m5stack-esp-emulator@eff1561`](https://github.com/m5agent/m5stack-esp-emulator/commit/eff1561e9f0da700c843ed14d9019c81f1e27e55)
- Base commit：`105ad247315644acccef96352a93269c27c67450`
- 环境：macOS arm64、Python 3.13、QEMU 9.2.2 virtual-device

## 结论

新增默认关闭的 `M5SW_TIMG_TRACE=1`，记录 ESP32 timer-group watchdog 的
reset、config、feed、arm 和 timeout 阶段。诊断结果否定了“某个固定外设缺失”
和“单一固定 firmware PC 死锁”这两个过于简单的解释：

- 默认单会话持续运行 `285` 秒，TG0/TG1 持续 feed，没有 interrupt-WDT 或
  TG reset；
- 两批独立四实例默认运行各 `84` 秒，interrupt-WDT 分别为 `3/4` 和
  `2/4`，合计 `5/8` 失败、`3/8` 未触发 WDT；
- 失败 CPU、PC 和串口长度都不固定；
- 显式 `thread=single`、`thread=multi`、`icount shift=5` 和
  `icount shift=0` 都没有修复；thread/icount 对照还触发了更早的 TG
  hardware reset。

`icount shift=0` 的单会话 trace 显示 TG1 在虚时 `13.782s` 后停止 feed，
`0.8s` 后进入 interrupt stage，再 `1.6s` 后 system reset。当前最可信的
边界是 legacy 启动期长同步路径与 QEMU 虚拟时间/宿主调度的交互，但还没有
定位到具体 guest 代码点，因此 frame 仍为 black，`RUNTIME-03` 保持开放。

## 关键证据

- firmware build：MicroPython `a3bd196ef-dirty`、MicroPython `1.12.0`、
  ESP-IDF `3.4.0`；
- QEMU binary SHA-256：
  `85fab9c048a31ba37bed930fe67a0e245e81f53ee6fbeb1749b4d4228116b505`；
- 默认并发：`5/8` interrupt-WDT、`3/8` no WDT；
- 默认单会话：`285s` no WDT；
- accelerator 对照：`thread=single` `4/4` TG reset，`thread=multi` `2/4`
  interrupt-WDT，`icount shift=5` `4/4` TG reset/panic，`icount shift=0`
  `4/4` TG reset；
- Core2 UIFlow2 外设组复跑 `6/6 PASS`；
- 平台 `499/499`、文档契约 `39/39`、compileall、catalog、coverage、
  QEMU profiles 和 selected Ruff PASS；
- GitHub Actions `40207023102` 两个 job 均成功。

## 文件

- `report.md`：对照设计、timer trace、验证层级和剩余边界；
- `run.json`：机器可读记录；
- `evidence/verification.summary.json`：并发、单实例、accelerator、trace
  时序和 CI 摘要。

## 未覆盖项

- 最后一次 feed 之后的具体 guest 函数/同步操作；
- 一个稳定可用的 accelerator 配置；
- 非空应用帧和完整 legacy firmware；
- `Core2FactoryTest` 修复后重跑；
- 物理 watchdog、I2C timing、RF、功耗和真机。
