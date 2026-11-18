# 具名出口网关在审核重启后的归属与回收

此前双服务重启复验覆盖了本地网络命名空间和直接运行的来宾。本轮另外核对命名空间、主机 veth、NAT 表及相邻会话的存续。Device Service 在释放旧会话资源前，需要凭会话归属验证外层网关管理进程与实际网络资源。暂时无法确认归属或清理完成时会保留恢复状态，供重试前继续核对。

## Linux 内核数据路径对照

无外部网卡的 ARM64 Linux VM 先验证对端与网关隔离，随后建立具名网关、veth 和 NAT。实际对端接到挑战包并回包，同时在对端核对源地址转换。清理调用刚返回时，对端 veth 和 NAT 表已消失，主机侧 veth 随后撤除。再次核对时，受测网关的命名空间、主机侧和对端的 veth、NAT 表均已清理，独立对端及其专用实验路径保持至单独清理。最终仅由实验创建的拓扑全部恢复原状。[有界内核回执](evidence/primitive.summary.json)

## 原版 CardputerDict 的审核与恢复

使用 CardputerDict 0.6.4 原版和已准备的字典存储，通过正常保存快照 Retry 启动类型化发音验证。隔离实验对端只响应合成的 SNTP 并读取 TCP 层的 TLS ClientHello，用于识别实际来宾流量和清理边界。无外部连接、无证书验收，未验证发音。

两组在同一类型的隔离 Linux VM 使用相同固件、存储种子、运行时及 Reviewer 0.26.0，分别终止两个服务并先启动 Device Service。旧版 Device 1.96.0；候选为 Device 1.97.0 的 `8fea7bb182afc0094b8c42461673459bb8f1d965`。在两组中，旧服务进程退出时都观测到旧会话的运行时仍存在。

| Device Service 先启动 | 用户 Retry 前的实际观察 | 随后结果 |
| --- | --- | --- |
| 旧版 | 旧会话留在 `stopping`，有 1 个活跃租约并保留可写 Flash。旧来宾、两层监督进程和原命名空间中的两个进程仍存在，具名命名空间、两端 veth 和 NAT 表均未回收。 | 使用仅指向本次实验所拥有外层进程的回收操作，清除旧拓扑。独立会话仍保留。 |
| 候选 | 结合内外层同一次启动的记录确认自动清理完成。旧来宾及监督进程已退出，具名命名空间、两端 veth、NAT 表、租约及 Flash 均已释放。审核记录 `E_SERVICE_RESTART`，恢复协调返回 `released`。 | 标准 Retry 返回 HTTP 202，创建新会话并验证同一原版的 SNTP 及 TCP/TLS ClientHello。新会话终态 `manual_review / E_CARDPUTER_PRONUNCIATION_PARTIAL`，已释放 Flash，活跃租约为零，独立会话仍保留。 |

旧版与候选各自的中断前后抓包均为 26→26 包，抓包和串口都是字节相同的同会话回执。候选新会话保存独立的 24 包抓包。所有参与此次结论的证据 ZIP 均通过 CRC 和清单核对，两组最终关闭实验 VM 并回收全部实验安装的拓扑。初期验证工具的 HTTP 或字段读取中断单独保留，未纳入这组实际 A/B。[有界 A/B 与启动顺序回执](evidence/linux-named-gateway-paired-restart.summary.json)

额外的候选组先启动 Reviewer。仍在用户 Retry 前确认同一次启动的内外层清理记录、目标进程及其命名空间和租约回收，以及独立网关存续。中断前后抓包均为 26 包并核对了字节前缀。新会话的独立抓包含 26 包，HTTP 202 和新会话传输通过，终态仍为同一发音审核 PARTIAL，随后租约归零并关闭 VM。[候选双启动顺序](evidence/linux-named-gateway-paired-restart.summary.json)

Device Service 1.97.0 固定在已实际执行的 `8fea7bb182afc0094b8c42461673459bb8f1d965`，OpenAPI SHA-256 `045a0b29b7b6c3983493b9a59fb3f4b6851f00854239e43740df2137efb745de`。Reviewer 0.26.0 固定在 `a295e0173a0e3157c120de8ba6fcec128aa665c1`。该 Device Service 的 2,469 项平台测试中 2,459 项通过、10 项跳过，验证器通过。[Device Service 源码](https://github.com/m5agent/m5stack-esp-emulator/tree/8fea7bb182afc0094b8c42461673459bb8f1d965)

## macOS Core2 恢复回归

固定 Device Service 1.97.0 候选和 Reviewer 0.26.0，在原版 2048 Game 1.0 的已创建、未收到响应时序终止 Reviewer。恢复后旧租约和可写 Flash 释放，前后证据仍可读取，独立会话持续保留。正常 Retry 仅创建一个新会话，左、右、上、下棋盘断言均通过，终态 `done / SIM_VERIFIED`。此用例覆盖原有 macOS 恢复路径。[原版 macOS 控制](evidence/macos-core2-control.summary.json)

## 复现和范围

1. 使用固定的 Linux 运行时、ROM、原版 CardputerDict 与存储种子。在无外部网卡的隔离 VM 中创建实验对端，使用真实具名出口网关和独立网络命名空间。
2. 在普通保存快照 Retry 后核对授权的类型化输入、同会话 SNTP 与 ClientHello 数据及活动证据。记录受测和无关实验会话的资源范围。
3. 仅终止自己的审核服务和设备服务，按实际场景重启。用户 Retry 前分别核对目标来宾、监督进程、命名空间、veth、NAT 表、租约、Flash 与同会话证据。再用标准 Retry 核对新会话，以及无关会话在恢复前后的对应独立资源。

真实公共 HTTPS、解码与音频、实体硬件和浏览器均为 **NOT RUN**。未提交 Burner。
