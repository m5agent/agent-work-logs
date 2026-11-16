# ESP32-C5 LP_I2C: read 终端的 STOP 缺失（M5GFX #421 订正复核）

- 日期：`2026-11-16`
- 结果：`REVIEW`（仅代码层复核；硬件 / 虚拟设备均 `NOT RUN`）
- 工作类型：`issue`
- 问题来源：<https://github.com/m5stack/M5GFX/issues/421>
- 源码版本：m5stack/M5GFX `develop` `b48dce0`；对照 `6f81929`、`aef1da8`、`40928dd`；ESP-IDF `v5.5` 的 ESP32-C5 侧源码
- 环境：macOS；无 ESP32-C5 实机；虚拟设备 profile 仅到 ESP32-C6，QEMU 无 LP_I2C / ST25R3916 模型

## 结论

报告者订正后的根因——LP_I2C 端口上，以 read 结束的事务没有把 STOP 发到总线，导致下一次事务被从机按上一次的状态解释——与 M5GFX 代码一致：`i2c_wait()` 对 `state_read` 无条件走强制 STOP 路径，该路径的 `i2c_stop()` 只用普通 GPIO 寄存器操作、不把 IO MUX 切回 GPIO，LP 焊盘仍留在 LP IO 功能上；随后 `lp_i2c_ll_reset_register()` 没有返回值，于是静默成功。前次回复中的「2 字节写 + RSTART 分割」假设撤回。

本次只做代码层复核，并核实了对方补丁相对当前 `develop` 的状态：补丁不能在 `b48dce0` 原样应用（`i2c_wait()` 的 hunk 因日文注释英文化而失配）；补丁中 init 的锁存 preset 已由 `aef1da8` 进入 `develop`；`route_lp_pad()` 在 C5 上使用的 `i2c_periph_signal[1].iomux_func` 在 IDF v5.5 中存在，不构成越界。已在 issue 回复一条，要求基于最新 `develop` rebase、补「修正 1 单独」的测量，并走 PR。

## 关键证据

- 代码定位（`develop` `b48dce0`）：`common.inl:1847-1882`（`i2c_stop()` 只操作 GPIO）、`:1984-1998`（read 终端的强制 STOP 分支）、`:1580-1592`（LP 复位无返回值）、`:2258-2277`（init 锁存 preset，`aef1da8`）、`:737`（`release_lp_pad`）。
- 补丁适配性：`evidence/apply-check.txt`（对 `b48dce0` 第 4 个 hunk 失配，对 `6f81929` 通过）。
- IDF 依据：`evidence/idf-c5-i2c-periph.txt`（`LP_I2C_MUX_FUNC = 3`）、`evidence/esp32c5-soc_caps.h`（无 `SOC_LP_GPIO_MATRIX_SUPPORTED`）。
- 回复：<https://github.com/m5stack/M5GFX/issues/421#issuecomment-6920387844>（仅一条，issue 保持 OPEN）。

## 文件

- `report.md`：完整复核与风险
- `run.json`：结构化记录
- `evidence/`：补丁应用检查、源码片段、IDF 片段、对方订正原文、已发布回复
- `patches/`：不适用（复核的是对方补丁，原文见 issue 评论）
- `code/`：不适用（本次无可执行验证）

## 未覆盖项

- 当方 C5 实机复现、SDA/SCL 波形、LP_I2C 寄存器 dump：`NOT RUN`（无设备）
- 虚拟设备复现：不可（无 C5 profile，QEMU 无 LP_I2C / ST25R3916 模型）
- 补丁构建与实机运行：`NOT RUN`（仅报告者环境；其 ToughC5 数据是唯一硬件证据）
- 修正 1 单独测量、NACK 强制恢复的实机确认：未取得
- 按任务要求未 push，仅本地提交
