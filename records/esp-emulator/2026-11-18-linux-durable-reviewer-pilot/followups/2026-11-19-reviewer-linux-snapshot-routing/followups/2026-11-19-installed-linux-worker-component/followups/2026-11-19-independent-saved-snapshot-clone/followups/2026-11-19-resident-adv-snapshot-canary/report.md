# Reviewer 0.31 常驻 CardputerDict ADV 原版发音复审

从常驻 Reviewer 0.31.0 的已终态审核发起一次 `POST /api/reviews/{job_id}/snapshots`，采用 `saved_snapshot` 并关闭提交。HTTP 202 创建一个独立子任务。实际创建记录和在线会话匹配 `cardputer_adv_pronunciation` 路由及同一常驻 Linux Worker。子任务终态为 `done / SIM_VERIFIED`。

原版 BIN 为 2,141,568 字节，SHA-256 `21b7a88e7e58f18674184a58193d30f2722ddd690b4803d9b403b63ec0796d14`。组合 Flash SHA-256 为 `f517333f24bcce896ff9f2a0e783102000ccfae2d2da212fafbe4e9a45c6598c`，核对了应用分区。Linux 采用 Device Service 1.99.3、`qemu-wifi` 及 ARM64 Xtensa QEMU `1733f511c4528cbd991e673069ecedf261b7043e8302553e050924089ce09bff`。运行时和 API 摘要见[执行记录](run.json)。

启动观察持续 60.130 秒并采集 13 个帧样本。真实按键按顺序打开配网菜单、选择预设网络、清空检索框、输入 `hello` 并触发发音，18 步均获设备接收确认。来宾抓包通过 DHCP、受控 DNS、SNTP 校时及 TLS 收发复核。宿主和 Linux 转发记录另对照 SNTP 与 TLS 的实际字节数量及 SHA-256。

预置的 64 MiB SD 镜像校验通过，起始镜像没有目标缓存。审核后从 SD 缓存读回 10,605 字节 MP3。实际 I²S 链路生成 84,992 字节 PCM，独立按有符号 16 位小端解码得到峰值 7,051。音频 API、Reviewer 证据和停止后的 Device Service 证据中 PCM 逐字节一致。独立复查还从已留存的 ZIP 提取抓包和网络证据，比对跨接口载荷，并核对网络命名空间已回收。

源任务 SQL、事件、文件和 API 前后相同。既有 133 条审核与 2,858 个证据文件重新比对一致，早先的 Core2 证据载荷也一致。保留新的停止会话，释放工作 Flash，结束时活动租约和待对账创建归零。macOS 主后端未新增会话。

复核时从同一原版终态选择保存快照，配置 `cardputerdict_adv_pronunciation` 放行及同 Worker 的 SD 种子。在一次 `submit=false` 请求中记录来源绑定、按键、网络与输出，停止后核对源记录及同会话归档。[证据摘要](evidence/resident-adv-snapshot.summary.json)给出夹具、输入顺序、压缩包和保留载荷摘要。

本轮为 virtual-device validation，覆盖这一版固件及批准的发音路径。物理设备、扬声器声学、浏览器和新的拒绝对照为 `NOT RUN`。本轮只发送一次请求，未提交 Burner。
