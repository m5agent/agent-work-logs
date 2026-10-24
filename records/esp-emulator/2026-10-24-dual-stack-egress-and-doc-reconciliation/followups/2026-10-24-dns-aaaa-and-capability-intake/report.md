# A/AAAA resolver 与固件 capability intake 报告

## 背景

上一阶段已让 Linux exact IPv4/IPv6 egress 经过真实双栈 veth/NAT 数据面。
后续审查发现两个直接缺口：

- Device Service 请求预检只要求 IPv4 forwarding，controlled resolver 只
  返回 A record；
- FirmwareManifest 虽然支持 capability mismatch，但 API/WebBurner 没有
  字段传递 required/optional capability，因此网页导入容易始终产生空声明；
- 包的 sdkconfig 有 WiFi/Bluetooth/PSRAM 信息，但没有作为可审计的
  “detected” 证据进入 manifest。

## 改动

### IPv6 preflight 与 DNS

- Device Service 的 `egress_capability` 调用同时传入
  `require_gateway` 和 `require_ipv6`。
- `ControlledDns` 接受同一名称的 IPv4/IPv6 精确记录列表。
- A query 返回 A，AAAA query 返回 type 28 和 16-byte payload。
- 未知名称返回 NXDOMAIN；名称允许但没有对应 family record 时返回
  NOERROR_NO_A/AAAA。
- 非法 IP、unspecified、multicast、超过 8 个地址和空列表 fail-closed。
- 修正 question class 解析；非 IN class 不返回地址记录。

### WebBurner/API capability 声明

- API 接受最多 64 个 required 和 64 个 optional capability。
- capability entry 去空白、转小写、展开 aliases 并排序去重；每项最多
  64 字符。
- Web client 发送两个数组；页面增加 required/optional 输入并展示 manifest
  结果。
- `camera` on StickS3 在 manifest 阶段返回结构化 409；非法输入返回 400。

### sdkconfig capability 观察

- 高置信映射：
  - WiFi build flags → `wifi`
  - Bluetooth/Bluedroid/NimBLE flags → `ble`
  - SPIRAM flags → `psram`
- 每个 detected entry 记录 capability/source/flag。
- target profile 缺失 capability 时产生
  `detected_capability_unavailable` warning。
- detected 不自动变成 required，manifest 不因此硬拒绝。

## 执行

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
node platform/tests/test_sha256.mjs
node platform/tests/test_firmware_upload.mjs
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check
python3 -m compileall -q platform tests
```

结果：

- Platform：`340/340 PASS`。
- Node：`2/2 PASS`。
- catalog/profile/coverage/snapshot：全部 PASS。
- CI：
  - `40099406977` for `fb16f26`：PASS。
  - `40099741923` for `dadfc96`：PASS。
  - `40099959100` for `ee335da`：PASS。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compileall、平台和 Node 测试 |
| transport | `PASS` | loopback-only UDP A/AAAA resolver 数据面 |
| device_response | `PASS` | structured HTTP 400/409 capability responses |
| data_behavior | `PASS` | canonicalization、NXDOMAIN、type/payload 与 detected warning |
| visual_or_physical | `NOT RUN` | 不涉及真机 UI 或 RF |
| delivery | `PASS` | 三个源码 commit 和 CI 已推送 |

## 验证边界

- resolver 是 host/namespace 数据面，不是 ESP firmware guest IPv6。
- capability 是操作者声明或静态构建观察，不是代码路径证明。
- 本记录没有真机、RF、功耗或公网 IPv6 结论。
- Core2 两小时 soak 继续独立运行，不受本轮改动影响。

## 风险与回滚

本轮只修改 manifest/API/browser/network sandbox，没有替换运行中的 QEMU。
可按三个 commit 分别 revert：

- `fb16f26588d33c03adb97bc404c87f98aacc1bed`
- `dadfc960d6ce176d0add95848e06969ae2fe8383`
- `ee335da6b11c9dbd30c7342426c712e1885c43b8`
