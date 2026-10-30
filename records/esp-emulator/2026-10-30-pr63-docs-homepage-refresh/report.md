# ESP Emulator PR #63 双语首页与维护指南合并报告

## 背景

- 来源：[PR #63](https://github.com/m5agent/m5stack-esp-emulator/pull/63)。
- 作者：`yuyun2000`。
- Base：`674665ea008e65f26aae105ac927e4b1e2909746`。
- Head：`34cc59264bb7a55aa46d90fe82f036ac67e2966f`。
- 需求：刷新首页的当前浏览器范围、部署边界和维护导航，并新增英文入口。

## 快速合并审核

- PR 状态：非 draft，`MERGEABLE`，`CLEAN`。
- PR head CI：platform contracts 与 network namespace policy 均成功。
- 范围：`35` 个文件，`1,882` additions、`830` deletions。
- 内容：Markdown、Python/JavaScript、JSON 和两张 PNG 截图。
- 安全：无固件、密钥、MAC、内网端点和超 1 MiB 文件；loopback 地址仅用于
  本地文档预览命令。
- 两张截图已人工核对，内容为公开模拟器工作台和明确标注未运行固件的模型画廊。
- 没有致命或阻断问题，因此直接合并。

## 文档与边界变化

- 中文 README 从 369 行收敛为 105 行，并增加 `README.en.md`。
- 根 `AGENTS.md` 精简，六个主要目录增加局部职责指引。
- 更新当前浏览器配置、原生后端、视觉库存、部署版本和旧运行时包兼容性说明。
- 生成快照单独登记浏览器源码 profile，不把候选配置计入公开运行类别。
- 更新真实 CoreS3 工作台和模型外观截图，旧截图保留。

## 合并与 CI

- Merge commit：
  `345c879c5a69bc1e0c03bbca66738592176c732e`。
- 远端 head 分支已删除。
- 合并后 CI：
  [41009177074](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41009177074)。
- platform：`1,680` tests，`OK (skipped=10)`。
- QEMU profile、peripheral catalog、runtime coverage、project snapshot：
  PASS。
- browser/preview contracts、offline Unit evidence、network namespace policy：
  PASS。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| docs render | PASS | 中文/英文 GitHub GFM 桌面与窄屏渲染、图片加载与语言切换 |
| build/contracts | PASS | CI platform 与四个生成器 |
| runtime | NOT APPLICABLE | 本轮没有设备运行时行为改动 |
| virtual-device | NOT RUN | 没有新增或重跑设备行为结论 |
| visual_or_physical | PARTIAL | 截图内容与加载通过；不构成新设备视觉或物理 PASS |
| delivery | PASS（远端） | merge commit 已推送且合并后 CI 两个 job PASS |
| local-main-sync | PARTIAL | 主 worktree 有 6 个原有改动，未覆盖 |

## 验证边界

文档截图只描述页面外观；CoreS3 图片中的就绪 frame 来自既有运行证据，
Atom/Stick 图片明确标注未运行固件。不能把本轮 README 刷新解释为触摸/PIR、
全设备浏览器或物理硬件验证完成。

## 风险与回滚

回滚应整体 revert `345c879c5a69bc1e0c03bbca66738592176c732e`。主工作区现有
未提交文件没有被 stash、reset 或覆盖。
