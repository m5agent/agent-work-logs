# 文档知识源与双知识库更新

- 日期：2026-11-06
- 结果：`PASS`（本次增量同步及服务内容回读）；历史原理图全目录复验 `PARTIAL`
- 工作类型：`code_change` / `service_debug`
- 问题来源：用户要求拉取最新主库和全部子知识源，并更新知识库。
- 源码：`nuxt-m5-docs @ 8513fb4e80226ccc5bb0fc03dd6e05d2cf225129`；输入基线 `c06d36fcf45e30c99d89c19dca991a41b975e216`
- 环境：独立 Python 环境、文档生成器与既有知识库客户端；内部运行信息已省略。

GitHub 316 页、原理图 556 份、UIFlow2 376 页已刷新。火山最终 3231 份 CSV 和 467 个 PDF 引用均在线且处理就绪；ESP 更新 198 个对象，复跑零上传/零删除。212 个 CSV 源对象、198 个 ESP 对象和远端根索引回读全部一致。

- [完整报告](report.md)
- [运行记录](run.json)
- [来源摘要](evidence/sources-summary.json)
- [知识库覆盖与恢复](evidence/huoshan-summary.json)
- [ESP 内容及索引回读](evidence/esp-summary.json)
- [检查与限制](evidence/checks-summary.json)
- [维护补丁](patches/0001-knowledge-source-normalization.patch)

硬件、虚拟设备、在线客服问答未运行；本次服务路径结果不替代这些层级的验收。历史原理图资源缓存缺失以及客户端旧 ID 回退风险详见完整报告。
