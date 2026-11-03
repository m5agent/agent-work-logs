# WeCom GPT bridge model and authorization recovery 报告

## 背景与目标

用户报告企业微信机器人没有正常回答，并授权调整桥接以使用当前已登录的 GPT 账户、测试连通性。验收分别覆盖模型运行、历史压缩、企微业务 API、常驻连接和真实自动回复，避免用某一接口成功替代整条链路。

## 结论

核心短文本通道 `PASS`：真实用户入站后，部署中的 GPT 完成任务，平台接受自动流式回复。整体 `PARTIAL`：旧混合 provider 历史压缩仍 `FAIL`；server recall 重写超时但普通装配回退成功；接收端已读及视觉显示、长任务和媒体回归未检查。

## 已确认的问题

旧 CLI 0.154.0 使用 ChatGPT 鉴权调用 `gpt-6.1-sol`，生成及远程历史压缩都返回 `400 model_not_found`。桌面内置 CLI 为 0.164.0-alpha.11.1，与服务原调用版本不同。

另一路企微会话列表返回 `850003 authorization expired`。本地显示已配置不能证明业务权限有效。用户在现有机器人的管理页续期，未重新创建机器人。

## 修改与运行配置

桥接显式指定 `gpt-6.1-sol` 与 `openai` provider，支持可选 CLI 可执行文件，改用桌面内置 CLI。子进程 PATH 前置该 CLI 目录，桥接专用 recall 模式改为 `server`。全局 Codex 和 plugin 配置未修改。

provider 通过 direct argv 传入 `-c model_provider="openai"`，不经过 shell。未配置可选项时保留原调用默认值。修改前保留本机回滚备份。[修改摘要](evidence/bridge-change-summary.md)包含通用逻辑和基线/部署文件指纹；宿主路径、配置全文、身份和凭据不对外归档。

## 新会话与 recall 对照

两次真实模型调用分别返回精确标记 `BRIDGE_MODEL_OK`、`BRIDGE_SERVER_RECALL_OK`，并产生 `turn.completed` 和 usage。

| 调用 | input | cached input | output | 结果 |
| --- | ---: | ---: | ---: | --- |
| 新会话，直连对照 | 27104 | 13184 | 8 | PASS：指定标记与完成事件 |
| 新会话，server recall | 27670 | 13184 | 10 | PASS：指定标记与完成事件 |

第二次模型探针已注入 2712 字符自动召回上下文。另一次直接运行实际 recall hook，服务端 `recall_context_assembled` 统计为 `entries=8`、`usedTokens=1267`、`rewrite=timeout`，随后 `server_assembled` 完成并返回 2120 字符上下文。这证明 server recall 装配及回退正常，**没有证明压缩重写成功**。[recall 摘要](evidence/server-recall-summary.json)保留源采集指纹和精确统计。

## 旧历史兼容性与迁移

对旧会话使用隔离 ephemeral fork，并将压缩阈值设为 4096，复测实际远程压缩路径。原先 `model_not_found` 已消失，但请求返回 `400 array_above_max_length`，指出 `input[99].content` 不兼容。**旧历史压缩仍为 FAIL，没有修复或宣称修复。**

隔离测试前后原会话文件和桥接映射哈希一致。随后保留原会话文件，备份六个旧映射，于 `2026-11-03T14:19:31+08:00` 将当前映射原子替换为空对象，以后续入站创建新的 GPT 会话。这是绕过不可复用的旧历史；新会话不自动承接旧聊天上下文。

确认无活动子任务后重启，`2026-11-03T06:19:31.751Z` 出现 `AUTHENTICATED`。认证就绪后再执行真实用户输入验证。

## 真实用户自动回复验证

| 时间（UTC） | 观察 |
| --- | --- |
| `2026-11-03T06:20:16.561Z` | 桥接收到真实用户短文本；2 字符、0 图片、此前 0 个运行任务 |
| 同次会话运行记录 | `model=gpt-6.1-sol`、`effort=ultra`，出现 `task_complete` |
| `2026-11-03T06:20:39.163Z` | 等待的 `replyStream` 操作成功；日志 `reply sent via stream`，回复 3 字符，四舍五入耗时 23 秒 |

该窗口没有 handler 或 failure-delivery 错误。SDK 的回复操作在平台错误回执时拒绝 Promise；此处等待成功后才记录 `reply sent`。这证明真实入站→GPT→平台接受自动回复的短文本路径，不能推断接收端已读或视觉渲染。用户确认发送测试输入，尚未独立检查接收界面。[自动回复摘要](evidence/automatic-reply-summary.json)保留原日志和会话快照 SHA256、字节数、采集时间及脱敏时序，不含原消息正文、响应正文、发送者或会话标识。

## 新 GPT 历史分叉回归

对新 GPT 历史执行阈值 4096 的 ephemeral fork，请求返回 `WECOM_NATIVE_COMPACT_OK`，exit 0，usage 为 input 52639 / output 70；源 rollout 与桥接映射哈希未改变。该隔离测试证明新 GPT 历史分叉及请求完成 `PASS`。

JSONL 仅观察到 `agent_message`，没有显式 compact 事件，stderr 为空。因此未确认实际远程压缩执行，**不宣称远程压缩 PASS**。[分叉摘要](evidence/new-gpt-history-fork-summary.json)保留结果、源采集指纹和该边界。此项不会覆盖旧混合 provider 历史仍然失败的结论。

## 企微业务接口验证

续期后会话列表返回五个最近会话；向授权用户发送诊断文本，平台返回 `success=true`。这些结果作为独立的业务访问及出站提交验证，不用于替代自动回复实测。[接口摘要](evidence/wecom-business-api-summary.json)保留脱敏结果及源采集文件指纹。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | NOT RUN（固件）/ PASS（脚本语法） | 无固件构建；部署脚本 `node --check` 通过，运行行为由真实流量另证 |
| transport | PASS（短文本核心路径） | 实际业务 API、长连接认证及真实入站到平台接受自动回复 |
| device_response | PASS（新会话）/ FAIL（旧历史压缩） | 新模型请求完成；旧历史压缩仍报 payload 不兼容 |
| data_behavior | PASS（短文本） | 同一入站任务的模型完成与回复成功时序一致 |
| recall rewrite | PARTIAL | server 装配/回退完成；rewrite timeout |
| visual_or_physical | NOT RUN | 未检查接收界面或已读状态；无嵌入式设备结论 |
| delivery | PASS（归档材料完整性） | 记录、派生证据和脱敏检查完成；双端提交结果以交付消息中的固定 commit 链接为准 |

## 未覆盖项与风险

- 接收端已读及视觉渲染未检查；平台接受不等于客户端已读。
- 旧历史压缩仍失败；新会话不自动继承旧上下文，旧文件与六个映射备份保留。
- server recall 重写超时，普通装配回退正常；后续如需压缩效果，应单独验证重写成功及质量。
- 长任务跨流式窗口、媒体收发、并发回归未在本次短文本检查中执行。
- 桌面应用更新后内置 CLI 位置或行为可能改变，服务需复核可执行文件与认证状态。

## 回滚

避开正在执行的任务，恢复修改前桥接脚本、配置和旧映射备份，再重启并核对认证。原会话文件未删除。恢复旧映射会重新引入已观测到的历史压缩失败，不能把回滚本身视为恢复验证。

## 参考

- [企业微信官方维护者说明](https://github.com/WecomTeam/wecom-cli/issues/114)：2026-10-20 回复说明应对现有机器人续期业务权限。
- [OpenAI 配置说明](https://learn.chatgpt.com/docs/config-file/config-reference)：模型和 provider 配置；文档会随版本更新，本次版本以上述实际 CLI 为准。
