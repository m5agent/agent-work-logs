# ESP Emulator 代码、文档与当前工作/待办收口报告

## 背景

用户反馈仓库文档存在大量旧结论，没有结合后续网络、Core2、固件审查和
runtime model gap 工作。旧文档混用了“计划”“历史证据”“当前能力”和
“accepted virtual-device scope”，容易把尚未关闭的项写成 PASS，也可能
把固件问题、fixture 缺口和模拟器模型缺口混为一类。

本轮目标是把当前代码、生成物和证据重新收敛到固定入口，并把实际完成项
与未完成项分开。

## 文档结构

当前入口按职责拆分：

| 文档 | 职责 |
| --- | --- |
| `project-status.md` | 今天支持什么、证据层级和风险 |
| `project-backlog.md` | 尚未完成的工作、依赖和验收 |
| `workstreams.md` | 工作流、代码面和未完成 Task ID |
| `code-map.md` | 稳定代码与测试入口 |
| `validation-ledger.md` | 带日期的历史验证 |
| `runtime-model-gap-register.md` | 固件与模拟器模型不一致的缺口 |
| `project-snapshot.md` | catalog/profile/evidence/Backlog 的自动事实快照 |

历史调查仍保留原日期和当时结论；被后续证据推翻时增加“由哪一页取代”，
不静默重写历史。

## 状态纠偏

### 已关闭或已推进

- `RUNTIME-01` C6 软件复位后的 Flash 地址和 PMP 问题已修复；
- `RUNTIME-05` S3 WPA2-PSK 正确/错误密码数据面已通过 accepted
  virtual-device scope；
- controlled DNS A/AAAA、TLS allowlist、exact IPv4/IPv6 egress、
  guest IPv6 TCP/HTTP 和 cleanup 已不再是“未实现”；
- worker durable queue、HTTP executor、HMAC、HTTPS/mTLS、rotation/drain、
  同主机 generation-pointer migration、本地 QEMU reattach、
  worker-local QEMU 已有执行证据；
- Core2 native-HCI、WiFi/公网、same-guest GATT 重连和 artifact-bound
  7200 秒功能保持已通过当前虚拟设备门禁；
- FirmwareManifest、WebBurner、capability/security preflight、LittleFS/
  FAT/SPIFFS、SD/NVS session fixture 已进入可执行路径。

### 仍未关闭

- WPA3-SAE、WPA2 group-key multicast、真实 RF/PHY、channel/rate、roaming；
- 跨主机 worker 自动发现、QEMU executor/reattach 和 companion/evidence
  continuity；
- Core2 bit-exact BT controller/baseband、物理 cache/PSRAM、吞吐/teardown；
- runtime ACL/权限、完整许可审批、真机 secure boot/Flash Encryption/eFuse；
- C6 Zigbee commissioning、Core2 legacy I2C routing、ATECC608；
- Tab5 缺失的 P4 数据面和 CardputerZero 长期回归；
- 代表设备同固件 SHA 的 physical hardware validation。

## 关键边界修正

最后的一致性检查发现 `AGENTS.md` 仍有两处旧表述：

1. exact endpoint policy 被写成 IPv4-only；
2. 所有 WiFi 数据面都被笼统写成不能证明 WPA2/WPA3。

当前规则改为：

- Linux policy 精确覆盖 IPv4 与 IPv6 `protocol + address + port`，
  CIDR/domain-set 仍 fail-closed；
- S3 WPA2-PSK 只证明 RSN、EAPOL、pairwise CCMP 和 guest
  DHCP/DNS/TCP；WPA3-SAE、group-key multicast 和物理链路安全仍是独立项。

## 验证

```text
platform tests                 377/377 PASS
documentation contracts        20/20 PASS
runtime coverage               PASS
peripheral catalog             PASS
project snapshot               PASS
git diff --check               PASS
GitHub Actions platform        PASS
GitHub Actions namespace       PASS
```

CI：`40138787543`，绑定文档边界提交 `e41bfd5`。

WPA2 功能证据在独立记录中绑定 firmware SHA
`b3597fcabbff57c98618caa8754af84745e9eac35b2868ab3c4cb0935b7c59b3`、
QEMU patch SHA、22/22 Device Service checks、Open/WPA2/wrong-password
对照和 15/15 S3 定向矩阵。

## 未覆盖与风险

- 本轮是 docs/contracts 收口，不重新证明所有历史 QEMU 功能；
- 完整 67-case 外设矩阵本次未重跑；
- 本文不把 virtual-device validation 写成 physical hardware validation；
- 文档计数和状态仍可能随代码变化，稳定入口必须继续由
  `project_snapshot.py --check` 和 `test_docs_consistency.py` 约束。

## 回滚

文档边界提交 `e41bfd5` 可单独回滚到能力提交 `08d8a21`；WPA2 功能提交
`08d8a21` 可回滚到 `3f4bf92` 的 Open-only 行为。回滚不影响物理设备或
生产凭据。
