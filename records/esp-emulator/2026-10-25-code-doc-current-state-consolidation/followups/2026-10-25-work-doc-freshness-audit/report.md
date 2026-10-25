# ESP Emulator Current-Code and Documentation Freshness Audit

## 背景

项目连续完成网络、worker、Core2 PSRAM 和固件审查里程碑后，代码事实已经
向前推进，但 README、当前状态、Backlog、工作流和网络专题仍存在不同层级的
重复叙述。人工维护多个“当前状态表”会让已完成项重新变成 TODO，也可能把
QEMU PID 回收误写成 guest/device side effect 已停止。

本次目标是建立单一事实链：

```text
source catalog/profile/code
  -> generated project snapshot
  -> project-status current capability
  -> project-backlog open work only
  -> validation ledger dated evidence
  -> work record publication
```

## 改动

### 当前状态和 Backlog

- README 压缩为产品定位、当前能力、验证入口、运行方式、边界和索引；
- `project-status.md` 增加工作流状态表，逐项列出当前结论、下一门禁和不能
  继承的边界；
- `project-backlog.md` 的 `NET-04` 只保留未完成的跨主机/companion 工作，
  已完成 TLS、rotation、restart、discovery 和 partition 作为 dependency 摘要；
- `CORE2-02` 保留已闭合门禁作为不可回退边界，并单独列出物理 PSRAM/cache、
  controller、长时并发、hook 校验和真机开放项。

### 网络与 worker 边界

worker partition QEMU lane 使用普通 `runtime=qemu`：

- 已验证：attempt 1 真实 QEMU 启动、失去 control、lease fence、QEMU PID
  reap；attempt 2 启动新 QEMU、取得 evidence 并 terminal PASS；
- 未验证：QEMU 内部 guest/device-controller quiesce、`qemu-unified` HTTP
  companion、BLE peer、pcap writer、磁盘 side effect 和 worker 未拥有的
  外部网络副作用。

下一项最小交付因此改为 worker-local `qemu-unified` partition/companion lane，
而不是直接把 process fence 扩大成完整设备 side-effect fence。

### 自动新鲜度与契约

`platform/tools/project_snapshot.py` 现在从 `docs/README.md` 的文档新鲜度
表派生：

- 非历史页和历史固定页数量；
- 文档职责分布；
- 复核日期早于当前事实日期的非历史页候选。

新增测试锁定：

- 文档索引同一 section 不重复链接同一页面；
- 状态/Backlog/handoff/workstream 权威页不重复长行；
- 项目快照必须暴露文档职责分布和过期候选；
- 历史页不会被误报为当前状态。

### 代码清理

- `qemu_profiles.py` 删除无占位符 f-string；
- `sd_image.py` 删除未使用的 MBR end 变量。

两项均不改变行为，Ruff `E9/F` 通过。

## 验证

```text
platform unittest       447/447 PASS
docs consistency         33/33 PASS
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
<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40162620429>

## 未覆盖项

- 本次没有启动 QEMU 功能 session，也没有重跑完整 67-case 外设矩阵；
- 文档新鲜度审计只识别日期落后候选，不能自动判断语义是否正确；
- 物理跨主机、真机、RF、功耗和电气结论仍未运行。

## 风险与回滚

- 文档测试可能因重复链接或重复长行更严格而阻止原本可提交的页面；这类失败
  应通过修正索引/重复叙述解决；
- 文档日期治理不改变运行代码；回滚实现为 revert `dc1f92f`，回滚验证台账
  与生成快照为 revert `7aa46c6`；
- 若保留本文档但回滚源码，必须同时撤回其中的能力结论，避免形成新的漂移。
