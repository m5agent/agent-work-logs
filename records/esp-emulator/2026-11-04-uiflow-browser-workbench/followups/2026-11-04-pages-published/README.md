# UIFlow工作台已合并并部署

日期：2026-11-04。PR #165已合并，静态工作台已上线。维护者要求先发布并记录已知问题，本次没有把未通过的完整运行门禁改写为PASS。

- [在线模拟器](https://m5agent.github.io/m5stack-esp-emulator/)
- [实际部署](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41816252534)：2026-11-04T10:45:44Z完成。
- [发布包](https://github.com/m5agent/m5stack-esp-emulator/releases/tag/pages-uiflow-workbench-20261104-23d38d8d)：完整上传/下载SHA一致。

2,130个HTTPS资产逐项字节/SHA与发布包匹配。Matrix、StickC Plus、CoreS3的实际HTTPS编辑器和按键共6例、222检查、35程序、10次键鼠输入通过，全部正常退出；其余34个HTTPS用例未运行。

已知问题保留：hosted Matrix启动超时、Lite硬复位PIF及RUNTIME-07/08/09；详见[报告](report.md)及[之前失败记录](../2026-11-04-pr165-release-qualification-failures/report.md)。

- [结构化执行](run.json)
- [部署与已知问题摘要](evidence/deployment-summary.json)
- [HTTPS首6例有界证据](evidence/https-first6-summary.json)

## 文档收尾

[PR #166](https://github.com/m5agent/m5stack-esp-emulator/pull/166)已合并为3e8f76b836009438b7d9312e1e7b8f822b7d64f5，50项文档合同与push/PR四项CI通过；合并树与已验head相同。
[收尾摘要](evidence/documentation-closeout-summary.json)保留校验身份；最终HTTPS manifest仍为685e…，运行时资产未变，原故障继续开放。
