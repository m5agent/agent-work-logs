# ESP Emulator SPIFFS 只读清单与文档对账

- 日期：`2026-10-24`
- 结果：`PASS`（static-image + platform contracts）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`7d274bcf3b8f7759f4d0d721bd6b234f6a67a928`
- 基线版本：`e5fbf39af5e69fb383249ab0a3b2fa88ac916c26`
- 环境：macOS Apple Silicon；Python 3；ESP-IDF v5.5.4 `spiffsgen.py`；静态镜像解析

## 结论

FirmwareManifest 现在可以在不挂载、不执行输入镜像的前提下，只读盘点 8 个
明确声明的 ESP-IDF SPIFFS 配置，并校验 block LUT、object-index page 和
data page 的对象 ID、span、flags、顺序与页号。

解析器按完整对象和有效数据页评分选择配置，避免 4096/65536 block 同时看似
可解析时选错布局。测试覆盖全部声明配置、跨多个 object-index page 的文件、
LUT mismatch、随机损坏和 erased 分区。真实 ESP-IDF generator 生成的
canonical 与 60000-byte 多索引镜像均 PASS。

同一轮已把代码地图、当前状态、工作流、Backlog、验证台账和 FirmwareManifest
契约与后续 SPIFFS/Core2 API-boundary 工作对齐。该结果是 `static-image`
验证；QEMU 功能矩阵和物理硬件本轮均为 `NOT RUN`。

## 关键证据

- 本机平台测试：`267/267 PASS`，`skipped=0`；
- GitHub Actions：run `40042218401`，`267` tests、`skipped=2`，全部合同检查
  PASS；
- SPIFFS 声明配置：`8`，每个配置均有自包含多索引 fixture；
- canonical `spiffsgen.py` image SHA256：
  `6951389cf0f200e011b5d4603a1e29405697b54e95f9291e7248a30c6d6b819c`；
- 60000-byte 多索引文件：3 个 index page、240 个 data page，SHA256 与输入
  一致；
- malformed/LUT mismatch：`INVALID`，erased partition：`UNFORMATTED`；
- 浏览器 SHA256/upload client：`2/2 PASS`。

## 文件

- `report.md`：实现、验证范围、文档对账和边界；
- `run.json`：机器可读记录；
- `evidence/verification.summary.json`：static-image 与平台验证摘要；
- `evidence/github-actions.summary.json`：对应源码 commit 的 CI 回读。

## 未覆盖项

- 本次未重跑 QEMU 67-case 功能矩阵；
- big-endian 与 `SPIFFS_ALIGNED_OBJECT_INDEX_TABLES=1` 布局未声明支持；
- 不恢复已删除对象，不证明 runtime 文件权限或许可证合规；
- 未执行物理硬件、RF、安全启动或生产 key 流程。
