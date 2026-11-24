# review-sta 便携网络审查

## 改动

- 模拟器 [m5stack-esp-emulator](https://github.com/m5agent/m5stack-esp-emulator) main `c5175868f2a798ec828f6a4bf38279d84bd2f2c0`
  （PR #237、#239）：新增 `qemu-wifi` 的 `review-sta` profile。来宾 Wi-Fi 网卡接每会话 UNIX socketpair，
  对端只为 `10.0.2.2` 应答 DHCP、DNS、HTTP、TCP、UDP 与 MQTT，不打开宿主 IP 端口，不需要 Linux
  网络命名空间。`/network` 返回 `PASS/FAIL/PARTIAL/NOT_USED`、固定失败码、事件、断言与 pcap
  隔离结论；`/devices/{id}/network-capabilities` 公布 8 款板卡，Tab5 为 `unsupported`。
- 审查服务 main `3ce2fe1`（OpenAPI 0.33.0）：声明网络功能的固件在板卡公布 `review_sta` 时优先使用该
  路径，不再检查 worker 的 Linux 命名空间；`FAIL` 记 `E_NETWORK_FAILED`，无网络尝试记
  `E_NETWORK_NO_ACTIVITY`，`unsupported` 记为能力边界 `NOT VERIFIED`。精确原版夹具保留原 profile。

## 验收

| 层级 | 结果 | 依据 |
| --- | --- | --- |
| build | PASS | 控制固件 ESP-IDF v5.5.4，镜像源码哈希与提交一致 |
| transport / device_response | PASS | 8 板 known-good PASS、错误口令 FAIL `wifi_auth_failed`、离线 NOT_USED、按住 B 的 setup PASS 与不输入 PARTIAL；`matrix3` `32/32`，32 个最终 pcap 隔离 PASS |
| data_behavior | PARTIAL | 隔离审查服务复跑 14 条当前网络任务，全部进入 `review-sta`，无 `worker_namespace_unavailable` / `board_not_advertised`；75 秒窗口内无固件发出 probe request，判 `PARTIAL no_network_activity` |
| delivery | PASS | 两仓 main 已合并；常驻 18853、8787、8790 已切换并回读 |

复审中 Monster 首次判 `FAIL host_egress_denied`，原因是其自建热点 `192.168.4.1` 的 mDNS 组播被
当作外发。已改为只统计站点单播外发，修正后同一抓包重新计算为 `PARTIAL`，控制矩阵重跑保持一致。

## 上线

- 新发布目录由 `a4343d86d` 发布目录 APFS 克隆，覆盖 57 个变更源码文件；原生 QEMU、C6、Tab5、
  浏览器站点资产不变（`qemu-system-xtensa` `04abc3ba…`）。
- 审查执行端 18853：`run.sh` 指向新发布并由 launchd 重启；保留 100 条历史会话。
- 工作台 8787：参数、状态目录与浏览器站点不变，只换发布路径；保留 46 条会话。
- 审查服务 8790：`3ce2fe1` 加原有常驻识别补丁（88 行，干净叠加）；233 条历史任务保留。
  叠加补丁后的两项 `test_review_claims` 差异与切换前相同。
- 上线后生产 dry-run `job-f63ed14dd63b`（Bruce CN 快照，未提交）走 `review-sta`，
  `PARTIAL no_network_activity`，pcap 隔离 PASS。Burner 提交为 0。

## 剩余

- 这批应用需要在界面内先配置 Wi-Fi，才会发起连接。要得到 PASS/FAIL，需按应用补保存快照的
  配网输入（键盘或按键序列）。
- StopWatch `job-687de4ba2337` 走固定 Linux STA 通道，未重跑。
- Core2 触摸条、Cardputer 键盘、PaperS3 触摸的 setup 对照；WPA3、真实 TLS、物理 RF 与浏览器 WASM：`NOT RUN`。

## 回滚

恢复 `run.sh.bak.20261124T071657Z` 与 `backups/app.py.20261124T071830Z`，删除
`review_sta_network.py`，按上一发布目录重新启动 8787。
