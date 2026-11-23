# 近 59 条固件审查的过程诊断与假失败修复

- 日期：`2026-11-23`
- 结果：`PARTIAL`（4 条转 SIM_VERIFIED，1 条交互转网络；网络准入与剩余交互/机型仍未闭环）
- 工作类型：`service_debug`
- 问题来源：用户反馈“这几天的审查过程有啥问题，为啥还是大部分都需要人工”
- 源码版本：常驻审查服务运行时（较新分支）与仓库 `main`；仓库 `main` 最近提交
  `9e62882`，运行时另有未合并的 managed worker / 原生网络准入改动
- 环境：macOS arm64；常驻审查服务（LaunchAgent）；本机 Device Service 原生 QEMU；
  Linux snapshot worker 仅准入 `cardputer_adv_pronunciation` / `core2_2048`；无真机

## 结论

窗口内（2026-11-20 00:00 至 2026-11-23 09:16 +08:00）共 **59 条**任务：

- `done/SIM_VERIFIED`：**26 条**
- `manual_review/SIM_PARTIAL`：**30 条**
- `failed`：**3 条**（`E_STATIC` 2、`E_CONTENT_AGENT` 1）

人工复核并不是“固件都失败了”，而是几类**取证/环境/规则**问题：

| 原因 | 数量 | 性质 |
| --- | --- | --- |
| 网络准入不可用 | 11 | 7 条 `worker_namespace_unavailable`、3 条 `board_not_advertised`、1 条 qemu-wifi `PARTIAL`；当前 macOS worker 没有 Linux 网络命名空间，任意 Wi-Fi 固件无法验证 |
| 交互输入未覆盖 | 8 | 剩余为 Cardputer 键盘应用、PaperS3 触摸/E-Ink、Game Boy SD、单键 UI、hold B 等应用/时序问题 |
| 无设备档案 | 3 | AtomS3Lite ×2（映射已补，历史任务无缓存 BIN）、原版 M5Paper ×1 |
| app-only 无启动基底 | 2 | StickC Plus2、PaperS3；Cardputer/ADV/PaperMono/StickS3 default_8MB 已覆盖 |
| Tab5 取帧缺 ELF | 2 | `E_EVIDENCE_UNAVAILABLE`，不是应用失败 |
| 无首帧 | 2 | BitMap16，已进入应用但无 UI |
| 显示less readiness | 2 | AtomLite 无屏幕，服务仍按首帧判定 `E_SIM_APP_READY_PARTIAL` |
| 静态/内容失败 | 3 | `E_STATIC` 2（含 Tab5 RONTO8）、`E_CONTENT_AGENT` 1（MuartKey 描述是重复占位文本） |

本轮修掉了 4 条明确的**假交互失败**，并把 1 条从交互失败变成仅网络未验证：

- AD Arcade for M5StickS3 / M5StickC Plus：`hold_a` 已经产生画面变化，但服务因为没有
  semantic assertion 而判 `PARTIAL`；现在声明动作只要画面变化即算输入响应。两条都转
  `SIM_VERIFIED`。
- Bubble Level：描述明确写 “No buttons or menus”，但 `button` 词仍触发 A/B 要求；
  增加否定判断后转 `SIM_VERIFIED`。
- 玄机OS：描述用 “方向键（; , . / 或 WASD）选择，OK 进入，ESC 返回”，原解析只发
  Tab/Esc；补充 OK/方向键/WASD 后交互 PASS，仅剩网络。
- Stick Arcade：描述里的 “without a Wi-Fi router” 和 “network tests” 被当成 Wi-Fi
  声明；为裸 `network`/`网络` 加连接上下文门槛后网络不再误报，转 `SIM_VERIFIED`。
- 另外补了 `ATOMS3_LITE` 映射，以及 MuartKey / Stick Arcade 的 StickS3 default_8MB
  vendor context（MuartKey 现在停在内容占位文本，属于真实内容失败）。

## 关键证据

- 窗口统计与逐条原因：[evidence/process-summary.json](evidence/process-summary.json)。
- 网络准入原因：7 条 `worker_namespace_unavailable`、3 条 `board_not_advertised`、
  1 条 qemu-wifi `PARTIAL`。
- 复审：
  - `job-cd404de9d2b8`（AD Arcade StickS3）：`E_INTERACTION_CLAIM_PARTIAL` →
    `done/SIM_VERIFIED`。
  - `job-43c707bc2bcc`（AD Arcade StickC Plus）：同上。
  - `job-e4f0a756e5b2`（Bubble Level）：`E_INTERACTION_CLAIM_PARTIAL` →
    `done/SIM_VERIFIED`。
  - `job-1397507cdf00`（Stick Arcade）：`E_APP_ONLY_BASE_REQUIRED` → 经 vendor context
    启动 → 网络误报修复 → `done/SIM_VERIFIED`。
  - `job-64eb67524a7f`（玄机OS）：交互 `PARTIAL` → `PASS`，仅剩 `E_NETWORK_PARTIAL`。
  - `job-baebccbe4704`（MuartKey）：app-only 上下文已解决，AI 内容审查因描述为重复
    “klavye” 占位文本判 `E_CONTENT_AGENT`（合理失败）。

## 文件

- `report.md`：完整过程诊断、修复和剩余项
- `run.json`：结构化记录
- `evidence/process-summary.json`：窗口统计与逐条原因

## 未覆盖项

- 没有 Linux 网络命名空间 worker 的通用准入；11 条网络人工复核无法在本机闭环。
- 剩余 8 条交互失败的应用语义/时序：Cardputer 键盘应用、PaperS3 触摸/E-Ink、
  Game Boy SD、Mouse 单键、PINGO hold B。
- StickC Plus2 / PaperS3 的 app-only 启动基底、Tab5 无 ELF 取帧、AtomLite 显示less
  readiness、BitMap16 无首帧。
- 本轮运行时改动是直接应用到常驻服务（运行时分支比仓库 `main` 新）；仓库同步和
  运行时单元测试尚未闭环。部署前已保留 `app.py` / `firmware_intake.py` / `config.json`
  备份。
