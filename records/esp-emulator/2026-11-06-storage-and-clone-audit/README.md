# 存储保留与普通完整 clone 审计

> 可用性更新（2026-11-06）：后续按用户要求，本文所述24个已结案全量冷包已删除，仅保留经校验的小证据及原索引/证明；这24包的完整原始材料现在无法恢复。此前完整恢复PASS是当时的执行结果。独立work-image冷包仍保留，详见[后续清理记录](../2026-11-06-completed-raw-retirement/)和[当前可用性摘要](evidence/current-raw-availability-summary.json)。

- 日期：`2026-11-06`
- 结果：`PASS`（主机存储与 clone 审计）；24个目录及旧磁盘的冷归档已完成。
- 工作类型：`infra_baseline` / `report`。
- 问题来源：用户要求清理非重要工程数据，并核实[源码仓库](https://github.com/m5agent/m5stack-esp-emulator)的实际 clone 负担。
- 源码版本：审计时 main `ea6a553b…`；产品源码未改，完整 SHA 见 `run.json`。
- 环境：macOS arm64，普通 Git 网络 clone、文件系统计数及只读镜像比较；无设备操作。

## 结论

普通完整 clone 接收 pack **118.31 MiB**，落盘 **371.55 MiB**；当前
`docs/evidence` 逻辑大小约 **4.95 MiB**。本机的大体积主要来自 ignored 的运行、
构建和历史材料，不能据此把 Git 历史认定为同样大小，也无需本轮重写历史。

已完成 qstr 中间缓存、重复 boot 分区副本清理及 work image 验证后冷存，连同24个旧目录归档，本轮约净
回收 **41.34 GiB**，项目目录从147.81降至106.47GiB。原始证据有复查价值；可重建中间物
可移除，关键字节及失败证据完整冷存。19 个源码仓库的已有状态及 active goals 保留。

## 关键证据

- 构建或运行：普通 full clone 非 shallow/partial，默认 tags 完整；qstr 有实际生成规则依据。
- 产物或部署：work image 完整实际解压、SHA/元数据与 QEMU raw compare 通过；无产品发布。
- 实机或服务执行：guest、browser-WASM、物理硬件 `NOT RUN`；本轮未启动或重启服务。
- 日志、测量或协议：allocated/净收益与 `df` 分列；首次 group 恢复 FAIL 及后续 same-owner PASS 保留。

## 文件

- [report.md](report.md)：方法、结果、恢复流程和限制。
- [run.json](run.json)：交付状态与范围。
- [clone 摘要](evidence/clone-summary.json)：实测 clone 与 HEAD 清单。
- [已完成存储摘要](evidence/completed-storage-summary.json)：三项收益、保护证明和 APFS 失败试验。
- [大批次摘要](evidence/archive-batches-summary.json)：10+14 scope 的真实终态、恢复检查与保留的中间失败。
- `patches/`、`code/`：不适用；本轮无产品 patch，不复制原始数据或测试工程。

## 未覆盖项

用户选择保留约27.4GiB的进行中验证任务，该目录未改动。五个 direct probe 默认使用的 raw work
image 已冷存，运行前必须恢复。原始归档包含私有数据，仅本地 `0600`，不随公开记录发布。
APFS 压缩未实际生效，其临时副本清理不计收益；没有压缩镜像 guest 兼容性结论。

[最终空间与保护核验](evidence/final-space-summary.json)。冷归档仍可恢复原始材料，原始数据和恢复索引不在公开Git中分发。
