# ESP Emulator A/AAAA resolver 与固件 capability intake

- 日期：`2026-10-24`
- 结果：`PASS`
- 工作类型：`code_change`
- 问题来源：P0 网络 DNS/egress 与通用固件 capability 审查持续任务
- 源码版本：`m5agent/m5stack-esp-emulator @ ee335da6b11c9dbd30c7342426c712e1885c43b8`
- 环境：macOS 平台测试主机；GitHub Actions `ubuntu-latest`

## 结论

三个独立 milestone 已交付：

1. `fb16f26`：Device Service 对 IPv6 egress endpoint 预检 IPv6
   forwarding；controlled resolver 支持 exact A/AAAA，非法、未指定、组播、
   空列表和超限记录 fail-closed。
2. `dadfc96`：FirmwareManifest API 和 WebBurner 可声明
   required/optional capabilities；别名归一化、上限、非法输入和
   `camera`-on-StickS3 mismatch 均有结构化响应。
3. `ee335da`：包内 `sdkconfig` 的 WiFi/Bluetooth/PSRAM 构建开关写入
   `capabilities.detected`；目标 profile 缺失时只产生 warning，不把编译
   开关自动提升为 required。

最终平台测试 `340/340 PASS`，Node 浏览器上传测试 `2/2 PASS`，三个对应
CI run 均成功。

## 关键证据

- A/AAAA resolver：UDP A/AAAA response type/payload、NXDOMAIN 和非法记录
  拒绝 PASS。
- WebBurner/API：成功导入规范化 `screen→display`，`camera` on StickS3
  返回 `409 unsupported_firmware_capability`，非数组返回 `400
  invalid_capability_requirements`。
- sdkconfig：Cardputer-ADV 的 PSRAM detected warning 不改变 manifest PASS，
  也不产生 validation error。
- `NET-06` 仍开放：同一 ESP firmware guest 的 AAAA + IPv6 HTTP 尚未执行。

## 文件

- `report.md`：改动、执行与验证边界。
- `run.json`：机器可读记录。
- `evidence/summary.json`：脱敏的 milestone 和 CI 摘要。
- `patches/`、`code/`：不适用；代码和测试位于公开源码仓库。

## 未覆盖项

- 同 guest firmware IPv6 DNS/TCP/HTTP；
- 物理网络、RF 和公网 IPv6；
- capability 声明与实际代码路径的一一映射；
- capability mismatch 的真机外设验证。
