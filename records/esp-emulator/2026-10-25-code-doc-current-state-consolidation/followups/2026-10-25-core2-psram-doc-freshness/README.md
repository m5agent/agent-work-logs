# ESP Emulator Core2 guest PSRAM and current documentation reconciliation

- 日期：`2026-10-25`
- 结果：`PASS`（virtual-device + docs/contracts；物理硬件 `NOT RUN`）
- 工作类型：`code_change`
- 源码仓库：<https://github.com/m5agent/m5stack-esp-emulator>
- 基线版本：`e679e303281496deb85a9ff09c8baef7cac7fdc0`
- 功能提交：`785101915939795f2fb91ed2d9871ff420fd7e84`
- 文档提交：`b4b793127dd3351ed4a7b398ab1e0de810d17ab0`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40148745338>
- 环境：macOS Apple Silicon；Python 3；真实 Device Service `/api/v1`；QEMU

## 结论

Core2 unified guest 的 PSRAM 验证已经从“QOM 能看到 4 MiB 节点”推进到
真实 guest 数据路径：

- 3 个独立 artifact-bound lease；
- 每轮从 QOM 生效的 4 MiB 外部堆分配 1 MiB bytearray；
- 每 4 KiB 写地址标记和确定性数据模式；
- 初始化校验后完成 3 轮全缓冲读回；
- 同一 guest 同时保持 WiFi DHCP/HTTP、公网 DNS/HTTP、外部 NUS GATT、
  PNG frame、34 节点 QOM、pcap、evidence 和 cleanup PASS。

同时完成代码/文档重整：README 不再复制静态设备表，机器生成的
`project-snapshot.md`、`project-status.md`、Backlog、工作流、代码地图、
证据台账和 Core2 专题页统一指向同一组证据与边界。平台契约、文档一致性、
Node UI、coverage、catalog、profile 和 GitHub Actions 均通过。

## 关键证据

- 结果：`3/3 PASS`；
- 每 lease 外部堆：`4,194,304 B`；
- guest 请求：`1,048,576 B`；
- 观测空闲量下降：`2,228,232 B`；
- sweeps：`1,2,3`；
- frame：`3,731 B`，三轮 SHA256 一致；
- QOM：`34` nodes；
- HLI：`45/45`，errors/queue/dropped/panic 为 0；
- firmware SHA256：`9294ac61c4ccf64b346dfb02273c855fc0d63b6f7cede81e66919e1ee63290e6`；
- ELF/QEMU/runner 哈希及运行期无漂移记录见 evidence。

## 文件

- `report.md`：实现、根因修正、文档整理、验证和边界；
- `run.json`：机器可读记录；
- `evidence/verification.summary.json`：脱敏验证摘要。

后续把三次读回扩展到 `3×120s` 持续 PSRAM/周期联网压力，见
[Follow-up: sustained PSRAM and network stress](followups/2026-10-25-sustained-psram-network-stress/)。

## 未覆盖项

- 物理板载 `8 MiB` PSRAM，当前 QEMU 模型上限是 `4 MiB`；
- 物理 cache/PSRAM 时序；
- bit-exact Espressif BT controller/baseband；
- 长时并发/吞吐和 active-stop 之外的其他 teardown；
- 物理 RF、功耗、电气和真机验证。
