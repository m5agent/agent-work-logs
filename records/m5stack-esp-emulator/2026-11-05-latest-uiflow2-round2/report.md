# 最新 UIFlow2 第二轮全量测试报告（全设备 / 全 Unit / 控制闭环）

## 背景

用户要求确认并补齐：(1) 全部设备的全部 UIFlow 固件测试；(2) 全部 Unit 代码测试；(3) 控制闭环（改变模拟器状态，guest 代码读到结果）。同时要求再次全量执行、问题先提 issue、并改善上一轮“8 个 agent 等 1 个长尾”的并行度问题。

前置 round-1 记录见 2026-11-05-latest-uiflow2-full-sweep。本轮复用 round-1 已完成执行的 104 Unit / 19 设备 boot / 60 外设证据，只重跑缺口并补闭环，所有原始证据仍在 ignored `.work/uiflow-latest-20261105/`。

## 方法

1. 固件：沿用 2026-11-05 拉取并校验的 30 台官方 UIFlow2 固件（v2.5.5×4、v2.5.4×23、v2.5.4-4MB×1、pinned×2）。
2. runtime：7 个隔离 Device Service 全部使用 canonical 43-machine/Unit-capable build `0e16a9bc…`；device 直连 lane 使用同 build 与矩阵派生 VFS 布局。
3. 并行队列（6 scope）：
   - R2-D：30 台设备一次全量执行（普通 S3/C6、classic host-image、4 台 matrix 契约不一致设备的派生 console lane、tab5 两 lane）。
   - U1：batch11(7)+batch12a(7)+can_lorawan(3) on 8901。
   - U2：batch12b(7)+batch12c(4)+io(12) on 8903。
   - U3：control(5)+sensor(7)+9 个无 batch runner Unit+service(3) on 8905。
   - CL-A：112 个 input Unit 的注入→guest 读取审计与补充执行 on 8907，含 16 个 fresh round-2 sessions。
   - CL-B：115 个 output Unit 的 guest 写→host 观测审计与 16 个 fresh round-2 sessions on 8911。
4. 负载控制：round-2 中段发现 load 10–13，统一要求各 teammate 降到 1 并发、串行重试；负载诱发失败单列 `INFRA-LOAD`，不混入产品失败。
5. issue 分流：沿用 round-1 的 #172–#185 与内部 GitLab #15–#26，本轮只新增 3 个新问题并追加 1 条更正评论。

## 结果

### 设备（30/30 执行）

- PASS 20：stopwatch、sticks3、atoms3r、cores3、cardputer-adv、stamplc、stackchan、papermono、nesso-n1、basic-v27（含 BtnB）、atom-lite、atom-matrix、atom-matrix-v11（首次执行）、atomu、atom-echo、atom-echos3r、atoms3r-cam、atoms3r-m12、atoms3u、tab5（旧 merged-image lane）。
- FAIL 10：atoms3（面板方向/反色 issue #179）、papercolor（#180）、dial（#181）、nanoc6（#182）、atoms3-lite（新 #187）、stickc/plus/plus-se（矩阵 fixture 契约 #184）、core2/stickc-plus2（INFRA-LOAD：负载 10.4–12.9/约 30 guest 下失败，静默低负载同 argv 重跑 PASS）。
- NOT RUN：m5stick/stickt2/cardputer-zero（无最新 UIFlow2 构建）；tab5 最新 v2.5.4 二进制 lane NOT RUN（新 #188）。

### Unit（160/160 有执行证据）

- round-2 新增执行：U1 17/17 PASS；U2 21/23 PASS + 2 known-blocker（buzzer UNIT-HOST-17、angle S3 eFuse 校准 → #186）；U3 22 PASS + 2 BLOCKED（mini-bps-v11/mini-pdm DEFER），其中 9 个无 runner Unit：7 PASS（2relay/scroll/flashlight/servo8-hat/8servos/joystick2/nfc）+ 2 DEFER blocked。
- 合并 round-1 后 160/160 覆盖；runtime 状态：implemented 124、unsupported 31、planned 5。
- 所有 PASS 绑定固件 version+sha、session_id、串口/QOM/frame 证据；失败有 candidate 卡与 issue。

### 控制闭环

- 输入方向（112 个 implemented input Unit）：107 COVERED + 5 PARTIAL（字段级）+ 0 missing；16 个 round-2 fresh 执行，含用户示例 ENV：注入 25.5°C/60.5%/100000Pa → guest 25.5/60.5/1000.0；注入 31.25°C/45.0%/90000Pa → guest 31.3/45.0/900.0。另 can/mini-can/lorawan-us915 用 CAN inject-hex 与 AT 响应做输入回读。
- 输出方向（115 output Unit）：115/115 COVERED；16 个 fresh 执行（4relay/ssr/rgb/rgb-led-10cm/dac/synth/midi/buzzer/ir/rs485-iso/hbridge/bldc-driver/vibrator/extio2/unit-id/qrcode），guest 写入 ≥2 个值均被 host QOM/controller/RMT/PCM 观测一致；U1/U2 的 20 个 output Unit 补齐后 NOT-RUN 为空。
- 未发现 zero/null/wrong-scaling mismatch；5 个 PARTIAL 仅是 probe 向量未覆盖全部字段，无错误读数。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| 固件身份 | PASS | 30/30 sha256 == manifest；每 case 记录 base/merged/runtime sha |
| 设备执行 | PARTIAL | 30/30 执行，20 PASS；10 FAIL 全部有 issue/known-blocker 或 INFRA-LOAD 分类 |
| Unit 覆盖 | PASS(覆盖) / PARTIAL(结果) | 160/160 有执行证据；U2 2 known-blocker、U3 2 DEFER blocked |
| 闭环输入 | PARTIAL | 107/112 COVERED，5 字段级 PARTIAL，16 fresh round-2 sessions |
| 闭环输出 | PASS(覆盖) | 115/115 COVERED，16 fresh round-2 sessions，0 mismatch |
| visual_or_physical | NOT RUN | 无物理硬件 |

## 验证边界

- 全部为 `virtual-device validation`；不能证明物理 RF/光学/电气/机械行为。
- `INFRA-LOAD` 两例（core2/stickc-plus2）保留双观测：负载下 FAIL、静默下同 argv PASS；不报产品失败，也不删除原 FAIL 记录。
- tab5 旧 lane PASS 与最新二进制 NOT RUN 分开；不迁移。
- CL-A/CL-B 的 PASS 包含“round-1 已执行证据审计 + round-2 fresh 执行样本”；不是全部 112/115 Unit 都在 round-2 重新跑（fresh 各 16）；PARTIAL/审计比例在 coverage.md 明示。
- 未修任何 repo tracked 代码；所有缺陷通过 GitHub/GitLab issue 跟踪。

## 风险与回滚

- 无源码改动，无需回滚；6 个 scope 的 guest 均 purge=0 停止，服务最终统一由 Lead 清理。
- 若 issue 被修复后需重跑，使用记录中的固定固件/sha/runtime/session 命令即可重建；派生的矩阵/console/make_image 适配只在 `.work`，不污染 repo。
