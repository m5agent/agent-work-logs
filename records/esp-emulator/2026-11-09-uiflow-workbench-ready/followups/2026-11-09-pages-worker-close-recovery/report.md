# Pages 浏览器的 QEMU Worker 关闭恢复

正式工作流的先前执行在 AtomS3 Lite UIFlow editor 路径观察到五个嵌套 pthread 退出，QMP 正常退出码为 0，外层 engine 的 CDP target 在正常窗口 120 秒和失败清理窗口 30 秒后仍可枚举。60 个用例最终为 15 PASS、1 FAIL、44 NOT RUN，部署跳过。CDP 的观察边界是 target 是否仍可枚举，具体浏览器原因未定位。[先前正式执行记录](https://github.com/m5agent/agent-work-logs/blob/ed77b7a73039f811b03ad4881a7707446451c54a/records/esp-emulator/2026-11-09-uiflow-workbench-ready/followups/2026-11-09-formal-pages-publication/report.md)

## 改动范围

候选 `fda5858e64462d67917fee885aa6ad429fdf39f6` 基于 `70ca46258598294eb5e5852115b1dfce386d8754`。12 个文件包含三个浏览器运行时模块、八个测试和一份部署文档。引擎先应答并关闭私有端口，再通知 iframe。iframe 是唯一的 Worker 终止方，在正常通知后执行一次 `terminate()`。未收到通知时保留受防重入保护的回退路径。运行时仍等待 iframe 的通知处理并在移除前读取归属状态，测试通过独立 CDP 观察验证 target 关闭。正式工作流的用例、门槛和超时沿用原配置。[PR #196](https://github.com/m5agent/m5stack-esp-emulator/pull/196)

## 本机 browser-WASM 虚拟设备验证

本机系统 Chrome 157.0.8103.38 使用 Apple M4 GPU。每轮绑定了站点清单、runtime 清单、WASM、ROM、UIFlow 固件、profile、探针哈希和各自独立的原始报告哈希。候选三个报告的 33 个 Web 源文件均对应候选提交。相较先前本机基线，33 个文件中有三个 Worker 生命周期文件的字节变化。先前 Hosted 与本机基线 Web 源与导出闭包、五个 runtime 资产、Lite 固件与 ROM、测试脚本哈希一致，站点和 runtime 清单及生产者元数据不同。候选和本机基线继续使用同一组 runtime 资产。程序探针包含每轮独立标记。[有界证据](evidence/local-candidate-summary.json)

| 用例 | 结果 | 同一路径观察 |
| --- | --- | --- |
| AtomS3 Lite 旧版本本机对照 | PASS 58/58 | 11 个程序及硬复位恢复，QMP 退出 0，6 个 CDP targets 在 context 关闭前清空。先前 Hosted 的目标滞留在本机对照中未复现 |
| AtomS3 Lite 候选首轮 | FAIL | 48 个检查通过后，硬复位阶段出现 Core 1 `LoadStorePIFAddrError`，PC `0x4038a853`，EXCVADDR `0x6002304c`。独立失败清理收齐 6 个 CDP targets，QMP 退出 0，正常 owner 终止 1 次，fallback 0 次 |
| CoreS3 候选 | PASS 24/24 | 就绪且执行计数为 0 时，320×240 客体帧和模型各有 76,800 个黑像素。1440 和 390 像素宽布局、编辑器焦点、真实程序串口输出均通过。绘图后客体帧与模型各有 76,800 个红像素。停止前后验证提示和正常 Worker 清理 |
| AtomS3 Lite 候选受控重试 | PASS 58/58 | 11 个程序、硬复位后 epoch 1 恢复和实际执行。QMP 正常退出 0，owner 通知 1 次、正常终止 1 次、fallback 0 次，iframe 保留时 6 个 CDP targets 全部消失 |

首轮 Lite 的复位失败独立保留。复位异常和先前 Hosted 关闭失败的共同根因未确定。

## 静态和回归检查

候选 Python 平台套件 2,041 项，跳过 10 项，其余通过。Node contracts、四项项目验证器、PR scope、`git diff --check` 均通过。精确验证入口是仓库正式工作流的 pinned QEMU 构建、导出和 `test_public_qemu_admitted_boards.mjs`。本机单板可用同一站点导出与相应系统 Chrome，运行 `platform/tests/test_public_uiflow_guest.mjs`，以 `M5_QEMU_DEVICE=atoms3-lite` 选择目标，以 `M5_PUBLIC_SITE`、`M5_PUBLIC_BASE_PATH` 指向隔离站点，以 `M5_WASM_GPU=hardware` 保留同类 GPU 路径。CoreS3 的探针身份、输入输出与布局检查见有界证据。[正式工作流源码](https://github.com/m5agent/m5stack-esp-emulator/blob/fda5858e64462d67917fee885aa6ad429fdf39f6/.github/workflows/public-site.yml)

## 兼容性修订

初版候选的 PR 和 push CI 都因历史启动证据固定了两个 runner 脚本的字节而失败。修订 `71c011d87690b46217e197b69bc8d8580dd2d103` 将两个 runner 恢复至基线字节，并保留旧通知计数字段作为同一归属通知的别名。历史启动检查 9/9、wrapper、项目快照和 PR scope 通过。此修订的 CoreS3 独立重跑为 24/24 PASS，两个通知字段同为 1、正常终止 1 次、fallback 0 次、CDP 6 → 0。前表中的本机 AtomS3 Lite 两轮仍绑定初版提交。[PR 首轮 CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42560814074) · [Push 首轮 CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42560658764)

## 合并后的正式发布尝试

PR #196 的四项 CI 通过后，合入 `5f15d1f824958829f7d62648a5efbfe5fcee2edb`。正式 run `42561655744` 绑定该合并提交。Hosted 的 33 个 Web 源文件与提交 blob 一致。Pinned C/QEMU 构建、静态导出和 Canvas 正负控制均通过，随后全量串行门槛在第二个用例失败。60 个计划用例结果为 1 PASS、1 FAIL、58 NOT RUN。[正式运行](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42561655744)

| Hosted 用例 | 结果 | 同一路径观察 |
| --- | --- | --- |
| Atom Matrix UIFlow editor | PASS 58/58 | 真实程序和复位恢复均完成。QMP 正常退出 0，正常 owner 终止 1 次、fallback 0 次，5 个 CDP targets 在 context 关闭前全部消失 |
| Atom Matrix UIFlow buttons | FAIL | 浏览器会话和固件按钮观察器已就绪。首个键盘按下后，客体心跳序号 2–8 在 22,002–28,040 ms 持续报告未按下，报告中的输入用例为空。首个输入的模型分发和控制器传输未取得可判定证据 |
| 上述按钮用例的失败清场 | FAIL | QMP 正常退出 0，正常 owner 终止 1 次、fallback 0 次，四个 pthread targets 消失。30 秒失败清理观察结束时，CDP 仍可枚举一个 engine target |

两用例绑定同一站点清单、五个 runtime 资产和 Atom Matrix 固件。失败清场的 CDP 证据与 QMP 退出和 owner 请求各自独立，target 滞留原因仍未定位。此次流程提前停止，先前失败的 Hosted AtomS3 Lite editor 没有运行。[Hosted 摘要](evidence/hosted-42561655744-summary.json) · [原始 Actions artifact](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42561655744/artifacts/13650691240)

## 合并提交的本机全量验收

同一合并提交 `5f15d1f824958829f7d62648a5efbfe5fcee2edb` 的本机 browser-WASM 全量串行门槛为 60/60 PASS。19 个 UIFlow editor、19 个按钮、1 个 Cardputer 键盘、1 个 StackChan 触摸和 20 个固定示例均完成，0 个未运行。复核 60 份子报告的字节和哈希以及测试脚本对应的 Git 源码。使用系统 Chrome 157.0.8103.38 和 Apple M4，逐用例独立浏览器和 VM。[本机全量摘要](evidence/merged-local-gate-summary.json)

本机 Atom Matrix 的键盘 Space 和指针均观察到模型事件及同一客体的 BtnA 按下、释放。QMP 正常退出 0，5 个 CDP targets 清空。AtomS3 Lite editor 58/58、11 个程序及虚拟复位恢复，6 个 CDP targets 清空。本机和 Hosted 使用不同的运行环境。各自执行结果独立保留。

从本机通过的站点导出制作发布包 `public-site-preview-live.tar.gz`。归档 146,977,854 字节，SHA-256 `ece3366be0e118f5424a7fd502827674e2e6e7eb09d6372aa46d3486b58212e0`，逐文件核对清单中 2,135 项及清单自身。发布后的下载包与本地包逐字节一致。

## 预构建包发布与 HTTPS 回读

以本机 60/60 通过的导出包走仓库现有预构建站点发布流程。公开预发行标签 `pages-uiflow-ready-20261109-5f15d1f` 解析到合并提交 `5f15d1f824958829f7d62648a5efbfe5fcee2edb`。部署 run `42569300648` 的 prepare 和 deploy 均成功，站点清单 SHA-256 为 `2cba4433a875d4b99e0776c9f4bf5f240f59e221e174971a016871dffc5fa39d`。[公开预发行](https://github.com/m5agent/m5stack-esp-emulator/releases/tag/pages-uiflow-ready-20261109-5f15d1f) · [预构建站点部署](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42569300648)

公开 HTTPS 的 CoreS3 browser-WASM 虚拟设备回读 31/31 PASS。比对线上站点清单、33 个 Web 闭包文件与 5 个 runtime 资产，另外核对浏览器实际收到的 HTML、JS、CSS 三个关键响应。390 和 1440 像素布局下，就绪时编辑器未执行代码，真实 320×240 帧和模型各为 76,800 个黑像素。通过实际编辑器执行程序，串口标记和同一客体的全红帧进入模型，提示消失。正常停止 QMP 退出 0、owner 正常终止 1 次、fallback 0 次，6 个 CDP targets 清空，停止提示状态通过。[公开站点](https://m5agent.github.io/m5stack-esp-emulator/) · [发布与线上有界证据](evidence/prepared-release-42569300648-summary.json)

## 交付边界

常规 Hosted 门槛 run `42561655744` 的 FAIL 和 deploy 跳过仍独立保留。预构建发布的线上验收范围为 CoreS3，其他型号的 HTTPS、物理硬件和 native Device Service 均为 NOT RUN。60 用例全量结果来自本机 browser-WASM。需要回滚时，将候选改动作为整体撤回，以使 Worker 协议字段、生命周期逻辑和对应断言保持一致。
