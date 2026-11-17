# Tab5 原版 Arduventure 长按的应用断言

- 日期 `2026-11-17`
- 结果 `PASS`（声明的非终止长按）
- 工作类型 `code_change`
- 来源 同一原版的审核交互
- 版本 原生 Device Service `dc685345`，固件审核 `f48301b`
- 环境 隔离原生 Tab5 与 saved-snapshot 审核

从同一个名称页 A 画面开始，右键点按移动到 B，右键长按 1.2 秒连续移动到 F。审核保留同一会话的按下、74 次刷新、释放和两张画面的区域指纹。九个既有点按亦通过。整单仍为 `SIM_PARTIAL`，关机终态与多点触摸以各自覆盖范围为准。

- [复现与判定](report.md)
- [结构化检查](run.json)
- [同会话脱敏回执](evidence/explicit-hold-summary.json)

真机、浏览器 WASM 与常驻部署未执行。隔离会话全部停止并释放 Flash，未提交 Burner，源提交包含变更。

最终冻结包 `bb91232a` 与 `952ba18` 同样通过九个点按和一次原版长按，观察 60.265 秒、13 个样本。 [组合复验回执](evidence/combined-frozen-review-summary.json)
