# 原生 Tab5 DSI 断线重连与旧帧失效

旧版 Device Service 1.99.1 在已出帧的 DSI socket EOF 后清空帧缓冲，接收线程退出。厂商 1.1.0 协议允许显示端重新注册并在新连接发送完整首帧。候选 1.99.2 在接收完整基准帧后为断线提供有界重连。断线期间无可用画面即返回原有 HTTP 409，与同版本 OpenAPI 一致。 [厂商 DSI 协议](https://github.com/espressif/esp-emulator/blob/v1.1.0/proto/esp_cosim.proto#L1070-L1086)。候选提交为 `b221c87632b087d099bba00385015668a131d0a1`。

两版均在独立 Device Service 使用标准 `/api/v1/artifacts`、`/firmware/import`、`/sessions` 和 `frame.png?max_age_ms=0&orient=panel`，原版 M5TabOS 0.9.1 经相同 ST7123 Part、ESP32-P4 ROM、eFuse 和 C6 固件运行。候选的唯一测试故障钩子让本机操作系统断开当前服务拥有的一条 DSI TCP socket。未停止来宾或变更来宾内存。取帧和触摸执行普通产品代码。 [固定源码、原版和工件哈希](evidence/tab5-dsi-reconnect.summary.json)

| 会话 | 实测结果 |
| --- | --- |
| 1.99.1 基线 | 断线后公开取帧返回 `409 tab5_dsi_frame_unavailable`，`capture_status=disconnected`，停机前 ZIP 报 `NOT_AVAILABLE`。独立客户端按官方协议重新挂接，读到完整欢迎页，第 213 帧。真实点击后该客户端读到时区页，第 259 帧。原服务仍返回 409。 |
| 1.99.2 首次冷启动 | 38 秒内 148 个取帧请求均为 HTTP 409，一个 ROM 启动且无软件复位。未注入断线，未执行重连验证。保存失败 ZIP。 |
| 1.99.2 欢迎页断线 | 9 次 `disconnected` 的 409。公开 API 恢复完整、同像素的欢迎页，原生帧号 147→211，来宾时间同步增加。从断开到完成恢复检查点 0.657 秒。实际点击 `(530,1147)`，2/2 个 ST7123 报告由来宾确认，更新为时区页。 |
| 1.99.2 时区页断线 | 10 次 `disconnected` 的 409。公开 API 恢复完整、同像素的时区页，原生帧号 264→315，来宾时间同步增加。从断开到完成恢复检查点 0.668 秒。实际点击 `(606,365)`，2/2 个报告获确认，应用从 UTC−3:00 更新为 UTC−2:30，第 369 帧。 |

候选成功会话只启动一次，没有软件复位。两次断线及后续触摸都属于相同的 P4、C6 和同一会话。依次核对 ZIP CRC、清单成员哈希和对应帧。`DELETE ?purge=0&retain_flash=0` 后历史保留，可写 Flash 释放，进程均已退出，租约为零。说明中的恢复时间包含采样与证据检查点的开销。

本轮覆盖连接断开后的完整首帧恢复。静默丢失稀疏行、持续高负载、其他面板、实体硬件、浏览器和常驻部署未执行。没有提交 Burner。原始 ZIP、PNG 和完整日志保持私有。
