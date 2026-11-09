# ESP Emulator 23 板正式 Pages 发布

| 项目 | 记录 |
| --- | --- |
| 日期 | `2026-11-09` |
| 工作类型 | `code_change` 与部署 |
| 结果 | `PARTIAL`，下载恢复，托管门禁未通过 |
| 问题来源 | 用户批准更新正式 Pages，纳入 #211 和主线浏览器机型更新 |
| 源码版本 | [发布提交 0ea7e36a](https://github.com/m5agent/m5stack-esp-emulator/commit/0ea7e36ae0dd769deb8bf83529756db5e9213e8e) |
| 环境 | GitHub Actions macOS 15 与本机独立静态导出，桌面 Chromium |

首次发布在 libffi 匿名 API 下载收到 HTTP 403，构建和部署均未启动。工作流现在先尝试锁定的官方归档地址，必要时回退到 release asset API。下载后的大小及 SHA-256 均校验，再交由原构建器复核。新任务通过下载步骤并完成源码构建，托管全量门禁在 Atom Matrix 引擎 Worker 回收失败，部署跳过。[首次失败](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42597136388) · [重跑](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42597576699)

当前源码的静态导出含 23 款准入设备。上一次托管失败的 StickC Plus 在该本机导出完成 63 项编辑器、显示、硬复位与 Worker 清场检查。它是本机独立结果，托管全板型门禁仍未通过，未更新实际 HTTPS 站点。

[详细报告](report.md) · [运行摘要](run.json) · [回退验证](evidence/archive-recovery-summary.json)

最新托管任务完成构建和 CoreMatrix 原版镜像验证，随后在 Atom Matrix 复位就绪超时及失败清场的引擎目标残留处受阻。部署任务跳过，公开站点仍是先前 19 板版本。 [第三轮验证摘要](evidence/hosted-self-close-reset-summary.json)
