# ESP Emulator Core2 sustained PSRAM and network stress

- 日期：`2026-10-25`
- 结果：`PASS`（virtual-device；物理硬件 `NOT RUN`）
- 工作类型：`code_change`
- 源码仓库：<https://github.com/m5agent/m5stack-esp-emulator>
- 基线版本：`b4b793127dd3351ed4a7b398ab1e0de810d17ab0`
- 结果版本：`2a3e8120c5548110fad032d0172a3f7dd7a15e13`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40150023648>
- 环境：macOS Apple Silicon；真实 Device Service `/api/v1`；QEMU

## 结论

Core2 `core2-native-hci` 已从短时三次 PSRAM 读回扩展为持续压力门禁：

- 3 个独立 artifact-bound lease，各 120 秒；
- 每轮从 QOM 生效的 4 MiB 虚拟外部堆分配 1 MiB；
- 分别完成 35、35、36 次全缓冲校验，累计 106 MiB；
- 每轮 10 次受控 HTTP recheck；
- 每轮 3–4 次公网 DNS/HTTP recheck，合计 10 次；
- active BLE、NUS GATT、frame、34 节点 QOM、pcap、evidence 和 cleanup 同实例 PASS。

pcap 分别包含 222、205、211 个包和 53/46/48 flows，三次都识别到
DHCP DORA、`example.com` DNS 和持续 TCP。HLI 为 `45/45`，errors、queue、
dropped 和 panic 均为 0。

## 关键证据

- 结果：`3/3 PASS`；
- 每轮外部堆：`4,194,304 B`；
- guest 请求：`1,048,576 B`；
- sweeps：`35/35/36`，累计 `106 MiB`；
- HTTP/public rechecks：`30/10`；
- frame：`3,731 B`，三轮 SHA256 一致；
- QOM：`34` nodes；
- firmware SHA256：`5ed4fcfad22c50d10d9a1af48bdb8e7b7e125a6fa278d3f8e30e53bd03aa43db`；
- 首次 `hold/3` sweep 阈值校准失败已保留，不覆盖为 PASS。

## 文件

- `report.md`：实现、阈值纠偏、执行结果和边界；
- `run.json`：机器可读记录；
- `evidence/verification.summary.json`：脱敏验证摘要。

## 未覆盖项

- 物理板载 8 MiB PSRAM；
- 物理 cache/PSRAM 时序、带宽和电气行为；
- bit-exact Espressif BT controller/baseband；
- 长时并发/吞吐和 active-stop 之外的其他 teardown；
- 物理 RF、功耗和真机验证。
