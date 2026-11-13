# m5stack/StackChan #110: v1.6.2 scan policy re-check

- 日期：`2026-11-13`
- 结果：`REVIEW`（源码级复核；未编译、未烧录、未在多 AP 网络实测）
- 工作类型：`issue` + `review`
- 问题来源：https://github.com/m5stack/StackChan/issues/110
- 复核对象：`m5stack/StackChan@0808a479`（"feat(firmware): update to v1.6.2"）
- 证据等级：`code-level verification`

## 结论

v1.6.2 的固件源码同步提交 `0808a479` 已在
`firmware/main/hal/utils/wifi_connect/wifi_station.cc` 的 `connectCurrent()` 中设置：

```c
config.sta.scan_method = WIFI_ALL_CHANNEL_SCAN;
config.sta.sort_method = WIFI_CONNECT_AP_BY_SIGNAL;
```

即此前建议的「全信道扫描 + 按信号强度选择」已落地。该文件在 v1.6.2 中只有这一处改动
（+3/−1），此后无新提交再修改该文件，因此 `main` 与 v1.6.2 在该路径上一致。

同版本还有两处与本问题相关的既有行为（v1.6.0 起已在，非 v1.6.2 新增）：

- `Poll()` 30 s 连接超时；已关联但未拿到 IP 时返回 `dhcp_timeout`，不再无限停留在
  "Verifying"；
- `WIFI_EVENT_STA_DISCONNECTED` 的 reason 经 `wifiDisconnectFailure()` 映射后上报。

`MAX_RECONNECT_COUNT` 仍为 1，重试次数建议未被采纳。

## 关键证据

- `evidence/scan-policy-review.txt`：行号、片段与文件 SHA256。

## 未覆盖项

- 无多 AP / 同 SSID mesh 环境，也未持有 StackChan 实机，DHCP 是否成功未验证（`NOT RUN`）。
- 未编译 v1.6.2、未烧录、未采集串口日志。
- 未验证 App 侧对 `dhcp_timeout` 的呈现。
