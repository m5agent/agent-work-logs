# StackChan Issue #139 pt-BR 语言支持请求

- 日期：`2026-11-25`
- 结果：`REVIEW`
- 工作类型：`issue`
- 问题来源：https://github.com/m5stack/StackChan/issues/139
- GitHub 回复：https://github.com/m5stack/StackChan/issues/139#issuecomment-7150663269
- 源码版本：`m5stack/StackChan @ 28b9f0c8bd6acd81cb3c70f1a93c3e373b39d400`（main，v1.6.2）
- 环境：macOS；只读 sparse clone（`app`/`firmware`/`server`）；本机 Device Service 设备列表只读查询；
  未使用任何 xiaozhi 账号凭据

## 结论

作者判断基本成立：`value_constant.dart` 的语言表只是显示名映射，Agent Setting 的语言下拉由远端
`GET https://xiaozhi.me/api/user/tts-list` 的 `tts_voices` key 集合决定，选中的 key 再作为
`language` 提交。所以缺 pt 选项不是 App 映射表的问题，而是该账号语音目录里没有葡语音色；
App 侧在目录返回 `pt` 后无需改动即会显示（显示名已存在）。设备界面语言另有 `pt-PT` 支持，
但那是界面文案、不是对话语言。

结论层级为 **code-level verification**；硬件与虚拟设备均 `NOT RUN`，真实语音目录也因需要账号
令牌而未能读取。

## 关键证据

- 下拉来源：`app/lib/view/popup/edit_agent.dart:88-91`、`:432-449`；
  显示名映射：`app/lib/util/value_constant.dart:163-205`（`pt` 在 `:180`）、
  未收录 key 回退：`edit_agent.dart:246-252`。
- 目录与提交：`app/lib/util/xiao_zhi_util.dart:33,259,309`；`edit_agent.dart:203`。
- 服务端同源：`server/internal/xiaozhi/xiaozhi.go:46,273-281`；
  合并 `languages`+`tts_voices`：`server/internal/service/agent.go:128-160`。
- 固件 UI 葡语：`firmware/main/Kconfig.projbuild:83-84`、
  `firmware/main/CMakeLists.txt:192-193,243`。
- 目录接口未认证探测：`401 {"success":false,"message":"No token provided"}`，
  说明目录需账号令牌，内容不可见。

## 文件

- `report.md`：完整报告
- `run.json`：结构化记录
- `evidence/source-excerpts.md`：带 commit 与行号的源码片段
- `evidence/tts-list-probe.md`：目录接口探测记录

## 未覆盖项

- 硬件验证 `NOT RUN`：问题在 Flutter App 与远端目录，实机不经过该路径。
- 虚拟设备验证 `NOT RUN`：本机 `stackchan` profile 只复现固件运行时，不执行 App 页面，
  也不持有 xiaozhi 令牌。
- 未读取真实语音目录；未构建/运行 App；未验证葡语音色质量与 ASR pt-BR 识别效果。
