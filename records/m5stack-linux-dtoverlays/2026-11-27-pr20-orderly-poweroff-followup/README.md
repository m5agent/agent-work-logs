# m5stack/m5stack-linux-dtoverlays #20 第二轮：ff4cd84 的 recheck / READY / restart 复核

- 日期：`2026-11-27`
- 结果：`PARTIAL`（四项修复在 host-level harness 上通过；实机与虚拟设备未跑）
- 工作类型：`pr_review`
- 问题来源：[PR #20 作者新评论](https://github.com/m5stack/m5stack-linux-dtoverlays/pull/20#issuecomment-7200264330)（2026-11-26T18:16:36Z）
- 已发布回复：[PR #20 comment 7200515708](https://github.com/m5stack/m5stack-linux-dtoverlays/pull/20#issuecomment-7200515708)（1 条英文；PR 保持 OPEN，未 push 上游）
- 源码版本：`m5stack/m5stack-linux-dtoverlays` @ `ff4cd84474787ea24a00b65d83b5b50e4a51c1c9`
- 环境：macOS arm64；无 Cardputer Zero；Device Service `cardputer-zero` 不可创建；无内核头文件，docker 不可用

## 结论

作者四项改动逐条成立，两个被点名的场景按描述工作，没有阻塞问题：

- 500 ms `check` 在 `0xB6` 为 2 时每 100 ms 重查，低电平期间不重新使能 IRQ，
  3/4 或读失败才 orderly。
- 倒计时中线路回高：不关机、不挂 backstop、IRQ 重新使能，`READY` 在 `0xB6` 回到 1 后写一次。
- `.shutdown` 时 `slider_off` 且线路高：`emergency_restart()`，不写 200 ms、不拉低 LCD 复位。
- 最小保持 12000、前缀属性、移除 `disabled-gpios` 回退均落实。

两个非阻塞残留：restart 只存在于 `.shutdown`（关机卡住时回高没有 restart 点，T25；
backstop 单次采样之后回高仍无路径，T26）；irq-gpios 读失败时每 100 ms 无限重查且不挂 backstop（T19）。
后者概率极低。另附一个只覆盖 backstop 之前的 proposal patch，T25 通过、T26 与其余场景不变。

## 关键证据

- 构建/运行：`code/build.sh`；head 26 个场景 / 109 checks 全过，proposal 108 checks 全过
- 点名场景：`evidence/requested-scenarios.txt`（T7 回高 + READY、T8 .shutdown restart、T25/T26 卡住关机）
- 原始日志：`evidence/host-harness-head.txt`、`evidence/host-harness-proposed.txt`
- overlay：`dtc 1.8.1` 重编无 warning；base→head 反编译差异恰好两条属性；`evidence/overlay-compile.txt`
- 参考寄存器表：`evidence/reference-register-map.txt`（Open-IOE1 @4369350 的 README/main.c）
- 内核 API：`evidence/kernel-api-checks.txt`（`emergency_restart` 为 GPL export）
- 条目：`evidence/pr-metadata.txt`；本机 profile：`evidence/local-profile-summary.txt`

## 文件

- `report.md`：完整复核表、残留分析与未覆盖项
- `run.json`：结构化记录
- `evidence/`：harness 原始输出、点名场景、overlay、参考寄存器表、内核与元数据
- `patches/0001-proposal-backstop-restart.patch`：可选的 backstop restart 收口（未推送）
- `code/`：可重建 harness、驱动源码、proposal 版源码、stub 头

## 未覆盖项

- hardware validation `NOT RUN`：无 Cardputer Zero；作者实机时序未独立复跑
- virtual-device validation `NOT RUN`：profile `backend_ready=false`，缺 QEMU/ROM
- 内核 `W=1` `NOT RUN`：无内核头文件、docker 不可用
- 计时真实性 `NOT RUN`：未建模 I2C 耗时、workqueue 并发与 cancel 竞争
- stock dtbo 字节一致 `NOT RUN`：仓库内 firmware dtbo 是更早构建，无法复核该声明
