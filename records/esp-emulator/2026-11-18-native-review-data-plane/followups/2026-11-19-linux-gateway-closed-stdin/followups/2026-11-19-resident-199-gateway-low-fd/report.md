# Device Service 常驻切换与读回

## 变更与验证依据

常驻 Device Service 从 `597e03214dc5f442787cec52f1720567e4ed2a00` 更新至主分支冻结版本 `981fdcdf09253b75be960772147258b677775d8c`。目标版本包含 `4216d548477d0b7a52b72f5e07dd07d98d7e8d63` 的 Linux 外层网关低位描述符修复。该修复已使用同一份原版 CardputerDict 0.6.4 实测关闭 stdin 的基线、拒绝和允许播放三条路径。 [同路径虚拟设备验证](../../report.md) · [修复源码](https://github.com/m5agent/m5stack-esp-emulator/commit/4216d548477d0b7a52b72f5e07dd07d98d7e8d63)

## 部署和独立回读

1. 固定切换输入的源码、原生运行时、浏览器包清单及两份服务文档，核对三套服务库存回执，并保留分开的有界备份。
2. 守护式协调切换按受理检查及角色身份核对后应用。随后在独立验证进程中重新读取服务就绪、目录、历史和文档。验证结束码为 0。
3. 工作台和审核侧设备角色实际返回 HTTP 200。在线 OpenAPI 文件逐字节匹配固定版本 1.99.0，SHA-256 为 `82758d20ff3d129ec57e2e1587bf699d683f44525f8dfa8befc05b433ed74325`，权威文档亦逐字节匹配。
4. 两个 Device Service 角色各有 36 个目录项和 33 个可创建型号，均接受租约，活动会话和租约均为零。工作台 55 条和审核侧 98 条历史与切换前一致。Tab5 USB Host 仍声明部分支持，USB endpoint 夹具未声明。已有的 SD 与 PCM 能力保持可用。
5. Firmware Reviewer 0.27.0 使用同一提交和应用文件，就绪返回 HTTP 200 且就绪值为真，绑定已验证的审核侧角色。其 129 条历史和抽样证据保持一致。Reviewer OpenAPI SHA-256 来自仓库契约。

两套原生运行时和浏览器包清单哈希均与切换前一致。回读摘要保留服务角色、资产身份和结果，省略本地拓扑、进程和会话标识以及用户数据摘要。 [脱敏回读摘要](evidence/resident-readback.summary.json) · [固定 Device Service API](https://github.com/m5agent/m5stack-esp-emulator/blob/981fdcdf09253b75be960772147258b677775d8c/docs/device-service-api.md)

## 范围与回退

本次通过的是协调切换和独立的常驻读回。生产来宾、Linux 常驻审核路由和实体设备均为 `NOT RUN`。隔离 Linux 原版功能验证保留在父记录。没有 API 契约或 Pages 发布变更，Burner 未提交。回退备份已保留，本次未触发回退。
