# ESP Emulator worker-local QEMU across network namespaces report

## 背景

前一个里程碑已经分离 worker 的中央 control API 与 runtime API，但真实
worker-local QEMU fixture 只有实现，尚未执行。它还存在三个执行障碍：

1. fixture 从没有 executable path 的 profile 注册表读取 QEMU 路径；
2. Device Service 只认识仓库登记的 macOS QEMU 路径，Linux worker 不能
   安全替换为同 commit 的 Linux build；
3. `qemu_reaped` 用完整命令字符串 substring 判断，runner 自己的
   `--qemu-path .../qemu-system-xtensa` 参数会被误认成活跃 QEMU。

首次远端 CI 还暴露了无 QEMU control-plane 与 QEMU execution 的 result
形状不同：前者是字符串，后者是对象。统一 evidence 摘要时必须同时接受两种
形状，且 QEMU 路径还要保留嵌套对象里的 evidence SHA256。

目标是在不改变 central job ownership 的前提下，让 worker namespace 内的
独立 Device Service 启动真实 StickS3 QEMU，并把 evidence 返回 central
queue 的 terminal result。

## 结论

worker-local execution path 已完成 `18/18 PASS`。central control service
没有接收 session API；runtime service 独立拥有 episode、artifact/firmware、
QEMU 和 cleanup。job 最终为 `completed/PASS`，firmware/QEMU SHA256、
serial/frame/QOM evidence、token 脱敏、QEMU reap 和 namespace cleanup
均成立。

该结论是 `virtual-device validation`，不是物理跨主机 executor。

## 改动

### Device Service QEMU 路径

- S3 与 LX6 后端支持 `M5_QEMU_XTENSA`；
- C6 后端支持 `M5_QEMU_RISCV32`；
- 绝对路径直接使用，相对路径从仓库根目录解析；
- 默认仍使用设备矩阵登记的路径。

### Worker fixture

- QEMU 可执行路径改从 `tests/uiflow2/device_matrix.json` 解析；
- 新增 `--qemu-path`，并同步设置 worker-local Device Service 的
  `M5_QEMU_XTENSA`；
- runtime 使用 host-image flash 模式，避免调用宿主架构专属的 preparer；
- 保存 worker result、server/runtime/worker logs 和 bounded diagnostics；
- diagnostics 和日志脱敏 token、ephemeral job/session ID 与 loopback host；
- QEMU reap 只识别 `ps` 中的 `argv[0]` 是否为 `qemu-system-*`，命令参数中
  出现同名文字不再产生假失败。
- result fact helper 同时支持 no-QEMU 的字符串 result 和 QEMU 的 object
  result；新增双形状单元测试，恢复 Linux CI 的 control-plane step。

### 文档

- 当前状态、Backlog、workstreams、code map、API、网络方案、服务架构和
  deployment 统一写回 worker-local QEMU PASS；
- 明确保留 cross-host executor/reattach、automatic discovery、
  companion/evidence continuity 和生产调度为 `NOT RUN`；
- 修正 Core2 三 lease 121 轮已经完成，但 platform README 仍写“尚缺两个
  lease”的旧状态；
- 新增文档契约，防止 worker-local QEMU 已 PASS 后重新写回“尚未执行”。

## 执行

环境：

```text
privileged Linux arm64 container
two private network namespaces connected by veth
real Linux arm64 qemu-system-xtensa
StickS3 UIFlow2 image
central Device Service + worker-local Device Service
```

执行的逻辑命令：

```bash
PYTHONPATH=platform/tools \
python3 tests/network/worker_cross_netns/run_test.py \
  --qemu \
  --qemu-path <linux-qemu-system-xtensa> \
  --firmware <sticks3-uiflow2-image> \
  --runtime qemu \
  --out-dir <private-output-directory>
```

## 验证结果

| 检查 | 状态 |
| --- | --- |
| worker exit 0 | `PASS` |
| runtime service started | `PASS` |
| worker route uses veth | `PASS` |
| registration recorded | `PASS` |
| job submitted | `PASS` |
| worker/job heartbeat | `PASS` |
| worker-local execution plane | `PASS` |
| real QEMU started | `PASS` |
| Device Service session created | `PASS` |
| manifest/serial/QOM evidence | `PASS` |
| source/normalized firmware SHA bound | `PASS` |
| QEMU SHA bound | `PASS` |
| terminal `completed/PASS` | `PASS` |
| token not retained in logs | `PASS` |
| QEMU reaped | `PASS` |
| two namespaces cleaned | `PASS` |
| platform tests `368/368` | `PASS` |
| docs contracts `19/19` | `PASS` |
| Node tests `2/2` | `PASS` |
| physical hardware | `NOT RUN` |

GitHub Actions run `40129700779` 在最终文档提交上通过；
`network-namespace-policy` 与 `platform-contracts` 两个 job 均为 `PASS`。
前一 run `40129437594` 的 control-plane result-shape 失败作为修复过程保留，
不计入最终通过证据。

## 验证边界

- 两个 namespace 位于同一 Linux 主机，不能替代物理多主机传输、延迟与
  丢包验证；
- central control service 与 worker directory/queue 的 production
  placement、secret manager 和多机 capacity scheduler 未验证；
- 只验证一个 worker-local StickS3 QEMU job，不是跨设备容量或并发结论；
- evidence-stream 可下载并校验，但断线后的 companion/BLE/evidence 流
  连续性未验证；
- 不是恶意固件 disposable VM，也不是真机、RF、功耗或电气验证。

## 风险与回滚

QEMU 路径 override 只替换可执行文件，不替代匹配的 ROM/eFuse、`pc-bios`、
固件或 target smoke test。错误架构或错误 build 仍应 fail-closed。

回滚最终 current-state 提交
`ec63754f183c7b059fab2d4aa520ab43a307d426`、CI 修复
`461d489f2c36825d4b4ce27421322b56231c34e1` 和实现提交
`902034997afbf1f47949c08f129da101bb90582a` 可恢复
`f0fe0553546032fdf6c5219f8b7278af823d24b2` 的基线。回滚不修改物理设备、
固件或外部队列数据。
