# UIFlow 就绪提示正式 Pages 发布

PR #195 将受测 UIFlow 就绪提示合入 `27fcebd438b6c412b272fe90d0f71a1ab7914735`。本地 browser-WASM 与 native CoreS3 证据已归档。正式站点使用独立的构建、门槛和线上回读结果。[PR #195](https://github.com/m5agent/m5stack-esp-emulator/pull/195) · [此前验证](https://github.com/m5agent/agent-work-logs/blob/17651d171c0774c70b466b326b01413f478cfd76/records/esp-emulator/2026-11-09-uiflow-workbench-ready/report.md)

首次调度 `42556851376` 的 build 在执行步骤前被取消，deploy 跳过。GitHub 检查标注指出 `macos-14-arm64-us-default` 配置已不支持。官方公告列出 macOS 14 runner 的退役日期为 2026-11-02。[首次运行](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42556851376) · [GitHub 退役公告](https://github.blog/changelog/2026-10-01-github-actions-macos-14-runner-image-retirement/)

`70ca46258598294eb5e5852115b1dfce386d8754` 将发布构建 runner 改为 `macos-15`，同步 `test_public_site.py` 和发布文档。逐字对比确认 workflow 仅改变 runner 标签，原构建与验收门槛完整。工作台的 HTML、CSS 和 JS 源码与本地受测提交一致。`test_public_site` 10/10、snapshot 与 PR scope 通过。[迁移提交](https://github.com/m5agent/m5stack-esp-emulator/commit/70ca46258598294eb5e5852115b1dfce386d8754)

正式运行 `42557006648` 完成固定 C/QEMU 构建、资产导出和 Canvas 正负控。60 个预定用例中 15 个通过、1 个失败、44 个未运行。首个失败为 AtomS3 Lite editor 的 `all-cdp-workers-closed-before-context`。证据已保留，Pages artifact 上传及 deploy 均跳过。[正式运行](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42557006648) · [门槛证据](evidence/hosted-gate-summary.json)

失败用例通过精确固件绑定，执行 11 个程序用例，硬复位后 console epoch 从 0 到 1 并恢复运行。QMP 正常退出码为 0，5 个 pthread 清空，强制处置与 engine fallback 均为 0。iframe 移除后，常规 120 秒等待及额外 30 秒清理等待均观察到同一个 `public-qemu-engine.js` CDP target。该结果限定于 context 关闭前的 target 检查，根因待后续诊断。[失败用例摘要](evidence/hosted-gate-summary.json)

本机独立对照使用相同的 33 个 Web 资产、5 个运行时资产、固件、ROM 和测试脚本。11 个程序及硬复位路径通过，58/58 检查成功，6 个 CDP target 全部退出。两次运行的浏览器环境及生成的 manifest 分别记录，hosted 失败保留。[本机对照](evidence/hosted-gate-summary.json)

本次正式部署、线上回读和物理硬件属于 `NOT RUN`。后续恢复按独立执行追加。
