# 审查服务：按声明控件取证、网络/翻页误报与非拉丁文件名修复

- 日期：`2026-11-17`
- 结果：`PASS`（代码修复、97 项回归、8 条复审验证）；`PARTIAL`（网络声明、未支持机型与个别应用崩溃仍未闭环）
- 工作类型：`code_change`
- 问题来源：2026-11-16 至 2026-11-17 的固件审核批次；用户反馈“最近大部分仍失败”
- 源码版本：`firmware-review-service @ 46529f1` → `9046a0b`
- 环境：macOS arm64；常驻审查服务（LaunchAgent）；本机 Device Service 原生 QEMU；
  复审均为 saved-snapshot，`submit=false`；未使用真机

## 结论

这批复审确认：最近失败的主因不是模拟器，而是审查服务的**输入计划**和**声明解析**。

- 修复了 5 类服务侧问题：非拉丁文件名上传崩溃、`graphics API` 触发网络误报、
  键盘翻页触发 A/B 翻页误报、`ATOM_LITE` 映射缺失、默认只发 A/B 点击而不读
  `Controls:`/`Keys:` 声明（含长按）。
- 回归 97 项通过；服务已部署重启。
- 复审结果：
  - `card-gcalc` 0.2/0.3：`E_NETWORK_PARTIAL` → **`done/SIM_VERIFIED`**（网络误报消除）。
  - `Cardputer ADV Frequency and Noise Generator` 1.1：`E_INTERACTION_CLAIM_PARTIAL` →
    **`done/SIM_VERIFIED`**（按 Controls 发送 Enter/Tab/; 等，3 个键产生画面变化）。
  - `CardputerDict`（普通版/ADV）：交互从 `PARTIAL` 变为 **`PASS`**（Tab/Space/Backspace
    等声明键生效），只剩网络声明未验证。
  - `Stock Ticker`：按住侧键 5 秒后画面变化，交互 **`PASS`**，只剩网络声明未验证。
  - `CardOS-zh`：上传不再因中文文件名崩溃，完成完整复审；交互 `PASS`，
    内容字段因“设备字段 Cardputer / 正文要求 Cardputer ADV、版本描述不匹配”转
    `E_CONTENT_MANUAL`（合理的人工复核）。
  - `All day watch + Chess + Tetris + Blackjack`：按住 B 后触发
    `Interrupt wdt timeout on CPU1` 并重启，`E_SIM_APP_CRASH`；这是本轮新暴露的
    应用/模型问题，尚无符号或真机证据，未开模拟器 issue。

因此“最近大部分是固件/模拟器失败”并不准确：多数交互失败是服务没有按固件声明的控件取证。
剩余 `SIM_PARTIAL` 主要集中在**网络声明无法在虚拟设备验证**、**未支持机型**和个别
应用自身卡死/崩溃。

## 关键证据

- 服务提交：`9046a0b`（rebase 到 `46529f1` 后推送 `main`）。
- 回归：`python3 -m unittest discover -s tests -v`，**97 项通过**。
- 复审：
  - `job-234a23521918`（card-gcalc 0.3）：`E_NETWORK_PARTIAL` → `done/SIM_VERIFIED`。
  - `job-9100d103aa42`（card-gcalc 0.2）：`E_NETWORK_PARTIAL` → `done/SIM_VERIFIED`。
  - `job-282e46098a8b`（Frequency 1.1）：交互 `PASS`，`done/SIM_VERIFIED`。
  - `job-ee74e7f677d8` / `job-152a7f59c47e`（CardputerDict）：交互 `PASS`，
    仅剩 `E_NETWORK_PARTIAL`。
  - `job-219e982655dc`（Stock Ticker）：`hold_a` 5 秒产生画面变化，交互 `PASS`，
    仅剩 `E_NETWORK_PARTIAL`。
  - `job-3eee7e7f2cb6`（CardOS-zh）：`E_INTERNAL` → `E_CONTENT_MANUAL`，交互 `PASS`。
  - `job-55ca380e66ea`（All day watch）：`hold_b` 后 `Interrupt wdt timeout on CPU1`，
    `E_SIM_APP_CRASH`；`NOT RUN` 真机复跑。
- 证据摘要：[evidence/verification-summary.json](evidence/verification-summary.json)。

## 文件

- `report.md`：完整改动、复审对照与剩余问题
- `run.json`：结构化记录
- `evidence/verification-summary.json`：脱敏后的复审摘要

## 未覆盖项

- 网络声明：Cardputer/Cardputer-ADV 没有网络模型；StickS3 的 `qemu-wifi` 对需要手机
  配网或按键启动的固件只能得到 `PARTIAL`。本轮未改网络取证策略。
- `XIAOZHI_CARD_KIT` 没有 M5Stack/模拟器档案；`ATOM_LITE` 已补映射，但历史任务无缓存 BIN，
  无法原地重跑。
- `CardputerDict` 0.5.0 无首帧、`Micropython editor` app-only 目标不匹配、`M5TabOS`
  的 Tab5 模型缺口、`Arduventure` 的 ELF 取帧限制：均未在本轮修复。
- 物理设备复跑：`NOT RUN`。
