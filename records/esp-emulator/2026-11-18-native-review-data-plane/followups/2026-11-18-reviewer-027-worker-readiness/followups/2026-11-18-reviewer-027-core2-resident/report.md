# Core2 2048 Game 1.0 原版保存快照干跑

在 macOS 隔离实例以 Reviewer 0.27.0 commit `a2d468b989139450ab95929597622bfa2074b7c3`、Device Service 1.99.0 commit `a729e24b1e4724b783ab2d59eec689cfdfeb24b3` 执行正常审核重试。使用同一份原版应用 BIN、原有的兼容厂商启动上下文、固定合成 Flash 和原生 QEMU。确切哈希见 [执行摘要](evidence/core2-dry-run.summary.json)。

1. 对原版保存快照发起标准重试，启用既有 `core2_2048_moves` 验收。Reviewer 返回终态 `done` 与 `SIM_VERIFIED`，实际读取的原版哈希和保存快照一致。
2. 上、下、左、右均通过合法棋盘变化验证。Reviewer 记录了四方向端到端结果。
3. 审核返回 Burner `NOT SUBMITTED`，提交请求字段为整数 0。第一轮在完成方向和源哈希检查后，测试脚本将该整数按布尔对象身份比较而中止。修正脚本断言后重新执行，完整通过全部终态及清理检查。
4. 校验停机前采集的同会话证据 ZIP，包含归一化 Flash 身份和原版源哈希。ZIP 为 328,586 字节，哈希 `1f207ec1ef8a3f11397038d89b5e8847ad7cf33f29e82b83af5cf79264858f8d`。检查各条目的大小和 SHA-256。实际会话状态 `stopped`，可变 Flash 已释放，活动租约为零，所启动的进程已退出。

四向交互的验收范围为隔离虚拟 Core2。物理 Core2、Browser WASM 与 Burner 为 `NOT RUN`。原始 ZIP、日志及会话标识保留本地。
## 常驻服务回读

安装相同 Reviewer 源码后，在线健康响应保留旧合约版本 0.5.0，并报告 OpenAPI 0.27.0。就绪检查返回 HTTP 200，工作器身份与实际 macOS Device backend 一致。两套 Device Service 角色仍为原 1.99.0 源码，活动设备租约、排队和运行中的审核均为零。

Reviewer 保留 125 条历史任务。核对了任务、批次、事件表，最早和近期各一份历史 ZIP，以及统计数据，切换前后均一致。在线 SQLite 备份完整性检查通过。常驻回读期间未另行执行 Core2 固件。[回读摘要](evidence/resident-readback.summary.json)
