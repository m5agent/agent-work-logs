# 修复后复测报告（模拟器 + UIFlow2 文档 + 产品文档）

## 背景

2026-11-05 提交的模拟器修复 PR #189 关闭了 #172–#187（#188 tab5 仍 open）。用户要求在此基础上再次全面测试，并新增两类文档测试：

1. 模拟器：全设备、外设矩阵、Unit、控制闭环；
2. UIFlow2 文档：不仅测 API 稳定性，还评估文档本身是否合理、是否会让使用者反复试错（`uiflow2-coder` skill 即由这些文档生成，文档质量=skill 质量）；
3. 产品文档（新增）：测试产品/Unit 时读取 nuxt-m5-docs 产品页，发现错误提交到原始仓库（internal GitLab 项目 121）。

全部结论为 `virtual-device validation`；无物理硬件。

## 方法

- 修复后 native runtime：`.work/issue-repair-20261105/runtime-clean/source/build/qemu-system-xtensa` sha256 `27df1b40…`（Xtensa）/ `.work/M5StopWatch-QEMU/build/qemu-c6/.../qemu-system-riscv32` sha256 `25497c52…`（C6）。
- 最新固件：`fetch_firmware.py --all --force` 重新拉取并逐台校验（30 台：v2.5.5×4、v2.5.4×23、v2.5.4-4MB×1、pinned×2）。
- 服务：7 个隔离 Device Service（8899/8901/8903/8905/8907/8909/8911），全部指向修复后 runtime。
- 并行 8 scope（7 teammates + Lead）：D1 Device Service 冷启动全设备；D2 tracked device matrix；P1 tracked peripheral matrix；U1 Unit battery；DOC1 UIFlow2 API 稳定性；DOC2 UIFlow2 文档合理性/首调成功率；DOC3 产品文档 Unit 页；DOC4 产品文档设备/HAT/Module 页。
- 失败规则：先二次复现；负载诱发标 `INFRA-LOAD`；每个 candidate 含身份/证据/复现/去重；Lead 统一提报（GitHub / GitLab 163 / GitLab 121）。

## 结果

### 模拟器

| scope | 结果 | 说明 |
| --- | --- | --- |
| D1 冷启动（29 台 ×2 轮） | 19 PASS + 10 PASS-flaky，0 hard FAIL，tab5 NOT RUN | #180/#181/#182/#187 VERIFIED；classic 烧录间歇失败（#178 reopened） |
| D2 device matrix（33 台） | primary 20 PASS / 12 FAIL / 1 EXCLUDED；重试+诊断后 30 PASS、2 NOT RUN、1 EXCLUDED | 10 个 FAIL 全为 classic flash lane（infra）；#172/173/174/179/183/184/187 VERIFIED |
| P1 peripheral matrix（68 case） | 66 PASS / 2 FAIL | #175/#176/#177 VERIFIED；core2-axp192 retry PASS；stackchan settle 时序 → #192 |
| U1 Unit battery（144/153 case） | 128 PASS / 7 PARTIAL / 7 FAIL / 2 BLOCKED；catalog 142/160 | #186 VERIFIED；#185 覆盖不全 → #193；buzzer known-blocker |

### UIFlow2 文档

| scope | 覆盖 | 发现 |
| --- | --- | --- |
| DOC1 API 稳定性 | 101 Unit 页 / 1303 文档方法；185 hardware/display/system 成员；1105 代码块（1101 编译、60 执行）；3 个 Unit-model 双波闭环 | 9 页类名不可导入；方法名拼写/case/不存在；3 个成员缺失；4 个官方代码块语法错误；稳定性（rotation/volume/rgb/joystick2/ENV 单位）PASS |
| DOC2 文档合理性 | 84 页评分（23 页人工）；10 API 首调实验；1113 代码块编译；437 literalinclude | 首调 9/10 一次成功（ADC 因缺 import 需 2 次）；display "(default -1)" 误导；display 方法缺失；extio 悬空 include；m5ui 示例缺 M5.begin；CAN 无方法文档；button 表无图例 |

产出 9 个新 UIFlow2 文档 issue（163 #27–#35）+ 3 条既有 issue 证据（#9/#15/#17）。

### 产品文档

| scope | 覆盖 | 发现 |
| --- | --- | --- |
| DOC3 产品文档 Unit 页 | 32 units / 64 页（EN+ZH；JA 抽查 8 页） | 5 个 finding → 121 #17/#18/#19 + GitHub #191 |
| DOC4 产品文档设备/HAT/Module 页 | 36 页（24 设备 + 12 HAT/Module，EN+ZH） | 2 个 finding → 121 #15/#16；跨仓库数据差异 → GitHub #190 |

同时确认产品文档 master 已修复历史 #3/#4/#5（ADC ranges、Hat SPK2、relay/DAC2/charger 电气表述）与 IMU 轴向/链接问题。

## 验证与边界

- 无 tracked 文件改动；无 gh/glab 写操作由 teammate 执行（全部 issue 由 Lead 复核、去重后提交）。
- 证据绑定：每条 case 记录 firmware version+sha256、runtime sha256、session/命令、输入与观测、evidence 路径；修复验收逐条对照 issue。
- 已知限制：
  * classic 烧录在 #178 重开后仍需修（重试可过，但不可作为稳定验收）；
  * tab5 最新镜像仍 open #188；
  * Unit 18 个未覆盖（9 无 runner + 9 时间盒），上一轮独立 probe 未全部重跑，已标 NOT RUN；
  * 负载 8–14 时 frame-sensitive case 出现 INFRA-LOAD（#192 建议硬化）；
  * 上游固件 fetch 的版本标签与 manifest 标签不一致（同 sha 不同 label）已观察并记录，未单独提 issue（属上游元数据，不影响测试身份，以 sha 为准）。
- 回滚：无源码改动；所有派生证据在 `.work/retest-20261106/`，服务最终停止。

## 后续建议

1. 先修 #178（classic 烧录稳定性）与 #193/#192（证据/时序完整性），再做全量回归；
2. UIFlow2 文档优先修 #27–#35（直接提升 uiflow2-coder 生成质量与首调成功率）；
3. 产品文档 #15–#19 为低风险高收益修正；
4. 剩余 Unit（无 runner 的 9 个 + 时间盒 9 个）补 runner 后再全量。
