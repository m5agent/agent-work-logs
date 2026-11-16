# M5GFX PR #423 评审：LP 端口的 read 终端改用控制器 STOP

## 1. 背景

M5GFX #421（作者 GOB52，日文）最初的描述是「ESP32-C5 的 LP_I2C 上，多字节写入后立刻用
repeated start 读取会静默丢失数据」。作者随后自行订正：真正的原因是 LP 端口上以 read
结束的事务没有把 STOP 送上总线，之后的下一个事务（read / write 均可）会被从机按上一个
事务的继续来解析；以 write 结束的事务由控制器自身 STOP 关闭，不受影响。

2026-11-16 的订正复核已确认该说明与 `develop` `b48dce0` 的代码一致，并要求作者按最新
`develop` 重做、补「控制器 STOP 单独」的隔离测量、走 PR。本条 PR #423 即该修复。

## 2. PR 内容

- 分支：`fix/lp-i2c-read-stop` → `develop`；head `cc60eaa`，base `b48dce0`；单文件 +6/-2。
- 变更：在 `i2c_wait()` 的终止分支前计算
  `force_stop_read = (state == state_read) && !isLpPort(port)`，用它在原来的
  `… || state == state_read || !int_raw.end_detect` 条件中替换掉无条件的 read 判断。
- 效果：LP 端口的 read 终端不再走 `i2c_stop()` 的 GPIO 位操作，而是走同分支的 else 侧，
  即用控制器的 `STOP` + `END` 命令关闭事务；HP 端口行为不变。
- 作者实测（ToughC5 + UnitNFC ST25R3916，400 kHz）：`develop` 下 Space B read 后紧接
  Space A read 为 0/100，本补丁为 100/100；read→read、B/A 交替等回归项在 100 kHz /
  400 kHz 下均为 100/100；「只把 LP 焊盘借给 GPIO」的版本为 0/100（且 `M5.begin()` 里
  PM1 配置也失败），「本补丁 + 借焊盘」为 100/100。
- 作者声明未覆盖：`i2c_stop()` 的总线恢复对 LP 焊盘仍然无效（另作）；C6 / P4 未试。

## 3. 代码事实（`b48dce0`）

| 位置 | 内容 |
| --- | --- |
| `:1847-1882` | `i2c_stop()` 只用 `gpio_set_level` / `gpio_set_direction` 造 STOP，最后 `i2c_periph_reset()`，并恢复 pin backup |
| `:1583-1587` | LP 端口的 `i2c_periph_reset()` 落到 `lp_i2c_ll_reset_register()`，无返回值 |
| `:2278-2300` | LP 端口由 `i2c_new_master_bus()`（`lp_source_clk` 在 `:2283`）打开，焊盘由 LP IO 域接管 |
| `:2555-2562` | `beginTransaction()` 对 LP 端口跳过 `set_pin()`，说明普通 GPIO/IO MUX 路径不适用于 LP 焊盘 |
| `:1988` | 终止分支：`state == state_read` 时无条件强制 STOP |
| `:2000-2037` | else 侧：`STOP` + `END`、`TRANS_COMPLETE` / `TIMEOUT` 等待（上限 25 ms，`:2011`）、失败回落 `connection_lost` + `i2c_stop()`（`:2016-2023`）、STOP 后 NACK 判定 |
| `:1952-1980`、`:1995-1998` | NACK 时等控制器自己的 STOP（`hw_stopped`），不再补 `i2c_stop()` |
| `:2545-2549` | `beginTransaction()` 的 bus busy 恢复，LP 上仍调用 `i2c_stop()` |
| `:2754` | `readBytes()` 读超时，LP 上仍调用 `i2c_stop()` |
| `:2620` | `endTransaction()` → `i2c_wait(port, true)` |

推导：

1. read 终端在 HP 上被强制 STOP 是历史行为；LP 上这条路径无效但静默成功（LP 复位无返回值），
   与作者描述的现象一一对应。
2. write 终端在两条端口上都走控制器 STOP（`force_stop_read` 为 false，且 `END_DETECT` 已置位），
   所以「write 结束不受影响」成立。
3. NACK 时 `hw_stopped` 为真，不经过 `i2c_stop()`，与作者「NACK 项不经过 `i2c_stop()`」一致。
4. `force_stop_read` 只在 `state_read && !isLpPort` 时为真，因此在 `LGFX_LP_I2C_NUM == 0`
   的构建里表达式与旧代码完全相同；HP 端口无行为变化。

## 4. 影响面

- 行为变化只发生在 `isLpPort()` 为真的端口，即 `SOC_LP_I2C_NUM > 0` 且 ESP-IDF ≥ 5.4 的
  构建（C5，以及 C6 / P4 等带 LP I2C 的芯片）。
- 作者仅实测 C5。若某芯片的 LP I2C 不接受「read 命令列结束后单独发 STOP 命令列」，则该芯片
  上每次 read 会等满 25 ms 并返回 `connection_lost`。这是比现状（静默缺 STOP）更显眼的退行，
  属于合并前唯一需要权衡的点。
- 反过来，只要 STOP 命令能完成，即使 STOP 时序有问题也不会比现状差（现状根本没有 STOP）。

## 5. 验证与证据

- `evidence/pr-view.json`：PR 元数据（base / head / mergeable / 正文）。
- `evidence/pr-diff.patch`：完整 diff。
- `evidence/apply-check.txt`：`git apply --check` 对 `b48dce0` 通过。
- `evidence/source-lines.txt`：上述代码位置摘录。
- `evidence/hardware-inventory.md`：内部硬件测试中心清单（脱敏），无 ESP32-C5。
- `evidence/virtual-device-check.md`：QEMU C6 的 LP 域 RTC I2C 为 all-ones / 忽略写入的桩，
  LP I2C 控制器未建模。
- `evidence/reply.md`：已发布的日文评审原文（结论 → 证据等级 → 代码位置 → 待确认 → 未覆盖）。

本机可执行的验证到此为止：没有 C5 实机，没有能跑 LP I2C 的虚拟设备，也没有 ESP-IDF /
Arduino-ESP32 工具链，因此 hardware validation、virtual-device validation、build 均为
`NOT RUN`，本记录整体为 `REVIEW`。

## 6. 风险与建议

1. 合并前最好取得一个 C6 或 P4 的 read→read 数据点；若拿不到，建议在正文/提交信息里保留
   「C5 のみ実測」的限定，出问题再按芯片收敛。
2. `beginTransaction()` 的 bus busy 恢复（`:2545-2549`）和 `readBytes()` 超时（`:2754`）
   在 LP 上仍调用无效的 `i2c_stop()`，建议单独开 issue 跟踪（作者已声明另作）。
3. 回滚方式：还原该单文件 diff 即回到原行为（LP read 静默缺 STOP），无数据/配置迁移。
4. 评审回复只发一条，未关闭 PR、未 push、未改上游仓库。

## 7. 时间线

- 2026-11-16：#421 订正复核，确认根因与代码一致，要求在最新 `develop` 上重做并走 PR。
- 2026-11-17 00:07（CST）：作者提交 PR #423（head `cc60eaa`）。
- 2026-11-17：本条代码层评审；发布一条日文评审回复。
