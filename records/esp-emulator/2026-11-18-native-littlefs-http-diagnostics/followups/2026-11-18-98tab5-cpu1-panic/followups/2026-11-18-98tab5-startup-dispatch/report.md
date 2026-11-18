# 98TAB5 启动派发表读回与实际跳转

## 背景与固定输入

此前证据确认 CPU1 先收到非零 ROM 交接地址，随后在转储写入前进入指令访问异常。本轮固定同一原版、同一服务和官方原生后端，使用只读硬件断点核对两者之间的启动派发。[先前记录](../../README.md)

| 项目 | 身份 |
| --- | --- |
| 98TAB5 1.3.0 原版 BIN | `ea4fb0889e4a2c68d472947137908c52c25a663152d3ff78262ce2605440dc6d` |
| 规范化 Flash | `35c636324ea1fcebd12f4752e458936c2ac151a9d171a67f1d624d944b96b0ff` |
| Device Service | [`13df3b8a7ab197df14f57d2ca8bc58919a7eb666`](https://github.com/m5agent/m5stack-esp-emulator/tree/13df3b8a7ab197df14f57d2ca8bc58919a7eb666) |
| esp-emu 1.1.0 | `633a35f993300a765634ed78a2dbcfd5ffcd5c3f2f354a2dddabeb6108240828` |

## 执行与观察

在隔离的原生 Device Service 导入原版，启用 GT911 内置识别寄存器及原生 DSI，绑定摘要中的 ROM、eFuse、C6 固件和运行时。以 GDB 硬件断点和读操作观察 ROM 交接、CPU1 的 DROM 读指令、后续间接跳转和异常保存帧。两次有效会话实际执行 `0x4ff003fc` 的读取，地址为 `0x4015cc58`。接下来的 `0x4ff00400` 间接跳转使用 `0x0`，异常帧记录 `MEPC=0`、`MCAUSE=1`、`MTVAL=0`。原版与规范化 Flash 对应偏移 `0x3cc58` 的四字节均解码为 `0x4ff00cca`。[证据摘要](evidence/98tab5-startup-dispatch.summary.json)

第二次有效会话在调试器分别选择 CPU0 与 CPU1 时，都读到两个派发表项为零。实际读指令的观测来自 CPU1。最初一次 GDB 批处理格式失败已保留，该次执行只作为观察器负对照。两轮有效执行均在 35 秒内记录到 18 次软件复位和零个完整 DSI 帧。三次执行的 ZIP 清单和终态均已核验，Flash、P4/C6 及租约均已回收。[证据摘要](evidence/98tab5-startup-dispatch.summary.json)

## 观察边界

现有证据定位了本轮启动异常的直接路径。活跃 DROM 与文件中同一位置数值不同，缓存或 MMU 的具体原因仍需与正常原版进行控制器级对照。本轮没有修改来宾数据、执行输入或连接外部网络。真机、浏览器和完整显示尚未验证，未提交 Burner。
