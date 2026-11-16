# M5GFX #421 订正复核报告

## 背景

M5GFX #421 最初报告「ESP32-C5 的 LP_I2C 上，多字节写入后 repeated start 读取会静默失败」。m5agent 在 2026-11-16 的第一条回复给出了代码层分析，把「2 字节写入后 RSTART」当作主要候选，并请报告者做三项切分实验。

报告者随后在 ToughC5 + UnitNFC 上重做切分，订正了现象与根因：

1. 失败条件不是「2 字节写 + RSTART」，而是「上一次事务是否以 read 结束」。
2. LP 端口上，以 read 结束的事务结束后总线上没有 STOP；从机因此把下一次事务当作上一次的延续（ST25R3916 的 Space B 访问会持续到 STOP）。
3. 写入结束的事务由控制器自己的 STOP 命令收尾，所以不受影响。
4. `write(&b0,1); write(&b1,1);` 与 `write(sel,2)`（含 100us 延迟）都能正确读取，原「2 字节写」假设不成立。
5. 原文「read 不碰缓冲区」也不成立：哨兵 `0xEE` 被 `0x00` 覆盖，read 实际收到了 1 字节。

报告者还给出 `common.inl` 的参考补丁：修正 1 让 LP 的 read 终端走控制器 STOP；修正 2 让 `i2c_stop()` 在 LP 上临时把焊盘借给普通 GPIO；修正 3 处理 LP 端口重开后的第一个事务。

## 复核结论

### 与代码一致的部分

- `i2c_wait()` 在 `flg_stop` 时，只要 `state == state_read` 就进强制 STOP 分支（`common.inl:1984-1998`），与「所有 read 终端都走 GPIO STOP」一致。
- `i2c_stop()` 只调用 `gpio_set_level()` / `gpio_set_direction()`，没有 `gpio_iomux_out(..., PIN_FUNC_GPIO)`（`:1847-1882`）。对照 `set_pin()` 在 `:1774` 明确切到 GPIO 功能。LP 焊盘若仍在 LP IO 功能上，这些写操作到不了焊盘。
- `i2c_stop()` 末尾的 `i2c_periph_reset()` 对 LP 调用 `lp_i2c_ll_reset_register()`（`:1580-1592`），无返回值，调用方无法得知 STOP 没发出去。
- 写入终端走 `i2c_wait()` 的 else 分支，由控制器发 STOP（`:2000-2040` 附近），所以「write 结束不受影响」成立。
- `readBytes()` 先写 FIFO 中已收到的字节，再在 FIFO 空时判超时（`:2749-2772`），因此 read 覆盖哨兵是可能的。

### 与当前 develop 的差异

- 补丁基于 `develop` `6f81929`（2026-10-16），当前 `develop` 为 `b48dce0`。`git apply --check`：前 3 个 hunk 带 102 行偏移通过，第 4 个（`i2c_wait()` 条件）因日文注释被 `40928dd` 英文化而失配。
- 修正 3 的锁存 preset 已在 `aef1da8`（2026-11-06）进入 `develop`，实现位置为 `common.inl:2258-2277`。该提交的说明正是 ToughC5 上「init 后第一个事务被 NACK」，与报告者的「相关别问题」一致。因此该症状应在最新 `develop` 上先复测。
- 修正 3 真正还没进 `develop` 的，是 `init()` 里 `i2c_stop()` 之前的两处 `gpio::release_lp_pad()`；`release_lp_pad()` 本身已存在于 `:737`。
- `route_lp_pad()` 在 C5 上走 `!SOC_LP_GPIO_MATRIX_SUPPORTED` 分支，读取 `i2c_periph_signal[i2c_port].iomux_func`。IDF v5.5 `components/soc/esp32c5/i2c_periph.c` 的 `i2c_periph_signal[SOC_I2C_NUM]` 含 LP 条目且 `iomux_func = 3`，索引合法。

### 对补丁的评审意见

- 修正 2 是恢复路径的必要修复；修正 1 是正常 read 终端的更轻量收尾。两者可以并存，但应分别验证。
- 报告者只测了「修正 2 单独」和「两者」，没有「修正 1 单独」。若修正 1 单独可用，正常路径不再需要每次 read 借出焊盘，修正 2 只保留给错误恢复与 init 的 bus-busy 路径，风险面更小。
- 修正 2 在 bus-busy 恢复时是在控制器仍可能运行的情况下先把焊盘切走，再 bit-bang，最后 reset。建议在恢复路径比较「先 reset/停控制器再借焊盘」的顺序。
- 修正 3 需要在最新 `develop` 上重测；其 preset 部分与 `aef1da8` 重复，应删除，只保留 init 的 `release_lp_pad()`。

## 已执行

- `gh issue view 421 --repo m5stack/M5GFX --comments` 读取全文与两条评论。
- 浅克隆 `develop` 到 `/tmp/m5gfx-421`，核对 `b48dce0`、`6f81929`、`aef1da8`、`40928dd`。
- 把评论中的 diff 抽出为 `/tmp/c421.patch`，分别在 `b48dce0` 与 `6f81929` 上 `git apply --check`。
- 下载 IDF v5.5 的 `esp32c5/i2c_periph.c` 与 `soc_caps.h` 核对 LP 条目与 `SOC_LP_GPIO_MATRIX_SUPPORTED`。
- 发布一条 issue 评论（见 README 链接）。

## 未执行与风险

- 无 C5 实机：无法独立复现、看波形或读 LP_I2C 寄存器。
- 无 C5 虚拟设备：Device Service profile 到 C6，QEMU 无 LP_I2C/ST25R3916 模型；不能做 virtual-device validation。
- 未构建补丁：本机无 C5 构建目标；报告者已在 ToughC5 上跑过，但构建日志未提供。
- 建议上游在合入前补：修正 1 单独、100k/400k、read→read / read→write / write→read、NACK 强制恢复、`begin()` 后首事务。
