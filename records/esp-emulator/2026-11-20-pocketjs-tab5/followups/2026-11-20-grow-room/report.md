# Grow Room 在原生 Tab5 上的双外设工作流

## Applet

Grow Room 使用 TypeScript 和 Solid 实现自定义界面与场景逻辑。ENV III 监测温度、相对湿度和气压，示例阈值为 30 °C 和 45% RH。Ultrasonic-I2C 识别水面与探头的间距，以 10 cm 为满、60 cm 为空换算储水百分比，低于 30% 提示补水。G53 SDA／G54 SCL 的 Port A 连接一次使用一款 Unit。切换或移除时清除旧显示值。底层 worker、驱动及消息协议复用 [Pocket M5 v0.1.4 Unit Swap](https://github.com/pocket-nexus/pocket-m5/tree/db98ac45916a8ec4a2d85fa2a7e9cb09fa95bd1c/apps/unit-swap) 的 MIT 代码。

## 构建与运行

1. 用 Bun 1.4.2、[PocketJS `806ac202`](https://github.com/pocket-nexus/pocketjs/tree/806ac202141ece274f47c938c2899ffe8d30921d) 和 Pocket M5 v0.1.4 的 Tab5 host config 运行 `bun tools/pocket.ts compile --manifest "$APPLET/pocket.app.json" --host-config "$POCKET_M5/programs/m5stack-tab5/pocket.host.config.ts" --plan-dir "$BUILD/plans" --outdir "$BUILD/staging" --output "$BUILD/Grow-Room.pocket"`。生成 QuickJS-NG 0.14.0 字节码与 625,656 字节的包。
2. 将包暂存进原版发布 BIN 副本的 `storage` LittleFS 分区。以 4 KiB 块、128 字节读写粒度和 512 字节缓存，在偏移 `0xC10000`、大小 `0x3F0000` 的区域写入 `/apps/<Applet ID SHA-256 的前 16 位>/package.pocket`。校验分区并重新挂载读回包。镜像扩展到 16 MiB，`storage` 外的规范化字节与原版一致。来宾随后自行将包迁移到 apps 分区。
3. Device Service 1.99.5 与 esp-emu 1.1.0 创建原生 Tab5 会话，并运行[先前验证过的 Port A ESP Part](../2026-11-20-port-a-unit-swap/)。在 Pocket Shell 横屏坐标 `(106,99)` 点击 Grow Room，GT911 控制器 8/8 报告确认。读取串口 `GROW_ROOM ready`，开始采集屏幕。
4. 按表施加刺激，记录软件 I²C 事务、来宾日志和 framebuffer。在同一会话中先移除 ENV III，再接超声波 Unit。导出证据 ZIP 并校验后停止会话，未保留可写 Flash。

| 模拟输入 | 来宾界面 |
| --- | --- |
| `none` | Waiting for readings |
| `env:24:55:101320` | 24.0 °C、55% RH、1013.2 hPa，Climate stable |
| `env:34:38:100800` | 34.0 °C、38% RH、1008.0 hPa，Heat stress |
| `none` | Waiting for readings |
| `sonic:460` | 46.0 cm、28% reserve，Refill tank |
| `sonic:190` | 19.0 cm、82% reserve，Water ready |

## 结果与限制

应用打包、原生启动器触控、GPIO 软件 I²C、两种 Unit 的响应与来宾显示层通过。捕获 535 个 720×1280 的原始帧快照和 8 个不同的帧哈希。模拟输入事件与首次观察到的状态屏幕样本相隔约 0.881 s（热浪）及 0.839 s（补水）。这是该会话的宿主抓帧时序，用于演示剪辑对位。脱敏证据含固件、Applet、ESP Part、帧和串口标记的摘要。[同一会话的可核对证据](evidence/virtual-device.summary.json)

较早尝试出现过 P4 TLSF 断言复位及 DSI DMA 取帧失败。用于本报告的标准原生会话在启动阶段自动复位一次，随后启动器开始输出画面，Applet 就绪后的采集窗口内无新增复位。真机、浏览器 WASM、实体水面测量、实际热插拔和联网传包未覆盖。常驻服务与公共模拟器没有部署变更。
