# 复现入口

从 [执行源码 f2f26604](https://github.com/m5agent/m5stack-esp-emulator/tree/f2f26604a5e8c8df898aa5ba2354364e6f1911d5) 使用 scripts/bootstrap-unit-runtime.py 和原生 Xtensa 源树，按锁定顺序应用 0203 和 0204。以匹配 ROM 和给定 runtime 启动独立 Device Service。按证据中的 SHA 上传固件，用相应 Cardputer 或 Cardputer ADV 配置创建原生 QEMU 会话，经 frame.png、serial 和 input 验证，先导出 evidence ZIP，再以 purge=0 停止。M5Apps 用原版验证默认空闲后 A 唤醒和 Enter 进入主菜单。

对控制器补充运行 tests/firmware/esp32s3_cache_occupy/run_qtest.py 与 tests/firmware/stickc_plus2_bt_lp_clock/check_gpio_lcd_readback.py。按 [应用与帧摘要](../evidence/combined-targeted-summary.json) 的检查与精确产物复验。完整原生矩阵入口是 tests/uiflow2/run_peripheral_matrix.py，执行时绑定 Xtensa 与 C6 及 ROM、固件和源码。
