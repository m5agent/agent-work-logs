# 发布后原版 UIFlow2 用户路径验收

## 目标与固定版本

在固定源码 `8598b1f603ae6638a3f6d27824431781429b9e49` 和原生运行时
`dcb5c9f3f33bab3915348d48ce5dfa35483889ef1255977b2d49df6c17bea8f1`
上复验官方启动和本地编程。只把真实 MQTT 响应、官方 framebuffer、guest 串口
及清理结果作为验收依据。`main` / `review` 是脱敏的执行角色，不描述部署拓扑。

## 执行结果

| 角色 | 型号 | 实际入口 | 结果 |
| --- | --- | --- | --- |
| main | CoreS3、StickS3 | 真实网页官方模式 | 两次均 PASS |
| main | Core2、AtomS3R、StopWatch、Cardputer ADV | Device Service API | 四次均 PASS |
| review | CoreS3、Core2 | Device Service API | 两次均 PASS |
| main | CoreS3 | 真实网页本地 MicroPython 编程 | guest 串口与蓝底 Local code OK 均 PASS |

八次配对分别保存原始与规范化固件 SHA、NVS overlay 摘要、实际 DHCP/DNS/SNTP/
MQTT 数据面、帧 SHA 与停止前 evidence ZIP SHA。API 路径另外读回实际进程二进制
SHA；网页路径记录固定部署 runtime pin 与同会话 `qemu-wifi` 回执，不冒充另一种
运行时的测量。执行者逐帧确认六位官方码，归档者独立重新解析 ZIP 内 PCAP，
确认成功 CONNACK 与非空六位数字配对回复。

所有原始参考 pin 与先前准入镜像一致。完整 Flash 只补尾部 `0xff`，NVS 在会话
副本上配置；原始 BIN、官方应用和启动文件保持原样。编程对照另核对提交源码与
ZIP 内 guest 程序文件相同，且其 print marker 见于同 ZIP 的真实串口。

## 保留的观察失败

首次 `review` CoreS3 并非固件配对失败：观察脚本以空格拆进程命令行，截断了合法
可执行文件路径，导致二进制身份采集未完成。guest 已收到真实六位回复，手工保存
的 evidence 清楚记录当时仍为 `running`。该次以 observer `FAIL` 独立保留。

观察器改为读取进程 `comm` 字段后，重新创建会话完成完整流程。后续 PASS 不覆盖
首次失败，也不把缺少自动化结果解释成固件黑屏或配对失败。

## 清理与历史

归档者独立回读确认八次成功配对、一轮观察失败和一轮本地编程对照均已停止，
worker lease 全部释放。证据 manifest 为 `running` 且生成时间早于停止时间。
`main` 历史由 8 条增至 15 条，`review` 由 16 条增至 19 条；执行者验证旧历史保留，
复核时两个角色均为零活动会话、零活动 lease。

## 验收与复现边界

沿用[原始记录的公开复现步骤](../../report.md#复现步骤与验证层级)，选择摘要固定
原版 SHA；实际网页和 API 两条路径分开运行。每次使用同会话的协议、frame 和
停止前 evidence，不以 `running` 或单次 HTTP 成功替代应用验收。

flash、transport、device_response、data_behavior、virtual visual 和限定交付
均 PASS；此 follow-up 不新增 runtime 构建声明，也不证明 RF、电气、物理安全、
功耗、声学、browser-WASM 公网、其它固件或长期稳定性。没有 Burner 提交。
原始摘要完全未改写，首次失败和各次新执行均保留独立证据。
