# M5Unified PR #447：PCF8563 `begin()` 保留运行中的定时器

- 日期：`2026-11-21`
- 结果：`PARTIAL`（`virtual-device validation`：寄存器语义已 A/B 验证；定时器实际计数/触发与实机为 `NOT RUN`）
- 工作类型：`pr_review`
- 问题来源：[m5stack/M5Unified#447](https://github.com/m5stack/M5Unified/pull/447)
  「PCF8563: keep the timer running across begin()」，作者 ainyan03，英语，OPEN，0 条评论；
  对应 [issue #446](https://github.com/m5stack/M5Unified/issues/446)
- 源码版本：`m5stack/M5Unified @ 4a0ebfd74ec5f2fd0087fd025e7d4c36b6261e6a`（PR head）；
  对照 `11bfd4bbb2705a36e7149a117c94f39511cee1bb`（develop）；`M5GFX @ 28d47949bdc84f30881623476f555398e2194313`（0.3.0）
- 环境：macOS arm64、ESP-IDF v6.0.2（`7101770`）、`esp32s3` target、8 MB flash、无 PSRAM；
  Device Service `dial`（M5Dial / QEMU / PCF8563 register model）profile

## 结论

PR 的寄存器行为与描述一致，未发现所测路径的回归。`cfg.disable_rtc_irq = false` 时，
`M5.begin()` 前已置 `Timer_control = 0x82`（TE=1、TD=1 Hz）的定时器在 `M5.begin()` 后仍为
`0x82`；develop 会改写为 `0x03`。再次调用 `Rtc.begin()` 同样保持 `0x82`。停止的定时器
（`0x00`）仍会被规范化为 `0x03`，运行中的 `0x83`（TE=1、TD=1/60 Hz）逐位保留。
`disableIRQ()` 现在留下 `0x03`（develop 为 `0x00`），与 `setTimerIRQ(0)` 原本写入的值一致。

虚拟设备的 PCF8563 模型只实现时间寄存器，不实现倒计时与 TF 标志，因此“定时器在
`M5.begin()` 后确实继续计数并触发”这一点无法在该虚拟设备上观测；作者在 CoreInk 实机上的
测量仍是该结论的硬件证据。实机、真实断电唤醒、INT 波形均为 `NOT RUN`。

## 关键证据

- `evidence/serial-pr.log`：PR head 构建，`POST_BEGIN TC=0x82`、`AFTER_REBEGIN_ARMED TC=0x82`、
  `AFTER_DISABLE_IRQ TC=0x03`、`AFTER_PRESERVE_TD60 TC=0x83`。
- `evidence/serial-base.log`：develop 构建，`POST_BEGIN TC=0x03`、`AFTER_REBEGIN_ARMED TC=0x03`、
  `AFTER_DISABLE_IRQ TC=0x00`、`AFTER_PRESERVE_TD60 TC=0x03`。
- `evidence/register-readback.txt`：十个阶段的 A/B 寄存器读回与解释。
- `evidence/build-and-run.txt`：构建环境、commit、artifact/firmware SHA256、session ID、命令。
- `evidence/pr-447.json`、`evidence/pr-447.diff`：PR 元数据与完整 diff。
- `patches/0001-pcf8563-keep-timer-across-begin.patch`：PR diff，可对 base `11bfd4b` 通过
  `git apply --check`。
- `code/pcf8563-pr447/`：同一 sketch 的 ESP-IDF 工程与 Device Service 执行脚本。
- 已发布回复：<https://github.com/m5stack/M5Unified/pull/447#issuecomment-7061111910>（1 条，英语；PR 仍 OPEN，未 approve/close/push）

## 文件

- `report.md`：完整评审、根因、A/B 结果、兼容性、未覆盖项与英文回复正文
- `run.json`：结构化记录
- `evidence/`：PR 元数据、串口日志、寄存器表、构建摘录
- `patches/`：PR 的改动（供复现，不代作者提交）
- `code/`：可重建工程

## 未覆盖项

- 定时器在 `M5.begin()` 后继续计数、TF 置位、INT 触发：`NOT RUN`（QEMU 模型缺倒计时逻辑）。
- CoreInk 或其他 PCF8563 板实机：`NOT RUN`（本机与硬件测试中心均无可用该型号）。
- 真实断电/RTC 唤醒周期、功耗、长期漂移：`NOT RUN`。
- 合并、关闭 PR 或向上游推送：`NOT RUN`（保持 OPEN，只发一条评论）。
