# 完整报告：审查服务设备映射、Tab5 ELF 取证与触摸声明修复

## 1. 背景

近两日 27 条 `SIM_PARTIAL` 中，有 13 条并非模拟器缺陷，而是审查服务侧问题。其中三类
最容易让结果看起来像“未采集到足够证据”：

| 现象 | 任务数 | 直接原因 |
| --- | --- | --- |
| `E_NO_SIM_PROFILE` | 4 | `DEVICE_MAP` 缺 `ATOM_S3`、`PAPER_S3`、`PAPER_DIY`，但模拟器已有可创建档案 |
| Tab5 0 s / 0 采样 | 5 | 抓帧 409 `screenshot_requires_matching_elf` 被当作致命错误 |
| 触摸声明误报 | 1（AD Arcade） | 描述里的 “tap to flap” 被 `TOUCH_CLAIM_TERMS` 当成触摸屏声明 |

本次只改审查服务，不改模拟器模型；三项修复均保留原始证据和历史 attempt。

## 2. 改动

### 2.1 设备映射

`service/app.py` 的 `DEVICE_MAP` 新增：

```text
ATOMS3    -> atoms3
ATOM_S3   -> atoms3
PAPER_S3  -> papers3
PAPERS3   -> papers3
PAPER_DIY -> paperdiy
PAPERDIY  -> paperdiy
```

模拟器目录中 `atoms3`、`papers3`、`paperdiy` 均为 `creatable=True`，有
`flash/serial/screenshot/input/qom/device_state` 能力。此前审查在下载前就返回
`E_NO_SIM_PROFILE`，完全没有进入 QEMU。

### 2.2 Tab5 ELF 取帧收口

`Reviewer.observe_session()` 的截图分支调整：

- 仅对 `HTTP 409` 且响应体包含 `screenshot_requires_matching_elf` 的情况做降级；
- 记录 `observation["frame_unavailable_reason"]="screenshot_requires_matching_elf"`；
- 不中断 60 秒观察窗口，每个采样记录
  `frame_status="NOT AVAILABLE (matching ELF required)"`；
- 最终 `frame_scope=serial_only`；如果后续采样成功拿到帧，则清除 reason 并按正常帧处理；
- 其他 409、404 后置错误、非 PNG 响应保持原有致命语义。

判定分支新增（位于 crash 与 `E_NO_FRAME` 之间）：

```text
manual_review / SIM_PARTIAL
error_code = E_EVIDENCE_UNAVAILABLE
conclusion = 虚拟设备已运行并完成 N 秒串口观察，但该机型截图需要匹配 ELF
             （screenshot_requires_matching_elf），本次未取得首帧；
             串口与运行证据已保留，补 ELF 后可复审。
```

`checks.virtual_observation` 同步增加 `frame_scope` 与
`frame_unavailable_reason`，`observation.json` 保留每个采样的 `frame_status`。

### 2.3 触摸声明

- `TOUCH_CLAIM_TERMS` 移除裸 `tap`，改为 `touch` / `touchscreen` / `touch screen` /
  `tap the screen` / `tap screen` / `触摸` / `屏幕手势` / `swipe`。
- 在执行计划拿到设备目录后，如果设备 `display.touch` 不为真而 `claims.touch_required`
  为真，则清除该声明并记录 `claims` 事件。这样“触摸”出现在无触摸屏机型上时不会再把
  整体判定压成 `PARTIAL`。

### 2.4 测试

新增/更新：

- `tests/test_device_map.py`：三款 Burner 设备码及别名映射。
- `tests/test_virtual_observation.py::test_tab5_elf_409_completes_serial_observation_with_limitation`：
  409 ELF 时完成 60 s 串口观察、13 采样、`frame_scope=serial_only`、无 PNG 证据。
- `tests/test_review_claims.py::test_tap_to_flap_is_not_treated_as_a_touchscreen_claim`：
  AD Arcade 文案不再要求触摸。

回归结果：`python3 -m unittest discover -s tests -v`，**86 项通过**。

## 3. 验证

### 3.1 AD Arcade 复审

| 项 | 修复前 | 修复后 |
| --- | --- | --- |
| 任务 | `job-4ed91eb1fa1f` | 同任务 saved-snapshot 复审 |
| 最终状态 | `manual_review` / `SIM_PARTIAL` | `done` / `SIM_VERIFIED` |
| 错误码 | `E_INTERACTION_CLAIM_PARTIAL` | 无 |
| 触摸声明 | `touch_claim_required=true` | `false` |
| 输入 | key_a 画面变化，touch NOT RUN | key_a 画面变化，`button_status=PASS` |
| 观察 | 60 s | 60.06 s，13 采样 |

复审使用同一 BIN 快照，`submit=false`，未回传 Burner；旧 attempt 已归档。

### 3.2 98TAB5 复审

| 项 | 修复前 | 修复后 |
| --- | --- | --- |
| 任务 | `job-59ccfe1dfc48` | 同任务 saved-snapshot 复审 |
| 错误码 | `E_SIM_OBSERVATION_INCOMPLETE` | `E_EVIDENCE_UNAVAILABLE` |
| 观察 | 0 s / 0 采样 | 60.07 s / 13 采样 |
| 帧 | 0 B，409 立即中止 | 仍无帧，但 `frame_scope=serial_only` |
| 结论 | “观察未完成” | “已完成串口观察，截图需要匹配 ELF，补 ELF 后复审” |

串口在 60 s 内保持 4,113 B、会话 running；没有 crash marker。该复审证明服务不再把
ELF 约束误报成“观察未完成”，但仍不声称固件首帧通过。

### 3.3 映射检查

使用实时设备目录和部署后的 `Reviewer.execution_plan()` 做只读检查：

| Burner 设备码 | 解析 profile | creatable | execution runtime |
| --- | --- | --- | --- |
| `ATOM_S3` | `atoms3` | true | `qemu` |
| `PAPER_S3` | `papers3` | true | `qemu` |
| `PAPER_DIY` | `paperdiy` | true | `qemu` |

三款完整固件复审未执行，因为当前待审列表没有对应机型；本轮只验证到映射/计划阶段。

## 4. 部署与回滚

- 仓库提交：`df0361d`，已推送 `main`。
- 常驻服务：部署前备份 `app.py`，替换后通过 LaunchAgent 重启；`/api/health` 返回
  `ok=true`，启动时无进行中任务。
- 复审均为本地 saved-snapshot 模式，`submit=false`；未提交 Burner，未改模拟器仓库。
- 回滚：恢复备份 `app.py` 并重启 LaunchAgent；或 revert `df0361d` 后重新部署。

## 5. 未覆盖项与后续

- `ATOM_S3` / `PAPER_S3` / `PAPER_DIY` 的完整固件复审：`NOT RUN`（无待审 BIN）。
- Tab5 带 ELF 的首帧、真实面板/触摸/CSI/USB/SDIO/C6 伴生芯片：`NOT RUN`。
- 物理设备复跑：`NOT RUN`。
- 网络路径（Stopwatch 通用网络档、Cardputer 无网络）与 app-only 启动上下文、
  StickC-Plus2 静态判定：本轮未改，仍为后续项。
- M5TabOS 的 Tab5 `E_SIM_MODEL_GAP`：未定位到单一模型，未在本次修复。
