# ESP Emulator Unified Companion Continuity Report

## 背景

上一里程碑已经证明 runtime Device Service 重启后可以重新接管同一 QEMU
PID，但 HTTP fixture 仍只存在于旧服务进程内，BLE peer 也只保存在内存
handle 中。重启后的服务无法证明 companion 控制面和重启后的数据面继续
有效。

目标是让 trusted-host unified session 在 runtime service 被强杀后：

1. 保持同一 QEMU guest；
2. 恢复 HTTP fixture 和 durable request history；
3. 安全 adopt 没有退出的 BLE peer；
4. 在重启后完成新的 GATT 和 HTTP 数据面；
5. 通过原 job/lease 收集包含两代 companion evidence 的 ZIP；
6. 清理 QEMU 和全部 companion。

## 实现

### Companion state

每个 session 在 `session.json` 持久化 companion ownership：

- HTTP：port、generation、state、service PID/recovery action；
- BLE：PID、精确 start token、完整 process command SHA256、port、state。

API snapshot 只暴露安全字段；raw start token 和 command hash 留在私有
session record。

### HTTP fixture

- 每个请求立即原子写入 `http-fixture.json`，不再依赖进程正常退出；
- 请求记录包含 path、Host、received_at 和 fixture generation；
- 重启时校验 profile port、读取 durable requests，并在同一端口创建
  generation 2；
- 如果端口、generation 或历史记录无效，reattach fail closed。

### BLE peer

- 启动后保存 peer PID、process start token 和完整 command SHA256；
- 重启后先检查进程存在、start token 和 command hash；
- 只对完全匹配的 peer 设置 adopted 状态和可清理 handle；
- 没有匹配 ownership 且没有既有完成证据时，整个 reattach 失败；
- fail-closed reattach 会终止已经验证为 running 的 QEMU 和已 adopt 的
  companion，避免遗留。

### Continuity workload

统一 StickS3 probe 现在统计 BLE receive：

- 正常单 cycle 路径没有行为变化；
- peer 可先输出初始 PASS，然后等待 session-local continuity trigger；
- 触发后 peer 完成第二个 GATT cycle；
- 第二次 BLE RX 让 guest 再访问 controlled HTTP，并输出
  `UNIFIED_STICKS3_HTTP_RECHECK_PASS`。

WorkerAgent 新增有界 `request.evidence_delay_seconds`（0-300 秒），用于在
session ready 后等待一个已声明的延迟数据面，同时保持 job heartbeat。

## 执行

1. 打包包含双 BLE RX/HTTP recheck 的 unified StickS3 镜像；
2. 通过 runtime Device Service 上传和导入 unified image；
3. central control plane submit `runtime=qemu-unified` job；
4. WorkerAgent 在 worker-local runtime 创建真实 QEMU session；
5. BLE peer 完成第一次 GATT，HTTP fixture 记录 generation 1；
6. session running 后只 SIGKILL runtime Device Service；
7. 2.2 秒后用同 port/state 重启；
8. 新服务 reattach 同 QEMU PID，恢复 HTTP generation 2，adopt BLE peer；
9. fixture 写入 continuity trigger；
10. peer 完成 GATT cycle 2，guest 发起第二次 HTTP；
11. Worker 等待 evidence delay 后下载 evidence ZIP；
12. 原 job/lease 完成 PASS；
13. 停止 session，核对 QEMU/BLE peer 清理。

## 验证结果

```text
same runtime session / QEMU PID            PASS
PID start-time + QMP ownership             PASS
HTTP generation 1 -> 2                     PASS
BLE PID/start-time/command-SHA ownership   PASS
BLE peer adopt                             PASS
post-restart GATT cycle 2                  PASS
guest controlled HTTP recheck              PASS
network evidence                           PASS
same job / lease / worker identity         PASS
evidence ZIP with two HTTP generations     PASS
session stop / QEMU + companion cleanup    PASS
```

```text
live fixture checks     26/26 PASS
platform tests          402/402 PASS
documentation contracts 22/22 PASS
Node SHA256/upload      2/2 PASS
runtime/catalog/profile/snapshot PASS
compileall / Ruff / diff PASS
GitHub Actions          PASS
```

## 验证边界

- 只覆盖 trusted-host QEMU unified session；
- HTTP fixture 是受控本地 endpoint，不是任意公网服务；
- BLE 是外部 Bumble peer 经 HCI-UART，不是 bit-exact S3 controller/RF；
- 不覆盖 namespace-managed、Tab5 或 cross-host companion；
- 不覆盖 cross-host process migration；
- 无 physical hardware、RF、功耗或电气验证。

## 风险与回滚

主要风险是把 PID reuse 或无关进程误当成 companion。当前要求 exact
start token 与完整 command SHA256 同时匹配，否则 fail closed。失败路径会
终止已证明由该 session 拥有的 QEMU/adopted companion，避免假 running 和
进程泄漏。

回滚到 `6120489` 会移除 companion persistence/recovery、continuity trigger
和 evidence delay；原有 QEMU/QMP runtime restart continuity 保留。
