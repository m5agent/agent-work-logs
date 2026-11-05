# ESP Emulator：统一 Web 工作台

- 日期：`2026-11-05`
- 结果：`PARTIAL`（代码、合并与Pages交付完成；线上独立CoreS3验收，其他板/Unit本轮未线上重跑）。
- 工作类型：`code_change`、`report`。
- 问题来源：用户要求设备、Unit 装配、UIFlow 编辑和已有会话在同一 Web 页面使用，并保持静态站点与服务页面的功能入口一致；无公开 Issue 编号。
- 源码版本：[m5stack-esp-emulator](https://github.com/m5agent/m5stack-esp-emulator)，base [3e8f76b836009438b7d9312e1e7b8f822b7d64f5](https://github.com/m5agent/m5stack-esp-emulator/commit/3e8f76b836009438b7d9312e1e7b8f822b7d64f5)；最终源码 [e31c2b4aed07c98fddea19018589f0f8751667c2](https://github.com/m5agent/m5stack-esp-emulator/commit/e31c2b4aed07c98fddea19018589f0f8751667c2)；[PR #168](https://github.com/m5agent/m5stack-esp-emulator/pull/168)已合并为082fffaf。
- 环境：JavaScript host 合同、独立 Device Service 验证入口与静态浏览器工作台；物理硬件未操作。

## 结论

统一入口的源码已实现：原生编程复用 Preview/Run API；Unit 草稿与实际会话装配分别保存；
已有会话可以在主视图打开，停止查看不会获得或行使其生命周期所有权。
当前已完成限定真实 virtual-device validation：原生 CoreS3+PIR 13/13，以及静态导出上的完整 CoreS3 browser-WASM 编辑器 63/63。
前者实际运行、导入、取消并验证 Unit 串口/QOM/红绿帧；后者完成12次 raw-paste、2次未修改默认程序、硬重置恢复与正常 Worker 清理。
最终同源码 Python1973项为1963通过/10跳过，Node30、四生成器和分支范围检查均通过。
两份 guest 摘要中的20个源码身份与最终提交逐字回核一致。PR已合并、Pages已发布；独立HTTPS CoreS3完整63项通过，详见交付后续。
不能从接口声明、页面出现编辑器或 host 控制通过推断全部型号、全部 Unit 或线上功能通过。
最终前端副本的 host18 通过取代当前依据，上一轮 [host18 收据](evidence/workbench-host-summary.json)仍独立保留，不覆盖历史。

## 关键证据

- 源码与根因：[实现审查摘要](evidence/implementation-review-summary.json)。
- 已完成的 adapter 15 项 host 控制、原控制器和浏览器 UART 合同：[host 摘要](evidence/host-contract-summary.json)。
- Unit 19 项 host 控制、Node 30 个合同脚本和 Chrome host 18 项均通过；[最终前端副本 host 收据](evidence/workbench-host-copy-final-summary.json)明确没有 guest、WASM 请求或运行时 Worker。
- 首次 native 前提失败、第二次 observer 失败及 r3/r4 工具前提失败：[验证时间线](evidence/validation-summary.json)；后续不得覆盖此前失败。
- [native13 摘要](evidence/native-summary.json)：精确固件/原生运行时、真实 PIR、同 VM、取消、pre-stop ZIP 与清理。
- [browser63 摘要](evidence/browser-summary.json)：精确 Flash/WASM、实际 raw-paste/输入/帧/reset、正常 QMP退出与两阶段6个 CDP targets 清场。
- 原生 r5 的30秒 observer 误截与 r6 的11项实际通过/ZIP body观察失败独立保留；最终 r7 使用产品已有 pre-stop Blob 验证 ZIP。
- [最终源码验证](evidence/final-source-validation-summary.json)：同源码完整检查及两轮旧元数据失败。
- [准备包](evidence/prepared-archive-summary.json)：2,134资产、251,977,755字节闭集与147,130,306字节归档包身份；部署与线上证据见交付后续。

## 文件

- [report.md](report.md)：问题、实现、验收入口和范围。
- [run.json](run.json)：结构化状态。
- [evidence/](evidence/)：明确标记为 summary 的派生证据；不包含原始日志、固件或设备标识。
- patches/、code/：不另附；实现与可重建入口由最终源码提交提供。

## 未覆盖项

其它主机、其它 Unit、旧普通会话的真实 guest 接入和性能均不继承本次限定结果；本轮线上仅独立验证CoreS3。
原生 argv 未单独捕获，既有 Flash 缓存复用不构成新工具传输或性能证明。旧运行时故障调查不属于本次修复范围。

## PR #168 交付后续

PR #168已合并为082fffaf，正式发行包与Pages发布成功；[独立后续](followups/2026-11-05-pr168-delivery/README.md)固定CI、全量资产回读和线上CoreS3完整63项。
首次归档的待交付状态保留在原公开固定提交，原失败与其它板/Unit未线上复测的边界继续保留。
