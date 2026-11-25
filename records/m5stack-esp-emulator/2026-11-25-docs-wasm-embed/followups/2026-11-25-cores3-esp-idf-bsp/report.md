# CoreS3 BSP 四个 LVGL 例程验证

按照教程建立空工程，用 ESP-IDF v5.4.1 和 `espressif/m5stack_core_s3^3.0.0`。在本次锁文件中，实际版本是 BSP 3.0.2、esp-lcd-ili9341 2.1.0、esp-lvgl-port 2.9.0、LVGL 9.6.0~1。关闭向后兼容 I2C 选项，Flash 设置为目标机型 16 MB。Widgets 启用文档的默认入口和对应 Kconfig，其他例程各按教程切换为对应的 `lv_demo_*` 调用。供顺序重建的变体工程启用了 Music、Stress 和 Benchmark 的 LVGL 配置，每个镜像各只调用一个。生成 ESP32-S3 合并镜像，比如 `idf.py merge-bin --fill-flash-size 16MB`。

Music 使用默认 factory 分区时，构建报告应用大小 `0x136ba0`，超过 `0x100000`。将 IDF 的 `Partition Table` 设为 `Single factory app (large), no OTA` 扩充应用分区到 1.5 MB。Music 原始程序没有改动，重建可通过，来宾随后输出原应用标记。这个修复覆盖构建和进入应用。

在固定静态导出的浏览器 WASM CoreS3 运行各合并镜像。四个来宾都先报告 `Display LVGL demo` 和 `Returned from app_main()`，随后只捕获黑色 320×240 RGB565 帧。相同 Widgets 合并镜像在独立候选正常时钟的结果一致。停止回执是退出码 0，实际 engine 和 5 个 pthread Worker 都释放。

BSP 界面问题根因待定位。应保留原镜像和 BSP 的 SPI3/ILI9341/显示 flush 路径，再验证实际区域像素、触摸和正常停止。真机、其他 BSP/IDF/版本组合 `NOT RUN`。脱敏摘要保留固件、WASM、屏幕和原始报告哈希，略去环境地址、Worker ID 及完整串口。
