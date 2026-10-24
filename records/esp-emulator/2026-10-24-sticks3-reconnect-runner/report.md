# StickS3 自动 radio 断线与重连回归报告

## 背景

网络 P0 已有一次手工 Device Service radio loss/recovery evidence，但缺少可从
公开 base 一站重建镜像、启动临时 service、在正确 guest marker 注入 QOM
radio fault、停止并验证 pcap 的自动化入口。

本轮新增 `tests/network/reconnect_probe/run_test.py`，不改变 guest probe
语义，只把现有 12/12 手工流程收敛为可复现 runner。

## 实现

runner 的默认路径：

1. 用公开 StickS3 UIFlow2 base 和 `build-M5STACK_StickS3-unified` 生成
   unified image；
2. 将 `tests/network/reconnect_probe` 的 `boot.py/main.py` 写入同一镜像的
   user LittleFS；
3. 选择空闲端口启动 disposable Device Service；
4. 上传 merged image，创建 `runtime=qemu-wifi`、
   `profile=uiflow2-sticks3-wifi` session；
5. 轮询 serial，在 `RECONNECT DISCONNECTED` 后执行
   `network-fault down target=radio`；
6. 在 `RADIO_DOWN_SCAN` 后执行 `network-fault up target=radio`；
7. 等待 `RECONNECT RESULT: PASSED`，然后 `purge=0` 停止；
8. 解析 network pcap summary，并将脱敏 evidence 写入输出目录。

构建子进程显式继承 `.work/py` PYTHONPATH，避免环境依赖 hidden state。

## 执行

```text
python3 tests/network/reconnect_probe/run_test.py \
  --out-dir /tmp/m5-reconnect-probe
```

本次实际输出：

```text
status=PASS firmware_sha256=3acf13906c1909e564639b7883583a3dba791905326eef71b7c28d7d066a1c8f pcap_bytes=9586
```

固件 SHA256：
`3acf13906c1909e564639b7883583a3dba791905326eef71b7c28d7d066a1c8f`

QEMU SHA256：
`667ec84c9e53ce73b0e63c7be69284837ff00b77a9194577ef757c164e8e31a1`

## 检查

| 检查 | 结果 |
| --- | --- |
| initial scan non-empty | PASS |
| first DHCP | PASS |
| `/before` HTTP 200 | PASS |
| radio down response | PASS |
| QOM radio false | PASS |
| scan while radio down = 0 | PASS |
| radio up response | PASS |
| QOM radio true | PASS |
| restored scan non-empty | PASS |
| second DHCP | PASS |
| `/after` HTTP 200 | PASS |
| final guest marker | PASS |
| pcap summary | PASS |
| two DHCP DORA exchanges | PASS |
| two controlled HTTP flows | PASS |
| stable guest address | PASS |

pcap DHCP txn：
`DISCOVER, OFFER, REQUEST, ACK, DISCOVER, OFFER, REQUEST, ACK`。

## 验证

```text
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
Ran 299 tests in 9.843s
OK

runtime coverage  PASS
peripheral catalog PASS
QEMU profiles      PASS
compileall         PASS
Ruff               PASS
Node 2/2           PASS
git diff --check   PASS
```

GitHub Actions `40064309448` 两个 job 全部 success。

## 边界

- guest 和 AP 都在 QEMU WiFi 模型中，不是物理 RF；
- 不覆盖 WPA2/WPA3、hidden SSID、真实 DHCP server、不同 lease IP；
- 不覆盖硬件功率、时序和恶意固件沙箱；
- 本轮没有重跑完整 67-case 外设矩阵。

## 回滚

回滚源码提交 `5b686a976e679af2638e5b65f83c75e143582977` 可移除 runner、
evidence 和文档；不会修改 QEMU build、固件二进制或历史 evidence。
