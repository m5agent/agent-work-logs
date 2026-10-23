# ESP Emulator DHCP Lease Renewal 报告

## 背景

已有 reconnect probe 证明 guest `WLAN.disconnect()` 加 QMP link down/up 后
可以重新关联和重新 DHCP；它不等同于 DHCP lease renewal。待审固件还缺少
不重启 guest、保留当前地址并发送 renewal REQUEST/ACK 的可验证路径。

## 实现

新增 `tests/network/idf_dhcp_renewal/`：

- ESP-IDF 5.5.4、ESP32-S3、2 MiB app image；
- 加入 QEMU OpenMAC `myssid` AP；
- 等待初始 `IP_EVENT_STA_GOT_IP`；
- 从 `esp_netif` 取得 lwIP `struct netif *` 和 `struct dhcp *`；
- 调用 `netifapi_dhcp_renew()`；
- 记录 initial/renew xid、lease、T1、T2 和 supplied state；
- renewal 后连接 controlled HTTP `10.0.2.2:18080`；
- 通过 Device Service 上传 normalized image、运行、停止并采集 pcap。

`pcap_summary.py` 同时扩展为无 payload 的 DHCP lifecycle 分析：

- message type：DISCOVER/OFFER/REQUEST/DECLINE/ACK/NAK/RELEASE/INFORM；
- transaction id；
- requested IP、server ID、lease、T1、T2；
- initial selecting request；
- renewal request；
- 与 renewal transaction 关联的 ACK；
- 最多 64 个 bounded transactions。

## 验证

```text
platform tests                 235/235 PASS
runtime coverage               PASS
peripheral catalog             PASS
QEMU profiles                  PASS
FirmwareManifest               PASS
pcap decoder tests             PASS
changed Python ruff            PASS
git diff --check               PASS
```

Guest serial：

```text
DHCP_RENEW_INITIAL: supplied=1 xid=00000001 lease=86400 t1=43200 t2=75600
DHCP_RENEW_SENT: err=0 xid=00000001
DHCP_RENEW_AFTER: supplied=1 xid=00000001 lease=86400 t1=43200 t2=75600
DHCP_RENEW_HTTP: PASSED HTTP/1.0 200 OK
DHCP_RENEW_RESULT: PASSED
```

Pcap：

```text
message sequence  DISCOVER, OFFER, REQUEST, ACK, REQUEST, ACK
renewal requests  1
renewal ACKs      1
lease seconds     86400
guest address     10.0.2.15
transaction       renewal=true
```

源码 `main` 已推送：

```text
base    e14169f4c49d8651444b987172b0ab0135a93e11
result  71ab6ef95094b9bfe89ab364035c940f9e14c893
```

## 验证边界

- 这是 virtual-device DHCP 行为，不是物理 AP/radio 或 RF 验证；
- 没有移除实际虚拟 AP/radio；
- 没有验证地址重分配、WPA2/WPA3 或隐藏 SSID；
- 未重跑 67-case UIFlow2 矩阵，因为本次修改 pcap parser 和网络测试；
- 物理硬件仍为 `NOT RUN`。

## 风险与回滚

probe 依赖 ESP-IDF 5.5.4 的 lwIP `netifapi_dhcp_renew()` API，并通过
Device Service 运行。build 输出和 firmware 二进制不提交。

回滚源码提交 `71ab6ef95094b9bfe89ab364035c940f9e14c893`
会移除 DHCP renewal probe 和 pcap lifecycle 字段；不会修改已保存的其他
session firmware 或设备数据面。
