# XIAOZHI_CARD_KIT dry-run 型号准入复现

[此前的审核记录](../2026-11-17-interaction-plan-and-upload-fixes/report.md)中的 `E_NO_SIM_PROFILE` 表明审核无法选择型号。此次使用网络收音机 1.0 和 1.1 的留存送审元数据，在隔离环境复现正常排队、终态和证据回读，并检查保存快照重试对原 BIN 的要求。

## 执行

1. 从 Firmware Review Service `aebbe38ce0fa2ba5c278270554ef8af6f5da8a32` 导出 `service` 和 `docs/review-service.openapi.yaml`，使用 Python `3.13.15` 从该源码启动独立 Reviewer。摘要固定了归档、入口和 OpenAPI 的 SHA-256。
2. 从留存记录只读取两份元数据。用本地待审查询夹具供给同样的标题、版本、描述、设备、分类和声明的固件 SHA-256 与长度。待审对象使用临时测试标识，文件地址指向会记录并拒绝请求的本地探针。外围检查限制出站连接和子进程，关闭 AI 内容复核和提交。
3. 分别经 `POST /api/reviews` 以 `submit: false` 入队，回读各自的任务详情、事件和证据索引。核对返回的解析后元数据与留存内容相同、类型化记录的文件哈希与证据索引一致、工作目录只有内容快照和型号准入记录。对两个终态任务分别走普通保存快照复审接口，验证拒绝发生在入队之前。

## 结果

| 层级 | 状态 | 观测 |
| --- | --- | --- |
| HTTP 与 worker | `PASS` | 两个请求均为 HTTP 202，正常 worker 处理并落盘，事件序列均为 `queued → state → content → done`。 |
| 型号准入 | `PASS` | 两个版本均为 `manual_review / SIM_PARTIAL / E_NO_SIM_PROFILE`，`category=unsupported_target`、`phase=model_admission`、`source=review_target_mapping`、`source_code=target_mapping_absent`。 |
| 缺失快照拒绝 | `PASS` | 两个保存快照重试均为 HTTP 409，缺少匹配的 BIN，终态和事件序列一致。 |
| BIN 读入、静态分析和设备功能 | `NOT RUN` | 只有四个待审元数据查询。BIN 下载、Device Service 请求和虚拟租约均为零，证据为 `guest=null`、`firmware_conclusion=NOT EVALUATED`。 |
| 真机和 Burner | `NOT RUN` | 仅执行隔离 Reviewer 准入验证；提交次数为零。 |

根因可定位到当前 Reviewer 的 `DEVICE_MAP` 缺少 `XIAOZHI_CARD_KIT` 映射，执行在固件读入前退出。`E_NO_SIM_PROFILE` 是外层审核错误码，服务写入 `emulator-failure.json` 以指明具体阶段。要运行同原版的保存快照复审，需要与留存 SHA-256 和长度均匹配的 BIN；要进行启动验证，还需要经过验证的该型号运行配置。

[执行摘要](evidence/reviewer-xiaozhi-model-admission.summary.json)仅保留版本、摘要哈希、协议结果和计数，省略待审身份、端点及原始描述内容。退出时关闭了测试进程和夹具监听，移除了临时状态。此次无代码和部署改动，回滚不适用。
