# ESP Emulator PR #30 扩展主机模型合并报告

## 背景

- 来源：[PR #30](https://github.com/m5agent/m5stack-esp-emulator/pull/30)。
- 需求：合并其余开放 PR，恢复更多可在浏览器运行的 Atom、Stick、Dial 和
  StackChan 主机模型，并推进 GitHub Pages 发布。
- 合并前 `main`：`02e6eb1f58f13346a6f4e8059ce401d3336d4c74`，已经包含
  PR #39。
- PR #30 head：`349b778ab2d57e39e2da84f634fc8f232bca129a`。

## 结论

PR #30 以双父 merge commit
`2f95ff23101b0b70f484eb8176a9a4c206a8e866` 集成。该提交的第一父为 PR head，
第二父为合并前 `main`。随后修复了两个只在合并树上出现的契约差异，最终
`main` 为 `e3f149c1ffad45ac923e677dea1af599a78c35a6`。

GitHub 已将 PR #30 标记为 merged；PR 列表为空。代码和交付层为 `PASS`，
物理硬件层为 `NOT RUN`，因此总记录保持 `PARTIAL`。

## 合并处理

### QEMU patch 编号

最新 `main` 已占用 `0085`–`0095`。PR #30 的 peripheral patch 整体后移到
`0096`–`0109`，native context patch 后移到 `0009`–`0014`。同步更新了
bootstrap recipe、README、fixture 和单元测试，并重新计算 browser runtime
lock：

- `65` 个总 patch；
- `47` 个 native patch；
- `158` 个 patched file；
- 干净 QEMU worktree 顺序应用全部 patch 成功；
- `bootstrap_qemu_browser_runtime.py --check` 与
  `bootstrap-unit-runtime.py` 路径检查通过。

历史 evidence JSON 中的旧编号保留为当时运行回执，不回写成新编号。

### 浏览器与 Device Service

合并保留了双方的设备 profile、display orientation、outputs、Device Service
lifecycle、classic LX6 确定性加速、S3 ADC calibration 和 eFuse package
覆盖。视觉模型升级到固定 upstream
`4879ab51eb8bb11ce024e670ae6880529e3d0f42` 后，local runtime patch 同时保留
boot-time pause/resume/dispose 与 focused device input。

### 合并后修复

首次候选 CI 捕获 4 个契约失败：

- Device spec 测试仍把 matrix 路径 patch 在旧聚合模块；
- 设备数量断言仍为旧值 `14`；
- 新视觉模型快照中的 local runtime patch 未包含主线的 focused input。

修复后，设备集合直接从 matrix 推导，eFuse 测试 patch 正确的 spec 模块，
visual runtime patch、patch hash、effective hash 和 vendor manifest 同步
更新。定向测试 `26/26` 与生成器检查通过。

### Pages preview

静态站源码构建成功，但首次 macOS 验收在第一个设备前被图形环境门禁拒绝：
runner 选择了 software WebGL，而发布门禁要求 hardware renderer。该失败没有
进入 guest，不是设备固件或 QEMU 行为失败。

为避免重复丢失已构建产物，临时 preview 分支将
`public-simulator-site-preview` artifact 上传改为 `if: always()`。该分支不进入
`main`。产物随后发布为
[pages-preview-20261030](https://github.com/m5agent/m5stack-esp-emulator/releases/tag/pages-preview-20261030)，
并通过仓库既有 prepared-preview workflow 部署：

- deploy run：
  [40988933566](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40988933566)；
- 线上 runtime：`20` 个 compiled profiles；
- 线上公开准入：`19` 款设备；
- preview WASM SHA256：
  `7612dfa18238122f52daea3b40cbf0a3055cb9fe4c6f7b5bc1cfecce7ba5e0dd`；
- 站点：
  [https://m5agent.github.io/m5stack-esp-emulator/](https://m5agent.github.io/m5stack-esp-emulator/)。

## 执行与验证

最终候选 CI：
[run 40985661773](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40985661773)

- platform：`1,658` 项，`OK (skipped=10)`；
- browser 与 preview contracts：全部通过；
- offline Unit evidence：全部命令通过；
- network namespace policy：全部通过；
- QEMU profile、peripheral catalog、runtime coverage 和 project snapshot：
  全部通过；
- Python entry points：compileall 通过。

PR 内已有虚拟设备结果：

- native peripheral regression `68/68`，`278` checks；
- StackChan browser strict suite `5/5`；
- 新增浏览器设备使用各自固定官方固件、显示/输入及可选 LED 数据面；
- 验证分类为 `virtual-device`，不是物理硬件测量。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | browser runtime lock、source replay 与 CI compileall |
| flash | PASS（virtual-device） | Device Service/browser 固定固件会话 |
| transport | PASS（virtual-device） | UART、GPIO、RMT、I2C、SPI/SCS 数据面案例 |
| device_response | PASS（virtual-device） | 对应外设与 StackChan motion/power 回归 |
| data_behavior | PASS（virtual-device） | native `68/68`、`278` checks |
| visual_or_physical | PARTIAL（virtual-device） | 浏览器显示/输入通过；物理光学与机械 NOT RUN |
| delivery | PASS | PR #30 merged，最终 `main` CI PASS |
| preview deployment | PASS | Pages prepared-preview deploy，线上回读 20 compiled / 19 public profiles |

## 验证边界

物理 AtomS3、StickC、Dial、Atom Matrix 与 StackChan 未执行。虚拟结果不
证明 RF、光学、声学、机械扭矩、伺服供电、电池保持或电气时序。StickC Plus
首次 240 秒 ready timeout 与自然 PWR 清理仍为 `PARTIAL`，不随合并放宽。

本次 preview artifact 的严格 hardware-renderer browser gate 为 `FAIL`，原因是
GitHub macOS runner 选中 software WebGL；guest 未执行。因此站点可用于效果
查看，但不得把本次 prepared preview 当作 production browser PASS。要升级
该结论，需在 hardware renderer runner 上完整重跑所有公开 board 和 CoreS3
示例。

## 风险与回滚

合并涉及 QEMU patch 重编号和 browser runtime lock。回滚应整体 revert
`e3f149c1ffad45ac923e677dea1af599a78c35a6` 或回到
`02e6eb1f58f13346a6f4e8059ce401d3336d4c74`，不要只改回部分 patch 编号，
否则 lock 与源码 receipt 会失配。
