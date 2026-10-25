# ESP Emulator full document inventory and stale-page audit

- 日期：`2026-10-25`
- 结果：`PASS`（docs/contract scope；QEMU 功能矩阵未重跑）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`35f5415ede3b635bccf5fac410faab49c0771dbf`
- 结果版本：`b8b48e46c79d65f151eca1a57431c3117fb95907`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40180394108>
- CI 结果：`PASS`（`platform-contracts`、`network-namespace-policy`）
- 环境：macOS Apple Silicon；Python 3.13；Node 20；无物理硬件

## 结论

文档治理从“人工维护 33 个权威页”扩展为“214 个 Markdown 页面的机器可读
总盘点”。自动快照现在区分权威页、设备档案、测试/用例说明、补丁说明、
平台说明、仓内历史、示例和第三方来源，并单独列出带显式旧复核日期的委派
文档。

同时修复了真实内容漂移：

- 14 个自动生成设备 README 不再复制长篇运行流水，只保留硬件档案、验证
  状态、blocker 和权威页链接；
- `tests/uiflow2/README.md` 的旧 PSRAM evidence 文件名已改为当前
  `core2-psram-sustained-8m-3x120.json`；
- Core2 native-HCI README 不再把已完成的 121 轮写成下一次门禁；
- worker queue/executor/reattach/TLS/lifecycle 页面不再把已完成的 executor、
  reattach、discovery 和 trusted-host companion recovery 写成全局开放项；
- README 与工程交接压缩为当前能力和依赖摘要，逐次运行保留在验证台账。

## 当前工作与待办

当前可执行主线：

- S3/C6/Core2 的 `qemu-unified` 单 lease 板级 + 网络 + BLE + evidence；
- controlled DNS/CNAME、CIDR egress、pcap、恢复与 worker 生命周期；
- FirmwareManifest/WebBurner、文件系统/NVS/SD fixture、安全与 capability
  审查；
- Core2 native-HCI、121 轮重连、长稳、PSRAM/MMU 和最多四实例并发。

仍开放的 P0：

- 物理跨主机 worker、迁移/reattach、跨主机幂等、QEMU guest/controller
  side-effect fence 和 namespace-managed/Tab5 companion；
- Core2 五实例及更高并发、持续吞吐、其他 teardown、物理 PSRAM/cache、
  bit-exact BT controller 和真机；
- 固件运行态 ACL/许可、live eFuse/trust root、生产 key、更多厂商和云端
  业务；
- C6 Zigbee commissioning、Core2 legacy I2C 和 ATECC608；
- 代表设备同固件 SHA 的 hardware validation。

完整列表只由源码仓库的[项目 Backlog](https://github.com/m5agent/m5stack-esp-emulator/blob/b8b48e46c79d65f151eca1a57431c3117fb95907/docs/project-backlog.md)维护。

## 关键证据

- 全量文档：`214` 页；
- 权威页新鲜度登记：`33` 页，非历史 `26`、历史固定 `7`；
- 委派文档：设备 `18`、测试/用例 `137`、补丁 `11`、平台 `3`、
  第三方来源 `2`、仓内历史 `5`、其他入口/示例 `5`；
- 所有权威非历史页和带显式日期的委派页均无旧复核日期；
- 平台测试：`467/467 PASS`；
- 文档契约：`37/37 PASS`；
- Node SHA256/upload：`2/2 PASS`；
- coverage/catalog/profile/snapshot、OpenAPI YAML、compileall、
  Ruff `E9/F`、`git diff --check`：`PASS`。

## 文件

- `report.md`：文档审计、代码生成器改动、当前工作和验证边界；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：脱敏验证摘要；
- `patches/`：不适用，改动在源码提交 `b8b48e4`；
- `code/`：不适用，权威入口是 `project_snapshot.py`、
  `generate_catalog.py` 和文档契约测试。

## 未覆盖项

- 完整 67-case UIFlow2 外设矩阵：`NOT RUN`；
- 新 QEMU 功能、网络或 worker 数据面：`NOT RUN`；
- 物理跨主机、真机、RF、功耗、电气、声学和光学：`NOT RUN`；
- 全量文档盘点能发现未分类页面和显式旧日期，但不能自动证明每个局部页面的
  语义完全正确。
