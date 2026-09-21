# ESP32-P4 Flasher 可配置 DUT 烧录波特率

- 日期：`2026-09-21`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：用户要求优化 UIFlow 等大镜像的 DUT 烧录速度，并允许 Agent 在旧设备上回退低速
- 源码版本：`esp-flasher-by-esp32p4 @ 90c3add18542bb1679efe7d2b9815f3c8bad05ec`
- 环境：Apple Silicon macOS；ESP-IDF Docker `v5.5.4`；target `esp32p4`

## 结论

原固件只在 115200 baud 完成 ROM loader 握手，后续镜像传输没有切换速率，因此大镜像烧录很慢。
本次改动把 DUT 烧录速率作为中台 target 配置和单次任务参数显式暴露，默认值统一为
1,500,000 baud；固件在 115200 完成握手后调用 esp-serial-flasher 切换主机与目标速率。旧设备
失败时，Agent 可依次回退到 921600、460800、230400 或 115200。

中心服务测试和 ESP-IDF v5.5.4 固件构建通过。真实 1,500,000 baud 硬件烧录尚未执行，因此整体
结果标为 `PARTIAL`，不能把它当作实机速率稳定性证明。

## 关键证据

- 固件构建：`PASS`，ESP-IDF `v5.5.4`，target `esp32p4`，应用镜像 1,211,648 bytes，
  SHA256 `674f893cddb5ed7328eb97539c19c7a533201464457eccd94a8b5cd9d4b7f8dc`。
- 中心服务回归：`PASS`，84 个 unittest 全部通过；Python compile 和 Web `node --check` 通过。
- 行为合同：默认 task plan 写入 `flash.args.baud=1500000`，单次 `firmware.flash_baud` 可覆盖，
  target profile 可设置设备默认速率，越界值返回 422。
- 硬件烧录、真实吞吐和不同旧芯片的稳定性：`NOT RUN`。

## 文件

- `report.md`：完整报告
- `run.json`：结构化记录
- `evidence/build-summary.md`：构建与静态检查摘要
- `evidence/center-tests-summary.txt`：中心服务测试摘要
- `evidence/behavior-contract.md`：波特率配置与回退合同
- `patches/0001-add-configurable-flash-baud.patch`：无上下文 patch，可在 base commit 上执行 `git apply --unidiff-zero`
- `code/`：不适用；源码仓库已包含可直接重建的工程和测试

## 未覆盖项

- 没有真实 P4 节点执行 1,500,000 baud 烧录，没有记录端到端耗时、CRC/MD5 或复位结果。
- 没有用 CH340/CP210x/原生 USB-Serial/JTAG 等不同桥接芯片分别验证高速率。
- 没有验证老旧 DUT 在 921600/460800/230400/115200 各档位的稳定性；这些档位是保守回退顺序，
  不是本次硬件实测结论。
