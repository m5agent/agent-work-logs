# StackChan #110 v1.6.2 扫描策略复核报告

## 背景

Issue #110 报告：在多 AP 广播同一 SSID（mesh）的网络中，StackChan 配网阶段可以关联，
但始终拿不到 IP；根因判定为 `wifi_config.sta.scan_method` 停留在 esp-idf 默认的
`WIFI_FAST_SCAN`，会选中最早应答的 AP 而不是信号最强的 AP。

维护者于 2026-10-29 确认该判断，并说明「仅在多 AP 网络实测通过后才关闭」；
2026-11-04 发布 v1.6.2，请报告者在同一 mesh 网络复测。

## 本次复核目标

在无法接触多 AP 硬件的前提下，确认 v1.6.2 是否真的包含建议的扫描策略改动，
并界定 issue 可以推进到哪一步。

## 执行环境

- 操作系统：macOS（本机）
- 方式：GitHub API 读取固定提交的文件内容，逐行比对
- 工具链：无 ESP-IDF，无 StackChan 源代码检出

## 事实

### 1. 扫描策略已设置

`0808a479` 中 `firmware/main/hal/utils/wifi_connect/wifi_station.cc`：

```c
void StackChanWifiStation::connectCurrent()
{
    ...
    config.sta.scan_method = WIFI_ALL_CHANNEL_SCAN;   // line 79
    config.sta.sort_method = WIFI_CONNECT_AP_BY_SIGNAL; // line 80
    auto error = esp_wifi_set_config(WIFI_IF_STA, &config);
```

该提交在此文件的 diff 为 +3/−1，新增的正是上面两行。

### 2. 超时分类已存在

同一版本 `Poll()` 中：

```c
expired = is_connecting_ && esp_timer_get_time() - connection_started_at_ >= 30000000;
...
if (associated) {
    fail(WifiConnectionFailure{"dhcp_timeout",
        "Connected to the router, but no IP address was assigned. ..."});
} else {
    fail(WifiConnectionFailure{"connection_timeout", "..."});
}
```

即「已关联但无 IP」会归入 `dhcp_timeout`，最迟 30 s 结束等待。

### 3. 断连原因已映射

```c
station->fail(wifiDisconnectFailure(event ? event->reason : 0, band));
```

### 4. 重试次数未变

`#define MAX_RECONNECT_COUNT 1`，与维护者「增加重试不能解决已关联但无 IP」的判断一致。

## 结论与边界

v1.6.2 包含所建议的扫描策略改动，这一点是源码级事实（`code-level verification`）。
但「改动是否让 mesh 场景拿到 IP」需要多 AP 网络与实机，本次 `NOT RUN`，
因此不构成关闭 #110 的依据；按维护者设定的验收标准保持 OPEN。

## 风险与回滚

本次为只读复核，未改动任何仓库，无回滚动作。

## 未覆盖项

- 多 AP mesh 下的 DHCP 结果；
- v1.6.2 的编译与烧录；
- App 侧对 `dhcp_timeout` 之外的错误呈现。
