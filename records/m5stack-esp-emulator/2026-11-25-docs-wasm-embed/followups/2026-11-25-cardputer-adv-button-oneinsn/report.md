# Cardputer-Adv 原 Arduino Button 调度 A/B

测试固定原 USB CDC 镜像 `07ebcecd…c0e7`、同一锁定 WASM `210db550…e211`、ROM 和浏览器。默认导出以正常 wall-clock 模式运行。私有导出只对精确固件绑定 `tcg,thread=multi,one-insn-per-tb=on`，时钟除数仍为 1。两种设置交替各执行三次，每次使用新浏览器进程和同样的等待条件。实际 F12 通过工作台发往虚拟 GPIO0，测试先等原程序打印按下，再松开并检查 USB 输出。私有站点以 `publication_eligible=false` 标记。

| 设置 | 通过原顺序 | 其余观察 |
| --- | --- | --- |
| 默认 | 2/3 | 第三次在长按等待截止后松开，随后日志出现 `Button A Pressed` 和 `Button A Released`。保留持键期超时，最终两条报文均看到。 |
| 单指令调度 | 2/3 | 第二次持键时显示 `Button A Pressed`，确认虚拟 G0 的松开后等待窗口内没有 `Button A Released`。 |

六次均收到 ROM 输出。最后地址 `0x403c88b8` 来自同一合并镜像的二级 bootloader 入口。原程序的初始化阶段没有应用串口标记，因此只有 ROM 文本不足以确定是否到达 `setup()`。这六次没有看到旧 `ipc1` 栈观察点、浏览器 Worker 错误或兜底终止。六次均 QEMU exit 0，所有 36 个观察到的 Worker 正常回收。重复次数仅支持报告现象，根因和稳定性仍开放。单指令候选未采用。

## 复现

1. 从之前的[同固件冷启动记录](https://github.com/m5agent/agent-work-logs/tree/758234a0240aa5f4e459cc42ca736db38046ef0f/records/m5stack-esp-emulator/2026-11-25-docs-wasm-embed/followups/2026-11-25-cardputer-adv-button-cold-start)准备同一固件、锁定 WASM、ROM 和相同静态导出。校验文件哈希。
2. 在本地执行 `python3 stage-button-oneinsn.py BASE_SITE PRIVATE_SITE`。脚本拒绝错误基线和已存在输出目录。它核对所有导出资产，只改变设备执行资料与站点清单。
3. 在模拟器根目录下的 `.work` 测试目录运行提供的 `run-button-oneinsn-comparison.mjs`。根据本地下游文件位置调整 `fixtures` 和 `previous` 两个路径，它们的内容将继续经过哈希校验。默认站点使用 `M5_CARDPUTER_ONEINSN=0 node run-button-oneinsn-comparison.mjs BASE_SITE on NEW_OUTPUT`。候选站点使用 `M5_CARDPUTER_ONEINSN=1` 和 `PRIVATE_SITE`，每次用新目录。Chrome 的 Worker `error` 和 `messageerror` 仅观察，前端资产继续使用对应清单内容。
4. 每次浏览器退出后交替启动下一组。按同会话 G0、USB 最终输出、持键中输出、ROM、Worker 事件和退出码核对。保留原始的超时报错。

[摘要和固定哈希](evidence/one-insn-ab.summary.json) · [候选准备脚本](code/stage-button-oneinsn.py) · [A/B 回放脚本](code/run-button-oneinsn-comparison.mjs)
