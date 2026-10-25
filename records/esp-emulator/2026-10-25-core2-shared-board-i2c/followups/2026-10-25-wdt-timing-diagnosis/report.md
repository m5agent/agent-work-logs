# ESP Emulator Core2 legacy UIFlow WDT timing diagnosis 报告

## 背景

- 前置记录：Core2 shared GPIO21/22 I2C routing 已修复，AXP/RTC/INA ACK，
  但同一 legacy UIFlow 随后触发 interrupt-WDT。
- 目标：判断后续失败是固定器件缺口、WDT/timer 模型错误、虚拟时间问题，
  还是固件自身死锁，并保留可重复的 timer-level evidence。
- 约束：不能用 `wdt_disable` 绕过；不能把单次模拟失败直接归因于固件；
  不能把 UIFlow2 的 accelerator 配置未经验证地套给 legacy firmware。

## 结论

问题对并发和宿主调度高度敏感：

1. 默认单会话持续 `285` 秒，TG0/TG1 watchdog 持续 config/feed/arm，
   没有 interrupt-WDT 或 TG system reset。
2. 两批四实例默认运行各观察 `84` 秒，`5/8` lease 出现 interrupt-WDT，
   `3/8` 没有出现。
3. 失败 PC 包括 `0x40087980`、`0x40084494`、`0x400938af`、
   `0x4026306e`、`0x4017477c`、`0x40087a85` 等，不是单一地址。
4. `tcg,thread=single,tb-size=128`：`4/4` 在 boot 阶段 TG hardware reset。
5. `tcg,thread=multi,tb-size=128`：`2/4` interrupt-WDT，`2/4` 未出现。
6. `icount shift=5`：`4/4` TG hardware reset，其中 `2/4` 同时出现
   interrupt-WDT。
7. `icount shift=0`：`4/4` TG hardware reset，失败时间被延后。

`icount shift=0` 单会话 trace：

```text
last TG1 feed:             13,782,001,927 ns
TG1 interrupt stage:       14,582,001,927 ns
TG1 system reset:          16,182,001,927 ns
```

因此 WDT 模型本身按配置的 `0.8s` + `1.6s` 两阶段计时；问题是这个 guest
启动路径在特定虚拟时间/宿主调度条件下停止 feed，而不是 watchdog 计数单位
简单少算或多算。

## 改动范围

- `hw/timer/esp32_timg.c` 增加默认关闭的 `M5SW_TIMG_TRACE`；
- 记录 watchdog reset config、WDTCONFIG/FEED/PROTECT 写入、实际 arm
  count/timeout、timeout stage 和 reset 触发；
- 新增 `0032-esp32-timg-wdt-trace.patch`；
- 不改变默认 watchdog 行为，也不改变 Device Service accelerator 选择；
- 更新 `RUNTIME-03` 当前状态、代码地图、Backlog、验证台账和测试契约。

trace 仅用于诊断；本轮在 Device Service 外层临时验证了不同 accelerator
参数，但没有把失败的 accelerator override 留在产品代码。

## 证据

### 固件和运行时

- firmware：`UIFlow_Core2 v1.15.4`；
- firmware ID：`1897200000000002280`；
- source SHA-256：
  `18d77e28adfacf7e719a167bd0c3450b78357d13cb1d2f2a8b7bccc2248a909a`；
- embedded build：MicroPython `a3bd196ef-dirty`、MicroPython `1.12.0`、
  ESP-IDF `3.4.0`；
- QEMU `9.2.2`；
- QEMU binary SHA-256：
  `85fab9c048a31ba37bed930fe67a0e245e81f53ee6fbeb1749b4d4228116b505`。

### 默认单会话

- duration：`285s`；
- interrupt-WDT：false；
- TG hardware reset：false；
- serial bytes：`507`；
- serial SHA-256：
  `e996276519b4f8882739ff1c494dcecba313c99278857a53a984c1c9986a1b62`。

### 默认四实例

- batch A：`3/4` interrupt-WDT；
- batch B：`2/4` interrupt-WDT；
- combined：`5/8` interrupt-WDT、`3/8` no WDT；
- representative failure serial SHA-256：
  `58520c05e0bcdff05ed8f6119f28c6aef49845f7a4c383d710008c044c691858`；
- representative stable serial SHA-256：
  `e996276519b4f8882739ff1c494dcecba313c99278857a53a984c1c9986a1b62`。

### ACCELERATOR 对照

| Mode | TG hardware reset | interrupt-WDT |
| --- | ---: | ---: |
| `tcg,thread=single,tb-size=128` | 4/4 | 0/4 |
| `tcg,thread=multi,tb-size=128` | 0/4 | 2/4 |
| `icount shift=5,align=off,sleep=off` | 4/4 | 2/4 |
| `icount shift=0,align=off,sleep=off` | 4/4 | 0/4 |

### 执行

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_docs_*_contract.py'
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check
python3 -m compileall -q platform tests
ruff check --select E9,F \
  platform/tests/_docs_contract_support.py \
  platform/tests/test_docs_consistency.py \
  platform/tests/test_docs_*_contract.py
PYTHONPATH=.work/py python3 tests/uiflow2/run_peripheral_matrix.py \
  --device core2 --out-dir /tmp/m5-core2-0032-trace
```

结果：平台 `499/499 PASS`、文档 `39/39 PASS`、Core2 UIFlow2 设备组
`6/6 PASS`；其余静态、契约和 patch reverse-check 通过。

GitHub Actions：
[CI 40207023102](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40207023102)
在 `eff1561e9f0da700c843ed14d9019c81f1e27e55` 上两个 job 均成功。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | QEMU rebuild、compileall、profiles、patch reverse-check |
| transport | `PASS` | guest I2C/PMIC/RTC path remains operational |
| device_response | `PASS` | AXP/RTC/INA and Core2 UIFlow2 peripheral regression |
| data_behavior | `PARTIAL` | watchdog feed is observable and timing-sensitive; exact stalled guest code point remains unknown |
| visual_or_physical | `FAIL` | legacy frame remains black; no hardware validation |
| delivery | `PASS` | product commit、CI 和本 follow-up |

## 验证边界

本记录是 `virtual-device validation`。它证明当前 watchdog 失败不是固定的
I2C/PMIC 外设缺口，也不由单一 accelerator 参数解释；它不证明某个固定
firmware 函数一定是缺陷，也不证明真实 Core2 会或不会在同一点卡住。
应用帧、FactoryTest 修复后重跑和物理硬件仍未完成。

## 风险与回滚

没有不可逆硬件操作。`M5SW_TIMG_TRACE` 默认关闭，不影响产品路径；如需回滚，
revert `eff1561e9f0da700c843ed14d9019c81f1e27e55` 可移除 trace、诊断
evidence 和对应文档更新。旧 shared-I2C 修复保持独立。
