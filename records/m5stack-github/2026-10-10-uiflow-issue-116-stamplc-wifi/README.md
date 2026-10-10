# UIFlow MicroPython #116: StamPLC `boot_option=2` Wi-Fi 启动失败

- 日期：`2026-10-10`
- 结果：`PARTIAL`（host 复现 + 固件构建 PASS；无 StamPLC 实机）
- 工作类型：`issue` + `code_change`
- 问题来源：https://github.com/m5stack/uiflow-micropython/issues/116
- PR：https://github.com/m5stack/uiflow-micropython/pull/118
- 源码版本：`m5stack/uiflow-micropython@69846518a8b0893987ba0512558c4b01c9161454`
- 环境：macOS arm64 + Docker/ESP-IDF v5.5.4；host Python 复现器

## 结论

`_connect_network_only()` 原来对 StamPLC 无条件创建 `PoEStamPLC()`，即使
`net_mode == "WIFI"`。没有 PoE 模块时，该对象构造抛出
`OSError("esp_eth_driver_install failed")`，导致 `boot_option=2` 在
`connect_network()` 之前终止。修复后仅在 `net_mode == "ETH"` 时初始化 PoE。

host 复现器对真实 `startup/__init__.py` 运行通过；`M5STACK_StamPLC` 固件构建通过。
本机测试台没有 StamPLC 节点，因此未做真机 `boot_option=2` Wi-Fi 连接验证。

## 关键证据

- `evidence/host-repro.txt`：未修复版本无法到达 `connect_network()`；修复版本跳过
  `PoEStamPLC()` 并到达 Wi-Fi 连接。
- `evidence/build-summary.txt`：ESP-IDF v5.5.4 构建 PASS，固件 SHA256 已记录。
- `patches/0001-startup-skip-poe-init-for-stamplc-wifi.patch`：最小修复 patch。

## 文件

- `report.md`：完整报告
- `run.json`：结构化记录
- `evidence/`：host 复现和构建证据
- `patches/`：修复 patch

## 未覆盖项

- 没有 StamPLC 测试槽位，未执行真机 `boot_option=2`、Wi-Fi 关联或重启验证。
- 未验证接入 PoE 模块时的 ETH 路径回归；代码路径保持不变。
