# M5TabOS 0.9.1 原版在最终 Device Service 1.91 的复验

固定 Device Service `c7e25be5410d3a9968107bc7a0cab5acb9d708bc`、OpenAPI 1.91.0、esp-emu 1.1.0 与同一份 M5TabOS 0.9.1 原版。隔离服务保留 GT911 默认板型，只给该原版的归一化 SHA 设置 ST7123 覆盖，以标准 HTTP API 上传、导入及创建会话。启动时没有连接调试器或上传 ELF，原生 co-sim 日志开启用于读取 GPIO/I²C 事件。[最终源码](https://github.com/m5agent/m5stack-esp-emulator/tree/c7e25be5410d3a9968107bc7a0cab5acb9d708bc) · [此前同版板型对照](../../README.md)

## 运行结果

- 原版输出 16 张完整画面，其中 15 张非黑，未见运行时读零告警。欢迎页帧和时区页帧的 SHA-256 分别与此前同版对照一致。
- 对原版同会话发送面板坐标 `(530, 1147)` 的单次触摸。ST7123 来宾消费了两份报告，坐标寄存器读取增量 9，状态读取增量 10。GPIO23 按来宾时钟出现低、高、低、高，随后回到空闲。点击从欢迎页进入时区页。
- 保留同会话证据 ZIP 并核对可读性、完整归一化 Flash、清单和各文件 SHA-256。停止会话后，工作 Flash 已释放、所属 P4/C6 进程退出、活动租约为零。[固定身份、输入和帧哈希](evidence/final-191-board-touch.summary.json)

本轮只覆盖这份原版的启动显示和指定触摸。未测试外网、账户、USB 枚举、浏览器或实体硬件。未提交 Burner。
