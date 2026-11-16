# 审查服务设备映射、Tab5 ELF 取证与触摸声明修复

- 日期：`2026-11-16`
- 结果：`PASS`（代码修复、86 项回归、AD Arcade 复审与 98TAB5 复审）；`PARTIAL`（三款新映射机型未做完整复审）
- 工作类型：`code_change`
- 问题来源：近两日审核归因记录
  [Cardputer 运行时板型探测回退与两日审核归因](../m5stack-esp-emulator/2026-11-16-cardputer-runtime-board-detect/)
- 源码版本：`firmware-review-service @ baeb680` → `df0361d`
- 环境：macOS arm64；常驻审查服务（LaunchAgent）与本机 Device Service；虚拟设备原生 QEMU；
  未使用真机

## 结论

修复了三类会制造“未采集到足够证据”假象的审查服务问题：

1. `DEVICE_MAP` 补 `ATOM_S3 → atoms3`、`PAPER_S3 → papers3`、`PAPER_DIY → paperdiy`
   （含 `ATOMS3` / `PAPERS3` / `PAPERDIY` 别名），不再在 QEMU 启动前返回
   `E_NO_SIM_PROFILE`。
2. Tab5 取帧返回 409 `screenshot_requires_matching_elf` 时，不再在第一次抓帧就中止观察；
   改为完成 60 秒串口观察，记录 `frame_scope=serial_only` 与
   `frame_unavailable_reason`，最终以 `E_EVIDENCE_UNAVAILABLE` 和明确文案收口，
   不再误报 `E_SIM_OBSERVATION_INCOMPLETE` / `E_NO_FRAME`。
3. 触摸声明不再由裸 `tap` 触发；并在执行计划拿到设备能力后，对没有触摸屏的机型清除
   `touch_required`，避免把按键 “tap” 当成触摸功能。

代码已推送 `main @ df0361d`，并部署到常驻服务。复审结果：

- AD Arcade（`job-4ed91eb1fa1f`）：原 `E_INTERACTION_CLAIM_PARTIAL` / `SIM_PARTIAL`，
  复审为 **`done` / `SIM_VERIFIED`**，`touch_claim_required=false`、`button_status=PASS`。
- 98TAB5（`job-59ccfe1dfc48`）：原 0 s / 0 采样 / `E_SIM_OBSERVATION_INCOMPLETE`，
  复审为 **60.1 s / 13 采样 / `E_EVIDENCE_UNAVAILABLE`**，串口保持 running，
  `frame_scope=serial_only`、`frame_unavailable_reason=screenshot_requires_matching_elf`。
- 三款新映射在实时设备目录中均为 `creatable=True`，`execution_plan` 返回 `runtime=qemu`。

本轮没有把服务侧问题开成模拟器 issue。

## 关键证据

- 服务提交：`df0361d`（`fix(review): map AtomS3/PaperS3/PaperDIY and keep Tab5 ELF evidence honest`）。
- 回归：`python3 -m unittest discover -s tests -v`，**86 项通过**。
- 复审：AD Arcade 与 98TAB5 的旧 attempt 已归档到任务 `attempts/`，新报告为当前
  `review-report.json`；两次复审均为 `submit=false`，未回传 Burner。
- 映射检查：`ATOM_S3`、`PAPER_S3`、`PAPER_DIY` 在实时目录中分别解析到
  `atoms3`、`papers3`、`paperdiy`，且 `creatable=True`。
- 部署：常驻服务重启后 `/api/health` 返回 `ok=true`，无进行中任务被中断。

## 文件

- `report.md`：完整改动、验证与边界
- `run.json`：结构化记录
- `evidence/verification-summary.json`：脱敏后的复审摘要

## 未覆盖项

- `ATOM_S3` / `PAPER_S3` / `PAPER_DIY` 的完整固件复审：`NOT RUN`（当前待审列表没有对应机型）。
- Tab5 的带 ELF 首帧、真实面板/触摸/CSI/USB/SDIO/C6 伴生芯片：`NOT RUN`。
- 物理设备复跑：`NOT RUN`。
- 网络路径与 app-only 启动上下文、StickC-Plus2 静态判定：本轮未改，仍为后续项。
