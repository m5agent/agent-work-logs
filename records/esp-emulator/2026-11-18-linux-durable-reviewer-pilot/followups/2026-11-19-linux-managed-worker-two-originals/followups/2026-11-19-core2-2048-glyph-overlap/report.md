# Core2 2048 审核器避开数值字形取样

Core2 的 2048 Game 1.0 原版在此前 A3 审核的最后一次向下滑动已受理，两张结果 PNG 完全相同。画面中的两个 8 合并为 16，并合法出现一枚 4。Reviewer 0.29.1 在每个方块内取三个相邻对角像素，左下方 16 的字形覆盖了取样点，导致 `board_postcondition_unavailable`，整单保留为 `SIM_PARTIAL`。原审核和证据已保留。 [原记录](https://github.com/m5agent/agent-work-logs/blob/a325a930fb3c8a2afcd6bb084384f38383de3be6/records/esp-emulator/2026-11-18-linux-durable-reviewer-pilot/followups/2026-11-19-linux-managed-worker-two-originals/report.md)

修复将颜色取样移至方块上下两条背景带，每条取三点。六点必须同色且属于已知颜色才可识别。检测器继续要求两帧棋盘一致，并逐次核对移动、合并与一枚合法新方块。功能补丁为 `55a36c7f2b2be8c5e077aa7e2868034debfa0a75`，发布源码为 `88ca2e3c325565c2cc0f1099c9d98260fd78386a`，合约 `0.29.2`。原生 Device Service 源码固定为 `2a7f979c0c7e67420d8b790a3cfdb692702abf05`。本轮改动范围为审核器取样、相关回归和版本说明。

| 验证路径 | 结果 | 实测依据 |
| --- | --- | --- |
| 原失败帧对重读 | PASS | 完全相同的原始 PNG，旧模块 PARTIAL，新模块识别 16、向下合法移动和新出现的 4 |
| 三次历史运行重读 | PASS | A2、A3 首次与 A3 复跑共 54 张 PNG、27 对稳定帧及 24 次合法移动；原先 PASS 的棋盘逐一相同 |
| 新标准保存快照审核 | SIM_VERIFIED | 同一 505,760 字节原 BIN，13 帧观察共 60.011 秒，四方向各两次合法移动；此轮最高方块为 8 |
| 独立停止后 ZIP 回读 | PASS | CRC、九个清单成员的长度和 SHA-256 全部通过，归一化 Flash 中的应用字节与原 BIN 精确一致 |
| 清理 | PASS | 保留已停止会话历史，释放可变 Flash，来宾和独立服务退出，活跃租约为零 |

独立复核使用方块内部区域的主色重算棋盘，再加载固定发布模块逐张比较。旧模块仅无法识别那两张数值 16 的结果帧，新模块重读全部历史画面通过。新运行还逐一比对实际输入、成对 PNG、移动后的预期棋盘和新方块位置。Reviewer 使用系统 Python 3.9.6，306 项测试通过。OpenAPI 除版本和说明外的结构与基线一致。 [完整有界证据](evidence/core2-2048-glyph-overlap.summary.json)

历史数据来自 Linux 原生虚拟设备，新审核来自 Darwin 原生 Device Service，两者使用各自固定的 QEMU 摘要。帧数据重读与新来宾执行分别记录。数值 16 的取样修正由历史帧对验证，新一轮验证标准入口和八次完整动作。当前没有可用的匹配 Core2 与已验证触摸执行路径，物理硬件为 `NOT RUN`。浏览器运行与 Burner 提交亦为 `NOT RUN`。原始 BIN、Flash、PNG、ZIP、会话标识和主机日志留在私有证据存储。
