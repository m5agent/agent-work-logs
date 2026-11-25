# M5CoreP4X UserDemo #1：IR “Repeat x2” 只发一帧

- 日期：`2026-11-25`
- 结果：`REVIEW`（仅 code-level verification；硬件与虚拟设备均 `NOT RUN`）
- 工作类型：`issue`
- 问题来源：<https://github.com/m5stack/M5CoreP4X-UserDemo/issues/1>，作者 `HalfSweet`，英文，OPEN；处理前 0 条评论
- 源码版本：`m5stack/M5CoreP4X-UserDemo` `cd1e1bd`（作者引用版本）与 HEAD `6b3c1c8`（2026-11-25）
- 环境：macOS；本机 ESP-IDF 6.1.0 源码树（`fff9895c`）；本机 Device Service 设备列表只读查询；
  硬件测试中心只读查询（未使用任何 DUT）

## 结论

作者判断成立。演示固件把 NEC 的 “Repeat x2” 映射为 `loop_count = 1`，而该仓库强制使用
ESP-IDF 6.1，`rmt_transmit()` 在 6.1 里把 `loop_count == 1` 归一化为 0（等同不循环），
所以 x2 与 x1 是同一笔单次发送，只有按钮文案变了。

修复建议两条都可行：`loop_count = 2`（NEC 一帧 34 symbol，通道 96 symbol，装得下），
或连续两次 `rmt_transmit()`（队列深度 2）；后者若要在 UI 上报告“已发完”，需
`rmt_tx_wait_all_done()`。RC5 路径不受影响。

## 关键证据

- `components/otool_esp_component/otool_ir/ir_encoder.cpp:137-139`：`loop_count = is_repeat ? 1 : 0`。
- `ui_function_irtxrx_window.cpp:556`：`pending_tx.is_repeat = s_ir_page.tx_repeat`；`:274` 仅改文案。
- `CMakeLists.txt:8,19-21`：只接受 ESP-IDF 6.1。
- IDF `rmt_tx.c:550-551`：`t->loop_count = config->loop_count == 1 ? 0 : config->loop_count;`。
- IDF `rmt_tx.c:131-136`：`mem_block_symbols=64` → 2 块 × 48 = 96 symbol；`:665-670` loop 整帧内存检查。
- Device Service：36 个 profile，无 CoreP4X；唯一 P4 profile 为 Tab5，无 IR/RMT 模型。

## 文件

- `report.md`：完整核对报告（结论、修复可行性、边界）
- `run.json`：结构化记录
- `evidence/issue.json`：issue 元数据与正文
- `evidence/repo-state.txt`：演示仓库代码事实（HEAD/`cd1e1bd` 行号、IDF 版本门槛、通道配置、NEC 编码器）
- `evidence/idf-rmt-facts.txt`：ESP-IDF 6.1 RMT 驱动与 P4 SoC 能力宏
- `evidence/device-profiles.txt`：本机设备 profile 清单与 Tab5 说明
- `evidence/hardware-availability.txt`：P4 实物节点不可用说明（已去标识）

## 未覆盖项

- hardware validation `NOT RUN`：唯一 P4 节点备注“已借出、勿分配”；夹具无红外接收/光电采集路径。
- virtual-device validation `NOT RUN`：无 CoreP4X profile；Tab5 为另一块板且未建模 IR/RMT 输出。
- 未采集出厂固件红外波形；未验证两帧在真实接收端可解码；未测量帧间隔与载波。

## 已发布回复

- <https://github.com/m5stack/M5CoreP4X-UserDemo/issues/1#issuecomment-7154557851>
  （1 条，英文；issue 仍 OPEN，未 close、未 push、未改他人仓库）
