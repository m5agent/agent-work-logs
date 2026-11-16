# Touch_ST7123 失败读取后解析未初始化缓冲区（M5GFX #417 代码级核对）

- 日期：`2026-11-16`
- 结果：`PARTIAL`（host 可执行复现通过；物理硬件与虚拟设备均 `NOT RUN`）
- 工作类型：`issue`
- 问题来源：[m5stack/M5GFX#417](https://github.com/m5stack/M5GFX/issues/417)
- 源码版本：M5GFX `28d47949bdc84f30881623476f555398e2194313`（0.3.0）
- 环境：macOS 主机 + host C++ 复现；本机无 Tab5 硬件；本地 Tab5 模拟器没有 ST7123
  控制器级模型，未做故障注入

## 结论

报告成立。`getTouchRaw()` 不检查三次 `_readParams()` 的返回值，`adv_info` 与
`touch_report[]` 都未初始化。当第三次读取（报表区 `0x0014`）失败时，循环会把栈上的
残留内容当作触摸报表解析。host 复现中，栈预填 `0xFF`、`count=5`、`max_touches=5`
时，master 返回 5 个幻触点（`id=0 x=16383 y=65535 size=255`），报告给出的补丁返回 0；
若读取在填入 3 字节后失败，master 返回 4 个幻触点。其余两种单读失败场景两版都返回 0，
与报告一致。

`_read_fw_info()` 的附带问题也复核成立：三次读取全失败时 `if` 被跳过，函数返回
`true`，`init()` 据此置 `_inited = true` 并返回成功，即使触摸芯片完全不应答。

## 关键证据

- `getTouchRaw()` 三次读取返回值均被忽略：
  [Touch_ST7123.inl:132-141](https://github.com/m5stack/M5GFX/blob/28d47949bdc84f30881623476f555398e2194313/src/lgfx/v1/platforms/esp32p4/Touch_ST7123.inl#L132-L141)。
- `_readParams()` 直接返回 `transactionWriteRead(...).has_value()`（同文件 `:39-44`），
  失败语义与报告描述一致。
- `readBytes()` 在收到字节时逐字节写入调用方缓冲区，NACK/超时后返回
  `connection_lost`（`src/lgfx/v1/platforms/esp32/common.inl:2542-2630`），因此失败时
  缓冲区可能完全未动，也可能只填了一部分；`transactionWriteRead()` 在
  `:2650-2661` 汇总该错误。
- 0.2.28 的 `Touch_ST7123.cpp` 与 master 的 `getTouchRaw()` 函数体逐字相同，
  “0.2.28 已存在、0.3.0 未修”成立。
- `_read_fw_info()`（`:47-71`）只在三次读取都成功时进入全零判断；失败路径直接落到
  `return true`。
- host 复现输出见 [evidence/get-touchraw-output.txt](evidence/get-touchraw-output.txt)
  与 [evidence/fw-info-output.txt](evidence/fw-info-output.txt)。

## 文件

- [report.md](report.md)：代码事实、复现结果表、补丁评估与未覆盖项
- [run.json](run.json)：结构化状态
- [code/get_touchraw_check.cpp](code/get_touchraw_check.cpp)：`getTouchRaw()` host 复现
- [code/fw_info_check.cpp](code/fw_info_check.cpp)：`_read_fw_info()` 返回值检查
- [code/README.md](code/README.md)：构建方法
- [evidence/source-pins.json](evidence/source-pins.json)：固定 commit、文件 SHA256

## 未覆盖项

物理 Tab5 上的 I2C 失败注入与长时间观测、esp-emulator/QEMU 虚拟设备复现、完整
M5GFX/固件编译、面板实机触摸回归、补丁对 #418 鬼触点的影响，均为 `NOT RUN` 或不在
本轮范围。未修改 M5GFX，未向上游 push 代码，未关闭 issue。
