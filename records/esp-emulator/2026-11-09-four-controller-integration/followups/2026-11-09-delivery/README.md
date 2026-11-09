# 四款主机接入合并与工作台复测

- 日期 `2026-11-09`
- 结果 `PARTIAL`
- 类型 `code_change`
- 源码 `e9bb9f2efa5201e024715dedd5152b54086f6a59`，与候选提交 `7dcfa0679719dfb221205220afc7be56ab75e954` 的文件树一致。[PR #197](https://github.com/m5agent/m5stack-esp-emulator/pull/197)
- 环境为 Chromium 157 和合并版原生 Xtensa Device Service。CoreMatrix 使用原记录的独立 C61 诊断运行时。

本地 2,035 项平台测试通过、10 项跳过。Node 契约、设备目录校验、模型浏览器检查、PR 和主分支 CI 均通过。合并前用精确候选代码补做两款 Paper 的真实工作台交互。

- [PaperS3 Factory V0.5 原生工作台](evidence/papers3-native-workbench-summary.json)
- [PaperDIY Factory V1.0 原生工作台](evidence/paperdiy-native-workbench-summary.json)
- [既有 PaperMono 原厂固件的新旧运行时对照](evidence/papermono-factory-baseline-summary.json)
- [交付报告](report.md)
- [结构化执行](run.json)

CoreMatrix 官方 UIFlow2 应用、正式浏览器 QEMU-WASM 和物理设备验收仍开放。
