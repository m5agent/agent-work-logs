# ESP Emulator PR #60 Cardputer/StackChan 输入与响应合并

- 日期：`2026-10-30`
- 结果：`PASS`（virtual-device + 远端交付；物理硬件 `NOT RUN`）
- 工作类型：`code_change`
- 问题来源：[PR #60](https://github.com/m5agent/m5stack-esp-emulator/pull/60)
- 源码版本：`m5agent/m5stack-esp-emulator@867ce788b3b42e0b9c55429cd9272781ffd15cb0`
- 环境：GitHub Actions、Chromium、QEMU WASM、Cardputer-ADV 与 StackChan 虚拟设备

## 结论

PR #60 已以普通 merge commit
`867ce788b3b42e0b9c55429cd9272781ffd15cb0` 合并，贡献者提交历史保留。
该提交的远端 CI 两个 job 均通过：platform `1,680` 项为
`1,670 PASS + 10 skipped`，network namespace policy 全部通过。

Cardputer-ADV 的物理键盘输入、局部绘图后的方向判断和玻璃安装方向已修复；
StackChan 默认示例将 SCS UART 舵机事务移到真实 MicroPython 后台线程，
触摸轮询最大观察间隔降至 `165 ms`。物理硬件与完整 native 矩阵未执行。

## 关键证据

- PR head：`444632fd04dcedd637bfb61f0971bd18d4e1f7cb`。
- Merge commit：
  `867ce788b3b42e0b9c55429cd9272781ffd15cb0`。
- CI：
  [run 40997493078](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40997493078)。
- 改动：`52` 个文本文件，`+8,897/-89`；无二进制、密钥或冲突标记。
- Cardputer 最终 V5：`33` 项通过，覆盖 56 个物理键、双 Shift/Fn/grave、
  四方向/四角旋转与局部更新。
- StackChan 最终 V5：`24` 项通过；运动中的实际触点间隔
  `104.800/302.020/802.660 ms` 均通过。

## 文件

- `report.md`：审核、合并、验证和边界。
- `run.json`：结构化记录。
- `evidence/summary.json`：机器可读摘要。

## 未覆盖项

物理硬件、标准 all-admitted Pages 发布门禁和本轮完整 native QEMU 矩阵均为
`NOT RUN`。V4 的 Stop 后 engine CDP target 清理未在预算内完成，因此资源
回收保持 `PARTIAL`，没有由后续清空改写为 PASS。

主工作区有 6 个合并前已有的未提交文件修改，因此本地 `main` worktree 的
`--ff-only` 快进被 Git 安全拒绝；远端 `main` 与 CI 已完成，用户改动未被覆盖。
