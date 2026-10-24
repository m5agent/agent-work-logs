# ESP Emulator 代码、文档与一页式交接报告

## 背景

用户指出项目完成项很多，但部分文档仍停留在较早阶段，没有反映后续
worker discovery、restart continuity、session idempotency、固件 SD/NVS
fixture、Core2 bounded soak 和 121 轮 reconnect 等结果。

目标不是再复制一张状态表，而是建立以下边界：

- 当前能力只由 `project-status.md` 维护；
- 未完成项只由 `project-backlog.md` 维护；
- 动态设备、Task、缺陷和代码规模由自动快照生成；
- 测试和补丁各有稳定总索引；
- case README、设备 README 和历史设计页保留当时语境，不单独定义当前能力。

## 主要发现

### 过期结论

- 固件审查专题页仍写“四个刷新公开样本 Device Service 功能执行 NOT RUN”，
  实际已有 `3 PASS / 1 PARTIAL / 0 FAIL`。
- Device Service API 仍把 S3 描述成只有 Open AP，没有区分 unified profile
  的 Open 路径与 `generic-observe` 的 WPA2-PSK pair-key 路径。
- API 的 Core2 摘要停在 20 轮 reconnect 和 RSS `REVIEW`，没有反映
  `3 × 121`、`600s` active BLE 和 bounded `7200s` 结果。
- 外设架构页手写动态设备/硬件需求计数，且把结构写成“四层”但实际列了
  五项。
- 代码地图手写大型模块行数，后续提交会继续漂移。

### 结构缺口

- 根 `tests/` 没有总入口，测试分层和 Agent 功能测试路由只能从多个
  专题页拼出来；
- `tests/network/` 有二十余个 fixture，但没有统一边界表；
- `patches/` 没有总索引，补丁先后关系只能从多个目录 README 推断；
- 自动项目快照有设备/Task，但没有代码、测试、补丁和文档规模。

## 改动

### 顶层状态和待办

- `project-status.md` 新增一页式交接，明确当前 companion continuity 门禁。
- `project-backlog.md` 和 `workstreams.md` 把当前执行顺序改为：
  companion continuity → 跨主机 worker → 固件业务结果 → Core2 物理/controller
  → runtime gaps/真机 → 服务池/专项。
- Backlog 明确区分“已具备但仍需扩边界”和“完全未实现”。

### 测试和补丁索引

- 新增 `tests/README.md`：
  - platform/UIFlow2/network/firmware/CardputerZero 分层；
  - evidence 命名和 SHA 绑定规则；
  - Device Service 功能测试与直接 runner 的使用边界。
- 新增 `tests/network/README.md`：为每个 network/worker fixture 列出
  “执行什么”和“不能证明什么”。
- 新增 `patches/README.md`：按 QEMU/S3/C6/Core2/Linux/Tab5 分组，不复制
  每个补丁的完整序列，指向子目录中的权威 apply order。

### 自动快照与契约

- `project_snapshot.py` 新增生成统计：
  - `platform/tools` 模块数和行数；
  - 最大 6 个工具模块；
  - 可执行测试文件/目录和 evidence JSON 数量；
  - 补丁组和 patch 文件数量；
  - Markdown 页面与行数。
- `test_docs_consistency.py` 新增：
  - 要求可执行测试目录和补丁目录必须有 README；
  - 相对链接检查覆盖全部 patch README；
  - 必需索引文件存在；
  - 自动快照必须包含代码/文档规模。

### 专题页纠偏

- 固件审查工作流写回四个刷新样本的实际结果和剩余 cloud/key 边界。
- Device Service API 写回 S3 Open/WPA2 分层和 Core2 最新长稳边界。
- 外设架构页移除易漂移的手写计数，并补充 S3 WPA2 与 Core2 native-HCI。
- Device Center 契约补充 worker lifecycle 当前能力。
- Core2 相关 patch README 指向 native-HCI authoritative gate。

## 执行与证据

```text
platform tests                 396/396 PASS
documentation contracts       21/21 PASS
Node SHA256/upload            2/2 PASS
runtime coverage              PASS
peripheral catalog            PASS
QEMU profiles                 PASS
project snapshot              PASS
compileall                    PASS
Ruff E9/F                     PASS
git diff --check              PASS
GitHub Actions two jobs       PASS
```

源码基线为 `0e3a913207dd8772d497a8e4dfb5580ba597f5b3`，结果提交为
`61204890a1442ea6b88652fd5da53d678a8a826e`。完整平台套件在结果提交前
本地执行；结果提交的 GitHub Actions 两个 job 均已成功，run 见
<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40143120598>。

## 当前实现项

companion continuity 是当前首要实现门禁：

- QEMU/QMP 已有 PID、start-time、socket ownership 和 running 校验；
- controlled HTTP fixture 当前是进程内对象；
- BLE peer 当前是 `_hci_probe` 子进程；
- runtime-restart evidence 明确把 companion HTTP/BLE continuity 记为
  `NOT RUN`；
- 新实现必须支持 adopt-or-recreate、端口去重、日志 offset、ownership
  failure 和 unified StickS3 同 lease evidence 连续性。

## 验证边界

- 本轮没有重跑 67-case 外设矩阵或完整 unified 功能矩阵；
- 没有修改 QEMU/controller，因此不产生新的虚拟硬件数据面证据；
- companion continuity 未实现；
- physical hardware、RF、功耗、电气、声学和光学为 `NOT RUN`；
- 本轮结论只覆盖文档、生成快照、平台契约和验证入口整理。

## 风险与回滚

主要风险是把历史页里的旧结论误当成当前事实，或继续维护多份动态计数。
本次通过自动快照、旧口号回归测试、链接检查和分层索引降低该风险。
回滚到 `0e3a913` 可撤销全部文档/索引改动，不影响运行时数据面。
