# AtomS3 Spirit Level / Motion Face：虚拟设备不初始化显示归因

- 日期 `2026-11-18`
- 结果 `ATTRIBUTED`，范围为一款 AtomS3 公共固件的启动失败归因
- 工作类型 `investigation`
- 工作来源 审查任务 `job-bfe1b7e32389`（lane `SIM_PARTIAL`，`E_NO_FRAME`）
- 关联 issue [m5stack-esp-emulator#235](https://github.com/m5agent/m5stack-esp-emulator/issues/235)
- 环境为审查用 Device Service 同款原生 QEMU 运行时、`m5atoms3-st7735`、8 MiB flash

## 结论

AtomS3 Spirit Level v1.0.0（`c41ba69a80bd83d387808f2c8e562eddbe114733b1bb6ed71aec0c0608e9e393`，609,856 B）在虚拟 AtomS3 上已完成启动并进入应用主循环，但**从未初始化 ST7735S 面板**：60 s 内 0 条 SPI 传输、0 条面板命令、`madctl=0`、帧恒为 125 B 全黑。无 panic、无看门狗、无复位、flash 零变化。同一构建链路的 AtomS3 Motion Face v1.0.0（`648246c46223449355057f22d3cfd959633c71d734a86546f0405646b84b373c`）在独立任务上表现相同。

两个镜像都带 M5GFX `board_detect/...` 与 `" (ST7735)"` / `" (GC9107)"` 标注，说明走运行时板型探测。失败点定位为“应用运行后显示未挂载到 SPI3 面板”，最可能为 M5Unified/M5GFX 运行时板型探测在虚拟 AtomS3 上未返回带显示的 board（与 #230 同类）。已按 virtual-device validation + code-level verification 提交 #235，未修改模拟器代码、未 push 模拟器仓库、未关闭任何 issue。

## 关键证据

- 串口 314 B，停在 `[   449][E][Preferences.cpp:503] getBytesLength(): nvs_get_blob len fail: off NOT_FOUND`。
- `M5SW_I2C_TRACE`：MPU6886 初始化一次，随后 2,759 轮 `0x3A–0x48` 突发读取，证明应用主循环在跑。
- `M5SW_SPI_XFER_TRACE=1`、`M5SW_SPI_TRACE=1`、`M5SW_PANEL_DC_TRACE=1`：12 s 内 0 条传输/命令。
- 帧 128×128、16,384 像素全 `0x000000`、unique colors = 1、frame SHA-256 `7659100791b0b0d9d5707576f6d04cdae4e769ae4ba3034169540fe3990efae5`。
- 默认 ST7735S 与 `M5SW_ATOMS3_GC9107=1` 覆盖运行结果一致。
- crash diagnostics `no_evidence`；QMP PC 落在 FreeRTOS idle `waiti` 桩；flash diff `changed_bytes=0`，QOM diff 为空。

## 未覆盖项

物理 AtomS3 复跑、USB CDC 串口捕获、按键/触摸注入、板型探测返回值插桩、真实面板光学与电气特性均为 `NOT RUN`。Motion Face 未离线复跑，仅有同服务任务证据。
