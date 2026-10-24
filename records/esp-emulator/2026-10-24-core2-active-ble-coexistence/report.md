# Core2 active BLE + WiFi/公网两分钟共存报告

## 背景

已有 Core2 `2×120s` hold 中，GATT 首次交换完成后外部 peer 关闭，guest
继续发 HCI command，TX queue 最终填满。它证明 teardown 后不 panic，但不
证明 BLE 链路在 120 秒内一直 active。

本轮在 Device Service 的 unified network 配置中增加：

```text
network.ble_linger_seconds: 0..600
```

Core2 runner 自动设置为 `max(20, hold_seconds + 60)`，让 peer 在 hold 期间
保持连接。

## 执行

输入：

- firmware SHA256：
  `b9c91c40e60867186717938e075da8b19271cc8e7a22323524be213beff81982`；
- ELF SHA256：
  `5bec056bb775bcc94bc020e4fa411def097ea17b108dcd597d9cdab3c347db49`；
- QEMU SHA256：
  `667ec84c9e53ce73b0e63c7be69284837ff00b77a9194577ef757c164e8e31a1`；
- `ble_linger_seconds=180`；
- 2 个独立 lease，每轮 hold 120 秒。

结果：

- `2/2 PASS`；
- frame SHA256 两轮一致：
  `5bfcdf8fc518a36385783a9b5bf09b3fbce9d8c07406326955569f6c7db8408b`；
- 每轮 34 QOM nodes；
- WiFi DHCP/受控 HTTP、公网 DNS/HTTP、NUS GATT、pcap 和 evidence PASS；
- 每轮 47/47 HLI posts/consumed、38 C2H events、9 ACLs；
- `hli-errors=0`、HLI/meta queue=0、TX queue=0、`last-error=0`；
- `peer-closed=0`；
- `gdb_bridge=false`。

## 验证

```text
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
Ran 299 tests in 9.788s
OK

runtime coverage  PASS
peripheral catalog PASS
QEMU profiles      PASS
compileall         PASS
Ruff changed files PASS
Node 2/2           PASS
git diff --check   PASS
```

GitHub Actions `40064909368` 两个 job 全部 success。

## 边界

- active BLE 由 Bumble controller/peer 提供；
- 不证明 bit-exact controller/baseband、物理 cache/PSRAM、RF、功耗或硬件；
- 同 guest peer 断开后再次连接仍未覆盖；
- 两分钟 active 共存不等于多小时 soak；
- 完整 67-case 外设矩阵本轮未重跑。

## 回滚

回滚源码提交 `4e055979c908d40d6c2ca31b78f3711599e90919` 可移除 linger
参数、active-BLE evidence 和文档；不会修改固件、QEMU build 或硬件。
