# 实验数据清理、快照共享与删除条件

- 日期：`2026-11-06`
- 结果：`PASS`（主机存储清理、哈希/属性/消费者读回及工具链入口实测）。
- 来源：用户要求继续清理，并说明剩余数据何时可删。先前选择保留的旧验证任务未取消。
- 源码：[esp-emulator](https://github.com/m5agent/m5stack-esp-emulator)，HEAD `ea6a553b702c636b10692665c475341b178cb662`。
- 清理仅涉及明确的ignored数据路径；并行源码修改原样保留，未作最终clean声称。
- 环境：macOS arm64；文件系统、SHA、属性、打开文件、APFS写入隔离及host编译/执行控制。
- [前一轮固定记录](https://github.com/m5agent/agent-work-logs/tree/9f8dd7eaba6bd621b74416cb8b20047cccc17d6d/records/esp-emulator/2026-11-06-storage-and-clone-audit/)的完整恢复PASS保留为历史结果。

## 最终结果

本轮全卷空闲空间实测增加 **30.6403GiB**，当前约153.6512GiB可用。
项目目录du从本轮开始的 **106.3374GiB降至87.5567GiB**。du会重复计入共享extent，
不能把目录数字当作独占物理空间；全卷观察也包含并行小写入。

- 删除24个已结案全量实验冷包，保留36,958条经两轮全SHA读回的小证据路径及原索引/证明，新增保留约0.31GiB。这24包完整raw为 **NOT AVAILABLE**，其它独立历史归档不作此声明。
- 精确删除旧构建中间物、重复天气工具链/下载缓存；两套相同browser SDK合并为一套，旧默认路径改为相对链接，四条实际编译/链接/Node控制通过。
- 旧任务35,157份大型重复快照改为写入隔离的COW副本，全部155,694原路径保留，进度/结果/observer不变；该步骤全卷空闲观察增加 **11.6843GiB**。

按最后链接计费并扣除各轮全部新增审计成本的删除净收益为 **19.0010GiB**。
COW的11.6843GiB另按实际卷观察分列，不重复扣审计成本，不把候选/du上限加入收益。

## 何时可以删除剩余数据

剩余87.6GiB并非永久保留清单。普通完整clone此前实测约371.55MiB，ignored实验目录不随clone下载。

| 数据 | 删除条件 |
| --- | --- |
| 已结束实验的全量Flash/连续帧/source副本 | 结论、准确身份、相关失败/关键样本与复现入口已核验留档，且无人依赖全量raw；删除后如实标注完整raw不可恢复 |
| 未完成任务的唯一输入/进度 | 任务完成或明确取消后逐叶清理；静态重复内容可先无损共享 |
| 下载包、构建缓存、重复工具链 | 无活动使用者，确认可再生成/重新取得，保护唯一源码和最终产物；同一版本尽量保留一套 |
| dirty源码及其SDK工作树 | 先保存提交或核验patch及全部未跟踪资产，再退役工作副本 |
| 虚拟磁盘/标准固件 | 核实使用者、准确恢复路径和整个backing依赖后，删除重复副本或退役不用的设备环境 |

旧任务目前只有observer，无guest/runner执行；第一批148项含110PASS/36PARTIAL/2FAIL，
后续工作仍为PREPARED_NOT_RUN。此前把observer存活当成实际执行不准确，现已更正。
本轮未取消该未完成目标，#188输入、唯一work-image冷包及标准runtime继续保护。

## 文件与边界

[报告](report.md)和[结构化记录](run.json)列出全部阶段与证据；主要入口：

- [24包退役](evidence/public-retirement-summary.json)、[身份与时间线](evidence/retirement-summary.json)、[选定样本](evidence/retained-samples-summary.json)。
- [旧构建缓存](evidence/build-cache-summary.json)、[天气缓存](evidence/weather-cache-summary.json)、[SDK别名](evidence/browser-sdk-alias-summary.json)。
- [COW共享](evidence/cow-snapshot-summary.json)、[旧目标真实状态](evidence/unfinished-goal-state-summary.json)。
- [最终目录/卷测量](evidence/followup-final-space-summary.json)、[第一阶段测量](evidence/final-space-summary.json)。
- [逐类删除条件](evidence/deletion-conditions-summary.json)、[剩余目录分类及条件](evidence/remaining-allocation-conditions-summary.json)、[原引用可用性核查](evidence/reference-update-plan.json)。

原始私有路径/会话配置、完整包、逐文件manifest及本地proof不随公开记录发布；摘要里的
私有proof文件名仅作本地索引。完整退役包不能从SHA还原。COW保持字节与必保属性，
inode/ctime/birthtime变化单列。SDK控制的首次测试配方FAIL与修正后PASS分开保留。
patch/code不适用；产品guest、browser-WASM与物理硬件验收均NOT RUN，无新的功能PASS。
