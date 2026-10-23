# ESP Emulator 代码地图、文档与当前队列重整

- 日期：`2026-10-24`
- 结果：`PASS`（文档、契约、回归入口与交付层）
- 工作类型：`docs_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`72c2b8d59edc0f446fb35809d4c8e73c818dd9f5`
- 基线版本：`07df1ffd6f3385a0dedf4c8e7bf663aa81785f73`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40027623120>
- 环境：macOS Apple Silicon；GitHub Actions Ubuntu；Python 3；Node.js；现有 QEMU 与设备证据

## 结论

把当前代码入口、项目状态、工作流队列和待办重新收敛到同一套入口，并清理了
已经被后续实现推翻的文档描述。主要结果：

- 最新 Core2 `HCI-3b` diagnostic、safe-point audit 和真实 controller-entry
  audit 已同步到状态、工作流、Backlog、代码地图和运行时契约；
- 明确禁止继续使用任意 safe-point callback 或 nested `r_eif_send` guest
  RPC，下一步改为 guest-visible controller-to-host IRQ/queue 或 in-process
  controller transaction；
- `AGENTS.md` 不再把已完成的流式上传列为未完成；
- Device Center 契约改为使用 `/api/v1` session lease，不再等待不存在的
  “后续进程级执行器”；
- Cardputer-ADV CC1101、controlled DNS 和其他已完成能力不再写成未来工作；
- 代码地图记录 `SVC-03` 的分阶段拆分边界，本轮不进行高风险的
  `device_service.py` 大搬家；
- 文档一致性测试新增 Core2 审计、设备中心、CC1101、DNS 和旧队列回归门禁。

## 当前工作队列

| 工作流 | 下一步最小交付 |
| --- | --- |
| 网络 | `NET-03` 双设备 private lab fabric，随后 `NET-04` 自托管 QEMU worker、`NET-05` 外部 IPv6 |
| Core2 | `HCI-3b` guest-visible C2H IRQ/queue 或 in-process controller，随后 `HCI-4` 无 GDB repeated lease |
| 固件 | `FW-01` SPIFFS/权限/许可、`FW-02` 生产安全配置、`FW-03` 跨厂商回归 |
| Device Service | `SVC-01` worker、`SVC-02` warm pool/调度、`SVC-03` 分阶段拆分编排热区 |
| 其他 | Tab5 后端、CardputerZero、视觉保真与 `HW-01` 同路径真机验证 |

## 关键证据

- 本机平台套件：`Ran 253 tests`、`OK`；
- CI：`Ran 253 tests`、`OK (skipped=2)`；浏览器 SHA256/upload `2/2 PASS`；
- runtime coverage、peripheral catalog 和 QEMU profiles：`PASS`；
- 文档索引、相对链接、API、测试数、任务和旧陈述检查：`PASS`；
- Python compileall、`git diff --check`：`PASS`；
- Linux namespace/egress CI job：`PASS`；
- 本次改动：`18` files、`173` insertions、`64` deletions。

## 文件

- `report.md`：整理范围、代码结构、当前工作和验证边界；
- `run.json`：结构化记录；
- `evidence/verification.summary.json`：本地与 CI 聚合证据；
- `patches/`：不适用，本次没有运行时补丁；
- `code/`：不适用，回归代码位于源码仓库。

## 未覆盖项

- 没有修改 QEMU 控制器、固件数据面、网络策略或 Device Service 运行时逻辑；
- 没有重跑 67-case、274-check 外设全矩阵；
- 没有新增 virtual-device 或 hardware validation；
- `HCI-3b`、`HCI-4`、物理 cache/PSRAM、RF、功耗、声学、光学和机械等价性
  仍未完成或未验证。
