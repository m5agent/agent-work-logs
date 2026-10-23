# ESP Emulator Core2 unified WiFi + stock native-VHCI BLE

- 日期：`2026-10-23`
- 结果：`PASS`
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`7823befc2cee622e6b086287f5ae903fda839885`
- 基线版本：`1546798de9db5df52e3045527281c2a8d01dcc4d`
- 环境：macOS Apple Silicon；QEMU `m5core2`；Bumble controller/peer

## 结论

stock Core2 UIFlow2 现在可以在同一 QEMU guest 中同时完成：

- 320x240 board/display/touch；
- AXP2101/INA3221/MPU6886/RTC QOM 注入与读取；
- 扬声器 PCM 和麦克风 PCM；
- OpenMAC WiFi/DHCP；
- 受控 HTTP 和公网 IPv4 DNS/HTTP；
- stock native-VHCI BLE 到外部 Bumble NUS GATT；
- 非黑 frame、touch 后画面变化。

扩展后的 `unified_core2` runner 连续 `3/3 PASS`。

## 关键修复

classic ESP32 BB idle page `0x3ff5d000` 原先作为未实现区域返回
`0xffffffff`，使 `phy_force_wifi_chan()` 看到假的 hardware-busy 状态。
新增 QEMU patch 将该 idle 区域改为 zero-valued readback，WiFi/BLE coexist
路径才能完成。

同时修复 GDB bridge 在 Wi-Fi 并发负载下执行 guest callback 时可能命中
nested breakpoint 的问题：注入窗口内临时禁用 breakpoint，完成后恢复。

## 验证

```text
native-VHCI unified     3/3 PASS
platform tests          213/213 PASS
Core2 peripheral        6/6 PASS（此前基线）
Core2 device frame      1/1 PASS（此前基线）
runtime coverage        PASS
peripheral catalog      PASS
QEMU profiles           PASS
physical hardware       NOT RUN
```

## 边界

- 仍是 standalone GDB bridge，尚未进入 Device Service `/api/v1` lease；
- Bumble 替代 Espressif controller 执行 controller 侧语义；
- bit-exact BT baseband/controller、RF、共存、配对/安全、吞吐和真机仍
  `NOT RUN`。

## 文件

- `report.md`
- `run.json`
- `evidence/verification.summary.json`
