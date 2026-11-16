# 审核链路回归

用固定仓库源码及之前完整原生矩阵验证的 Xtensa 06db397c…、C6 69493c4e… 启动专用测试实例。候选 HTTP OpenAPI 字节与源码一致，目录 36 项、33 项可创建。

从历史材料核对原版 BIN 的 SHA 和长度，复制准备好同一描述及固件的保存快照。在独立审核进程通过 HTTP retry 启动任务，提交开关为关闭。审核控制面基线源码 116664d0… 执行了前三个样本，待合入的新分类 ff5cf39c… 执行了 CarPlay。

- 错位镜像报告 E_STATIC，输出两个偏移，分配 0 个会话。
- M5Apps 原版约 60 秒，按键证据帧为 31,931 个非黑像素，最终空闲帧为全黑。Tiny Journal 原版约 60 秒，最终帧 4,545 个非黑像素。两者保留 E_NETWORK_PARTIAL，其声明的网络功能没有运行期数据面证明。
- CarPlay 原版静态通过，匹配版本的 P4 0.50.0 后端收到 15 次截图 HTTP 409，约 60 秒串口观察，记录 E_EVIDENCE_UNAVAILABLE。证据目录的空 frame.png 是占位，实际没有取得 PNG。明确的缺少 ELF 信号优先于通用观察未完成，完整的 91 项审核测试覆盖不明 409、短观察及真实崩溃的优先级。

首次 Tab5 候选出现依赖资产未挂入导致的 E_SIM_COVERAGE，发生在创建会话前。补齐已验证的固定后端后重新跑原版，保留两次结果。两条控制面测试均使用保留历史的停止路径并关闭所属实例。

## 复现入口

从明确源码构建本机服务，使用已绑定运行时与 ROM，启动单独的设备后端、控制面和状态目录。配置禁用 Burner 提交及内容代理。复制保存的原版 BIN 与描述到独立 Store，核对声明 SHA 和长度，通过 POST /api/reviews/{id}/retry 发送 sourceMode=saved_snapshot 和 useAgentReview=false，再轮询 GET /api/reviews/{id}。复验错误码、会话差异、ZIP 和非黑像素。测试环境不启动新 Tab5 后端，不改变任何原版镜像。

本结果适用于隔离原生验证。物理设备、WASM、联网功能和驻留切换为 NOT RUN。Tab5 的上游控制器限制参考 [既有原版证据](https://github.com/m5agent/agent-work-logs/blob/e6eb65e47fcf94077409f0cf9e37f6ffc13ed707/records/esp-emulator/2026-11-14-p4-v1-originals/followups/2026-11-16-tab5-touch-usb-csr/report.md)。
