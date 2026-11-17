# 完整报告：按声明控件取证、网络/翻页误报与非拉丁文件名修复

## 1. 背景与数据

2026-11-16 至 2026-11-17 共 19 条审核任务。修复前：5 条 `done`、1 条静态 `FAIL`、
1 条 `service_error`、12 条 `manual_review`。`manual_review` 中：

| 错误码 | 数量 | 初步判断 |
| --- | --- | --- |
| `E_INTERACTION_CLAIM_PARTIAL` | 6 | 默认 A/B 点击，未按固件声明的 Controls/Keys |
| `E_NETWORK_PARTIAL` | 3 | 网络声明未验证 / 网络误报 |
| `E_NO_SIM_PROFILE` | 3 | `ATOM_LITE` 漏映射、`XIAOZHI_CARD_KIT` 无档案 |
| `E_NO_FRAME` | 1 | CardputerDict 0.5.0 无首帧 |
| `E_SIM_MODEL_GAP` | 1 | M5TabOS Tab5 崩溃循环 |
| `E_EVIDENCE_UNAVAILABLE` | 1 | Arduventure Tab5 缺 ELF |
| `E_CONTENT_MANUAL` | 0 | — |
| `E_INTERNAL`（service_error） | 1 | 中文文件名上传失败 |

## 2. 改动

### 2.1 非拉丁文件名上传

`SimApi.upload_artifact()` 直接把 `X-Artifact-Name` 写成原始文件名。含中文的文件名在
`http.client.putheader()` 的 latin-1 编码处抛 `UnicodeEncodeError`，任务以
`E_INTERNAL` 结束。

修复：新增 `safe_artifact_name(name, data)`，去掉路径、把非 ASCII 字符替换为 `_`，
保留安全扩展名；空名时用内容 SHA-256 前缀。头部只发送 ASCII 名称。
`CardOS-zh` 复审已越过上传阶段，进入完整审查。

### 2.2 网络声明误报

`NETWORK_CLAIM_TERMS` 含裸 `api`，导致 card-gcalc 描述中的 “graphics API”、
“script API”被当成网络功能，最终 `E_NETWORK_PARTIAL`。

修复：移除裸 `api`，改为 `web api`、`rest api`、`http api`、`api server`、
`remote api`。card-gcalc 0.2/0.3 复审网络均为 `NOT APPLICABLE`，两条都转为
`done/SIM_VERIFIED`。

### 2.3 A/B 翻页误报

`ab_navigation_required` 原逻辑只要描述里出现“翻页”等词，就要求 A/B 双键翻页。
CardputerDict 描述里的“翻页”指键盘 `[ / ]`、`Fn+;` 等，不是 A/B。

修复：新增 `ab_navigation_claim(text)`，只有 **A/B 与翻页词在 60 字符内成对出现**才
要求 A/B 导航。CardputerDict 的 A/B 翻页要求消失。

### 2.4 按声明控件取证

原 `input_plan()` 对所有 `button_required` 的固件只发 A/B 单击。新增：

- `declared_control_keys()`：解析 `Controls:`/`Keys:`/`操作:`/`按键:` 行，提取
  Enter/Tab/Space/Backspace/Esc/方向键/`; . , / [ ] = -`/单字母键；Cardputer 无显式
  图例时回退扫描常见键盘键；
- `declared_hold_buttons()`：解析 “hold the side button for 5 seconds”、
  “hold B”、“长按/按住 X 秒”等，生成 `hold_*` 计划和 `input_options.hold_seconds`；
- `review_claims()` 新增 `probe_keys`、`hold_buttons`、`input_options`；
- `input_plan()` 优先发送 `probe_keys`，再发显式 A/B，最后才回退 A/B；有 hold 时不再
  补默认 A/B；
- `interaction_summary()` 新增 `keyboard_status`：声明键任意一个产生响应即 PASS，
  不再要求所有声明键都变化；
- 复审时把 `claims.input_options` 合并进 `validation.input_options`（显式 validation
  优先），让 hold 走既有 down/up 时序。

### 2.5 设备映射

`DEVICE_MAP` 补 `ATOM_LITE`/`ATOMLITE` → `atom-lite`。ATEM HD8 EMULATOR 的历史任务
在下载 BIN 前停止，未缓存固件，无法原地重跑；后续同类待审项会进入 QEMU。

## 3. 复审结果

| 任务 | 固件 | 修复前 | 修复后 | 说明 |
| --- | --- | --- | --- | --- |
| `job-234a23521918` | card-gcalc 0.3 | `E_NETWORK_PARTIAL` | `done/SIM_VERIFIED` | 网络误报消除 |
| `job-9100d103aa42` | card-gcalc 0.2 | `E_NETWORK_PARTIAL` | `done/SIM_VERIFIED` | 同上 |
| `job-282e46098a8b` | Frequency 1.1 | `E_INTERACTION_CLAIM_PARTIAL` | `done/SIM_VERIFIED` | Enter/Tab/; 产生响应 |
| `job-ee74e7f677d8` | CardputerDict 普通版 | `E_INTERACTION_CLAIM_PARTIAL` | `E_NETWORK_PARTIAL` | 交互 PASS；只剩网络 |
| `job-152a7f59c47e` | CardputerDict ADV | `E_INTERACTION_CLAIM_PARTIAL` | `E_NETWORK_PARTIAL` | 交互 PASS；只剩网络 |
| `job-219e982655dc` | Stock Ticker | `E_INTERACTION_CLAIM_PARTIAL` | `E_NETWORK_PARTIAL` | hold 5 s 打开菜单；只剩网络 |
| `job-3eee7e7f2cb6` | CardOS-zh | `E_INTERNAL` | `E_CONTENT_MANUAL` | 上传修复；设备/版本字段需人工核对；交互 PASS |
| `job-55ca380e66ea` | All day watch | `E_INTERACTION_CLAIM_PARTIAL` | `E_SIM_APP_CRASH` | hold B 后 CPU1 中断 WDT |

## 4. 剩余问题归因

### 4.1 网络声明（当前最大剩余项）

- Cardputer / Cardputer-ADV 设备档案 `features.network=false`；描述里只要有 WiFi/联网
  就会得到 `E_NETWORK_PARTIAL`。CardputerDict 的查词主功能离线可用，网络只用于可选
  发音缓存；当前策略仍要求人工复核。
- StickS3 有 `qemu-wifi`，但 Stock Ticker 这类需要“按住侧键 5 秒 + 手机配网”的固件，
  网络 lane 只得到 `PARTIAL`，且网络 lane 不执行按键启动序列。
- 这不是固件失败，也不是模拟器崩溃；需要决定“可选网络未验证”是否允许不阻塞主判定。
  本轮未改该策略，避免把未验证网络功能自动放行。

### 4.2 未支持机型

- `XIAOZHI_CARD_KIT` 没有 M5Stack/模拟器档案，审查返回 `E_NO_SIM_PROFILE`。应在
  受理阶段标记“非受支持设备”，而不是让人误以为模拟器缺模型。
- `ATOM_LITE` 映射已补，但 ATEM 历史任务没有缓存 BIN，无法复审。

### 4.3 应用/镜像问题

- CardputerDict 0.5.0（`job-4f049024a594`）无首帧，串口只有
  `No core dump partition found!`；同项目 0.6.4 可出帧，需应用侧或 SD 依赖排查。
- `Micropython editor for cardputer ADV` 的 app-only 镜像声明 Flash code 4，目标要求
  8 MiB，静态拒绝；需作者确认构建目标。
- M5TabOS 在 Tab5 上 `Core dump` 后 `SW_CPU_RESET` 循环，Tab5 外设覆盖多处 partial，
  无单一模型证据。
- Arduventure 的 Tab5 取帧受 ELF 约束，服务已按 `E_EVIDENCE_UNAVAILABLE` 收口。

### 4.4 新暴露的 All day watch 崩溃

`hold_b` 后约 28 s 出现：

```text
Guru Meditation Error: Core 1 panic'ed (Interrupt wdt timeout on CPU1).
Backtrace: 0x4037cb92 ... 0x4205f3d5
Rebooting...
```

同一固件在只发 A/B 单击的旧轮次没有崩溃，说明与 hold B 的屏旋转/放大路径或双核
时序有关。当前没有 ELF 符号、也没有真机对照，不能归因模拟器或固件；保留
`E_SIM_APP_CRASH` 和串口证据，待后续定位。

## 5. 部署与回滚

- 代码提交 `9046a0b`，已 rebase 到并发合入的 `46529f1` 并推送 `main`。
- 部署前备份常驻 `app.py`；替换后重启 LaunchAgent，`/api/health` 返回 `ok=true`。
- 所有复审使用 saved-snapshot、`submit=false`；未回传 Burner、未修改模拟器仓库。
- 回滚：恢复备份并重启，或 revert `9046a0b` 后重新部署。

## 6. 未覆盖项

- 网络取证策略（可选网络、StickS3 配网输入序列）：`NOT RUN`。
- `XIAOZHI_CARD_KIT` 支持、ATEM 历史任务复审：`NOT RUN`。
- CardputerDict 0.5.0 无首帧、All day watch 崩溃、M5TabOS 模型缺口的真机/符号级定位：
  `NOT RUN`。
- 物理设备复跑：`NOT RUN`。
