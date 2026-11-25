# 根因和复验

## 同源故障对照

在 cores3-wasm-uiflow-workbench-lvgl-wallclock-candidate 运行 CoreS3 编程镜像 b9fe8334023c1b1f95e7c51b3a63724e621a6789812083848ed3ea7eaa332d49。上一版锁定运行时 9c37ace1ef22b32ab1c640f20dc3043dfad200f2b83a104a9d6d96ecffae1372 收到两条 guest-reset。软件复位在 ROM entry 后出现 TCG init_ffi_layout 参数数量断言。文档 WDT 确实触发，观察 40.688 秒无新 READY。两种失败分别保留。

早期 96c7f8ba… 的只读 HMP 诊断中，CPU0 进入 ROM，CPU1 固定于固件 IRAM 0x403894f4 的自跳。匹配固件的反汇编显示这是 esp_restart_noos() 在最后一个 APPCPU 软件复位脉冲后的指令。ESP-IDF 双核重启从 CPU1 向 CPU0 发出两次 RTC 复位请求，并在解除 CPU0 停顿后复位 CPU1。旧模型把两个 CPU0 请求都作为全机复位处理，忽略 CPU1 的本地复位，RTC 的 CPU stall 回调也为空。[ESP-IDF 参考重启流程](https://github.com/espressif/esp-idf/blob/v5.5.1/components/esp_system/port/soc/esp32s3/system_internal.c)

## 改动和复验

浏览器 QEMU 源层 0040 在目标核心的安全执行点处理 RTC 软件复位脉冲，并把 RTC 的停顿及释放请求接到 Xtensa RUNSTALL。CPU0 复位仍会让浏览器结束旧的 UART 控制台代次。正常启动中的 CPU1 本地复位可独立完成。宿主全量复位在重置 CPU 前清除 RTC 软件停顿位，保留 RTC scratch 与复位原因。QEMU 的数字复位和 -no-reboot 退出分支继续走原路径。

按模拟器仓库 scripts/qemu-wasm-build/README.md 使用锁定 Emscripten 3.1.50 做完整源构建，生成 WASM 42da214947ba6a0c57aff53f49732fd8bb815ea950ebf808319f1ef670db7558。用 platform/tools/build_public_site.py 导出隔离的静态站点。通过真实浏览器工作台提交软件复位和文档 WDT，单独通过 QMP 路径测试宿主复位。可用 M5_UIFLOW_GUEST_RESET=software 或 watchdog 运行仓库 platform/tests/test_public_uiflow_guest.mjs 中相应回归。文档 WDT 复验使用已验证显式 from hardware import WDT 的示例源，SHA-256 741f27a3801f312125da258aa58bfb2a3610e458c3bc6285380b7c4d9c7a813a。

软件复位在两个实际 CPU0 复位事件后，于代次 2 输出新 READY，旧程序取消，随后在同一来宾执行新的 UART 程序。随后普通宿主复位进入代次 3 再次运行。独立文档 WDT 会话看到 Task watchdog got triggered 和 mpy_machine_wdt，代次 2 约 10.6 秒获得新 READY，并运行新程序。写入 PROCPU 停顿位后执行宿主 Reset，实际 RTC 读回由 2 33 变为 0 0，代次 1 恢复编辑。这三个锁定浏览器会话均为 QMP 正常退出，实际 Worker 全部回收。

同一锁定 WASM 复验 Cardputer-Adv 原 Arduino Display 和 Keyboard 镜像。实际渲染 240×135 动态帧，Delete 删除末尾字符，Enter 提交输入。此前同一路径的 UIFlow2 键盘固件通过 69 项检查，含 TCA8418 FIFO 的 11 个键按下和释放。三次均正常退出并回收全部 Worker。独立的 56 键 IRQ 镜像未执行。[Cardputer-Adv 证据](evidence/cardputer-adv-regression.summary.json)

该记录覆盖上述固件、镜像和浏览器执行路径。正式托管、原生和真机未执行。旧版 TCG 断言作为失败信号保留，未验证其是否可由无关指令流独立触发。摘要保留实际身份和观察结果，省去完整 UART、QMP、机器路径、浏览器端点和会话标识。
