# UIFlow MicroPython #116 StamPLC Wi-Fi 启动失败报告

## 背景

- 来源：m5stack/uiflow-micropython issue #116
- 现象：StamPLC 设置 `boot_option = 2` 且 `net_mode = "WIFI"` 后，等待 40 秒
  `network.WLAN(network.STA_IF).isconnected()` 仍为 `False`。
- 目标：让 `_connect_network_only()` 在 WIFI 模式下跳过 PoE 初始化并调用
  `connect_network()`。

## 结论

- 状态：`PARTIAL`（host 复现与固件构建通过；实机 Wi-Fi 未验证）
- 根因：`_connect_network_only()` 对 `M5StamPLC` 无条件执行
  `from stamplc import PoEStamPLC; lan_if = PoEStamPLC()`。没有 PoE 硬件时构造失败，
  异常在 `connect_network()` 前向上传播。
- 改动范围：仅改变 StamPLC 分支的条件；`net_mode == "ETH"` 行为不变。

## 证据

### 代码或配置

```diff
-    elif board_id == M5.BOARD.M5StamPLC:
+    elif board_id == M5.BOARD.M5StamPLC and net_mode == "ETH":
         from stamplc import PoEStamPLC

         lan_if = PoEStamPLC()
```

### 执行

- 环境：macOS arm64；Docker `uiflow-idf:v5.5.4`；ESP-IDF v5.5.4。
- host 复现：见 `evidence/host-repro.txt`。
- 构建：
  `make -j$(nproc) BOARD=M5STACK_StamPLC pack_all`
- 结果：构建 PASS；固件
  `uiflow-69846518-esp32s3-8mb-stamplc-v2.5.3-20261010.bin`，
  SHA256 `18579131e64ae20d8a291d3f9c120d1fd3d278067448b24776c0828a2c2572ec`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | ESP-IDF v5.5.4 StamPLC 构建完成并生成合并固件 |
| transport | NOT RUN | 无 StamPLC 测试节点 |
| device_response | NOT RUN | 无 StamPLC 测试节点 |
| data_behavior | NOT RUN | 未执行真机 Wi-Fi 关联 |
| review | PASS | 源码路径与 issue 根因一致 |

## 验证边界

host 复现器验证的是真实 `startup/__init__.py` 的控制流，不是 MicroPython 实机执行。
没有 StamPLC 节点，因此不能声称真机 `boot_option=2` 已恢复；补测条件为可用的 StamPLC
测试槽位。

## 风险与回滚

改动只影响 StamPLC 的 WIFI 分支。若需要回滚，恢复 `net_mode == "ETH"` 条件即可；
没有不可逆硬件操作。
