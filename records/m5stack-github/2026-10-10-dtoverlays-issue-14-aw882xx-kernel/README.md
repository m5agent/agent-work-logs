# m5stack-linux-dtoverlays #14: aw882xx on Linux 6.13+

- 日期：`2026-10-10`
- 结果：`PARTIAL`（6.12/6.14 构建 PASS；未执行 insmod/音频运行时验证）
- 工作类型：`issue` + `code_change`
- 问题来源：https://github.com/m5stack/m5stack-linux-dtoverlays/issues/14
- PR：https://github.com/m5stack/m5stack-linux-dtoverlays/pull/15
- 源码版本：`m5stack/m5stack-linux-dtoverlays@75518549a2640486f5d13ea72ca4935b198d7c20`
- 环境：Docker arm64；Debian 6.12.111 和 Ubuntu 6.14.0 kernel headers

## 结论

Linux 6.13 起 `MODULE_IMPORT_NS` 需要字符串字面量；同时从旧内核到 6.14 还涉及
`strlcpy`、`GPIOF_DIR_IN`、`devm_gpio_free` 和 i2c `probe`/`remove` 签名变化。
补丁按内核版本保留兼容分支，并在 6.12.111 与 6.14.0 headers 上完成模块构建。

本记录未执行 `insmod` 或音频播放，因此运行时行为仍是 `NOT RUN`。

## 关键证据

- `evidence/build-summary.txt`：6.14 上的原始报错、修复后的 6.12/6.14 构建结果。
- `patches/0001-aw882xx-support-linux-6.13-and-newer.patch`：模块兼容修复。

## 文件

- `report.md`：完整报告
- `run.json`：结构化记录
- `evidence/`：构建摘要
- `patches/`：修复 patch

## 未覆盖项

- 未在目标 Linux 设备上加载 `aw882xx_drv.ko`。
- 未播放音频或验证 codec probe、DSP、GPIO 中断路径。
- 7.x 内核上还有 `linux/of_gpio.h` 移除等独立兼容问题，本记录不宣称支持 7.x。
