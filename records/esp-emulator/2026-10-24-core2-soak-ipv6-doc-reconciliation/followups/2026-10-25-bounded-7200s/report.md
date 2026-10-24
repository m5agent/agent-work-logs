# ESP Emulator Core2 bounded 7200-second soak report

## 背景

旧 artifact-bound 两小时 active-BLE hold 功能 PASS，但 QEMU host RSS 增长
`458016 KiB`。后续 macOS `vmmap` 将增长归因到未限容 TCG translation
buffer。Core2 所有路径改用 `tcg,thread=single,tb-size=128` 后，120 秒复测
稳定，最终两小时门禁仍待执行。

## 执行

使用隔离的 Device Service 与固定 CLI 环境启动单次 7200 秒 lease：

```text
profile=core2-native-hci
runtime=qemu-unified
hold-seconds=7200
attempts=1
accelerator=tcg,thread=single,tb-size=128
icount=shift=auto,align=off,sleep=off
```

runner 在首 lease 前冻结：

- firmware SHA256；
- ELF SHA256；
- QEMU SHA256；
- runner、Device Service、QEMU accelerator 和 BLE runtime limits 工具 SHA256。

运行期重新计算资产哈希，差异为空。

## 结果

```text
status=PASS
gate_result=PASS
input_assets_unchanged_during_run=true
input_asset_drift={}
attempts_passed=1/1
hold state=running
```

功能/数据面：

- frame 3710 bytes；
- QOM 34 nodes；
- WiFi DHCP + controlled HTTP；
- public DNS + HTTP；
- external NUS GATT + notification；
- active peer at end of hold；
- pcap 71967 bytes；
- evidence ZIP 56203 bytes；
- cleanup error null、panic count 0。

HLI：

```text
hli-posts=45
hli-consumed=45
hli-errors=0
hli-c2h-events=36
hli-c2h-acls=9
queues=0
dropped=0
last-error=0
peer-closed=0
```

资源：

```text
state polls=1436
samples=240
RSS start/end=323536/252992 KiB
RSS min/max=147136/323808 KiB
phys start/end=250880/188416 KiB
phys min/max=187392/256000 KiB
```

## 验证边界

- PASS 只证明该固件 SHA、`core2-native-hci` profile、`tb-size=128` 和单
  lease 7200 秒窗口的 host-memory 行为。
- 不证明物理 cache/PSRAM 时序、TCP/BLE 吞吐、并发多 lease、bit-exact
  controller/baseband、RF 或真机。
- 服务 session 最终为 stopped，QEMU PID 已消失。

## 回滚

回退源码提交
`aa656c029697940f805442ab37f578edc73485b2`。
