# M5Stack GitHub 公开仓库近期未回复 Issue 盘点

- 日期：`2026-09-18`
- 结果：`REVIEW`（盘点）+ `PARTIAL`（5 条 issue 的 host/编译级闭合验证；无完整工具链与实机）
- 工作类型：`report`
- 问题来源：用户要求盘点 GitHub 公开仓库近期“没人回复”的 Issue，并评估哪些可以验证和回复
- 源码版本：多个公开仓库，逐条记录于 `report.md` 的 commit SHA 与 `file:line`
- 环境：GitHub 公共 API（`gh` CLI）+ 本地 shallow clone + host C++/TSan/编译级复现；无 ESP-IDF/Arduino/ESPHome 完整工具链与实机

## 结论

公开组织 `m5stack` 当前 618 个 open issue，其中 241 个完全没有任何评论。近 30 天创建的
“零评论” issue 有 10 个，30–60 天 9 个，60–90 天 4 个。已完成 9 个 issue 的源码/配置级核对，
其中 7 个可以直接形成实质回复（构建步骤、代码缺陷、配置根因），2 个只能给配置级结论并明确
标注未做整机验证。本记录为 `REVIEW` 级别，不代表已复现或已回复。

## 关键证据

- GitHub Search API 快照：`org:m5stack is:issue is:open` 共 618 条，零评论 241 条。
- 近 90 天零评论清单：见 `report.md` 第一节。
- 源码核对：`M5Unit-8Encoder@a75ab1a`、`StackChan-BSP@8d4d6fc`、`StackChan@1b57655`、
  `M5GFX@641944b`、`HAT_8Servos_v1.1_Firmware@4c5dc44`、`esphome-yaml@cc708dd`、
  `M5Unified@e79eb6e`，具体行号见 `report.md` 第二节。
- 结构化摘要：`evidence/summary.md`

## 文件

- `report.md`：完整盘点报告、可回复性评估与闭合验证结果
- `run.json`：结构化记录（14 项 checks）
- `evidence/summary.md`：查询口径、快照计数和核对摘要
- `evidence/verification.md`：5 条 issue 的可执行复现/验证证据与限制

## 未覆盖项

- 未执行整机硬件复现、ESP-IDF/Arduino/ESPHome 实际构建或烧录。
- 公开评论已发布并回读验证（5 条首轮 + 5 条验证补发）；本记录的固定 commit 链接尚未发布，待归档推送后补充。
- 未检查 private 仓库。
- 源码结论基于记录时的公开仓库 HEAD，不等同于报告者所用版本（如 M5GFX 0.2.27、固件 2.5.3）。
