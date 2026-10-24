# ESP Emulator 当前工作、代码文档与 Core2 extended-run 对账

- 日期：`2026-10-24`
- 结果：`PARTIAL`（文档/平台回归 PASS；Core2 extended-run/soak FAIL）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`83ad2492b1ea95f83071a599fc29490e729b7e13`
- 基线版本：`303e10744f3826763e355ee2c49e7715fe58a254`
- 环境：macOS Apple Silicon；Python 3；Node.js；QEMU Core2 virtual device

## 结论

本次把现有代码、生成设备档案、状态页、Backlog、工作流、验证台账和专题
文档重新对账到同一组事实，并补上了当前最关键的 Core2 长稳失败证据。

- `HCI-4` 的五个独立 Device Service lease 仍是一个有效的功能基线：
  frame、QOM、WiFi/公网、外部 NUS GATT、pcap 和 evidence 均通过；
- 后续带 hold 的独立运行出现真实失败：READY/联网/BLE 连接后 guest panic，
  一次首轮 `IllegalInstruction` 落在 controller task 的
  `semphr_give_wrapper`，随后进入 `InstrFetchProhibited` reboot loop；
- 另一轮 extended run 在 attempt 4 直接出现 `PC=0`，最终单 lease smoke 也
  复现了 `PC=0` panic；
- 因此不能把 `HCI-4 5/5` 写成 soak PASS，`CORE2-02` 当前状态为 `FAIL`；
- runner 已改为在失败时保留 partial serial/peer/pcap/evidence，并生成
  aggregate `FAIL`，不再只留下 traceback；
- 同主机 worker 目录、durable queue、HTTP executor、QEMU/QMP reattach 和
  HMAC 已从旧“未实现”文档中移出，剩余待办明确为跨主机/companion 等边界。

## 关键证据

- 本地平台套件：`296/296 PASS`，0 skipped；
- runtime coverage、peripheral catalog、QEMU profiles：全部 `PASS`；
- Node SHA256/upload client：`2/2 PASS`；
- Python compileall、Ruff、Markdown 表格结构和 `git diff --check`：`PASS`；
- Core2 最终 single-lease smoke：`FAIL`，失败时成功保留 serial、BLE peer、
  pcap 和 evidence；
- 完整 UIFlow2 外设矩阵：`NOT RUN`；
- 物理硬件、RF、电气、功耗、声学、光学和机械验证：`NOT RUN`。

## 当前工作与待办

| 优先级 | 当前状态 | 下一步 |
| --- | --- | --- |
| Core2 `CORE2-02` | `HCI-4` 功能基线 PASS；extended-run/soak FAIL | 固定 5 次、无 retry、每轮 hold 10 秒复现；先分类首轮 panic，再查 controller task、HLI/ACL ownership、Bumble teardown 和 process-stop 顺序 |
| 网络 `NET-04` / `NET-05` | 单机 namespace/DNS/TLS/exact IPv4/pcap/queue/executor/QMP reattach 已交付 | 跨主机 executor/reattach、TLS/mTLS、credential rotation、companion/evidence continuity、生产多机调度、外部 IPv6 |
| 固件 `FW-01..03` | Manifest、WebBurner、文件系统、静态审查、SBOM、声明级 license policy 已交付 | 运行时权限、完整源码级许可/法律结论、真机 secure boot/Flash Encryption/key、跨厂商样本 |
| 服务 `SVC-01..03` | 本地 lease/worker/queue/HMAC/evidence 已交付 | 跨主机 companion 连续接管、warm pool、多机调度，以及按 API/evidence 边界拆分 `device_service.py` |
| 专项 | Tab5、CardputerZero 和大部分视觉外壳仍 partial | Tab5 P4 数据面、设备级视觉模型、长期回归 |
| 真机 `HW-01` | `NOT RUN` | 代表设备使用同固件 SHA、同测试计划和同关键输入验证 |

## 文件

- `report.md`：代码/文档范围、Core2 失败分析、验证结果和回滚；
- `run.json`：机器可读记录；
- `evidence/verification.summary.json`：本地验证摘要；
- `evidence/core2-extended-run.summary.json`：脱敏的 Core2 失败摘要；
- `evidence/github-actions.summary.json`：对应源码 commit 的 CI 回读；
- `patches/`：不适用，变更已进入源码仓库；
- `code/`：不适用，runner 与 evidence 位于源码仓库。

## 未覆盖项

- 没有完成 Core2 extended-run 根因定位，也没有变成长稳 PASS；
- 没有重跑 67-case、274-check 外设全矩阵；
- 没有物理硬件验证；
- 没有声明 bit-exact BT controller/baseband、RF、cache/PSRAM 物理等价性或
  恶意固件隔离能力。
