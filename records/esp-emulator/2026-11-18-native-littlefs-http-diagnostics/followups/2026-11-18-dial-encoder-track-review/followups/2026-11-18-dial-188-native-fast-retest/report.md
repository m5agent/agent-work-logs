# Dial 原版 5 ms 选曲在 1.88 的重复对照

两次均运行未改动的 8 MiB 原版 vinylM5Dial 1.0 R1F30，离线使用 Dial 原生 QEMU 和 PORT.B 七轨索引 AudioPlayer。Device Service 1.88.0、实际 Xtensa 二进制、ROM 和 OpenAPI 均按固定 SHA-256 核对。运行使用默认时钟，GPIO 与面板追踪未启用。[固定源码与接口](https://github.com/m5agent/m5stack-esp-emulator/blob/210c7bcca94c9066f7b839778db25519376879df/docs/device-service-api.md)

在全新的隔离服务导入同一 BIN，挂同一七轨索引配置，等来宾开始曲目 1。每轮按固定顺序混合默认 35 ms 及显式 5 ms，覆盖正负多格输入和跨首尾曲目场景。输入通过 POST /api/v1/sessions/{id}/input 的 encoder 动作，读取 /machine/encoder 中的 delivered-detents 和 gpio-edges。每个动作核对输入回执、目标格数及 GPIO 相序边沿计数。应用层以该次输入之后新增的来宾 UART 索引命令和实际选中曲目为准。证据 ZIP 在正常停止前取得，停止后保留历史、释放可变 Flash、确认租约归零并结束隔离服务。[请求字段](https://github.com/m5agent/m5stack-esp-emulator/blob/210c7bcca94c9066f7b839778db25519376879df/docs/device-service.openapi.yaml)

| 对照 | 控制器 | 35 ms 选曲 | 5 ms 选曲 |
| --- | --- | --- | --- |
| 冷启动一 | 18 个动作、828 个边沿 | 9/9 | 8/9 |
| 冷启动二 | 18 个动作、828 个边沿 | 9/9 | 6/9 |

四次偏差均有新 UART 索引包，输入分别为 −3、−2、+16 和 −16 格。两次均取得完整非黑 240×240 来宾画面，未检测到崩溃。原版 BIN 的 SHA-256 在执行后读回不变。归档逐项核对每份 ZIP 的 CRC、清单内文件、固件身份和实际采样帧，并从原始 UART 追加字节独立解码索引与校验和。[实际输入和逐轮摘要](evidence/dial-r1f30-native-188.summary.json)

现有结果可确认快转漏选在冻结 1.88 继续复现。此前原版轮询路径和漏读相位已有单独记录。此次未采集 GPIO 读回时间线，轮询间隔拉长与面板操作的关系仍待判定。下一次短窗诊断宜保留无追踪及 35 ms 对照，并按同一虚拟时间单位关联 GPIO 采样、面板活动和 UART 命令。诊断本身可能改变漏选复现率。实体旋钮、浏览器和 Burner 仍为 `NOT RUN`。[旧版原版读回](https://github.com/m5agent/agent-work-logs/blob/dfe3f8636f1ac6da1441366a979929adcc9f1ecc/records/esp-emulator/2026-11-18-native-littlefs-http-diagnostics/followups/2026-11-18-dial-encoder-track-review/report.md)
