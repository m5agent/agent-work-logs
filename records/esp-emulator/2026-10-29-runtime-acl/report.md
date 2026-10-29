# ESP Emulator operator runtime ACL 报告

## 背景

`FW-01` 已有镜像内 FAT/LittleFS/SPIFFS 权限属性和许可声明扫描，但 Device
Service 对运行中 guest 的 serial/input/reset/program/flash 操作没有设备级
runtime policy。仅记录镜像属性不能阻止未授权 API 操作，也不能证明运行态
强制。该改动只解决 service 管理的 guest-facing 操作，不冒充 firmware
filesystem ACL。

## 实现

新增 `platform/tools/runtime_acl.py`：

1. 严格解析最多 64 KiB 的 regular UTF-8 JSON，拒绝 symlink、duplicate key、
   unknown field/device/operation/entrypoint/path；
2. 支持 `"*"` fallback 与 device-specific override；
3. allowlist 覆盖 `serial.read`、`input.write`、`guest.reset`、
   `program.read`、`program.execute`、`program.interrupt`、
   `filesystem.write` 和 `flash.read`；
4. `program.execute` 必须声明 `main.py`/`main.mpy`；
5. package write 必须声明 canonical path allow rule，deny 优先，支持 exact
   path 与 trailing `/` directory prefix；
6. policy ID 使用规范化语义 JSON 的 SHA256，不受字段顺序或格式影响。

Device Service/API `1.51.0` 在以下边界强制执行：

- serial read、serial-marker wait、input/unit input、reset 和 flash read；
- program read/execute/interrupt，package 在 revision 发布前检查路径；
- Session/capacity 暴露 policy hash 和有效权限；
- denied operation 产生有界、去重的 policy-bound event；
- denied program detail、serial/runtime log 与 virtual Flash 从 snapshot 和
  evidence ZIP 中省略，并写 redaction receipt；
- `SIGHUP` 与 token/TLS 共用 request-drain reload；新策略完整验证后才发布，
  无效文件保留旧策略。

未配置 ACL 时状态为 `NOT_CONFIGURED`，保留既有 local-control 兼容行为。
静态检查同时发现并修复 isolated controlled-HTTP 配置中未初始化的
`http_profile` 名称。

## 兼容性

公开 API 和既有 Session 默认无 token/ACL 配置时行为不变。新增字段为扩展：
`runtime_acl`；`403 runtime_acl_denied` 只在 operator 配置 ACL 后发生。
Program/Preview 的既有 generation、revision、超时和取消顺序保持不变；
reference package 仍在 stale generation 检查之后读取。

## 执行

真实 HTTP runner 使用 production `RuntimeACL`、`DeviceService`、
`DeviceSession`、Handler 和 package preflight，并执行：

```text
tests/firmware/runtime_acl/run_test.py --out /tmp/runtime-acl-evidence.json
```

checks 包括：

- unconfigured compatibility、device/default deny、writable-action denial；
- allowed program status、denied program/serial/input/reset/flash/interrupt；
- serial-marker wait 不能绕过 read ACL；
- package deny path 不创建 revision，allowed path 到达 unavailable-console gate；
- denied events 去重；
- snapshot/evidence 对 denied program、serial/log 和 Flash 写 redaction；
- invalid CLI policy 在 listener 启动前失败；
- 真实服务进程有效 `SIGHUP` 更新 policy hash，无效 `SIGHUP` 保持旧策略。

结果为 `23/23 PASS`。全平台套件 `1550 OK + 10 skipped`。runtime coverage、
peripheral catalog、QEMU profiles、project snapshot、compileall、scoped
Ruff、OpenAPI/YAML、JSON、artifact hash 和 PR scope 均 PASS。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compile、Ruff `E9/F`、OpenAPI parse |
| transport | `PASS` | 真实 Device Service HTTP server、capacity/session/program/input/reset/wait |
| device_response | `PASS` | allow/deny 返回和 policy ID 一致；denied event 可审计 |
| data_behavior | `PASS` | package deny path/revision、snapshot/evidence 脱敏、SIGHUP replacement |
| visual_or_physical | `NOT RUN` | 无 QEMU guest 或硬件测量 |

## 验证边界

这是 host/management-plane runtime policy，不是 firmware-authored filesystem
ACL。它不证明：

- guest 对 Unix mode/ACL 或只读分区的执行；
- arbitrary native firmware 被限制在 sandbox；
- QEMU 内 guest/controller 完全停止或 quiesced；
- physical cache/PSRAM、RF、电气或真机行为；
- 完整源码/依赖许可与法律审批。

`FW-01` 因此保持进行中。

## 风险与回滚

配置 ACL 后，旧客户端若依赖未声明操作会收到 `403 runtime_acl_denied`；
部署前应先在测试 state directory 验证策略。未配置或 revert 实现提交可恢复
既有 local-control 行为；已生成 history/evidence 不需要迁移。策略文件由
operator 管理，CLI 不接受 inline credential 或固件自报权限。
