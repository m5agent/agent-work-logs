# Linux 冷启动恢复修订的 macOS 常驻切换

前序冻结提交为 `981fdcdf09253b75be960772147258b677775d8c`。更新到主分支冻结提交 `9837c3f84df4383eb74881a1f44fcd3f460daefa`，其中 Linux 恢复实现为 `97339c1137e4e8564114e7476ba607f1129fe68c`。隔离虚拟设备已用 CardputerDict 0.6.4 原版验证无凭据继续阻断、可信凭据回收旧会话以及标准重试后的 MP3 缓存与 PCM 播放。 [功能验证](../../report.md) · [主分支源码](https://github.com/m5agent/m5stack-esp-emulator/commit/9837c3f84df4383eb74881a1f44fcd3f460daefa)

切换前两套设备服务与审核服务无活动会话、租约、工作任务或恢复意图。协调切换及独立回读成功。

| 验收项 | 回读结果 |
| --- | --- |
| 工作台与审核侧 Device Service | 两角色均接受租约，各有 36 个目录项、33 个可创建型号。分别保留 55、98 条历史。 |
| Device Service API | 两角色的 OpenAPI 1.99.0 均返回 HTTP 200，响应字节与固定版本匹配。 |
| 审核服务 | 0.27.0 源码与应用保持一致，就绪返回 HTTP 200。连接已验证的 macOS 审核角色，129 条历史和抽样 ZIP 保持一致。 |
| 运行时与能力 | Xtensa、C6 与浏览器包清单身份保持一致。Tab5 USB Host 仍为部分支持，USB endpoint 夹具未声明。 |
| Linux 宿主凭据 | 两套 macOS 常驻角色保持默认启动参数，未传入宿主停机凭据。 |

本次验证范围为 macOS 常驻版本、API 和历史读回。Linux 常驻切换与生产来宾为 `NOT RUN`，Burner 未提交。隔离 Linux 试验中的宿主控制器先确认旧 VM 停机并独占交接状态卷。发放凭据前也需撤销和回收该租约在宿主侧的资源。 [回读摘要](evidence/resident-readback.summary.json)
