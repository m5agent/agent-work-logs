# ESP emulator：性能优化合并与 Pages 交付

- 日期：`2026-11-03`
- 结果：**PARTIAL**。两项修复已合 main，新 producer runtime/build/privacy、完整新 20 例、上传回读和 prepared-preview 部署已通过；实际 HTTPS 48 个资源回读一致。线上四阶段为前三阶段 PASS、第四阶段启动 FAIL，独立触摸输入/推导 NOT RUN。
- 工作类型：`code_change`、`report`
- 来源：[PR #163](https://github.com/m5agent/m5stack-esp-emulator/pull/163)、[PR #164](https://github.com/m5agent/m5stack-esp-emulator/pull/164)，用户授权合 main 并更新 GitHub Pages。
- 源码版本：当前 [main @ b41eba70eb61f7ddc5c41e0b981341064f9d1d1f](https://github.com/m5agent/m5stack-esp-emulator/commit/b41eba70eb61f7ddc5c41e0b981341064f9d1d1f) 为文档收口；已部署 runtime 仍由 producer `1b86ed6f7edcc36deafc4834b45a28c6a6017c79` 构建，其 merge 是 `10788607feefb9e532c2dd1fe4679adcd6aa0fc2`。b41 仅修改 docs，未重部署。
- 环境：固定 Emscripten `3.1.50` 的单一 QEMU/TCI WASM；host CI、已准备的静态站点及真实浏览器虚拟设备 gate。无物理硬件测量。

## 结论

性能 PR163 合入 main `189dc01a5ee42a23ac7e246f8390c2acfe471ffa` 后，首次正式 Pages run `41617152984` 在第三个 e950 CoreS3 案例的 engine Worker target 关闭门禁失败，deployment skipped，不能描述为发布成功。旧本地 runtime 另因 producer 私有路径撤回，先前部分四例结果不构成新发布准入。

producer 修复 PR164 已合入 main107，四项 PR CI 检查通过；随后文档收口合入当前 main b41，所有非 docs 字节不变。新构建保留单 QEMU 和原 SoC/外设实现，不集成实验 JIT：8 个库与 QEMU 全 fresh；new runtime manifest `897114f09d5e0c695e44e665611fec4fa98aa62856cddce6eb1cbb906d21071c`，WASM `3c6b249002d83118e0ddcbd82e4ee6336223293b98566fc7709d5087d9df4567`，新准备站点 manifest `c5991d737d4b20c4b1ae96b71587cec907a1e72f3c57fe2fee63c08e23daf323`。这些产物已通过完整本地功能门禁并经 prepared-preview 部署；实际 HTTPS 读取的 48 个 URL 已与冻结出口逐字一致。这里只确认已读取的路径，不声称线上全部 2127 个资产均被下载。

完整新 gate 已 **20/20、19 板型、552/552 PASS**，22 个 VM 的 102 个 pthread 与 22 个 engine、共 124 个实际 Worker targets 全关闭，fallback 为 0。上传的完整包经读回逐字校验；prepared-preview run [41629045946](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41629045946) 的 prepare/deploy 均成功。实际 HTTPS 48 GET / 49,173,223 bytes 全部 HTTP200、无重定向且与冻结出口一致。线上 CoreS3 原始示例 49 检查、StackChan reference 24 检查和 c854 两轮 20s 舞蹈通过；独立触摸轮在 ready 前发生真实 ROM 异常，故线上整体仍 **PARTIAL**。线上目标为[GitHub Pages](https://m5agent.github.io/m5stack-esp-emulator/)。

## 关键证据

- [固定历史性能报告](https://github.com/m5agent/agent-work-logs/blob/73cf198d7d3808e9f66e9cce8faa1349f9a0a9e4/records/esp-emulator/2026-11-03-emulator-performance/report.md)：性能调查和前一阶段虚拟证据；不授新 runtime/线上执行 PASS。
- [文档与证据收口](evidence/docs-source-delivery-summary.json)：17 项 docs 变更已推送；50 docs tests/四生成器/scope 检查通过，新 main CI `41631441210` **PASS**（platform/network，1949 tests、10 skipped）。
- [固定 producer 子结果](https://github.com/m5agent/agent-work-logs/blob/2c4f5fcf9469ac8f6935a29359489003705cc76e/records/esp-emulator/2026-11-03-qemu-producer-paths/report.md)：新 fresh build、privacy/source/export 审计与 Cardputer-ADV 同路径验证。
- [PR163 head CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41616464176)、[另一触发](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41616455584)：四检查通过；[main189 CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41617122831)两检查通过。
- [PR164 push CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41625517780)、[PR CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41626388927)：各 platform/network 通过，共四检查。
- [失败的正式 Pages run](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41617152984)：保留构建通过、e950 cleanup FAIL、deployment SKIPPED 的完整层次；不被本地通过覆盖。
- [新完整 gate](evidence/full-browser-gate-summary.json)、[main107 CI](evidence/producer-main-ci-summary.json)、[包闭包](evidence/prepared-package-summary.json)与[独立 tar 审计](evidence/prepared-tar-independent-summary.json)均已完成。
- [Release 上传回读](evidence/release-readback-summary.json)三项 asset 全部一致；[prepared-preview 部署](evidence/prepared-deployment-summary.json)成功。
- [线上四阶段总摘要](evidence/online-four-stage-summary.json)：三阶段 scoped PASS、一阶段首启动 FAIL、touch/derive NOT RUN，cleanup 独立。
- [实际 HTTPS 资源摘要](evidence/live-https-assets-summary.json)和[独立 canonical manifest 回读](evidence/canonical-online-manifest-summary.json)已通过；[CoreS3](evidence/online-cores3-stock-summary.json)、[StackChan reference](evidence/online-stackchan-reference-summary.json)与[舞蹈](evidence/online-dance-summary.json)通过；[触摸轮首启动失败](evidence/online-touch-startup-failure-summary.json)保留，触摸输入和响应推导未执行。

## 文件

- [report.md](report.md)：交付时间线、失败保留、构建身份、复现、边界与回滚。
- [run.json](run.json)：两 PR/CI、新产物、精确哈希与各层终态；未执行部分明确标为 NOT RUN。
- `evidence/`：审核后的 full gate、CI、package、tar audit、upload readback、deployment 和实际 HTTP/canonical manifest 摘要；四阶段 online guest、四阶段总审计与文档交付摘要均保留，包括首次失败。
- `patches/`：不适用；源码已合 main，producer 子记录已有可应用补丁。
- [code/README.md](code/README.md)：严格四项 SHA/固定 HTTPS 的原 adapter seed 恢复包；15 个源成员 identity 未变，恢复验证本身不执行 guest。

## 未覆盖项

已完成的 19 板型功能验收不等于 19 个设备都提速。实际 HTTP 回读只覆盖列明的 48 个 URL；线上独立触摸轮的首启动失败不能由先前两轮舞蹈、reference 或历史 R6 通过替代。该轮 120s 未 ready、零帧/零输入，触摸响应未验证；根因未定、没有普通重试覆盖。全部六 VM/36 targets 清理通过是独立维度。正式 CI engine cleanup、Factory gap、任意固件和长稳仍保留，physical/RF/功耗/机械等未运行。

最终主分支 CI 两检查通过，见[CI 摘要](evidence/current-main-ci-summary.json)。[独立四阶段审核](evidence/online-independent-review.json)确认线上 PARTIAL；[ROM 定位](evidence/startup-rom-literal-diagnosis-summary.json)只定位合法字面量读取失败，根因仍未确定。
