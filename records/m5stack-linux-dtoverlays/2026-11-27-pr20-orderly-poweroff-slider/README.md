# m5stack/m5stack-linux-dtoverlays #20：拨杆关机改为 orderly poweroff

- 日期：`2026-11-27`
- 结果：`PARTIAL`（驱动状态机在主机级 harness 上逐条验证；实机与虚拟设备未跑）
- 工作类型：`pr_review`
- 条目：[m5stack/m5stack-linux-dtoverlays#20](https://github.com/m5stack/m5stack-linux-dtoverlays/pull/20)
  「powerfail_suo: orderly poweroff from the power slider」，作者 shrimpapplepro，英文，
  OPEN、可合并、评审前无评论
- 源码：PR head `5623292f043f5b4617f5d035130f464281f13dd1`（单 commit），
  base `main` `a3fd3e83c0247e16e194e7e40f7fc1f5be933dd4`；2 文件，`+248/-52`
- 环境：macOS arm64；本机无 Cardputer Zero 硬件；Device Service 的 `cardputer-zero`
  profile `supported=false creatable=false backend_ready=false`（Linux ARM64 后端，
  缺 `__missing_qemu__` / `__missing_rom__`）；无内核头文件，docker 守护进程状态目录只读，
  因此没有重建模块
- 证据等级：**host-level test**（stub 头文件编译驱动真实源码 + 模拟 M5IOE1 寄存器/时间）
  \+ code-level verification（overlay 编译、内核 API 逐条核对）
- 已发布回复：<https://github.com/m5stack/m5stack-linux-dtoverlays/pull/20#issuecomment-7199260631>
  （1 条，英文；PR 仍 OPEN，未 close、未 push 上游、未改他人代码）

## 结论

设计方向正确、无阻塞问题：以“能否真正编程 M5IOE1”为开关，失败即退回旧的 SysRq U 行为；
`.shutdown` 的 `system_state` 门控、I2C block 写帧格式、i2c client 引用释放、`remove` 还原
`2000` 都成立；新增属性在编译出的 dtbo 里与 `disabled-gpios` 走同一条 local fixup 路径。

一处逻辑问题：`powerfail_confirmed()` 把 `0xB6` 的 `DEBOUNCE(2)`（驱动注释里就是
“slider off, 100 ms debounce”）判成“拨杆还开着”。若 150 ms 后重读仍是 2，事件被丢弃，
而 probe 写入的 `OFF_TIME = 20000` 保持、backstop 不挂、边沿中断在仍为低的线路上重新使能
——板子可能带可写文件系统再跑 20 s 后被硬切电，比旧行为更差。harness 已复现；把 2 也算
确认并在丢弃分支还原 `2000` 后，全部场景通过（`patches/0002`）。

两个小项：backstop 偏移固定 4 s 与最小保持 8 s 不匹配（最小配置下 4.0 s 就会插进一次约
4.9 s 的健康关机中间）；`power-hold-ms` 缺厂商前缀，且 `disabled-gpios` 回退会让将来任何把
该属性指向 M5IOE1 的 overlay 静默进入新路径。

## 关键证据

- 构建/运行：`code/build.sh` 编译驱动真实源码（stub 内核头）+ 模拟 M5IOE1，15 场景全过；
  基线 `evidence/host-harness-pr-head.txt`，建议修复 `evidence/host-harness-proposed-fix.txt`
- overlay：`dtc 1.8.1` 编译 PR 版 v5 overlay 无 warning，dtbo 内含
  `m5stack,power-controller` 与 `power-hold-ms = <0x4e20>`，`evidence/overlay-compile.txt`
- 内核 API：`system_state` 先于 `device_shutdown()`、I2C block 写无长度字节、
  `device_shutdown()` 逆序，`evidence/kernel-api-checks.txt`
- 本机 profile：`evidence/local-profile-summary.txt`
- 条目元数据：`evidence/pr-metadata.txt`、`evidence/pr-scope.txt`

## 文件

- `report.md`：完整评审、逐条核对、结论与未覆盖项
- `run.json`：机器可读记录
- `code/`：可重建 harness（`build.sh`）、驱动源码、建议修复版、stub 头
- `evidence/`：harness 输出、overlay 编译、内核 API 摘录、profile 与条目元数据
- `patches/0001`：PR 原始提交；`patches/0002`：建议的 DEBOUNCE/还原改动

## 未覆盖项

- hardware validation：`NOT RUN`。无 Cardputer Zero 实机；作者的掉电计时、5 s 关机、
  15.7 s 兜底与下次启动 fsck 干净均未独立复跑。
- virtual-device validation：`NOT RUN`。`cardputer-zero` profile 不可创建，缺 QEMU/ROM，
  后端为 Linux ARM64。
- 内核模块构建 `W=1`：`NOT RUN`。无内核头文件；docker 可用但 containerd 状态目录只读。
- 计时真实性：`NOT RUN`。`msleep` 只推进 jiffies，无定时器抖动/I2C 耗时/队列并发。
- `0xB6` 状态值与 countdown 期间重读 `OFF_TIME`：依赖作者寄存器表与实测，无数据手册独立确认。
- 新增属性的启动路径：作者声明未测，实机跑的是 `disabled-gpios` 回退。
