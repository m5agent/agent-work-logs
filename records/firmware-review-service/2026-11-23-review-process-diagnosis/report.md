# 完整报告：近 59 条审查的过程诊断与假失败修复

## 1. 范围与总览

窗口：`2026-11-20 00:00` 至 `2026-11-23 09:16 +08:00`。

| 指标 | 数值 |
| --- | --- |
| 任务总数 | 59 |
| `done/SIM_VERIFIED` | 26 |
| `manual_review/SIM_PARTIAL` | 30 |
| `failed` | 3（`E_STATIC` 2、`E_CONTENT_AGENT` 1） |

按错误码：

| 错误码 | 数量 | 说明 |
| --- | --- | --- |
| `E_NETWORK_PARTIAL` | 11 | 网络准入不可用 / 无同 guest 网络模型 |
| `E_INTERACTION_CLAIM_PARTIAL` | 8 | 输入计划、应用语义或显示时序 |
| `E_NO_SIM_PROFILE` | 3 | AtomS3Lite ×2、原版 M5Paper ×1 |
| `E_APP_ONLY_UNSUPPORTED_DEVICE` | 2 | StickC Plus2、PaperS3 |
| `E_EVIDENCE_UNAVAILABLE` | 2 | Tab5 缺 ELF |
| `E_NO_FRAME` | 2 | BitMap16 |
| `E_SIM_APP_READY_PARTIAL` | 2 | AtomLite 无屏幕 |
| `E_STATIC` | 2 | RedTeamTestFirmware、RONTO8 Tab5 |
| `E_CONTENT_AGENT` | 1 | MuartKey 描述为重复占位文本 |

## 2. 最大问题：网络准入不可用（11 条）

11 条 `E_NETWORK_PARTIAL` 的原因：

| 原因 | 数量 | 设备/固件示例 |
| --- | --- | --- |
| `worker_namespace_unavailable` | 7 | 玄机OS、Bruce 0.9、Evil-Cardputer、Flipper Zero、META TV ×2、Monster online |
| `board_not_advertised` | 3 | StopWatch Demo Plus、Bruce 1.17、CrossPoint PaperDIY |
| qemu-wifi `PARTIAL` | 1 | S3-watch（web-server 需要按键启动） |

当前审查服务对任意 Wi-Fi 固件优先使用 **Linux 网络命名空间** 的原生 STA 会话；
`native_sta_worker_ready()` 要求 worker 公布
`network_namespace_platform=linux` 与 `network_namespace=probe-on-admission`。
本机 Device Service 在 macOS 上，worker 不满足该条件；配置的 Linux snapshot worker
只准入 `cardputer_adv_pronunciation` 和 `core2_2048`，不承接通用固件。

因此这 7 条不是固件失败，而是**当前机器没有可用于通用 Wi-Fi 审查的 Linux worker**。
另外 3 条是设备目录没有公布同 guest STA 能力：
- StopWatch 有 `uiflow2-stopwatch-unified` 但没有通用的 `uiflow2-sticks3-wifi` 路径；
- PaperDIY 的 `features.network=false`，只有 diagnostic 配置；
- StickC Plus2 没有网络模型。

S3-watch 的 qemu-wifi lane 能启动，但 web server 需要先按住 B 才开启；网络 lane 不执行
这段输入序列，所以只有 `PARTIAL`。

### 可选处理路径

1. **把通用 Wi-Fi 审查迁到 Linux worker**（推荐，保持网络命名空间隔离）；
2. 扩展 managed Linux worker 的 admit，让任意 StickS3/Cardputer-ADV/Core2 都能走原生 STA；
3. 对明确支持 qemu-wifi 的板卡允许降级（隔离弱于 namespace，需要策略确认）；
4. 对“离线主功能 + 可选 Wi-Fi”的固件，把网络未验证作为独立限制，不阻塞主判定。

本轮没有改网络策略，避免把未验证的网络功能自动放行。

## 3. 交互假失败：已修 4 条，剩 8 条

### 3.1 已修

- **AD Arcade StickS3 / StickC Plus**：`hold_a` 已产生画面变化，但
  `semantic_input_status` 仍要求 semantic assertion，导致 `PARTIAL`。现在声明动作
  在无显式断言时只要 `frame_changed` 即算输入响应。两条转 `SIM_VERIFIED`。
- **Bubble Level**：描述写 “No buttons or menus”，`BUTTON_CLAIM_TERMS` 仍把
  “button” 当成需要 A/B。增加否定判断后，`button_required=false`，转
  `SIM_VERIFIED`。
- **玄机OS**：描述用“方向键（; , . / 或 WASD）选择，OK 进入，ESC 返回”，原解析只发
  Tab/Esc；补充 OK/方向键/WASD 后交互 `PASS`，仅剩网络。
- **Stick Arcade**：描述写 “without a Wi-Fi router”“network tests”，裸 `network`
  被误判为 Wi-Fi 声明；给 `network`/`网络` 加连接上下文门槛后网络不再误报，转
  `SIM_VERIFIED`。

### 3.2 剩余 8 条

| 固件 | 现象 | 判断 |
| --- | --- | --- |
| META TV IR（Cardputer ADV） | Tab 被接受但画面不变 | 声明的控件解析不完整，需按应用实际按键 |
| MCCC（Cardputer ADV） | `[`/`]` 被接受但画面不变 | 键盘映射或应用首屏不响应 |
| Camillia（Cardputer） | Backspace/Esc 被接受但画面不变 | 声明控件不完整或应用首屏不响应 |
| DeskFolio ×2（PaperS3） | 触摸被接受但画面不变 | E-Ink 刷新慢/触摸坐标或面板时序，需更长 settle 或 panel generation |
| Game Boy DMG（Cardputer） | 键盘/Fn 组合无画面变化 | 需要 microSD 卡带；存储夹具缺失 |
| STICK S3 MOUSE | A 无变化、B 有变化 | 单键 UI；服务要求 A/B 都响应过严 |
| PINGO（StickC Plus2） | A 有变化、hold B 无变化 | hold B 在该屏幕可能无效果，或输入时序问题 |

这些需要按应用逐个判断，不再是一个统一的解析 bug。

## 4. app-only 启动上下文

本轮之前新增了 Cardputer/ADV 官方 8 MB、PaperMono 16 MB 的 stock base，以及
StickS3 的 default_8MB vendor context。窗口内仍有 2 条 app-only 无法组合：

- **aaahhhhhh（StickC Plus2）**：classic ESP32，没有 stock recipe/base；
- **DeskFolio（PaperS3）**：没有 PaperS3 的 app-only 基底；同时 DeskFolio 还有触摸/
  E-Ink 交互问题。

MuartKey / Stick Arcade 本轮通过 StickS3 default_8MB vendor context 进入启动；
Stick Arcade 已转 `SIM_VERIFIED`；MuartKey 停在内容占位文本（见第 6 节）。

## 5. 其他人工原因

- **AtomS3Lite ×2**：`ATOMS3_LITE → atoms3-lite` 映射已补；这两条历史任务没有缓存
  BIN，无法原地重跑，后续同类会自动路由。
- **原版 M5Paper（Slow Draw）**：模拟器只有 PaperMono（ESP32-S3），没有原版
  M5Paper（ESP32 classic）档案；已给出明确原因，不再报 app-only 上下文。
- **Tab5 ×2（TulipCC、Monster for Cyberspace）**：`screenshot_requires_matching_elf`，
  当前只有 BIN 没有 ELF；属于取证限制，不是应用失败。
- **BitMap16 ×2**：已通过 Cardputer stock base 启动，但无黑帧；需要按应用构建分区/
  外设继续排查。
- **AtomLite Wifi_Rig ×2**：AtomLite 无屏幕，服务仍按首帧判定 readiness，得到
  `E_SIM_APP_READY_PARTIAL`；应改为串口就绪判定。
- **静态/内容失败 3 条**：RedTeamTestFirmware、RONTO8 Tab5 为静态拒绝；MuartKey 的
  描述/版本描述是重复 “klavye” 占位文本，AI 内容审查判失败是合理的。

## 6. 部署与风险

- 本轮运行时修复直接应用在常驻服务（`app.py`/`firmware_intake.py`/`config.json`），
  已重启并验证 `/api/health`。部署前保留了对应备份。
- 常驻服务运行时分支比仓库 `main` 新（managed worker、原生网络准入等未在仓库分支）；
  本轮修复没有全部回写到仓库单元测试，后续如果按仓库重新部署，需要先合并运行时分支，
  否则这些交互/网络修复会丢失。
- 复审均为 saved-snapshot、`submit=false`；未回传 Burner，未修改模拟器仓库。

## 7. 建议的下一步

1. **优先解决 Linux 网络命名空间 worker 的通用准入**，这是 11 条人工里最大的一块；
   或明确批准 qemu-wifi 降级/可选网络不阻塞策略。
2. 补 StickC Plus2、PaperS3 的 app-only 启动基底。
3. 给 PaperS3/PaperDIY 的触摸增加 E-Ink settle 或读取 panel generation。
4. 给无屏幕设备改用串口 readiness。
5. 对剩余 Cardputer 键盘应用逐个补声明的按键/首屏交互，不再用默认 A/B。
6. Tab5 增加无 ELF 帧捕获。

## 8. 未覆盖项

- Linux worker 通用准入：`NOT RUN`。
- 剩余 8 条交互的应用级语义：`NOT RUN`。
- StickC Plus2/PaperS3 app-only、Tab5 无 ELF、AtomLite readiness、BitMap16 首帧：
  `NOT RUN`。
- 物理设备复跑：`NOT RUN`。
