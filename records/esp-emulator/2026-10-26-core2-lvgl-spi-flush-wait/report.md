# Core2 legacy LVGL flush wait and SPI transaction-done diagnostic report

## 背景

- 来源：
  [m5stack-esp-emulator](https://github.com/m5agent/m5stack-esp-emulator)
- 现象：legacy `UIFlow_Core2 v1.15.4` 在 normal WDT 下首帧前 reset；
  302-byte 黑帧保持不变。关闭 WDT 后 Flash/SSI 活动约在 44 秒结束，
  但 CPU1 持续自旋到至少 120 秒，仍无 setup/REPL。
- 目标：判断 `0x40100049` 等待的是什么对象，并验证 SPI transaction-done
  IRQ 是否能让 display completion callback 继续执行。

## 结论

- 状态：`PARTIAL`
- 关键判断：CPU1 的 `0x40100049` 属于 LVGL 7
  `lv_refr_vdb_flush`，当前在等待 `lv_disp_buf_t.flushing` 清零。
- 模型改动：`0042` 增加 stateful `SPI_SLAVE.TRANS_DONE/TRANS_INTEN`，
  SPI IRQ level 只在两者同时置位时为高；同时增加有界 object-word dump。
- 结果变化：`flush_cb` 已执行，但 completion callback
  `0x40174884`/`lv_disp_flush_ready` 仍未执行；normal WDT 仍由 TG0
  stage-1 首 reset。

## 调查过程

### 1. 排除旧的“未知对象”状态

WDT-off 45/120 秒快照均停在：

- CPU0：`0x4026306e`，`waiti` idle；
- CPU1：`0x40100049`，running spin；
- Flash/SSI counter 在约 44 秒后不再增长；
- cross-core writes 仍增长。

后续 BIN-bound 反汇编确认：

- `0x40100010`：`lv_refr_vdb_flush`；
- `0x401002b2`：`lv_refr_area_part`；
- `0x40174758`：display driver `flush_cb`；
- `0x40174884`：display flush completion callback；
- `0x402605ec`：`lv_disp_flush_ready`。

### 2. 绑定运行时对象

late state 中：

- `A2` 是 `lv_disp_buf_t`，地址 `0x3f953a40`；
- `buf1=0x3ffe436c`，`buf2=0x3ffe8e70`，`buf_act=0x3ffe8e70`；
- size 为 9600 pixels；
- `flushing=1`，`flushing_last=0`；
- `A10` 是 display driver，地址 `0x3f953c60`；
- driver `buffer=0x3f953a40`，`flush_cb=0x40174758`，
  `wait_cb=0x00000000`。

该对象形态说明不是永久 handoff deadlock，也不是缺少 `wait_cb`；LVGL 正在
等上一帧异步 flush 完成。

### 3. PC trace 与 SPI IRQ 模型

WDT-off 50 秒 trace：

- pre-SPI-IRQ model：`flush_cb` 调用 1 次，首次时间 `44.198632 s`；
- `0x40174884` completion call 为 0；
- `lv_disp_flush_ready` call 为 0；
- frame 仍为 302 bytes，SHA-256
  `57580743a08a3f4ebdf57240cbcc997002ef63b7234531f946127f1495973f43`。

`0042` 加入 SPI transaction-done IRQ 后：

- 可观察到 `trans_done=1`、`trans_inten=1`、`level=1`；
- `flush_cb` 仍在 `47.893660 s` 调用 1 次；
- completion 与 `lv_disp_flush_ready` 仍为 0；
- frame 字节与 SHA 不变。

normal WDT 60 秒对照：

- stage-0 timeout：`5.914197 s`；
- stage-1 timeout：`15.915653 s`；
- first reset：`15.915713 s`；
- TG1 before reset：`7,248` feeds，`0` timeout；
- 分类：`BOOTLOADER_TG0_STAGE1_RESET_WITH_TG1_LIVE`；
- serial 无 REPL，frame 仍为 302-byte 黑帧。

## 改动范围

- 新增
  `0042-esp32-spi-trans-done-irq-diagnostic.patch`；
- 新增 LVGL/SPI wait evidence 和契约测试；
- 更新 Core2 运行时 profile blocker；
- 同步项目状态、Backlog、运行时缺口、QEMU 矩阵、代码地图、验证台账和
  工程交接文档。

该 patch 只用于可重放诊断，不是 `RUNTIME-03` 修复，也未改变产品启动结果。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | compileall、selected Ruff `E9/F`、patch reverse apply check |
| virtual-device execution | `PARTIAL` | flush callback observed；SPI IRQ level observed；completion 未 observed |
| firmware legacy boot | `FAIL` | normal WDT reset，无 REPL，302-byte 黑帧 |
| data_behavior | `PARTIAL` | Flash/SSI 有终点，LVGL `flushing=1` 的等待对象已绑定 |
| platform contract | `PASS` | `544/544`；Core2 docs `12/12`；生成器与 CI 均 PASS |
| visual_or_physical | `NOT RUN` | 没有真机、物理显示、RF、PSRAM/cache timing 或电气验证 |
| delivery | `PASS` | product commit `f206175`；CI `40254086653` 两 job PASS |

## 验证边界

matching ELF/MAP、guest interrupt matrix/queue completion、normal-WDT 非空
应用帧和完整 67-case 矩阵均未完成。`0042` 的 IRQ level 只证明模型状态能
抬高电平，不证明 SPI ISR、queue 或 display callback 已完成。

## 风险与回滚

本轮没有物理烧录、不可逆设备操作或生产配置变更。回滚产品提交
`f2061759897955e6017d4aa2a41bd5ba962c35b6` 可恢复到上一版文档与运行时
profile；`0042` 是默认诊断补丁，移除后不会迁移 Flash 或保留设备状态。
