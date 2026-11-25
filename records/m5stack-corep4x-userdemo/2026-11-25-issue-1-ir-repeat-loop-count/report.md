# M5CoreP4X UserDemo Issue #1：IR “Repeat x2” 只发一帧的源码核对

## 背景

- 条目：<https://github.com/m5stack/M5CoreP4X-UserDemo/issues/1>，作者 `HalfSweet`，英文，OPEN，
  处理前 0 条评论。
- 现象：红外 TX/RX 页面打开 “Repeat x2” 后，发送结果与 “Repeat x1” 相同，只出一帧 NEC。
- 作者自述：通过阅读源码发现 `ir_encoder.cpp` 用 `loop_count = is_repeat ? 1 : 0`，
  而 ESP-IDF v6.0 起把 `loop_count == 1` 归一化为 0，因此 “x2” 与 “x1” 等价；
  作者未采集出厂固件的红外输出。
- 本次任务：只读核对结论是否成立，发一条英文回复；不关 issue、不 push 到他人仓库。

## 结论

作者结论成立，且属于源码层面可完全确定的 API 语义问题：

1. 演示固件把 NEC 的重复开关映射成 `rmt_transmit_config_t.loop_count = 1`。
2. 该仓库在 `CMakeLists.txt` 中硬性要求 ESP-IDF 6.1（版本不符直接 FATAL_ERROR），
   而 IDF 6.1 的 `rmt_transmit()` 在写入事务描述符时执行
   `t->loop_count = config->loop_count == 1 ? 0 : config->loop_count;`，
   即 `1` 被当作“不循环”。
3. 因此 “Repeat x2” 与 “Repeat x1” 走的是同一条单次发送路径，UI 上的按钮只是改了文案
   （`Repeat x1`/`Repeat x2`）与设置字段，不改变实际发送次数。

当前 HEAD（`6b3c1c8`，2026-11-25）该行未改动；`cd1e1bd` 与 HEAD 在 `otool_ir/` 与
`ui_function_irtxrx_window.cpp` 上没有差异。

修复建议的可行性：

- `loop_count = 2` 可行：NEC 编码器一帧是 34 个 `rmt_symbol_word_t`（1 个引导 + 32 个数据位
  + 1 个结束位），加 EOF 也远小于该通道的实际硬件容量。通道配置
  `mem_block_symbols = 64`，驱动按 `SOC_RMT_MEM_WORDS_PER_CHANNEL = 48` 向上取整为
  2 个 block = 96 个 symbol，满足 loop 模式“整帧必须一次装入硬件内存”的要求
  （驱动在超过容量时打印 `encoding artifacts can't exceed hw memory block for loop transmission`）。
- 两次 `rmt_transmit()` 也可行：`trans_queue_depth = 2`，两笔事务都能入队，第二帧在第一帧
  完成后紧接着发出；若要让 UI 的 “TX ... -> ESP_OK” 表示“已发完”而不只是“已入队”，
  需要在报告前调用 `rmt_tx_wait_all_done()`。
- RC5 路径不受影响（`loop_count` 始终为 0）。

需要向作者确认的一点（已写入回复）：若 “Repeat” 的本意是 NEC 协议里的 repeat code
（9 ms + 2.25 ms + 562 µs 的短帧），那修法不是改 `loop_count`，而是发另一种码型；
按现有 `Repeat x1/x2` 文案与作者描述，本次按“同一帧连发两次”理解。

## 代码位置

- `components/otool_esp_component/otool_ir/ir_encoder.cpp:137-139`（HEAD 与 `cd1e1bd` 相同）：
  `config.loop_count = request.is_repeat ? 1 : 0;` → `rmt_transmit(...)`。
- `components/m5_corep4_component/corep4_lvgl_ui_sync/ui_function_windows/ui_function_irtxrx_window.cpp:556`：
  `s_ir_page.pending_tx.is_repeat = s_ir_page.tx_repeat;`；`:274` 只改按钮文案。
- `components/otool_esp_component/otool_ir/ir_tools.cpp:341`：TX 通道 `mem_block_symbols = 64`，
  `:344` `trans_queue_depth = 2`。
- `components/otool_esp_component/otool_ir/format/nec/nec_encoder.cpp:127-165`：一帧 34 个 symbol。
- `CMakeLists.txt:8,19-21`：强制 ESP-IDF 6.1。
- ESP-IDF `components/esp_driver_rmt/src/rmt_tx.c:550-551`：`loop_count == 1` 归一化为 0；
  `:131-136` 内存块向上取整；`:665-670` loop 模式的整帧内存检查。

## 验证方式与证据

- 只读 sparse clone `m5stack/M5CoreP4X-UserDemo`，核对 `cd1e1bd` 与 HEAD `6b3c1c8` 的对应文件。
- 本机 ESP-IDF 树 `~/Documents/esp-idf-6.1`（`fff9895c`，IDF 6.1.0）核对驱动实现与 P4 SoC 能力宏：
  `SOC_RMT_MEM_WORDS_PER_CHANNEL 48`、`SOC_RMT_SUPPORT_TX_LOOP_COUNT 1`。
- 本机 Device Service 设备列表只读查询：36 个 profile，无 `corep4`/CoreP4X。
- 硬件测试中心只读查询：唯一 ESP32-P4 节点备注为“已借出、勿分配”，未使用。

## 未覆盖项与边界

- hardware validation：`NOT RUN`。仅有的一块 ESP32-P4 测试节点处于“已借出、勿分配”状态；
  即使可用，夹具也没有红外接收器/光电采集路径来计数 NEC 帧。
- virtual-device validation：`NOT RUN`。Device Service 没有 CoreP4X profile；唯一的 P4 profile 是
  Tab5（`ESP32-P4NRW32`，`esp-emulator-native`），它是另一块板、没有 CoreP4X 板级模型，
  其 profile 说明也没有覆盖 IR/RMT 输出；仿真器仅有 classic ESP32 的 RMT 发光模型，
  没有 P4 RMT 循环语义。
- 出厂固件的实际红外波形未采集（作者同样未采集）；本记录只证明“代码路径上 x2 与 x1 等价”。
- 未验证修复后的两帧能否被真实 NEC 接收端正确解码（需要硬件与接收端）。
- 未测量两帧之间的间隔、载波占空比与 LED 驱动电流。

## 回滚/影响面

无代码改动，无仓库写入，仅发布一条 issue 回复。
