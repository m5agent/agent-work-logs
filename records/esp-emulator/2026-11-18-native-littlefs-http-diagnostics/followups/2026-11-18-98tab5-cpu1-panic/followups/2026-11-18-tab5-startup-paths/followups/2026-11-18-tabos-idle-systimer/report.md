# M5TabOS 原版空闲任务与定时中断报告

此前用同一原版 M5TabOS 0.9.1 观察到两个核心在 WFI 后的相同地址，没有完整画面。本轮固定 Device Service 源码 `57d397462e661e608e7c3ae2a878e80527d08e84`、原生 esp-emu 1.1.0 及原版固件 SHA-256 `08aa10d0caeaf7835cd2f93ee66a8d2042ce15bd6e52350df6b96c70ec8bbe3e`，在普通 Device Service 会话使用只读 GDB 采样。[此前原版观察](../../README.md) · [本轮回执](evidence/tabos-idle-systimer.summary.json)

## 两核等待与中断

- 两核现场 PC 都是 `0x4ff08c9a`，原版二进制在前一条指令 `0x4ff08c96` 执行 WFI。调用栈和当前任务控制块指向 IDLE0 与 IDLE1，两核都在 FreeRTOS 空闲任务中。
- SYSTIMER 周期目标 0 和 1 均出现 raw 状态，分别映射到 CPU0 IRQ 19 和 CPU1 IRQ 17，SYSTIMER 中断使能掩码为 `0x7`。
- 原版处理函数 `0x4ff11ef2` 清除 SYSTIMER IRQ，按当前 hart 更新各自的已处理 tick 计数。在约 4、10、16 秒的对照中，两个计数都从 3,252 增至 9,567，再增至 15,929。FreeRTOS 的全局调度 tick 同期从 3,252 增至 9,567 和 15,928。采样时常见同一空闲地址，两核仍处理了周期中断。
- 三个 25 秒会话各一次 ROM 启动，无软件复位、低功耗看门狗复位及完整画面。九次采样均正常分离。证据 ZIP 验证通过，所属进程退出，工作 Flash 已释放，各会话停机后活动租约为零。[三个会话统计和 ZIP 哈希](evidence/tabos-idle-systimer.summary.json)

## 复现和边界

按回执固定后端、ROM、eFuse、C6 工件和原版 Tab5 固件。经标准 HTTP 接口上传、导入并创建普通会话。核对固件及应用区字节后，依次在约 4、10、16 秒用 GDB 读取两个 hart 的 PC、保存返回地址与当前 TCB 名称、SYSTIMER 状态、路由和 RAM 中三个计数器。记录同一会话的串口、画面采样和停机后的 ZIP。原版指令与 ESP-IDF v5.5.5 的等待函数、PM idle 路径和 SYSTIMER 处理流程一致。[等待函数](https://github.com/espressif/esp-idf/blob/v5.5.5/components/esp_hw_support/cpu.c) · [PM 空闲逻辑](https://github.com/espressif/esp-idf/blob/v5.5.5/components/esp_pm/pm_impl.c) · [SYSTIMER ISR](https://github.com/espressif/esp-idf/blob/v5.5.5/components/freertos/port_systick.c)

固定原版在当前模型中的通用周期中断已交付到两个核心。应用就绪、显示初始化和首次应用任务等待仍未归因。以上采样在调度启动后进行，未捕获首次应用事件。未执行真机、浏览器、外网或 Burner 路径。
