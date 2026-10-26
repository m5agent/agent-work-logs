# ESP Emulator WebBurner import policy and documentation audit report

## 背景

- 来源：
  [m5stack-esp-emulator](https://github.com/m5agent/m5stack-esp-emulator)
- 需求：继续推进通用固件审查，完整整理当前代码和文档，区分已实现能力、
  未完成 Task、日期化 evidence 与历史样本。
- 目标：消除 WebBurner 导入器的非确定性/平台相关选择，并修正会误导当前
  状态的文档入口。

## 修复前问题

静态审计确认以下输入可能得到静默选择或平台相关结果：

1. 多 build WebBurner manifest 总是使用第一个 build，即使目标设备 SoC
   对应另一个 build；
2. 同时存在多份 WebBurner manifest、flasher、eFuse 或同角色资源时，旧代码
   可能选择排序第一份；
3. ZIP entry 只做基本路径逃逸检查，没有统一处理 NFC、Windows 保留名、
   反斜杠、空/点段、文件与目录的 casefold/父子冲突和 symlink；
4. JSON 布尔 offset 是 Python `int` 子类，旧逻辑可能把 `true` 当成整数；
5. 文档快照把 2026-10-24 的 21 个历史样本写成“公开样本快照”，容易被
   `2026-10-26` 的最新 evidence 日期误读为当前全量覆盖。

## 修复

### ZIP path policy

- entry path 先做 Unicode NFC 与 POSIX 归一；
- 拒绝绝对路径、反斜杠、控制字符、空/`.`/`..` 段、Windows 保留名、
  首尾空白、尾随点/空格等不可移植名称；
- 拒绝 casefold 后的文件冲突、目录拼写冲突和文件/目录父子歧义；
- 拒绝 symlink entry；
- archive read/write 错误转换为结构化 `ManifestError`。

### Resource and build selection

- 多份 WebBurner manifest 直接拒绝；
- `flasher_args.json`、eFuse summary、ELF、MAP、SBOM 等同角色资源必须唯一；
- `sdkconfig` 与 `sdkconfig.defaults` 各自必须唯一；两者同时存在时明确选择
  实际 `sdkconfig`，不把 defaults 当成已生效配置；
- 多 build 包必须提供目标设备，并按 SoC 唯一匹配一个 build；
- 布尔 offset 不再按整数接受。

### Documentation ownership

- 项目快照把 21 个样本改为带来源日期的“历史哈希绑定公开样本基线”；
- 新 evidence 不会被自动并入该历史计数，刷新、fixture、安全和导入结果
  分别回查专题页与验证台账；
- FirmwareManifest 契约、代码地图、工程交接、工作流、当前状态、Backlog、
  根 README 和测试 README 同步新增的导入策略；
- stale-claim 门禁禁止“公开样本快照覆盖”旧说法回到当前入口。

## 当前工作与待办

本轮整理后的权威分层是：

- 当前能力与边界：`docs/project-status.md`；
- 未完成 Task、依赖和验收：`docs/project-backlog.md`；
- 某项结论的执行时间和 evidence：`docs/validation-ledger.md`；
- 动态设备、样本、Task 和代码规模：`docs/project-snapshot.md`；
- 源码、测试和维护债入口：`docs/code-map.md`。

当前 P0 剩余范围：

| Task | 当前缺口 |
| --- | --- |
| `RUNTIME-03` | Core2 legacy UIFlow 仍无正常 WDT 下的非空应用帧；需要绑定 late-boot flag/object 与 matching ELF/MAP |
| `NET-04` | 物理跨主机 executor/reattach、跨主机幂等、任意 NAT 和外部 side-effect ownership |
| `CORE2-02` | 大于当前服务容量、持续吞吐、其他 teardown、bit-exact controller、物理 PSRAM/cache 与真机 |
| `FW-01/02/03` | 运行态 ACL/许可、live eFuse/trust root、生产 key、真实云端业务和更多固件族 |
| `HW-01` | 代表设备同固件 SHA 的 hardware validation |

其余服务化、Tab5、视觉保真和 CardputerZero 专项继续由 Backlog 的
`SVC-*`、`TAB5-01`、`UI-01` 与 `CZ-01` 跟踪，不从本轮静态修复继承完成度。

## 验证

```bash
PYTHONPATH=platform/tools python3 platform/tests/test_firmware_manifest.py

PYTHONPATH=platform/tools python3 \
  tests/firmware/webburner_import_policy/run_test.py

PYTHONPATH=platform/tools python3 \
  tests/firmware/manifest_policy/run_test.py

PYTHONPATH=platform/tools python3 \
  tests/firmware/secure_boot_image/run_test.py \
  --out-dir /tmp/m5-secure-boot-rebind \
  --date 2026-10-26

PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'

python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check
python3 -m compileall -q platform/tools platform/tests tests
git diff --check
```

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| static import policy | `PASS` | `16/16` checks |
| manifest unit tests | `PASS` | `36/36` |
| manifest policy regression | `PASS` | `14/14` |
| Secure Boot v2 static regression | `PASS` | `26/26` |
| platform contract | `PASS` | `543/543` |
| schema/coverage/catalog/profile/snapshot | `PASS` | generated checks |
| firmware flash/boot/runtime | `NOT RUN` | 本轮只验证导入选择与静态策略 |
| visual_or_physical | `NOT RUN` | 无 QEMU 画面或物理设备验证 |
| delivery | `PASS` | 产品提交 `7f9f248`；CI `40251653367` 两个 job 均成功 |

## 验证边界

本轮使用合成镜像和本地包 fixture 验证拒绝路径，没有重新下载公开固件并执行
真实导入、烧录、启动或网络/外设功能。通过只证明歧义输入不会被静默接受，
不证明任意真实固件兼容。Secure Boot v2 仍保持 signature authenticity、
trust root 和 anti-rollback enforcement 为 `not-verified`。

## 风险与回滚

没有烧录、设备写入、凭据变化、生产 key 操作或持久迁移。回滚 product commit
`7f9f248544fea950fc1b13050f604634ed02637e` 会恢复旧的导入选择行为与文档
基线，并使本轮 tool/evidence 哈希失配；不能保留新 evidence 同时声称旧实现
通过。
