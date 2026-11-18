# CoreMatrix C61 浏览器原版内存路径

## 执行

使用本地导出页面和 Chromium 启动 CoreMatrix（ESP32-C61）。上传官方 UIFlow2 v2.5.4 原版，核对 16,773,120 字节原文件和填充至 16,777,216 字节的执行 Flash。浏览器运行时绑定 C61 源码及 JavaScript、Worker、WASM、ROM 和站点清单的完整摘要。启动串口出现 v2.5.4、CoreMatrix 和 MicroPython 提示符。16×16 的共享 RGB565 帧与页面渲染的 256 个像素一致。独立解码得到 36 个非黑像素。

保持同一原版会话，在页面的 Python 编辑器执行试验代码，经来宾 USB Raw REPL 返回结果。先查询 `esp32.idf_heap_info(esp32.HEAP_DATA)` 及 `MALLOC_CAP_SPIRAM`（掩码 1024），再分别尝试分配 32 KiB 和 1 MiB 普通 `bytearray`。32 KiB 每隔 4096 字节写读一个位置并核查最后一个字节，共 8 个采样页。实验后重读原启动帧的哈希与会话身份。独立的浏览器 Worker 观察覆盖终止过程。

## 结果

| 验证项 | 结果 | 实测 |
| --- | --- | --- |
| 原版启动与页面 REPL 输入 | PASS | 初始 36 像素图案，同一来宾执行并回读 |
| 普通内存 32 KiB | PASS | 8 个采样页和末字节一致，错误为 0 |
| 普通内存 1 MiB | MemoryError | 分配未完成 |
| SPI RAM | NOT VALIDATED | 外部能力查询返回 `[]`，无可选 SPI RAM 堆区 |
| 浏览器退出 | PASS | 共观察到 5 个 Worker，退出后活跃为 0，iframe 移除 |

`HEAP_DATA` 查询返回两个区域，所报告的总容量之和为 179,624 字节。该值对应来宾可见的堆区，无法据此确定整机 RAM 容量。普通 1 MiB 分配异常与外部能力查询是两项独立观测，当前记录没有确立缺少外部堆区的原因。[MicroPython esp32 堆查询](https://docs.micropython.org/en/latest/library/esp32.html#esp32.idf_heap_info) · [Espressif C61 能力分配](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c61/api-reference/system/mem_alloc.html)

CoreMatrix C158 官方规格标注 8 MB PSRAM。本轮该容量和数据路径仍为 `NOT VALIDATED`，保留实际空查询和异常。执行范围为本地导出浏览器，当前托管页、原生 Device Service、真机和板上按键未执行。[M5Stack CoreMatrix 规格](https://docs.m5stack.com/zh_CN/core/CoreMatrix)

[前次同板浏览器验证](../../README.md) · [本次脱敏证据](evidence/corematrix-stock-browser-memory.summary.json)
