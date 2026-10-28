# ESP Emulator：PR #16 CoreS3 C/QEMU 浏览器工作台合并

- 日期：`2026-10-28`
- 结果：`PASS`
- 工作类型：`pr_review`
- 问题来源：[PR #16](https://github.com/m5agent/m5stack-esp-emulator/pull/16)
- 源码版本：[`m5agent/m5stack-esp-emulator`](https://github.com/m5agent/m5stack-esp-emulator)
  @ [`90f55638`](https://github.com/m5agent/m5stack-esp-emulator/commit/90f556387560a47230141946e96f6f0166266721)
- 合并结果：[`ef5f6d79`](https://github.com/m5agent/m5stack-esp-emulator/commit/ef5f6d79c0529eb6aa72a2212d8c951438d039b8)
- 环境：macOS arm64、Python 3.12.14、Node.js、Chromium；
  `browser-local-qemu-evidence` 与 `browser virtual-device validation`

## 结论

PR #16 已在独立 worktree 合并到最新 main。唯一冲突是自动生成的
`docs/project-snapshot.md`，已按合并后的真实源文件重新生成。远端 main
现指向 merge commit `ef5f6d79`，GitHub 已将 PR #16 标记为 `MERGED`。

独立复验覆盖静态工作台与公开 Pages 上的真实 CoreS3 C/QEMU 客体：

- 导出的静态工作台完成 `16/16` 浏览器检查；
- 公开 Pages 的实际 CoreS3 客体完成 `21/21` 检查，包括真实 RGB LCD
  帧、DOM 触摸正反例、PIR 双向状态、QMP 暂停/继续、四档布局、
  正常停止、Worker 清理和分享链接重开；
- Node 契约、四个生成器、Python compileall 与 PR 自带 CI 通过；
- 本地平台套件为 `1390/1391 PASS + 8 skipped`。唯一错误是 macOS
  multicast loopback 的既有 worker-discovery 测试超时；对应实现与测试
  文件均未被本 PR 修改，Linux CI 的对应 job 已通过。

## 关键证据

- 合并提交：`ef5f6d79c0529eb6aa72a2212d8c951438d039b8`
- 公开地址：<https://yuyun2000.github.io/m5stack-esp-emulator/>
- CoreS3 固件 SHA256：`78961297e751ec9c743b4cdf89cc2c137e7e2c801dda3ead9df2ea45d59fbd3f`
- C/QEMU WASM SHA256：`716f3b6a8750335613da2897be0933d1497965962d0dc1b3f2754ebf76316c89`
- ROM SHA256：`b5c7090cc22efce51c1323cef31ca96fcd673a5b1d1b1017e219d393f2659913`
- 公开验收报告 SHA256：`d21740e4d365dea8c2dab839b4c585dddfc4093c7ff3809e2e46cc51e77099cc`
- GitHub PR CI：`platform-contracts` 与 `network-namespace-policy` 均通过

## 文件

- `report.md`：合并、冲突处理、复验和边界
- `run.json`：机器可读结果
- `evidence/public-qemu-browser-summary.json`：脱敏后的浏览器验收摘要
- `patches/`：不适用；改动已在合并 commit 中
- `code/`：不适用；复现入口位于主仓

## 未覆盖项

- 物理硬件、RF、电气、声学与光学：`NOT RUN`；
- C/QEMU 默认墙钟调度、长期稳定性和 Flash 持久化：`NOT RUN`；
- 网络、音频、其它设备、其它 Unit 和任意固件兼容性：未由本 PR 验收；
- Linux CI 已在 PR 与 main push 上执行；本地 macOS 平台套件保留一个
  与 PR 无关的 multicast 环境错误。
