# ESP Emulator Core2 legacy shared board I2C 报告

## 背景

- 来源：
  [m5stack-esp-emulator](https://github.com/m5agent/m5stack-esp-emulator)
- 现象或需求：公开 legacy UIFlow 在 AXP chip-id 读取成功后，对 RTC address
  `0x51` 的下一事务无 ACK，并返回 `OSError: I2C bus error (19)`。
- 目标：用 controller port 级 trace 定位错误总线，修复板级路由，同时确认
  现有 UIFlow2 Core2 外设数据面不回归。不能通过复制 PMIC/RTC 到多条 bus
  或伪造寄存器值绕过固件路径。

## 结论

根因是 controller-to-physical-bus routing，而非 AXP 寄存器值：

- ESP32 有两个 I2C controller register block，legacy 固件选择 controller 0；
- Core2 板级 AXP、RTC、touch 和 IMU 实际共享 GPIO21/22 的一条物理 bus；
- 旧模型只把 AXP/INA 挂在 controller 0，把 RTC/touch/IMU 挂在 controller 1；
- controller 0 上的 RTC transaction 因此无法到达 slave，`start_rc=1`。

QEMU patch `0031` 将两个 controller 都路由到同一 physical board bus，并将每个
slave 只挂一次。修复后 AXP、RTC 和 INA transaction 都 ACK，原 I2C 错误消失。

同一 legacy image 随后进入独立 interrupt-WDT。该失败发生在 I2C ACK 之后，
不能归因于已经修复的 shared bus；应用仍无非空 frame。

## 改动范围

- `hw/i2c/esp32_i2c.c`：环境变量开启时记录 controller QOM path 和 bus path；
- `hw/m5stopwatch/m5core2.c`：两个 controller 共享唯一物理 GPIO21/22 bus；
- 新增 `0031-core2-shared-board-i2c.patch`；
- 新增 shared-board evidence；
- 状态、Backlog、工作流、交接、代码地图、QEMU/公开固件矩阵和测试 README
  统一为“I2C routing FIXED、WDT/black frame OPEN”。

公开固件矩阵中的 2026-10-24 无 ACK 结果保留为历史；当前入口不再把它当作
当前首个失败点。`Core2FactoryTest` 只完成了修复前运行，修复后重跑明确标为
`NOT RUN`。

## 证据

### 代码或配置

- 公开 firmware：`UIFlow_Core2 v1.15.4`，firmware ID
  `1897200000000002280`；
- source SHA-256：
  `18d77e28adfacf7e719a167bd0c3450b78357d13cb1d2f2a8b7bccc2248a909a`；
- normalized flash SHA-256：
  `152127c808b9212e3a5b55dd9e0a2d24e71b902e225452b67db381c76caba1cc`；
- QEMU binary SHA-256：
  `a8070d23866f514e33fd9b09c9223ee757c69b1a0bad48cc2bf8511d05fb5ca7`；
- trace 开启：`M5SW_I2C_CTRL_TRACE=1`。

### 修复前

- controller/bus：`/machine/soc/i2c0` 与 `/machine/soc/i2c0/i2c`；
- transaction count：`123`；
- AXP `0x34`：write/read ACK；
- RTC `0x51`：`start_rc=1`；
- serial：`OSError: I2C bus error (19)`。

### 修复后

- controller/bus：全部仍由 legacy 固件发往 controller 0；
- transaction count：`480`；
- AXP `0x34`：write ACK `60`，read ACK `25`；
- RTC `0x51`：write ACK `15`，read ACK `4`；
- INA3221 `0x40`：write ACK `9`，read ACK `4`；
- 原 I2C error：不存在；
- AXP192 override：同样越过原 I2C error；
- UIFlow2 Core2 device group：`6/6`、`24/24` checks，无 retry。

### 后续失败

- `Guru Meditation Error: Core 1 panic'ed (Interrupt wdt timeout on CPU1)`；
- `TG1WDT_SYS_RESET`；
- `WDT reset info: PRO CPU PC=0x0` / `APP CPU PC=0x0`；
- reset loop；
- frame SHA-256
  `57580743a08a3f4ebdf57240cbcc997002ef63b7234531f946127f1495973f43`，
  仍为 black。

### 执行

环境：macOS arm64、Python 3.13、Node 20、项目 QEMU worktree。

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_docs_*_contract.py'
npm test --prefix platform/tests
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check
python3 -m compileall -q platform tests
ruff check --select E9,F \
  platform/tests/_docs_contract_support.py \
  platform/tests/test_docs_consistency.py \
  platform/tests/test_docs_*_contract.py
git diff --check
```

结果：平台 `498/498`、文档 `38/38`、Node UI smoke PASS；其余静态和生成物
检查 PASS。

GitHub Actions：
[CI 40204089670](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40204089670)
在 `105ad247315644acccef96352a93269c27c67450` 上两个 job 均成功。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compileall、profile/catalog/coverage、patch reverse-check |
| transport | `PASS` | QEMU controller 0 到共享 GPIO21/22 board bus 的 AXP/RTC/INA transaction |
| device_response | `PASS` | `0x34`、`0x51`、`0x40` write/read ACK |
| data_behavior | `PARTIAL` | UIFlow2 Core2 `6/6` 无 retry；legacy UIFlow 无应用帧 |
| visual_or_physical | `FAIL` | legacy frame 仍为 black；没有 hardware validation |
| delivery | `PASS` | product commit、CI 和本归档 |

## 验证边界

本记录是 `virtual-device validation`。它证明 controller-to-board-bus routing
修复和现有 UIFlow2 Core2 外设回归，不证明：

- legacy UIFlow 能完成应用初始化；
- WDT 来自固件还是另一个缺失运行时模型；
- `Core2FactoryTest` 修复后的行为；
- 物理 I2C timing、电源、RF、功耗、电气或真机行为；
- 其他 Core2 firmware SHA 自动兼容。

`RUNTIME-03` 继续开放，关闭条件仍是同一固件 SHA 渲染非空应用帧并稳定运行。

## 风险与回滚

没有不可逆硬件操作、烧录或持久状态迁移。若需回滚，revert
`105ad247315644acccef96352a93269c27c67450` 可恢复旧 controller/bus 拆分；
这会重新引入 legacy UIFlow 的 RTC 无 ACK，但不会影响仓库外的物理设备。
