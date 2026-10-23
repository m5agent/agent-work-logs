# Public network evidence summary

Raw serial logs containing QEMU-private network addresses are intentionally not
copied. This summary preserves the validation markers and values.

## Device-side public request

```text
APP WIFI_CONNECTED <guest DHCP address>
APP DNS_OK api.open-meteo.com <public DNS mapping>
APP HTTP 200 783
APP WEATHER_OK Shenzhen temp=31.0 hum=39 code=0
APP READY Shenzhen
```

Device Service checks:

```text
status: PASS
marker:1 through marker:5: true
```

## Host-side comparison

```text
endpoint: https://api.open-meteo.com/v1/forecast
temperature_2m: 30.8
relative_humidity_2m: 39
weather_code: 0
```

The small temperature difference is consistent with the API update interval.

## NTP server probe

```text
ntp.aliyun.com   UDP/123 timeout
ntp.tencent.com  UDP/123 timeout
pool.ntp.org     valid 48-byte SNTP response
time.google.com  UDP/123 timeout
```

LWIP default:

```text
SNTP_RECV_TIMEOUT=15000 ms
```

CYBER CLOCK waiting window:

```text
NTP_RETRIES=20
NTP_RETRY_MS=250
total=5000 ms
```
