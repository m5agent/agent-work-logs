# 合并与远端回读

PR #209 的分支头为 `4b1dbc8bea1b79a7e1cf5ce3e26a67a3c0982e61`。完成该头的 platform-contracts
与 network-namespace-policy 检查后合并到 main，merge commit 为 `8131c4682e4ef89b7a28ec6a47ab09f38a2636f1`。
在此合并提交上的两个 CI job 通过。[PR #209](https://github.com/m5agent/m5stack-esp-emulator/pull/209) · [检查链接和当前 issue 状态](run.json)

本次合并关闭 #178、#199–#204、#206。#201–#204 交付的是矩阵具名缺口，
模型验收仍在 RUNTIME-10。#188 受 P4 运行时行为限制，#192 仍需完整两轮
高负载验收，#205 仍需帧方向数据。

主报告记录源证据和第一轮失败。所有相关固件执行是虚拟设备验证，物理硬件 NOT RUN。
[主报告](../../report.md)
