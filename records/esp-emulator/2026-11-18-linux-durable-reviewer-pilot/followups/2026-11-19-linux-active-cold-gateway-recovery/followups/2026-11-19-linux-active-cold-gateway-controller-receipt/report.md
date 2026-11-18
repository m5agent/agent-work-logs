# 用宿主停机凭据恢复 Linux 活动审核

## 问题和改动

此前原版 CardputerDict 的活动审核在独立 Linux 启动后留下待清理会话、工作器租约和可写 Flash。新内核看不到旧网络对象，但仅凭 boot ID 变化无法判定旧宿主已停止。Reviewer 保留未确认的清理记录，标准复审返回 HTTP 409。

候选增加只由本地进程启动配置指定的 `--namespace-cold-recovery-receipt`。凭据位于工作器状态目录以外的只读宿主挂载，绑定原内核、后继内核、工作器、确切会话与启动以及原网关记录的摘要。匹配后生成独立的 `prior_vm_terminated` 回执并继续常规回收。既有网关与隔离记录原样保留。未提供相符凭据时，跨内核恢复继续保留待清理状态。

## 同一原版和同一 Linux 后继启动的对照

1. 在隔离无网卡的 Linux VZ 中启动标准保存快照审核，收到 HTTP 202。实际观察到原版 QEMU、Reviewer 任务、已提交的具名网关、一个租约、可写 Flash 和 SNTP 回包。
2. 拥有旧虚拟机的宿主进程撤销该实例的两个 Virtio Socket 监听，调用 VZ 停机并等到完成，以当时的真实持久卷和旧网关记录生成宿主确认。旧来宾未执行正常退出。下一台 VZ 使用同一独占私有持久卷和固定后端配置。
3. 在后继 Linux 启动中，先以标准配置重启两项服务。未提供凭据时，Device Service 保留一个租约和可写 Flash。Reviewer 保留清理未确认结果，重试返回 HTTP 409。旧 ZIP 已成功导出。
4. 停止以上两个自有进程并继续使用同一 Linux 内核。宿主核对停机确认、卷和会话记录后才发放只读凭据。用相同监听地址、Reviewer 后端和认证配置启动服务。旧会话进入 `failed`，租约和 Flash 释放，Reviewer 记录 `released`。
5. 同一已保存的原版重试 HTTP 202，成立的 DNS、SNTP、TLS、MP3 缓存和 PCM 应用断言最终返回 `done / SIM_VERIFIED`。测试代理到宿主取得的 SNTP 和 TLS 转发字节数及摘要相互匹配。

## 证据

| 检查 | 结果 |
| --- | --- |
| 旧历史 | 待清理和已恢复两份 ZIP 均校验 CRC、清单与成员哈希。旧文件的 9,259 字节 PCAP 与宿主在停机后留存的原始文件完全一致 |
| 旧网关记录 | 网关和隔离记录原样保留，并有单独的 `prior_vm_terminated` 回执和生命周期事件 |
| 原版音频 | SD 缓存与固件 CA 预检取得的 10,605 字节 MP3 一致。证据 ZIP 和 API 的 84,992 字节非零 PCM 摘要一致 |
| 新审核证据 | 标准 Reviewer 和 Device Service ZIP 均通过校验，22,702 字节 PCAP 逐字节一致 |
| 清理 | 旧可写 Flash 已释放，新会话停止并释放 Flash。工作器租约归零，旧与新测试 VZ 和转发进程全部退出 |

本试验覆盖宿主已确认停机且持久卷交接明确的虚拟路径。宿主控制器发放凭据前还须确认按租约分配的宿主侧资源已撤销和回收。后端迁移、宿主崩溃后没有停机证明、常驻 Linux 部署和实体设备为 NOT RUN。Burner 未提交。

[此前无凭据的失败记录](../../README.md) · [结构化记录](run.json) · [脱敏证据摘要](evidence/linux-active-cold-gateway-controller-receipt.summary.json) · [ESP Emulator 源码仓库](https://github.com/m5agent/m5stack-esp-emulator)
