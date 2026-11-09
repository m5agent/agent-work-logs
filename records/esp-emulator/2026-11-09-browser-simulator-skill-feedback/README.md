# ESP Emulator #211 浏览器 Skill 与运行证据

| 项目 | 记录 |
| --- | --- |
| 日期 | `2026-11-09` |
| 结果 | CoreS3 浏览器 WASM 定向验证通过 |
| 工作类型 | `code_change` |
| 问题来源 | [GitHub #211](https://github.com/m5agent/m5stack-esp-emulator/issues/211) |
| 源码 | [Skill 和工作台提交](https://github.com/m5agent/m5stack-esp-emulator/commit/6d02f46685e4b60d4553fcb312e2c81a4b45c2e8) |
| 环境 | 正式 GitHub Pages 基线和独立导出的静态工作台，桌面 Chromium，CoreS3 C/QEMU WASM |

Skill 现在区分浏览器选档权限、固件校验、客体首帧和应用画面。工作台增加可读取的启动阶段、双 SHA 和下载请求状态。自定义 BIN 的显示与 REPL 探测分别报告。

- 正式站点固定示例 49 项通过。两轮真实鼠标按住后释放均收到客体触摸事件并更新画面，PIR 单独获得控制器和客体回读。
- 更新后的静态工作台用同一份官方 CoreS3 UIFlow2 v2.5.3 BIN 验证选档、320×240 Develop 画面、双 SHA、本地记录和正常停止。原厂固件的 REPL 握手超时单列。内置编程环境 29 项通过。
- 平台回归 2,051 项通过，10 项跳过。浏览器契约、Skill 包装测试及生成物验证通过。

[详细报告](report.md) · [结构化记录](run.json) · [双 SHA 界面](evidence/firmware-identity.png)

真机、反馈中的一次短点击及本轮外的机型未复测。工作台改动在独立导出的静态站验证，正式站点基线结果只覆盖旧部署实际运行的路径。
