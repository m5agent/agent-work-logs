# ESP Emulator full document inventory and stale-page audit 报告

## 背景

项目已经从早期单设备 PoC 演进到多设备 unified runtime、网络/worker、
FirmwareManifest 和 Core2 native-HCI。主 README、状态页、Backlog、
验证台账和专题页持续更新，但仍有大量设备 README、测试说明和补丁说明没有
进入同一个新鲜度视图。

直接问题是：

1. 自动生成的设备 README 复制完整 `detail`、memory 和 concurrency 长文，
   形成第二份会漂移的事实源；
2. 部分局部页把已经完成的 executor、reattach、discovery、companion
   recovery 写成全局未完成；
3. UIFlow2 测试总索引仍指向旧 PSRAM evidence 名称；
4. Core2 native-HCI 页在 121 轮通过后仍把 121 cycles 列为下一次门禁；
5. 自动快照只审计新鲜度表中的权威页，不能说明其余页面由谁负责。

## 改动

### 全量文档盘点

`platform/tools/project_snapshot.py` 现在：

- 枚举项目内 214 个受管 Markdown 页面；
- 跳过 `.work`、`.pytest_cache`、`node_modules` 和第三方 checkout；
- 将页面分类为权威、设备、测试、补丁、平台、历史、示例、治理和第三方；
- 从页面头部读取 `Last reviewed`、`最近核对` 或 `日期`；
- 单独列出早于当前事实日期的委派文档；
- 保留原有 33 页权威新鲜度台账和历史页分类。

快照显示当前没有带显式旧复核日期的委派文档，且全部非历史权威页与事实日期
一致。

### 设备 README 生成器

`platform/tools/generate_catalog.py` 不再把 `runtime.validation.detail`、
`memory_validation` 和 `concurrency_validation` 复制进设备 README。生成的
页面只保留：

- 设备硬件档案；
- 当前验证 date/status；
- 设备声明 blockers；
- 项目状态、验证台账、Backlog 和代码地图链接；
- 可选的设备专属 `README.extra.md`。

新增测试遍历 14 台设备，要求 README 链接权威页且不得包含完整 validation
detail；生成器 round-trip 测试同时要求 README、device JSON、firmware JSON、
index 和 catalog 逐字节一致。

### 局部页纠偏

- UIFlow2 总索引改指
  `evidence-2026-10-25-core2-psram-sustained-8m-3x120.json`；
- Core2 native-HCI 的剩余门禁改为吞吐、超过四实例和物理 cache/PSRAM；
- worker queue 页面只负责 queue，明确 executor/reattach/companion/容器
  路径已有独立 fixture；
- worker executor 页面补上 cross-netns、cross-container、discovery 和
  trusted-host companion 的实际归属；
- worker reattach 页面明确仅覆盖 QEMU/QMP，companion 由 runtime restart
  fixture 覆盖；
- worker TLS 页面不再把 discovery 和 trusted-host companion 写成未实现；
- 读取并复核后更新 14 个带旧日期的委派页面，使快照的旧日期候选归零。

### 当前状态与交接

顶层 README 的“当前状态”压缩为后端、Device Service、网络/worker、Core2、
固件和验证边界六组摘要。

`engineering-handoff.md` 的里程碑段只保留已完成依赖和开放边界，逐次轮次、
SHA 和 evidence 统一交给验证台账。

## 验证

```text
platform unittest       467/467 PASS
docs consistency         37/37 PASS
Node SHA256/upload        2/2 PASS
runtime coverage         PASS
peripheral catalog       PASS
QEMU profiles            PASS
project snapshot         PASS
OpenAPI YAML             PASS
compileall               PASS
Ruff E9/F                PASS
git diff --check         PASS
GitHub Actions           PASS
```

CI：
<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40180394108>

## 当前工作与下一门禁

| 工作流 | 当前可执行面 | 下一门禁 |
| --- | --- | --- |
| 设备/网络 | unified 单 guest、DNS/CNAME、CIDR、pcap、WiFi/BLE | 物理跨主机与剩余模型缺口 |
| Worker | queue、HMAC/TLS、discovery、restart/reattach、容器、fence | 物理跨主机、guest/controller 与外部 side effect |
| Core2 | native-HCI、121 轮、长稳、PSRAM/MMU、最多四实例 | 五实例及更多、物理/controller 边界 |
| 固件 | Manifest/WebBurner、文件系统、安全与 capability | live trust root、运行态 ACL/许可、真机 key、更多固件 |
| 真机 | 规则和测试入口 | 同固件 SHA hardware validation |

完整开放项与验收只在项目 Backlog 维护。

## 验证边界

本次是 docs/contract 和生成器改动，没有启动新的 QEMU 功能 session，也没有
重跑完整 67-case 矩阵。Core2、网络和 worker 的运行结论均来自此前独立记录
与 evidence，不因本次文档整理而升级。

全量扫描能发现未归类和显式旧日期，但不能替代人工语义审查；本页所列局部页
修复正是人工审查结果。

## 风险与回滚

设备 README 不再显示完整运行详情，读者必须通过页面链接查看状态、台账和
Backlog；这是有意的单一事实源设计。若发现关键信息只存在于旧 README，应将
它补到专题页或验证台账，而不是恢复生成器复制长文。

回滚方式是 revert `b8b48e46c79d65f151eca1a57431c3117fb95907`。回滚后
设备 README 会重新复制长运行流水，全量委派文档盘点也会退回 33 页权威视图。
