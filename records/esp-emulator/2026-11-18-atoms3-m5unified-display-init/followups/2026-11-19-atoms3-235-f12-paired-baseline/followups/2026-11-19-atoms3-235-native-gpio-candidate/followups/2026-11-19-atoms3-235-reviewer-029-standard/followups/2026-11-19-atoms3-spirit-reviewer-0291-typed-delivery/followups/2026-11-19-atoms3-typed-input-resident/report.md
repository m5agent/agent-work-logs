# Device Service 1.99.3 与 Reviewer 0.29.1 常驻回读

本次发布将原版 Spirit Level 在独立环境中验证的 AtomS3 类型化按键路径应用到两套 macOS 常驻角色，再更新 Reviewer 的按压描述解析。先切换 Device Service，确认旧 Reviewer 0.29.0 仍在相同 Darwin 服务角色上就绪，随后上线 Reviewer 0.29.1。两个步骤分别留存实际切换与独立回读结果。 [原版标准路径](../../README.md)

## Device Service

从 `c25fdfc9623cdd716a395b881466c426b319474d` 切换至 `2a7f979c0c7e67420d8b790a3cfdb692702abf05`。冻结清单 SHA-256 为 `c6e575ba562ea0815331018c2a4a1b2400ca2531fa7ef53fdfd9322557f2eb8b`。隔离标准审核使用 `86aa77a9e8eb7df4e582614cb3d4b48028645e11`，到实际发布只新增三份文档变更，包括状态、积压和验收说明，输入模块、设备 API 及运行时字节一致。签名 Xtensa 通过严格签名检查，C6、P4 及浏览器冻结清单保持原有字节。

| 常驻 Device Service 角色 | 保留会话 | 目录设备 | 可创建 | OpenAPI |
| --- | --- | --- | --- | --- |
| 工作台 | 55 | 36 | 33 | HTTP 200，1.99.3 |
| 审核设备服务 | 98 | 36 | 33 | HTTP 200，1.99.3 |

两个角色通过 `GET /api/v1/openapi.yaml` 回读与冻结 YAML 一致，SHA-256 为 `1cfe820f82c08d1295563b8f760ba1a39026661241c74170554e2732ab2cca18`。确认 Cardputer SPI SD 和 Tab5 SD slot 0 原有能力。Tab5 USB host 继续标为 `PARTIAL`，未启用 USB endpoint 夹具。设备启动与回退校验先在离线夹具通过，两角色切换后独立验证退出码为零。

## Reviewer

从 0.29.0 `69386c6a162a1c786d6745c46eaa330c14558d3c` 更新至 0.29.1 `3a45e3dd59c2163e0ffd8f948a484a8213b6b82b`。切换前在系统 Python 3.9.6 上针对同一份冻结 Device Service 分别验证旧、新 Reviewer 的 Darwin 后端就绪。常驻发布只替换一个应用模块，保留配置、SQLite 数据库和现有状态。切换后 `GET /api/ready` 返回 HTTP 200，独立核对 130 条任务、统计及抽查的早期和近期证据 ZIP；备份通过一致性门槛，回退未触发。Reviewer 的 OpenAPI 0.29.1 仓库契约 SHA-256 为 `d20d0934ad027575c1b8b4a3dee52b8a88020982a9da929d5df659df099cd7b0`，就绪 HTTP 回读确认该版本及实际后端。

## 功能范围

同原版标准审核在隔离会话中验证了 BtnA 三次 GPIO41 送达及启动，仍以 `SIM_PARTIAL` 结束。本次常驻验收依据 API、运行身份与历史回读。生产固件访客、实机、Linux 常驻路由和浏览器站点更新均未运行。Burner 未提交。公开记录保留精确版本、冻结摘要、角色与历史计数、证据回执哈希，省略服务位置、交易编号和历史内容哈希。 [脱敏证据摘要](evidence/atoms3-typed-resident.summary.json)
