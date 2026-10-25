# ESP Emulator current work queue and documentation freshness refresh

- 日期：`2026-10-25`
- 结果：`PASS`（docs/contracts；完整功能矩阵未重跑）
- 工作类型：`docs_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`79a23213167365b60653d23d14e78cd1bd41c46a`
- 安全功能提交：`ee4ad8f33ffa9083b41ddcbc8419189cd6fcbac1`
- 文档提交：`cb4267116d6cf9061f08484902be5a88864e7d99`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40166166903>
- 环境：macOS Apple Silicon；Python 3；Node 20；无物理硬件

## 结论

当前状态、Backlog、工作流、README、代码地图、验证台账和专题页已重新
对齐到最新代码和 evidence：

- README 增加 Secure Boot v2 signature math 与包内
  `SECURE_BOOT_DIGEST` 对照的当前能力，但仍把 live eFuse/production key
  标为未闭环；
- `project-status.md`、`engineering-handoff.md`、`workstreams.md`、
  `project-backlog.md` 和 `validation-ledger.md` 使用同一安全证据分层；
- 文档契约在“没有过期非历史页”时正确断言“全部已复核”，不再强制要求
  stale-page 文案；
- Tab5、P4 backend、视觉保真和 CoreS3 image boundary 四页重新核对，
  复核日期更新为 `2026-10-25`，但能力基线仍明确停留在各自原始证据；
- 自动项目快照现在报告所有非历史页复核日期与当前事实日期一致。

完整安全实现与 21 项静态 fixture 证据见
[eFuse summary digest comparison](../../../2026-10-25-secure-boot-v2-image-evidence/followups/2026-10-25-efuse-summary-digest-comparison/)。

## 当前工作和待办

| 工作流 | 当前状态 | 下一门禁 |
| --- | --- | --- |
| 网络与 worker | DNS/CNAME、CIDR egress、discovery、TLS/mTLS、重启恢复、跨容器 QEMU、进程与 companion partition fence 已有证据 | 物理跨主机 executor/reattach、跨主机幂等、任意 NAT、QEMU guest/controller 内部和外部 side effect |
| Core2 | native-HCI、121 轮重连、7200 秒、active-stop、8 MiB QOM/MMU、PSRAM 虚拟压力已有证据 | bit-exact BT controller/baseband、物理 PSRAM/cache timing、长时吞吐/并发、其他 teardown |
| 通用固件 | Manifest/WebBurner、capability、文件系统、SD/NVS、网络预期、Secure Boot v2 结构和数学验证、包内 eFuse digest 对照已可用 | live eFuse trust、ROM 执行、运行态 ACL/许可、真实 key/cloud、更多固件族 |
| 运行时缺口 | `RUNTIME-01` 和 accepted `RUNTIME-05` 已关闭 | `RUNTIME-02` C6 Zigbee、`RUNTIME-03` Core2 legacy I2C、`RUNTIME-04` ATECC608 |
| 真机与服务化 | 虚拟设备路径可用 | `HW-01` 真机同 SHA、跨主机 worker、warm pool、模块拆分 |
| 专项 | 有可用子集 | Tab5 P4 backend、逐设备视觉、CardputerZero 收尾 |

未完成项和验收只以
[`project-backlog.md`](https://github.com/m5agent/m5stack-esp-emulator/blob/cb4267116d6cf9061f08484902be5a88864e7d99/docs/project-backlog.md)
为准。

## 关键证据

- 平台测试：`454/454 PASS`；
- 文档契约：`34/34 PASS`；
- Secure Boot fixture：`21/21 PASS`；
- Node SHA256/upload：`2/2 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  `PASS`；
- Ruff `E9/F`、compileall、`git diff --check`：`PASS`；
- GitHub Actions `platform-contracts` 与 `network-namespace-policy`：`PASS`。

## 文件

- `report.md`：整理范围、状态/待办、验证和边界；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：脱敏验证摘要；
- `patches/`：不适用，代码已提交到公开源码仓库；
- `code/`：不适用，权威入口是源码测试和自动快照。

## 未覆盖项

- 完整 67-case UIFlow2 外设矩阵：`NOT RUN`；
- 新 QEMU/worker 网络功能路径：`NOT RUN`；
- live eFuse、ROM secure boot、Flash Encryption 和生产 key：`NOT RUN`；
- 物理硬件、RF、功耗、电气、声学和光学：`NOT RUN`。
