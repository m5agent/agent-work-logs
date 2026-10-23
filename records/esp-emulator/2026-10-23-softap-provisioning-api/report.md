# 固件 SoftAP 配网 API 实现与虚拟设备验证

## 背景

部分 ESP32 固件会在首次启动时创建自己的 WiFi SoftAP，让手机连接后访问本地配网
页面。底层 `esp-emu` 已支持模拟器作为 station 加入该热点，并通过 `hostfwd`
访问固件 TCP 服务，但 Device Service 没有暴露这项能力，正式固件审查无法通过
`/api/v1` 驱动配网页。

本次目标是补齐 API、参数校验、凭据脱敏和生命周期证据，而不是宣称已经完成真实
手机配网验收。

## 根因与缺口

1. `network.net_mode` 只接受固定 user-mode 字符串，调用方不能增加 loopback
   forward。
2. Device Service 没有传递 `--wifi-fw-ap-password`，无法加入加密的固件热点。
3. 持久化 session 只脱敏了不存在的旧字段名，实际的 `wifi_password` 会留在
   session JSON 中。
4. `runtime=network` 手动停止时直接终止 runner，最终 `evidence.json` 可能没有
   写入。

## 实现

- 新增 `network.firmware_ap_password`：
  - 空字符串表示开放热点；
  - 非空值限制为 8-63 个字符；
  - 不填写时沿用 `wifi_password`。
- 新增 `network.hostfwd`，最多 8 项：
  - `protocol` 为 `tcp` 或 `udp`；
  - host port 为 1024-65535；
  - guest port 为 1-65535；
  - host address 固定为 reviewer loopback；
  - duplicate protocol/host-port 组合拒绝。
- 运行态 session snapshot 返回规范化后的 forward 列表和 AP secret 是否配置，
  不返回 secret 内容。
- 修正 `wifi_password` 与 `firmware_ap_password` 的持久化和命令/串口脱敏。
- network runner 收到 SIGTERM 后退出运行循环、终止 guest、写最终 evidence，再退出。
- Device Service 手动停止 network session 后读取最终 evidence，并区分
  `stopped` 与真正的 lane failure。
- OpenAPI 升级到 `1.5.0`，同步 API、network lane 和后续工作文档。

## 验证环境

- 源码 base：`42edb77`
- 修复 commit：`6bcd6e88c485ec89fe70e8fa35d91282230929a0`
- Device Service：OpenAPI `1.5.0`
- Emulator：`esp-emu 0.50.0`
- 固件构建：ESP-IDF `v5.5.4`，`examples/protocols/http_server/captive_portal`
- Target：ESP32-S3
- Device profile：StickS3，`runtime=network`

该验证属于 `virtual-device validation`。它没有执行物理射频、手机 OS 或屏幕链路。

## 构建与镜像

构建命令：

```bash
idf.py -C <captive-portal-project> -B <build-dir> set-target esp32s3
idf.py -C <captive-portal-project> -B <build-dir> build
idf.py -C <captive-portal-project> -B <build-dir> merge-bin -o <merged-image>
```

结果：

- merged image：855,360 bytes；
- merged SHA256：`0fb48462902ec70a886ae0db8d06bf08b35e3ca5646fc9d690f54e3d890d66c9`；
- Device Service 补足到 8 MiB 后 SHA256：
  `35f383ffd03718c7a42e3faccdf9d97491d9286239d3b3cc462be327bf79ee9d`；
- virtual flash 校验：`PASS`。

## API 执行

创建 session 时使用：

- `runtime=network`
- `profile=generic-observe`
- `console_mode=uart0`
- 一组 AP password；
- 一项 TCP portal forward。

请求中实际凭据和 review 端口未写入本记录。结构化摘要见
`evidence/api-session-summary.json`。

## 结果

### 关联与 DHCP：PASS

串口显示 SoftAP 启动、虚拟 station 关联，并由固件内置 DHCP server 分配 lease。
脱敏后的关键标记见 `evidence/serial-markers-redacted.txt`。

### 配网页 GET：PASS

通过 loopback forward 请求配网根页面：

- HTTP status：`200`
- body size：`259` bytes
- body SHA256：
  `020854836e150511586bb17849dff5783d369c7f574260f20e93284a3d7c51f8`
- guest serial：出现 `Serve root`

只保存响应摘要，不保存固件页面正文。

### 手动停止与证据：PASS

停止 session 后：

- state：`stopped`
- network status：`PARTIAL`
- `stop_requested=true`
- `timed_out=false`
- final `evidence.json` 已写入
- session 记录的 WiFi/AP 凭据为 `<redacted>`

network status 保持 `PARTIAL` 是因为本用例没有声明自动应用 marker，也没有验证
表单 POST、NVS 和 STA 切换；这不是进程或证据保存失败。

### 自动回归：PASS

- `python3 -m unittest discover -s platform/tests -p 'test_*.py'`：176 tests passed；
- `runtime_coverage.py --check`：通过；
- `peripheral_catalog.py --check`：通过；
- OpenAPI YAML 解析：通过，version `1.5.0`。

## 结果分层

| 层级 | 结果 | 依据 |
| --- | --- | --- |
| build | PASS | ESP-IDF S3 captive portal 构建与 merge |
| flash | PASS | Device Service 8 MiB virtual image 校验 |
| transport | PASS | SoftAP 关联、DHCP、loopback TCP |
| device_response | PASS | 配网页根路径 HTTP 200 |
| data_behavior | PARTIAL | 未执行表单 POST、NVS diff、AP→STA |
| visual_or_physical | NOT RUN | network lane 无 framebuffer/input；无物理硬件 |
| review | PASS | API、文档、校验和脱敏边界一致 |
| delivery | PASS | 源码提交已推送 |

## 安全边界

- forward 固定绑定 reviewer loopback，不允许调用方绑定工作站 LAN；
- session 持久化、命令 evidence 和串口均对 WiFi/AP 凭据脱敏；
- 不可信固件仍应运行在 disposable VM 或隔离 network namespace；
- 仅观察到一次 portal 请求不能作为固件安全结论。

## 未覆盖与后续

- 自动发起 portal 探测并记录 HTTP request/response；
- POST 配网表单、失败路径、重放和输入校验；
- NVS snapshot/diff、重启持久化；
- 配网后离开 SoftAP、关联指定 STA、访问受控 endpoint；
- 虚拟手机 network namespace，以及 Android/iOS/Windows captive portal 探测；
- WPA3-SAE-only、隐藏 SSID 和企业级热点；
- 同一 guest 中 framebuffer/input 与配网页面的联合验证；
- 物理设备验证。

## 回滚

回滚 `6bcd6e8` 即可移除新增 API、脱敏修复和 network stop 证据收尾。现有调用方不传
新字段时行为不变；OpenAPI 版本号需随代码一起回退。
