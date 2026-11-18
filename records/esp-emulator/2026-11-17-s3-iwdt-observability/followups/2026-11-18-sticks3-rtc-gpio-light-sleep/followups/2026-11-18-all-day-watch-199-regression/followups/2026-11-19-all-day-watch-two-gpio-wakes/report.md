# 原版浅睡、短时出帧与后续黑帧

上一轮同一原版在 B 键唤醒后取得非黑帧，证据包末帧为黑色。本轮在同一个原版会话中，对每次新截屏的前后各读取一次 QMP `query-status`，核对黑帧出现时的客体状态。使用冻结 Device Service 1.99.0、原版合成 Flash、S3 ROM 和原生 QEMU，身份见摘要。该次会话禁用来宾网卡。

1. 使用独立的 Device Service，通过 `POST /api/v1/artifacts` 上传保留原版，然后 `POST /api/v1/firmware` 以 `device_id=sticks3`、`kind=merged` 合成，确认原版与归一化 Flash 的 SHA-256。通过 `POST /api/v1/sessions` 创建单个 `runtime=qemu` 来宾。
2. 从首次有效帧起，按摘要的时间分别发送 A 点按、B 点按、B 按下和释放。两个点按的稳定等待为 1.0 秒，按下与释放各为 0.1 和 0.05 秒。等待 QMP `suspended` 并取得黑帧。
3. 用 `POST /api/v1/sessions/{id}/input` 发送语义按钮 `B` 的 `click`，用只读 QMP 确认恢复 `running`。使用 `GET /api/v1/sessions/{id}/frame.png?max_age_ms=0` 取新帧，采集前后均读 QMP。第二次自然挂起后只再点一次 B。
4. 观察窗口中收集崩溃 API、串口和同会话证据 ZIP。核对 ZIP CRC 和清单中每项 SHA。以 `purge=0` 停止，核对历史可读、可写 Flash 释放、租约清零及独立服务退出。

两次在按键请求后约 0.43 秒读到 `running`，并有新的完整非黑帧。两轮各采集 15 帧。每轮前 14 帧都在持续运行时取得并均有非黑像素，最后一帧前后均为 `suspended` 且像素全黑。两轮的状态转变分别发生在 18.792 至 20.817 秒和 18.766 至 20.795 秒的采样间隔。最后的证据包同时保持黑帧与一次上电，未见 IWDT、panic 或软件复位。

这解释了此原版在此路径上先能出帧、后续取证变黑的场景。客体进入浅睡与黑帧在同次观测中一致，未测实体背光、电气行为、外部 32.768 kHz 慢钟或其他唤醒源。该轮无代码改动，Burner 未提交。
