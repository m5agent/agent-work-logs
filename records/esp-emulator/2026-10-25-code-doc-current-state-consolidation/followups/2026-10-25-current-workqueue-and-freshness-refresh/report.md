# ESP Emulator Current Work Queue and Documentation Freshness Refresh

## 背景

项目连续完成 Secure Boot v2 signature、
Network/worker partition fence 和 Core2 PSRAM 工作后，多个当前事实页
仍可能让读者把以下边界混淆：

- 签名数学有效与公钥 trust root 可信；
- 包内 eFuse summary 对照与 live eFuse read；
- worker-owned process fence 与 QEMU guest/controller 内部 side effect；
- QOM PSRAM 大小与物理 cache/PSRAM timing；
- virtual-device validation 与 physical hardware validation。

本次目标是校准当前事实，建立清楚的已完成、部分完成和待做入口，而不是
制造新的功能 PASS。

## 文档改动

### 当前能力

- README 只保留当前能力摘要，并明确 Secure Boot v2 已覆盖 RSA-PSS/
  ECDSA 数学验证和包内 eFuse digest 对照，但 live trust root 仍未完成；
- `project-status.md` 增加最新签名/eFuse 里程碑及不可继承边界；
- `engineering-handoff.md` 更新成熟度、最近成果和 FW-02 下一门禁；
- `workstreams.md` 与 `project-backlog.md` 使用同一能力语义；
- `validation-ledger.md` 更新 Secure Boot fixture 为 `21/21` checks。

### 文档新鲜度

自动快照此前标记四页为非历史、但复核日期早于当前事实日期：

- `tab5-deferred-backlog.md`；
- `p4-peripheral-backend-requirements.md`；
- `device-visual-fidelity-backlog.md`；
- `cores3-image-rendering-boundary.md`。

四页均与当前状态和 Backlog 逐项核对。没有新增 P4、视觉或 CoreS3 image
数据面，因此只更新复核日期并保留原始证据日期，不把后续 S3/C6/Core2
无线工作继承给这些页面。

### 文档契约

原测试无条件要求快照出现“复核日期早于当前事实日期的非历史页”。当所有
非历史页已经对齐时，生成器会正确输出“所有非历史页…一致”，测试反而失败。
现在测试根据 `document_audit.older_current` 选择对应断言。

## 当前工作与待办

### P0

1. `NET-04`：物理跨主机 executor/reattach、跨主机 idempotency、无
   reachable seed 的 NAT traversal、QEMU guest/controller 和外部 side
   effect、namespace-managed/Tab5/cross-host companion。
2. `CORE2-02`：bit-exact BT controller/baseband、物理 PSRAM/cache timing、
   长时吞吐/并发和其他 teardown。
3. `FW-01/02/03`：运行态 ACL/许可、live eFuse/ROM secure boot、生产 key、
   真实 cloud business、更多固件族。
4. `HW-01`：代表设备同固件 SHA 的 hardware validation。

### P1/P2

- `RUNTIME-02/03/04`：C6 Zigbee、Core2 legacy I2C、ATECC608；
- `SVC-01/02/03`：跨主机接管、warm pool、编排拆分；
- `TAB5-01`、`UI-01`、`CZ-01`：专项后端、高保真视觉和 CardputerZero。

## 验证

```text
platform unittest       454/454 PASS
docs consistency         34/34 PASS
secure boot fixture      21/21 PASS
Node SHA256/upload        2/2 PASS
runtime coverage         PASS
peripheral catalog       PASS
QEMU profiles            PASS
project snapshot         PASS
Ruff E9/F                PASS
compileall               PASS
git diff --check         PASS
GitHub Actions           PASS
```

CI：
<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40166166903>

## 验证边界

- 文档一致性 PASS 只证明页面、生成物和契约没有漂移；
- 没有重新执行完整 UIFlow2 外设矩阵；
- 没有启动新的网络/worker/QEMU 功能会话；
- eFuse summary 仍是自报数据，未进行 live read 或 ROM secure boot；
- 所有物理硬件、RF、功耗、电气、声学和光学结论仍为 `NOT RUN`。

## 风险与回滚

- 文档内容变化不改变运行时行为；回滚为 revert `cb42671`；
- Secure Boot eFuse 对照代码回滚为 revert `ee4ad8f`；
- 若只回滚代码而保留文档，会形成能力漂移，因此两个提交应一起考虑；
- 没有修改存储、设备状态或外部服务配置。
