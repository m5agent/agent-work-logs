# Cardputer-Adv CC1101 Cap 双来宾验证

- 日期 `2026-11-25`
- 结果 `PARTIAL`。私有 WASM 双来宾行为验证 `PASS`，正式发布构建与工作台入口 `NOT RUN`
- 工作类型 `issue`
- 问题 [m5stack-esp-emulator #247](https://github.com/m5agent/m5stack-esp-emulator/issues/247)
- 源码 [模拟器基线 915faa6bf9882579e10668c315a5f8e74b2491af](https://github.com/m5agent/m5stack-esp-emulator/tree/915faa6bf9882579e10668c315a5f8e74b2491af)
- 环境 桌面 Chromium、静态导出的浏览器 QEMU-WASM、两台独立 Cardputer-Adv 虚拟设备、UIFlow2 v2.5.3

## 结果

发端的原例程通过实际 SPI TX FIFO 送出 `CC1101, SEQ=0, Hello`。验证脚本把同一 21 字节帧交给进入 SRX 的收端。收端产生一次 GDO0 完成通知，原驱动从 SPI RX FIFO 读取 23 字节并报告 `RX=1 CRC=0`，收到的有效载荷逐字节匹配。在对端送入帧之前，接收、通知与 FIFO 读取计数均为零。两台来宾各退出 0，共 12 个 Worker 在浏览器上下文关闭前回收。

执行镜像 SHA-256 为 `b6255f6af5ad10236380eae09a76b44ca174b5c4de391aef16413bdc590952bd`，候选 WASM 为 `4bcb05893348b37877858b729a85d15f72bf5734ded099b0e4c3ff1cef2cf183`。验收层级为浏览器虚拟设备。物理 RF、正式发布构建及 UI 配对入口未经验证。

## 文件

- [完整报告和复现步骤](report.md)
- [机器可读运行记录](run.json)
- [双来宾脱敏证据和原始文件哈希](evidence/cc1101-dual-guest-summary.json)

- [精确预览补丁、浏览器差异与复现脚本](code/README.md)

原始报告、页面截图和私有构建保存在独立测试目录。该记录附带摘要和哈希。
