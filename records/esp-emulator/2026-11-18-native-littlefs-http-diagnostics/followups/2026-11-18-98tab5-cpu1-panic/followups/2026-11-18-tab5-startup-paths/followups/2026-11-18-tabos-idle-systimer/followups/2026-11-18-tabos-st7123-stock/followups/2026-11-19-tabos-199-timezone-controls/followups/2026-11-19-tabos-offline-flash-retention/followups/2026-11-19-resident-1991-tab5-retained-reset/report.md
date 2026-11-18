# Device Service 1.99.1 发布与常驻回读

## 发布依据

两个 macOS Device Service 角色从 `9837c3f84df4383eb74881a1f44fcd3f460daefa` 更新至 `c9ec0f274579b78d87a4a301147f351e8b7a48fa`。发布提交在已用原版 M5TabOS 0.9.1 实际验证的 `76e734f5cf061bc7985a1bf6146f2cb5de223023` 之后仅更新文档。核对完整差异、冻结发布清单和三份库存收据，保留原有 Xtensa、C6 和浏览器清单字节。平台测试报告共 2,491 项，其中跳过 10 项，测试结果通过。运行覆盖、外设目录、QEMU 配置和项目快照检查均通过。

发布前确认工作台、审核设备和 Reviewer 空闲，活动会话、租约、审核任务和待恢复请求均为零。通过 APFS 写时复制准备冻结发布，并完成有界备份及可回退的切换检查。Reviewer 在依赖角色切换期间短暂停住，随后使用原有运行文件与配置启动。切换成功，无需回退。

## 独立回读

| 角色 | 验证结果 | 历史 |
| --- | --- | --- |
| 工作台 Device Service | 健康且接受租约，36 个目录设备，33 个可创建，HTTP 200 提供精确 OpenAPI 1.99.1 | 55 条会话 |
| 固件审核设备 Device Service | 健康且接受租约，36 个目录设备，33 个可创建，HTTP 200 提供精确 OpenAPI 1.99.1 | 98 条会话 |
| Reviewer 0.28.0 | 实际 macOS 后端 HTTP 200 就绪，运行文件与配置相同 | 130 条审核任务，抽样证据 ZIP 相同 |

独立校验退出码为 0。另行读取两套角色的 OpenAPI 响应，确认版本、完整字节摘要及 `tab5_flash_save_failed` 契约。Reviewer 的 OpenAPI 摘要对应仓库文件，常驻端分别回读就绪状态和实际后端。Tab5 SD 能力、Cardputer SPI SD 能力继续提供。Tab5 USB host 保持 `PARTIAL`，没有宣告 USB endpoint 夹具。

## 验证范围

[原版固件的独立原生运行](../../README.md)验证了同会话复位和停机导出两种 Flash 保留路径，[后续受控中断](../2026-11-19-tabos-p4-reset-save-fence/README.md)验证了写回无法确认时的 HTTP 409。该常驻里程碑记录正式服务接管、契约回读及历史保留。生产固件会话、真机、Linux 常驻路由和 Pages 发布均未执行。Burner 未提交。
