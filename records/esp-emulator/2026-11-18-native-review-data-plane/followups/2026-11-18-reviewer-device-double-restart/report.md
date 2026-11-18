# 两套服务同时退出时的活动审核恢复

## 两个基线场景

之前已验证 Device Service 持续运行时单独重启 Reviewer。本轮在隔离 ARM64 Linux 虚拟机内，对活动审核同时 SIGKILL Reviewer 和 Device Service。两组都在来宾 STA 数据面工作时采集同会话证据，核对两个服务退出且旧 QEMU 和网络监督进程仍存在，再用各自的持久状态启动服务。新版前的共同源码和 OpenAPI 指纹见[机器摘要](run.json)。

| 旧版实际启动次序 | 用户 Retry 前的观察 | 第一次标准 Retry |
| --- | --- | --- |
| 精简 Linux，Device Service 先启动 | 旧 worker 身份保留，世代推进。旧会话和审核已记录终态，Flash 后续释放。旧 QEMU 和监督进程仍存在，原命名空间仍有两个进程，审核协调已记录 `released`。 | HTTP 202，旧进程仍存活时创建新会话。 |
| 安装 procps，Reviewer 先启动 | 设备服务离线时记录 `device_service_unavailable`。Device Service 就绪后，两个旧进程、租约和 Flash 均已释放，原命名空间已清理。到自动观察窗口结束时，Reviewer 的协调记录仍为 pending。 | HTTP 202，只创建一个新会话。 |

两组均保留中断审核的 `service_error / E_SERVICE_RESTART / SIM_PARTIAL`。活动与重启后同会话证据 ZIP 均可读，校验清单与 CRC 通过。抓包各为 54→57、56→57 包，活动抓包和活动串口均为重启后证据的精确字节前缀。两组随后用同一份 Cardputer ADV STA SDK 固件验证实际 STA 与 HTTP POST/TCP，Retry 的综合审查均为 `manual_review / E_NO_FRAME`。该固件无界面，画面未验收。[有界基线回执](evidence/baseline-double-service-recovery.summary.json)

旧版精简场景缺少已保存的进程启动身份，procps 对照保存了身份。第二次冷启精简场景复现同一结果，确认 `ps` 不存在，且存活的是原 QMP 绑定的监督进程和来宾。这两组基线同时改变 Linux 进程工具和启动顺序，因此只分别记录观察到的失败。有界摘要保留完整回执的 SHA-256、证据指纹和顺序观察，移除了进程标识、连接地址、插槽路径与原始抓包。

## 候选和验收边界

Device Service 根据 Linux 内核提供的进程启动身份以及对应会话的命名空间、进程和 QMP 限定归属，确认受控旧运行时已清理。Reviewer 在 Device Service 暂时离线时保留等待状态，恢复连接后自动继续协调，完成确认前暂缓重试。功能测试绑定 Device Service `7e2cca17c5bbae40b6e4380b65e891a7ca9d0454` 和 Reviewer `a295e0173a0e3157c120de8ba6fcec128aa665c1`，具体 OpenAPI、Linux QEMU、ROM 和固件指纹见机器摘要。

| 新版实际启动次序 | 用户 Retry 前的观察 | 同会话抓包 |
| --- | --- | --- |
| Device Service 先启动 | 旧 QEMU、网络监督进程、原命名空间、Flash 和租约均已释放，审核协调返回 `released`。 | 57→57 包，活动内容是停止后抓包的精确字节前缀。 |
| Reviewer 先启动 | 设备服务离线时先记录 `device_service_unavailable`，设备服务上线后自动转为 `released`。旧来宾、命名空间、Flash 和租约均已释放。 | 56→57 包，活动内容是停止后抓包的精确字节前缀。 |

两组中断审核均保留原有服务错误记录。在启动标准 Retry 之前，已核对旧租约为零、原命名空间里无残留进程，并成功验证旧证据 ZIP 的 CRC 与文件清单。两组标准 Retry 各新建一个会话，实际同固件 STA 与 HTTP POST/TCP 均通过。两组新会话均释放 Flash、恢复命名空间数量并保留相同抓包来源。综合审核仍为 `manual_review / E_NO_FRAME`。隔离虚拟机未接外部网卡或发布端口，数据仅在本地网络命名空间内流动。[有界 Linux 候选回执](evidence/linux-paired-restart-release.summary.json)

同一候选源还在 macOS 用原版 Core2 2048 独立回归既有的单 Reviewer 退出场景。创建响应扣住后终止 Reviewer，恢复旧会话时释放租约和 Flash，保留旧证据与独立会话。标准 Retry 新建实际来宾，左、右、上、下四方向棋盘断言通过，终态 `done / SIM_VERIFIED`。[原版 macOS 回执](evidence/macos-active-create-regression.summary.json)

最终 Device Service `a7dbd9808a09bc507b657995dba079b8075badcf` 调整了状态文档长度和 API 清单指纹，并重新生成项目快照。实际运行使用的 `7e2cca17…` 与最终提交的服务代码和 OpenAPI 字节一致。最终平台完整套件 2,462 项中 2,452 项通过、10 项跳过，验证器通过。Reviewer 套件 289 项通过。[Device Service 最终源码](https://github.com/m5agent/m5stack-esp-emulator/tree/a7dbd9808a09bc507b657995dba079b8075badcf)

## 复现

1. 离线 ARM64 Linux 虚拟机复用固定 Linux 原生 QEMU、ROM 和 Cardputer ADV STA SDK 固件。为每组独立使用持久状态，通过 Reviewer 的保存快照标准 Retry 创建一个活动网络审核，核对来宾 DNS、UDP、HTTP POST/TCP 与本地证据 ZIP。
2. 两个拥有的服务均 SIGKILL。观察旧 QEMU 与网络监督进程、实际命名空间、租约和 worker 身份。Device Service 先启动组在设备健康时读取会话恢复状态。Reviewer 先启动组在设备服务离线时先读取审核协调状态，然后恢复 Device Service。
3. 在触发标准 Retry 前记录自动恢复是否收敛，核对旧进程、命名空间、租约、可写 Flash 及同会话证据。标准 Retry 后确认仅创建一个新会话，分别核对 STA 数据链路、综合审核终态和证据。释放所拥有的进程和租约，关闭隔离虚拟机。

实体设备、浏览器和 Burner 提交为 **NOT RUN**。
