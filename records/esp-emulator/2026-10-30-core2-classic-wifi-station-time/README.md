# M5Stack ESP Emulator Core2 classic WiFi station timing and data path

- 日期：`2026-10-30`
- 结果：`PARTIAL`（virtual-device validation）
- 工作类型：`code_change`
- 问题来源：`RUNTIME-03` classic Core2 WiFi/startup path
- 源码版本：`m5stack-esp-emulator @ 7965a01c93af1f633231e5ba1d3f2986fa080cb8`
- 交付：PR #54 已合并为 `1497c0601f405a2fe078aa061fd1b165c724962a`
- 环境：macOS arm64、QEMU 9.2.2 virtual Core2、Device Service/API and direct repository regression runners

## 结论

`0093` 将 classic ESP32 WiFi beacon、injected frame 和生成 timestamp 的
调度从 host realtime 改为 virtual time；`0094` 将 station DHCP 与双向
host data 统一放到正常 Ethernet/slirp 路径，并在收到 DHCP reply 后进入
`STA_ASSOCIATED`。Device Service 也把请求的 SSID 与认证配置同时传给
classic 与 S3 WiFi NIC。

最终 binary 的 stock Core2 UIFlow2 WiFi probe 五轮独立首启动均完成
scan、association、DHCP、IPv4 和 controlled HTTP；Core2 UIFlow2 设备组
也 `6/6 PASS`。legacy public firmware 在 WDT-off 诊断控制下稳定运行到
guest virtual `457.794095092 s` 并保持 API Key 页面；normal WDT 仍触发
`TG0WDT_SYS_RESET`，所以 `RUNTIME-03` 保持 OPEN。

## 关键证据

- Base commit：
  `0e788b7ac8795ab4d037c55e1abd379afd0f126c`
- Source commit：
  `7965a01c93af1f633231e5ba1d3f2986fa080cb8`
- Merge commit：
  `1497c0601f405a2fe078aa061fd1b165c724962a`
- Final QEMU：
  `3e61aa644074598e7b37e2cd9d4e7c1e194d2073b453f4fd9fdc5ffce62738f8`
- Stock WiFi probe：`5/5 PASS`；IPv4 `10.0.2.15`；HTTP 200
- Core2 UIFlow2 device group：`6/6 PASS`，attempts 1，retry false
- Platform suite：`1,609` run，`1,608 PASS + 1 skip`
- PR/merge CI：`4/4 PASS`

## 文件

- `report.md`：实现、执行、证据、边界和回滚
- `run.json`：机器可读记录
- `evidence/verification-summary.json`：脱敏后的检查摘要
- `patches/`：不适用；patch 已作为源码仓库文件交付
- `code/`：不适用；测试位于源码仓库

## 未覆盖项

- legacy normal-WDT stable startup、setup/REPL 和完整应用帧
- physical hardware、RF、电气、物理 cache/PSRAM timing
- WPA3、roaming、coexistence 和长期吞吐
