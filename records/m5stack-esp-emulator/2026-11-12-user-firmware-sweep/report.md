# 26 设备 × 5 固件公开固件扫描报告

## 1. 背景与目标

用户要求：对每台模拟器设备各找 5 个固件，烧录运行，判断固件能否正常运行；模拟器测出的缺陷向仓库提 issue。

本轮用仓库现成的 `platform/tools/user_firmware_matrix.py`（M5Burner 选择 + 静态校验 + Device Service 会话 + 串口/帧采集）并把机型映射从 13 台扩展到 26 台。

## 2. 方法与环境

- 设备服务：agent 自有实例 `127.0.0.1:18787`，独立 state 目录；不使用用户的 8787/8830 实例。
- 运行时：xtensa QEMU `9.2.2`（`2026-11-11` 本地同步构建）+ C6 riscv32 运行时；`runtime=qemu`。
- 固件来源：M5Burner 公开 API，按 `MOST_DOWNLOADED` 排序，排除可用替代之外的 UIFlow2 基线；每个固件经 `firmware/analyze` 校验后上传。
- 观察：每样本 ready 时间线 `0/5/10/30 s`、稳定后 3 s、总观察 40 s；输入探针按板级按键/触摸。
- 分片：3 个进程 × `--jobs 2`，共 26 设备 × 5 = 130 计划，127 个样本完成（stamplc 只有 2 个可用固件，nesso-n1/stackchan 有下载失败跳过）。

命令：

```bash
python3 .work/agent-sweep-20261112/run_matrix.py \
  --service-url http://127.0.0.1:18787 --devices <shard> \
  --per-device 5 --observe-seconds 40 --jobs 2 \
  --out-dir .work/agent-sweep-20261112/matrix-<shard>
```

## 3. 设备级结果

| 设备 | 样本 | 有 UI | UI 后崩溃 | 启动崩溃 | 空白帧 | 无帧 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| atom-lite | 5 | 0 | 0 | 2 | 0 | 3 |
| atom-matrix | 5 | 0 | 0 | 2 | 0 | 3 |
| atom-matrix-v11 | 5 | 0 | 0 | 2 | 0 | 3 |
| atoms3 | 5 | 1 | 0 | 1 | 3 | 0 |
| atoms3-lite | 5 | 0 | 0 | 0 | 0 | 5 |
| atoms3r | 5 | 1 | 0 | 1 | 3 | 0 |
| basic-v27 | 5 | 4 | 0 | 0 | 1 | 0 |
| cardputer | 5 | 5 | 0 | 0 | 0 | 0 |
| cardputer-adv | 5 | 4 | 1 | 0 | 0 | 0 |
| core2 | 5 | 0 | 1 | 1 | 3 | 0 |
| cores3 | 5 | 3 | 0 | 0 | 1 | 1 |
| dial | 5 | 4 | 0 | 0 | 1 | 0 |
| nanoc6 | 5 | 0 | 0 | 2 | 0 | 3 |
| nesso-n1 | 5 | 0 | 3 | 1 | 1 | 0 |
| papercolor | 5 | 4 | 1 | 0 | 0 | 0 |
| paperdiy | 5 | 5 | 0 | 0 | 0 | 0 |
| papermono | 5 | 4 | 1 | 0 | 0 | 0 |
| papers3 | 5 | 4 | 1 | 0 | 0 | 0 |
| stackchan | 5 | 3 | 2 | 0 | 0 | 0 |
| stamplc | 2 | 1 | 0 | 0 | 1 | 0 |
| stickc | 5 | 1 | 1 | 1 | 0 | 2 |
| stickc-plus | 5 | 3 | 1 | 1 | 0 | 0 |
| stickc-plus2 | 5 | 2 | 2 | 1 | 0 | 0 |
| sticks3 | 5 | 5 | 0 | 0 | 0 | 0 |
| stopwatch | 5 | 5 | 0 | 0 | 0 | 0 |
| tab5 | 5 | 0 | 0 | 1 | 0 | 4 |

说明：

- 无显示设备（atom-lite、atom-matrix、atoms3-lite、nanoc6 的部分样本）没有帧是预期行为，应只按串口判定。
- `stamplc` 仅 2 个固件满足静态度量；其余被静态校验拒绝或下载失败。
- StickS3、StopWatch、Cardputer、PaperDIY、Dial 等设备在本轮 5/5 有可用画面。

## 4. 崩溃分类

| 类别 | 数量 | 典型设备 |
| --- | ---: | --- |
| 启动期崩溃（无可用首帧） | 16 | atom-lite、atom-matrix、nanoc6、tab5、nesso-n1 |
| 首帧后崩溃（UI 已出现） | 14 | nesso-n1、stackchan、stickc-plus2、papercolor |
| host 进程 SIGABRT | 1 | papercolor（`atomic_mmu_lookup`，6 次中 1 次） |

常见签名：`Guru Meditation`（LoadProhibited/InstrFetchProhibited/Interrupt wdt）、`task_wdt` + `abort()`、`assert failed: xTaskPriorityDisinherit`、`assert failed: do_core_init (... flash_ret == ESP_OK)`。

## 5. 已提交 issue

| issue | 主题 | 证据 |
| --- | --- | --- |
| [#216](https://github.com/m5agent/m5stack-esp-emulator/issues/216) | Nesso N1 5 款固件全部无法启动，3 款 `xTaskPriorityDisinherit` 崩溃-重启循环 | 2 次独立复跑，178/203 KB 串口重启循环 |
| [#217](https://github.com/m5agent/m5stack-esp-emulator/issues/217) | PaperColor 厂测固件触发 QEMU TCG `atomic_mmu_lookup` 断言，进程 SIGABRT | `qemu.stderr`、会话 8.7 s 退出码 -6，6 次中 1 次 |
| [#218](https://github.com/m5agent/m5stack-esp-emulator/issues/218) | PM1 主动关机被记为启动失败（PaperColor / PaperDIY UserDemo） | `M5PM1_PWR: Shutdown requested`、退出码 0、全白末帧 |

## 6. 追加定位（2026-11-12 晚）

按“固件大概率正常、优先归因模拟器”的假设补查后新增 3 个 issue：

| issue | 主题 | 关键证据 |
| --- | --- | --- |
| [#219](https://github.com/m5agent/m5stack-esp-emulator/issues/219) | AtomS3 UserDemo / Snake Game 启动卡死 | 串口 225 B 停在 ROM `entry`；QMP 观测 PC 固定 `0x4208804e`、CCOUNT 前进、宿主 CPU 6%（UserDemo）vs 102%（Snake）；同机 StampFly 正常 |
| [#220](https://github.com/m5agent/m5stack-esp-emulator/issues/220) | PaperColor TinyUSB 初始化失败 | `check_dwc2 183: ASSERT FAILED`、`dwc2_core_init 221: ASSERT FAILED`，每次会话必现 |
| [#221](https://github.com/m5agent/m5stack-esp-emulator/issues/221) | Atom-Lite / Atom-Matrix 厂测固件 IDLE watchdog | 12.5–28.6 s `task_wdt ... IDLE (CPU 0)`、`main` 占用、abort 重启循环 |
| [#222](https://github.com/m5agent/m5stack-esp-emulator/issues/222) | Core2 显示写入未到达面板模型 | 失败固件 `m5-panel` GDDRAM 仅 15/230415 非零；对照固件 229551 非零 |
| [#223](https://github.com/m5agent/m5stack-esp-emulator/issues/223) | StackChan 约 39 s 崩溃 | BREAK instr PC=0x403783c0；InstrFetchProhibited PC=0x00385cde、A0=0x80385cec 高位截断形态 |

## 7. 未定位 / 未开 issue

- **AtomS3**：ATOMS3 UserDemo 与 Snake Game 启动后串口停在 bootloader `entry`（225 B），60 s 内无应用输出、帧全黑；另有 HAL9000 载入 MJPEG 但无帧。尚未确认是模型侧还是固件侧，未开 issue。
- **Tab5**：4/5 无首帧，1/5 watchdog；与既有 [#188](https://github.com/m5agent/m5stack-esp-emulator/issues/188) Tab5 启动问题一致，本轮不重复开。
- **stackchan**：2 例 `Guru Meditation (Unhandled debug exception / InstrFetchProhibited)`；可能与 PSRAM/缓存或固件自身有关，未定位。
- **经典 LX6 厂测固件**（Atom-Lite/Atom-Matrix Factory Test、Atom Printer）：`IDLE` task watchdog，可能与缺失外设或调度模型相关，未定位。
- **core2**：5 个社区固件中 0 个完整 UI（1 个 UI 后崩溃、3 个空白、1 个崩溃），与历史 Core2 legacy 边界一致，未开新 issue。

## 8. 边界与风险

- 结果只代表 virtual-device 启动/显示层；不涉及真机、射频、音频、功耗、电气、光学。
- 矩阵“PASS”要求 UI + 输入响应；大量 `PARTIAL` 是输入无响应或帧未就绪，不等于固件不可用。
- 42 个样本在 40 s 窗口内未见首帧，部分慢启动固件可能需要更长观察。
- 未修改仓库代码；设备服务与 QEMU 会话为 agent 自有实例，结束后已清理。

## 9. 回滚

- 无仓库改动，无需回滚。
- 证据与缓存位于 ignored 的 `.work/agent-sweep-20261112/` 与 `platform/.cache/user-firmware/`。
