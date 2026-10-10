# UIFlow MicroPython #117 RTC UTC 同步报告

## 背景

- 来源：m5stack/uiflow-micropython issue #117
- 现象：TZ 为 `JST+9` 时，每次 `M5.begin()`/重启后 RTC 和系统时间增加 9 小时。
- 目标：确认 RTC IC 始终保存 UTC，重复启动不再漂移。

## 结论

- 状态：`PASS`（host 复现、固件构建、StopWatch 实机复现与修复验证、原镜像恢复）
- 根因：`rtc_sync()` 使用 `localtime_r()` 写 RTC，而 `setSystemTimeFromRtc()`
  按 UTC 读取。两次转换之间累计时区偏移。
- 改动范围：`rtc_sync()` 改用 `gmtime_r()`；调用点和接口不变。

## 证据

### 代码或配置

```diff
-    localtime_r(&tv.tv_sec, &now);
+    gmtime_r(&tv.tv_sec, &now);
@@
-    // get local time and sync to RTC IC
+    // get UTC time and sync to RTC IC
```

### 执行

- 构建环境：ESP-IDF v5.5.4（Docker arm64）。
- 实机：StopWatch + RX8130；测试固件为 UART-REPL 构建，TZ 设置为 `JST+9`。
- 基线：
  - 写入 11:15:00 UTC 后，RX8130 为 `00 15 11 ...`；
  - `M5.begin()` 后变为 `00 15 20 ...`，即 20:15 本地时间（UTC+9）。
- 修复后：
  - 写入 04:11:15 UTC 后，RX8130 为 `15 11 04 ...`；
  - 第一次和第二次 `M5.begin()` 后系统时间与 RX8130 都保持 `04:11:15 UTC`。
- 恢复：
  - 重新烧录原 Wi-Fi 镜像，flash task PASS；
  - REPL probe 返回 `not_micropython`（符合 stock UART-REPL 关闭状态）；
  - `read_flash` 0x10000 前 160 字节 SHA256 与原始 artifact 一致；
  - reset task PASS。

详细命令输出已脱敏汇总到 `evidence/`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | StamPLC 和 StopWatch UART-REPL 构建完成 |
| flash | PASS | 基线、修复应用和恢复镜像的 flash task 均 passed |
| transport | PASS | UART-REPL probe 成功；`repl_exec` 返回预期 stdout |
| device_response | PASS | RX8130 寄存器在修复前后行为不同且符合 UTC 预期 |
| data_behavior | PASS | 修复后两次 `M5.begin()` 时钟不漂移 |
| visual_or_physical | NOT RUN | 本测试不依赖显示或机械行为 |

## 验证边界

StamPLC 本体不可用，使用 StopWatch 验证同一 M5.Rtc / `rtc_sync()` 代码路径。
StopWatch 的 RX8130 与 issue 中的 StamPLC RTC IC 相同；issue 描述的根因位于
板级无关的 `M5.begin()` 路径。未做长期电池保持测试。

## 风险与回滚

RTC 写策略从本地时间改为 UTC，与 M5Unified 的读侧和 `machine.RTC().datetime()` 一致。
如发现兼容性问题，可回滚为 `localtime_r()`；但这会重新引入每次启动漂移。硬件测试后已
恢复原 StopWatch Wi-Fi 镜像。
