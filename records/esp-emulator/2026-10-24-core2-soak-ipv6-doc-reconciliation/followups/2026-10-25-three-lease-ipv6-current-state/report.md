# ESP Emulator 三 lease Core2、guest IPv6 与当前工作总整理

## 背景

- 来源：用户要求完整整理代码和文档，说明已经做过的工作和剩余待办，并指出
  部分文档没有跟上后续验证。
- 现象：当前状态页已经记录 Core2 单 lease 121 轮和 UIFlow2 direct IPv6，
  但多个接口、专题和代码地图仍保留“还差两个 lease”“同 guest AAAA/
  denied-port 未运行”等旧结论。
- 目标：把新验证变成可追溯的当前事实，删除互相冲突的旧口径，同时保持
  `virtual-device validation` 与 `hardware validation` 的边界。

## 结论

- Core2 `3 × 121` reconnect 门禁：`PASS`，仅限 virtual-device。
- UIFlow2 test-build guest IPv6 namespace 生命周期：`PASS`，仅限测试构建。
- `NET-06`：当前 accepted virtual-device scope 已关闭。
- 文档/契约重整：`PASS`。
- 物理 cache/PSRAM、bit-exact controller、RF、吞吐/teardown 和真机：
  `NOT RUN`。

## 代码与文档改动

### IPv6 probe

- `main.py` 对 `getaddrinfo()` 返回的 sockaddr 做长度和 tuple 类型检查，
  显式使用 `AF_INET6`，地址比较忽略大小写。
- UIFlow2 test-only patch 增加 MicroPython esp32 port 的 IPv6 sockaddr tuple
  序列化，使 guest 能按四元组调用 IPv6 connect。
- Linux runner 将 libslirp guest DNS 转发目标修正为 IPv4 host socket，
  sandbox 退出等待提升到 20 秒，并动态写 evidence 日期。

### Core2 evidence

- 保留首次 readiness 预算错误和 accelerator sampling 假失败 evidence。
- 新增 3 个独立 lease 的聚合 evidence，统一绑定 firmware、ELF、QEMU、
  runner、service、accelerator 和 BLE limits 哈希。
- 聚合结论只覆盖同一已验证 UIFlow2 v2.5.3 构建；其他 Core2 固件仍要重新
  校验 hook/符号和偏移。

### 文档收敛

- README、项目状态、Backlog、工作流台账、验证账本、代码地图、Device
  Service API/OpenAPI、网络/Core2 专题、设备 catalog/profile 和自动快照
  同步。
- `workstreams.md` 删除动态 PASS 数、轮数和 RSS 数字，只保留工作流归属、
  在途工作和下一门禁；具体事实指向状态页和自动快照。
- 文档测试禁止旧的“仍差两个 121 lease”“same-guest IPv6 remains NET-06”
  和“controlled AAAA/denied-port NOT RUN”等表述重新进入当前文档。
- 设备 catalog 与 QEMU profile 由源文件重新生成，没有手工维护第二份事实。

## 执行与证据

### Core2

```text
profile=core2-native-hci
runtime=qemu-unified
leases=3/3 PASS
cycles=121 per lease
accelerator=tcg,thread=single,tb-size=128
HLI=3405/3405 per lease
events=2316
ACLs=1089
frame=3710 bytes
QOM=34 nodes
queue/error/dropped/peer-close/panic=0
```

firmware、ELF、QEMU 和工具输入在三个 lease 之间无漂移。原始两批运行聚合
SHA256 为 `f4df55f2e139aad47b705974095b1879256ffbea2cb0c6e17fe6e5cba4dd063e`。

### IPv6

```text
guest=same UIFlow2 StickS3 test build, one lifecycle
DNS AAAA=FEC0::2
HTTP path=/ipv6, HTTP/1.0 200 OK
denied endpoint=FEC0::2:18096
pcap TCP 18095=5 packets
pcap TCP 18096=2 packets
controlled AAAA generation and connect
private namespaces and NAT cleanup
DNS/HTTP close and QEMU reap
```

raw aggregate SHA256 为
`06b7861895f3b0511c2c64b25da3229fac1bea060c2c845735a0d67d6918c7c1`。

### 仓库回归

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
node --test platform/tests/test_sha256.mjs \
  platform/tests/test_firmware_upload.mjs
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check
```

结果：平台 `355/355 PASS`、文档 `19/19 PASS`、Node `2/2 PASS`，其余
contract/generated checks 全部 PASS。源码已拆分为 `64b00be`、`97eb73a`
和 `a4ef8b8` 三个结果提交并推送 `main`；随后由 `fa66e18` 把 CI 结果写回
验证台账。`40125359517` 的 `network-namespace-policy` 与
`platform-contracts` 两个 job 均在 `a4ef8b8` 上成功；最终文档提交的
run `40125476618` 也以两个 job 全部成功结束。

## 当前工作与剩余 Backlog

| 优先级 | 当前状态 | 下一项最小交付 |
| --- | --- | --- |
| P0 `NET-04` | 同主机 worker、HMAC、HTTPS/mTLS、rotation、跨 namespace control plane PASS | 真实 worker-local QEMU + evidence；随后跨主机 executor/reattach、主机发现和 companion continuity |
| P0 `FW-03` | manifest、capability/security、WebBurner、公开 BIN 强制刷新和静态审查 PASS | 重跑当前 AtomS3R/PaperMono 四固件 Device Service 功能样本，再扩设备和固件族 |
| P0 `FW-01/02` | 静态权限来源、SPDX、声明级许可、安全证据冲突检查 PASS | 运行态 ACL/许可、法律审批、真机 secure boot/Flash Encryption/eFuse/key 流程 |
| P0 `RUNTIME-02/03/04` | 缺口已结构化分类并保留 evidence | C6 Zigbee commissioning；Core2 legacy I2C/board-bus；ATECC608 fixture |
| P1 `CORE2-02` | 同 guest 多轮重连、3×121、active-BLE、bounded-TCG 和时间门禁 PASS | 长时吞吐/并发/teardown、bit-exact controller/baseband、物理 cache/PSRAM |
| P0 `HW-01` | 无 | 代表设备同固件 SHA 的 physical hardware validation |
| P1/P2 | 已登记 | `SVC-01/02/03`、`TAB5-01`、`UI-01`、`CZ-01` |

网络剩余能力按 `NET-04`、CIDR/domain-set 和不可信固件 disposable VM 分开，
不能由当前 namespace/egress PASS 推导。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build/contract | PASS | 355/355、19/19、Node 2/2、catalog/profile/coverage/snapshot |
| transport | PASS | Device Service、HCI/HLI、Bumble GATT、IPv6 TCP、controlled DNS、pcap |
| device_response | PASS | NUS GATT、IPv6 HTTP 200、denied-port block、fixture records |
| data_behavior | PASS | 3×121 reconnect、IPv6 namespace cleanup、artifact/tool hash stability |
| visual | PASS（virtual） | 3710-byte Core2 frame |
| physical | NOT RUN | 无真机、RF、功耗、电气或物理 cache/PSRAM 测量 |

## 验证边界

- Core2 结果只覆盖同一已验证 firmware/ELF/QEMU/profile。
- 121 轮 PASS 不等于 controller/baseband bit-exact，也不等于物理 cache/PSRAM。
- IPv6 使用 test-only 构建；原厂 UIFlow2 没有默认创建 link-local。
- 本轮没有重新跑 67-case full matrix；最近一次完整矩阵 evidence 仍单独存在。
- CI run `40125359517` 与最终 `fa66e18` 的 run `40125476618` 均已成功。

## 风险与回滚

- 无不可逆硬件操作。
- 可分别 revert `64b00be`、`97eb73a` 和 `a4ef8b8` 恢复网络 probe、Core2
  evidence 和文档对账。
- 网络测试使用临时 namespace、端口和 fixture，失败路径 fail-closed 并清理。
