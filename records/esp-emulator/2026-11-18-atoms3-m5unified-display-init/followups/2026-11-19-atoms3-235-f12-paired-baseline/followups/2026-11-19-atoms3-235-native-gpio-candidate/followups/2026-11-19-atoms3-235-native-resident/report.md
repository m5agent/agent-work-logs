# AtomS3 原生运行时发布回读报告

本次验收目标是确认常驻角色使用 AtomS3 原生显示修复的签名 QEMU，以及切换后的服务和历史记录可核验。发布从 `f12b15fb3dc2c27e31b804ccfffd63e8cbce89b8` 切换到 `c25fdfc9623cdd716a395b881466c426b319474d`。冻结清单中仅一个原生可执行文件的哈希发生变化，来源为 QEMU 上游提交 `40edccac415693c5130f91c01d84176ae6008566` 与板级补丁 `0232-atoms3-lcd-gpio-probe.patch`。候选的 SHA-256 为 `04abc3ba8cb115919e7faebd55425c802f4f6e40b10bc3cc422c51700add728e`，冻结后二次计算一致并通过严格签名检查。源码、旧新哈希和补丁摘要见[脱敏证据](evidence/atoms3-native-resident.summary.json)。

切换前校验空闲条件和原有运行身份，并在隔离夹具中演练两个角色的启动与回退。演练确认旧版本身份、新清单绑定、错误绑定拒绝、两角色启动选择器和历史恢复，未访问常驻端口。实际切换后，独立验证器重新检查两角色的新 QEMU 选择器、精确签名及保留历史，执行返回 0。生产回退未触发。

| 角色 | 历史保留 | 服务回读 |
| --- | --- | --- |
| 工作台 Device Service | 55 会话 | OpenAPI HTTP 200，36 设备目录，33 可创建 |
| 审核设备 Device Service | 98 会话 | OpenAPI HTTP 200，36 设备目录，33 可创建 |
| Reviewer 0.29.0 | 130 任务和抽查证据 | Darwin 后端就绪，应用代码固定为 `69386c6a162a1c786d6745c46eaa330c14558d3c` |

两份实际提供的 Device Service OpenAPI 均为 1.99.2，SHA-256 `cd1a84391f6f091fef671f05720c13f7d453c7378b70117e34b83ba6515b8689`。公开可复查的步骤是分别读取两角色的 `GET /api/v1/openapi.yaml`，对比冻结清单中的哈希，按角色核对历史和已保留证据，再验证签名产物及启动选择器绑定。C6、浏览器运行时和 Tab5 P4 哈希保持原值。Cardputer SPI SD 和 Tab5 SD slot 0 原有能力保留；Tab5 USB host 仍为 `PARTIAL`，未启用 USB endpoint 夹具。

功能验收链接记录同一签名 QEMU 跑过原版 Spirit Level、Motion Face、Pocket Clock 与官方 UIFlow2 对照。标准 Reviewer 复验另行记录应用就绪通过、交互项待验收。此次发布使用常驻 API 和配置回读，生产固件访客、Linux 常驻路由和浏览器站点发布均未运行。Burner 未提交。公开记录保留版本、计数、限定的能力状态与回读记录哈希，省略服务位置、进程和私有标识。 [原版虚拟设备验收](../../README.md) · [Reviewer 独立复验](../2026-11-19-atoms3-235-reviewer-029-standard/README.md)
