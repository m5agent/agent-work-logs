# ESP Emulator 文档与工作流总整理

- 日期：`2026-10-23`
- 结果：`PASS`
- 工作类型：`docs_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`88c88ab46b23da09c9216bc603133d69bacfb250`
- 基线版本：`bf500ec3a6287586bdb28713a0feedc7e19a9eaf`
- 环境：macOS Apple Silicon；Python 3；本地 QEMU/esp-emu 工作树

## 结论

完成一次从当前代码、catalog、测试和 evidence 反推文档的整理：

- 新增文档总导航和新鲜度规则，区分当前事实、契约、专题、历史证据和待办；
- 修正 Core2 native-VHCI 已进入 Device Service、但仍依赖 GDB 后端的交叉文档
  漂移；
- 更新过期的 `platform/README.md`，移除“网络模拟暂不开放”等旧状态；
- 增加工作流总表和带 ID 的可执行任务板；
- 明确 `67/67` 全矩阵是 `7823bef` 之前的里程碑证据，当前 release 级全矩阵
  为 `NOT RUN`；
- 扩展文档契约测试，检查全部文档已入索引、相对链接、设备计数、API 版本、
  平台测试计数和已知过期陈述。

## 关键结果

- 平台测试：`215/215 PASS`
- runtime coverage：`PASS`
- peripheral catalog：`PASS`
- QEMU profiles：`PASS`
- OpenAPI：`3.1.0`，runtime contract `1.7.0`，33 paths，解析 `PASS`
- 所有 `docs/*.md` 均进入 `docs/README.md`
- `README`、`AGENTS`、`platform/README`、设备文档、docs 和 tests README
  的相对链接检查 `PASS`
- 物理硬件：`NOT RUN`
- 当前 release 级 67-case 全矩阵：`NOT RUN`

## 文件

- `report.md`
- `run.json`
- `evidence/verification.summary.json`

## 未覆盖项

- 本次不修改 QEMU 控制器、固件路径或 Device Service 运行逻辑；
- `7823bef` 后的 `67/67` 发布级全矩阵尚未复跑；
- 不产生真机、RF、功耗、声学、光学或机械证据。
