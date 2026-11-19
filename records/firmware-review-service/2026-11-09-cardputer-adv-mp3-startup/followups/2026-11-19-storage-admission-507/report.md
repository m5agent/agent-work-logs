# Reviewer 507 存储不足与同任务恢复

## 问题与改动

Device Service 对单个原版 BIN 写入作容量预检。Reviewer 0.31.0 的二进制上传调用把 HTTP 异常交给通用处理，保存为 `E_INTERNAL`。新版把 `507` 与 `storage_exhausted` 绑定到 `environment_unavailable`，记录发生阶段，并在数值和不等式校验后保留 `storage_bytes`。`firmware_conclusion` 为 `NOT EVALUATED`，`guest` 为空。

上传、组合和创建会话分别记录归因阶段。已有创建意图由同一恢复流程核对清理。其余 HTTP 错误沿用原路径。API 0.31.1 将容量数据纳入归因结构，读取审核详情或 `emulator-failure.json` 均能复查原回执。详细数据见[mp3-storage-admission.summary.json](evidence/mp3-storage-admission.summary.json)。

## 同原版对照

| 步骤 | 结果 | 可复查观测 |
| --- | --- | --- |
| Reviewer 0.31.0 保存快照 | `service_error / SIM_PARTIAL / E_INTERNAL` | Device Service 上传 `507 storage_exhausted`，未生成设备会话、固件 artifact 或创建意图 |
| Reviewer 0.31.1 同路径 | `service_error / SIM_PARTIAL / E_SIM_STORAGE_EXHAUSTED` | 同一 Device Service 返回 `507`，核对 `artifact_upload`、环境不可用及无来宾，容量回执出现在审核详情和证据文件 |
| 正常容量条件的同一子任务 `/retry` | `done / SIM_VERIFIED` | 返回 HTTP 202，无新子任务，旧失败回执 SHA-256 一致，父任务行、事件、BIN、内容描述和旧证据保留 |
| 恢复轮来宾 | `PASS` | 回车已送达，SPI 完整块数 4 → 58，60.017 秒虚拟取证 |

两个隔离 Reviewer 走标准 `POST /api/reviews/{job_id}/snapshots`。Device Service 1.99.3 的负对照仅将独立实例的 `M5_SERVICE_MIN_FREE_BYTES` 设成 8 GiB，未写入填充文件。实际原版为 885,600 字节，候选回执记录可用 4,685,262,848 字节、需求 8,590,820,192 字节、保留 8,589,934,592 字节。上述数值来自候选的 Reviewer 请求；同轮独立探查返回相同需求和保留字节数。

恢复轮以同一数据目录启动普通容量策略的独立 Device Service，注册固定 FAT32 夹具，用 `sourceMode=saved_snapshot` 复跑同一子任务。`Cardputer ADV MP3 Player v1.0.0` 的原始 SHA-256 为 `c5918ff914a51b0dc4398f331c8306c25e26a4b157592d3e7d9c0dff2d0c5e45`。8 MiB 启动 Flash 的 SHA-256 为 `10d42a08a69d3e1f628fd9078015a64b598a74f02437c26ecc7201cc2db3e78d`。独立读取归档中的来宾 Flash，应用从 `0x10000` 到原镜像末尾逐字节一致，原镜像范围内 86 个差异字节全部位于 NVS。

复核 ZIP 的 12 个载荷条目均通过 CRC、长度与 SHA-256。数字 PCM 为 48 kHz 单声道，共 1,651,712 字节，七个窗口匹配 524 Hz。两段与主动断言关联的 PCM 窗口在 ZIP 中逐字节对应，主频为 522.792 与 522.582 Hz。串口有一条启动标记，无本次断言覆盖的崩溃标记。设备最终停止，可写 Flash 释放，活动租约和待处理创建均为零。两套隔离进程退出。

另以同一原版和发布源码执行两个阶段专用对照。测试夹具仅在目标 HTTP 路由调用原有容量检查时调高门槛，两轮均从真实 Device Service 收到 507，需求为 8 GiB 预留加 8 MiB Flash。组合返回 `firmware_composition`，会话返回 `session_admission`。会话创建意图通过标准恢复接口查得 `not_created`，其后两个实例均无会话、活动租约或待处理创建。附加对照未挂载 SD。

## 复现与边界

1. 固定 Cardputer ADV MP3 Player v1.0.0 的原版 BIN、描述快照和 FAT32 夹具。其 SHA-256、容量与执行版本见[mp3-storage-admission.summary.json](evidence/mp3-storage-admission.summary.json)。
2. 分别启动基线和候选 Reviewer，连接同版本 Device Service 的独立实例。负对照设置 8 GiB 保留，并在各自已保存的原任务上调用 `/snapshots` 进行本地 dry-run。
3. 比对两次审核终态、容量回执、空会话和空 artifact。恢复候选隔离实例为普通容量策略并上传夹具，对同一任务调用 `/retry`。用停止状态、读取证据 ZIP 和 SPI/PCM 断言验收。
4. 回滚 Reviewer 到基线提交即可恢复旧行为。保留原 BIN、父任务和两轮证据，以免丢失故障来源。

Reviewer 运行提交 `4024a0d2b931315028e020277641ed6662c48b43` 和交付源码提交 `883ccf08d8ef3f9afd111199974e57c08b09a1fd` 的 Git 树都为 `66c36037958b93d8c99688cf375d764a15d2c886`。这是 virtual-device validation，实机、物理声学、browser-WASM、Linux 受管来宾及 Burner 提交均为 `NOT RUN`。
