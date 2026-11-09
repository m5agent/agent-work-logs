# ESP Emulator GitHub Pages 固件画面 Skill

| 项目 | 记录 |
| --- | --- |
| 日期 | `2026-11-09` |
| 结果 | `PASS`，限两种导入方式的启动与显示 |
| 工作类型 | `code_change` |
| 问题来源 | 轻量在线虚拟烧录与画面预览需求，独立公开 Issue 不适用 |
| 源码版本 | `8131c4682e4ef89b7a28ec6a47ab09f38a2636f1` 为 Skill 开发基线，公开工作台对应 `5f15d1f824958829f7d62648a5efbfe5fcee2edb` 的静态导出 |
| 环境 | 公开 GitHub Pages、桌面 Chromium、CoreS3 C/QEMU WASM |

## 结论

新增 `m5stack-browser-simulator`，与 AIFlow 代码预览和 Device Service 联调 Skill 并列。Skill 只需要浏览器控制能力，按已部署的板型选择完整合并 BIN，启动后观察客体屏幕，再停止运行。

## 关键证据

- Skill 校验和打包契约通过。平台回归 2,042 项通过，10 项跳过。独立 ZIP 包含说明、MIT 许可证和校验清单。
- ZIP 的 SHA-256 为 `2069554003cc975131af548b0713094f9371a386af57dd18fe2ffb9de358afa0`。公开工作台直接复用当前部署。
- CoreS3 使用官方 UIFlow2 v2.5.3 完整镜像，分别经公开 HTTPS BIN 链接和本地 BIN 导入运行。两次均取得 320×240 客体帧。直链试验显示 UIFlow2 Develop，本地文件试验保留了启动画面。两次均正常停止，本地文件试验的 6 个 CDP Worker target 全部消失。
- 裁切保留状态栏和菜单，原始 RGB565 帧的 SHA-256 在运行摘要中。 [运行摘要](run.json) · [客体帧裁切](evidence/cores3-develop-frame-crop.png)

## 文件与边界

- [验证报告](report.md)
- [运行摘要](run.json)
- [直链导入后的 Develop 界面裁切](evidence/cores3-develop-frame-crop.png)
- [本地 BIN 导入后的启动画面](evidence/cores3-local-bin-splash.png)

结果限于该 CoreS3 固件和部署配置的启动、屏幕及停止。物理设备、其它板型、应用交互及网络功能未执行。固件二进制、完整运行记录和原始会话标识保留在测试端。
