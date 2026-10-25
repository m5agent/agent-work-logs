# ESP Emulator Core2 five-instance staggered concurrency 报告

## 背景

父记录通过扩大真实 guest HLI event/ACL 备用对象，关闭了 Core2 四实例
零错峰启动门禁。runner 仍把 `--concurrency` 硬限制为 `4`，与 Device
Service 已有的单设备容量不一致，因此不能直接执行五实例验证。

本 follow-up 的目标是：

1. 让 runner 使用服务实际定义的单设备并发上限；
2. 在两批独立五实例 workload 中验证完整的数据面；
3. 单独保留五实例同时冷启动的 PASS/FAIL 对照，不把错峰稳态扩大解释。

## 结论

runner 现在通过 `MAX_CONCURRENCY` 与
`device_service.DEFAULT_MAX_PER_DEVICE` 绑定，并增加契约测试，当前允许
`1–8`。

两批独立、30 秒错峰的 `5×120s` workload 均为 `5/5 PASS`，合计
`10/10 PASS`，实际最大并发为 `5`。每个通过 lease 都在同一 guest 内
完成：

- WiFi association、DHCP 和受控 HTTP；
- public DNS/HTTP；
- external BLE NUS scan/connect/write/notify；
- `1 MiB` PSRAM 全缓冲 sweep；
- frame、31-node QOM、pcap、evidence 和 cleanup。

通过 lease 的 HLI 为 `45/45`，36 events/9 ACLs 走真实 guest-object fast
path，结束 reserve depth 为 `8/4`，scheduler reset、panic、queue residue
和 HLI errors 均为 `0`。

零错峰五实例没有关闭。相同实现下，一次 `5×120s` batch 为 `5/5 PASS`，
但独立确认批为 `3 PASS / 2 FAIL`：

- attempt 1 在 NimBLE `ble_hs_hci_process_ack` 路径出现
  `LoadProhibited @ 0x402630cc`，HLI post/consume 为 `6/5`，queue depth
  为 `1`，并记录 scheduler reset；
- attempt 2 已完成 boot、WiFi、public network 和 PSRAM 前缀，但 external
  BLE peer 没有完成 GATT exchange。

失败已推到公开 evidence，没有通过重试或放宽 gate 删除。

## 根因边界

当前证据只能把问题收敛到“五实例同时冷启动期间的 HCI/HLI 与外部 GATT
调度竞争”，不足以宣称某个单独 QEMU 寄存器或 guest 库函数就是根因：

- 错峰时两批 `10/10` 通过，说明单实例功能路径和 `8/4` reserve 足够；
- 同时启动时既有 NimBLE ACK 路径 panic，也有 external GATT
  exchange failure，表现并不单一；
- 不能从一次 panic PC 直接推断所有失败都由同一事务引起；
- 本轮没有提交新的 QEMU 数据面补丁，也没有用 host 假值或重试掩盖失败。

因此该边界保持 `OPEN / UNSTABLE`，后续应以独立、可重复的最短冷启动实验
继续收敛，而不是扩大超时、增加 retry 或无条件注入 IRQ。

## 改动

源码结果版本：`8c4349cd09a0c2cfd7362830df1825d76615ac9b`。

- `tests/uiflow2/core2_native_hci/run_service_5x.py`：
  `MAX_CONCURRENCY=8`，新增 `validate_concurrency()`；
- `platform/tests/test_core2_concurrency_contract.py`：
  锁定 runner 上限与服务单设备容量一致；
- 四份五实例 evidence 与对应哈希；
- current status、Backlog、workstreams、API、code map、QEMU profile、
  catalog source 和生成物同步；
- 文档测试区分历史三/四实例 evidence 的旧 runner SHA 与当前五实例
  evidence 的新 runner SHA，不覆盖历史记录。

## 执行

五实例错峰和零错峰均使用以下核心参数：

```text
attempts=5
concurrency=5
hold-seconds=120
require-psram
```

区别只有：

```text
stagger-seconds=30
stagger-seconds=0
```

错峰两批均绑定 launch assets，
`input_assets_unchanged_during_run=true`。零错峰 PASS/FAIL 两批使用相同
firmware、ELF、QEMU 和工具哈希，确认失败不是输入漂移造成。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| source/build | `PASS` | result commit 的 CI 两个 job PASS |
| runner contract | `PASS` | `MAX_CONCURRENCY` 与 `DEFAULT_MAX_PER_DEVICE` 一致；接受 1/5/8，拒绝 0/-1/9 |
| virtual staggered steady state | `PASS` | 两批独立 `5×120s`，合计 `10/10` |
| virtual zero-stagger cold start | `FAIL` | 一批 `5/5 PASS`，独立批 `3/5 FAIL` |
| guest HCI/HLI happy path | `PASS` | 每个通过 lease `45/45`、36 events/9 ACLs、depth `8/4` |
| WiFi/public network | `PASS` | 每个通过 lease 的 DHCP、controlled HTTP、public DNS/HTTP |
| BLE GATT | `PASS` | 每个通过 lease 的 external NUS scan/connect/write/notify |
| board/UI/QOM/pcap evidence | `PASS` | 每个通过 lease 的 frame、31-node QOM、pcap、evidence、cleanup |
| physical controller/PSRAM/RF | `NOT RUN` | 无物理设备或测量 |

仓库验证：

```text
platform tests: 470/470 PASS
docs consistency: 37/37 PASS
node units: 2/2 PASS
runtime coverage / peripheral catalog / QEMU profiles / snapshot: PASS
compileall / Ruff E9,F / git diff --check: PASS
```

## 验证边界

- 本记录的 PASS 只指五实例 30 秒错峰稳态；
- 相同实现的零错峰五实例仍不稳定，必须保留 PASS 和 FAIL 两侧 evidence；
- 结论只覆盖当前 firmware/ELF/QEMU/runner/hook ABI；
- 大于五实例、持续吞吐和其他 teardown 模式没有执行；
- HCI 是功能级 virtual-device 路径，不是 bit-exact controller/baseband；
- 本记录不证明物理 PSRAM/cache timing、RF、功耗、电气或真机行为。

## 风险与回滚

本改动只扩展 runner 命令行并发上限，并补充验证与文档，不修改 QEMU guest
数据面。回滚方式是 revert `8c4349c`；回滚后 runner 重新限制为四实例，
不会影响已有三/四实例 evidence。

零错峰五实例不应进入稳定 SLA。若服务允许五实例同时冷启动，调用方仍应
使用受控 stagger 或把结果标为不稳定；生产承诺需要先关闭该失败边界。
