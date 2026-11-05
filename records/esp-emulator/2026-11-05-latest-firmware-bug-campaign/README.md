# ESP Emulator：最新固件问题逐项处理与存储清理

- 日期：`2026-11-05`
- 结果：`PARTIAL`；17 项问题中 16 项为收口候选，集成门禁待补；#188 保持 open。
- 工作类型：`code_change` / 问题复现与验证。
- 问题来源：[公开 issue 列表](https://github.com/m5agent/m5stack-esp-emulator/issues)。逐项链接见报告。
- 源码版本：基线 `73ed554fba02a2397dad81e39e12b5b4b92d0500`；最终集成/合并 commit：`NOT RUN`，由根代理填写。
- 环境：macOS arm64、native QEMU、独立 P4 esp-emu；Unit 经专用 Device Service，源码回归经受控 direct runner。

## 结论

本轮修复了镜像/VFS/eFuse 夹具、实际 runtime 身份、UART 观测、面板/PMIC 和
固件版本绑定等问题，并保留原始失败。**所有功能证据均为 virtual-device validation**。
Basic v2.7 在首次冻结全矩阵复现漏 B；真实 guest 重绘完成围栏修复输入顺序，
450 ms 脉冲不变，独立 A/B/C 与新 18 板全矩阵通过；早先 standalone PASS 和首次 FAIL 均保留。
Tab5 的二次 VFS 注入损坏和旧 ELF 误用已修，但最新官方应用仍在 DSI PHY PLL lock 等待，无 Python/UI/touch
通过证据；独立 0.51 后端诊断与旧模拟器构建的通过结果分列，#188 不关闭。

已按精确白名单清理和不可变内容去重，计
`46,361,821,184` allocated bytes（约 **43.178 GiB**）。约 204 GiB 来自工程目录，
主要是构建/运行产物；聊天记录或 App 缓存不是主要来源。保留当前任务、固件/ELF、
源码、会话、配置与有效证据。

## 关键证据

- 构建或运行：受影响设备/Unit 有独立 guest、输入、串口/帧/数据面摘要；完整身份集中在证据 JSON。
- 产物或部署：冻结 native 设备新矩阵 18/18；外设首轮 67 PASS / 1 FAIL 与独立 Mic 后续 PASS 分开。完整平台 2020 PASS + 1 skip、Unit 300 PASS + 1 skip、30 Node 脚本及 validators/snapshot 均通过；[PR189](https://github.com/m5agent/m5stack-esp-emulator/pull/189)已合并，head4/4与merge2/2 CI通过。
- 实机或服务执行：物理硬件 `NOT RUN`；native、P4 和 browser-WASM 不相互转授。
- 日志、测量或协议：真实 UART/Flash readback、EPD AUTO、RMT、ADC 数值、保留的失败和 cleanup 证明均按层记录。

## 文件

- [report.md](report.md)：逐项结论、复现入口、限制与回滚。
- [run.json](run.json)：最终交付状态与门禁占位。
- [evidence/validation-summary.json](evidence/validation-summary.json)：逐项状态、runtime 身份、清理证明与分组索引。
- [矩阵与 Flash 传输](evidence/matrix-transport-summary.json)、[服务与 ADC](evidence/service-adc-summary.json)、[启动与 Tab5](evidence/startup-tab5-summary.json)：各组脱敏派生证据和首次失败。
- [冻结设备矩阵](evidence/root-integration-summary.json)、[外设首轮第一部分](evidence/root-peripheral-summary.json)、[第二部分及独立 Mic 后续](evidence/root-peripheral-more-summary.json)：实际 base/派生镜像、runtime/ROM、串口和帧身份。
- [Tab5 0.51 后续](evidence/tab5-v051-followup-summary.json)、[最终构建/缓存清理](evidence/storage-final-summary.json)：最新 DSI PHY 卡点与额外保留回读。
- `patches/`：不附重复 patch；源码见 [3f24fa6b](https://github.com/m5agent/m5stack-esp-emulator/tree/3f24fa6b5a056991c37018cedb41c42d6df19b1e)。
- `code/`：不复制测试工程；使用最终源码中的 checked-in 回归入口。

## 未覆盖项

最新官方 Tab5 Python/UI/touch 和既有 Buzzer 默认路径失败仍开放；远端CI与交付均完成，见[最终交付](evidence/delivery-summary.json)。
物理硬件、RF、光学、声学、电气以及 browser-WASM 功能复验 `NOT RUN`。

[最终本地主机检查](evidence/host-gates-summary.json)、[native 依赖冻结审计](evidence/native-freeze-audit-summary.json)。

最终交付：[delivery-summary.json](evidence/delivery-summary.json)。16个issue已关闭；#188仍OPEN。CI后续Unit为303 PASS+1skip（304 total），早期300+1记录保留。
