# Linux 活动 CardputerDict 网关跨冷启动恢复阻塞

## 方法

1. 在独立无网卡的 Linux ARM64 VZ 中运行 Device Service 1.99.0、Reviewer 0.27.0、初代 Cardputer 原生 `qemu-wifi` 和原版 CardputerDict 0.6.4。通过标准保存快照入口发出 dry-run，收到 HTTP 202。
2. 观察原版 QEMU、Reviewer 任务及 Device Service 会话均在运行。确认租约为 1、具名网关交接已提交、命名空间及 veth/NAT 存在、可写 Flash 已分配，并观察到原版的 SNTP 流量。同步持久卷后由持有虚拟机的宿主程序直接停止该虚拟机，来宾没有执行退出和主动清理。
3. 另起独立 Linux 启动，挂载原持久卷并以原后端地址和认证配置启动同一 Device Service 与 Reviewer。Linux boot ID 改变，worker 身份保留且代次递增。恢复前核对旧命名空间、网关接口及 NAT 表均已消失。
4. 读取正常的会话详情、生命周期事件和证据 ZIP，核对 Reviewer 的重启和恢复回执。用相同原版及参数调用标准保存快照重试。

## 结果

| 检查 | 实际结果 |
| --- | --- |
| Device Service 会话 | `stopping`，`stop_pending=true`，旧可写 Flash 仍在 |
| Worker | 活动租约仍为 1 |
| Device Service 生命周期 | `stop_cleanup_pending`，网关属于不同内核或 worker namespace |
| Reviewer | `service_error / SIM_PARTIAL / E_SERVICE_RESTART`，恢复记录为 `device_service_recovery_unconfirmed` |
| 旧证据 | HTTP 200，ZIP 12,729 字节，CRC、清单和成员摘要通过，含 6,812 字节 PCAP |
| 标准保存快照重试 | HTTP 409，提示上次设备会话清理尚未确认；旧会话仍占唯一租约 |

前一轮也复现了 Device Service 的阻塞，但测试程序替换了 Reviewer 连接所用的后端端口，导致 `backend_identity_mismatch`。本次修正对照保留两个服务的监听端口、后端 URL 和认证配置，消除了该测试变量，仍得到 HTTP 409。

## 原因和边界

当前 Device Service 恢复流程要求网关记录与当前 Linux 内核和 worker namespace 匹配。跨启动后该检查返回待清理，保留租约和 Flash。Reviewer 在收到未确认的清理结果后拒绝重试。设备服务的中断事件与旧证据仍可读。

修复设计需要由可信的宿主或部署控制面证明原虚拟机已经停止，并将证明绑定到原 VM incarnation 和对应持久卷的独占交接。部署控制面证明缺失、状态被迁移或所有权仍不明确时，应保持现有保护。修复、同原版的中断后播放成功、常驻 Linux 路由和实体设备均为 NOT RUN。两台测试虚拟机已停止，Burner 未提交。

[结构化记录](run.json) · [脱敏证据摘要](evidence/linux-active-cold-gateway-recovery.summary.json) · [ESP Emulator 源码仓库](https://github.com/m5agent/m5stack-esp-emulator)
