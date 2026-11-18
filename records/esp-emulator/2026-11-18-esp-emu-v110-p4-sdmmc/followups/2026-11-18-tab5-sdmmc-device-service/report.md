# Tab5 SDMMC 原生会话、复位与导出

## 固定环境

复位批次固定 Device Service 构建 57d397462e661e608e7c3ae2a878e80527d08e84，独立无复位批次使用 002c490083707cd0966551d53b2463e9797f349c。后续提交同步验证清单，运行时实现字节和 OpenAPI 1.90.0 SHA-256 28e57b04345a9bf6b5e65b1cb8e0a44d11bdb734d15a69581ebd6e60ad78cb55 保持相同。P4 与 C6 进程使用固定 esp-emu 1.1.0。固件是 ESP-IDF v5.5.4 的 SDMMC 示例改编，按官方 Tab5 BSP 使用 SDMMC slot 0、4-bit 和板载 LDO4。ROM、eFuse、固件、规范化 Flash、SD 种子和证据的 SHA-256 见回执。[复位批次](evidence/tab5-sdmmc-http-reset-summary.json) · [无复位批次](evidence/tab5-sdmmc-http-no-reset-summary.json)

## 会话与负控

- 两批各执行三个会话，分别使用 32 MiB FAT16 种子、该批停机导出的 SD artifact 和空卡控制。各有卡会话均发生实际挂载、文件写读及卸载，随后停机 inventory 和独立 FAT 检查验证内容。空卡控制中来宾挂载失败。
- 运行中 inventory/export 被拒绝。停机后核对 ZIP CRC、清单和 SD 收据，保留历史。导出的镜像按 SHA-256 标识。新会话的输入哈希与上一会话的输出哈希匹配。示例进入新会话后会重写并读回文件。
- 复位批次在写入后调用正常会话 reset。返回 HTTP 200，同一会话租约保留，P4/C6 进程均替换。新 P4 启动前独立确认会话 SD inode 与 SHA-256 仍是复位前的写入结果。来宾之后再次挂载、写读、卸载，输出另一个哈希。输入种子保持原样。
- 未准入固件与旧后端均返回 HTTP 409 storage_not_supported。两个负控没有创建会话目录、历史、租约或进程。所有启动过的会话均释放工作 Flash，停机后零活动租约，所属进程退出。

## 容量

直接控制器对照使用 48 MiB 和 48 MiB 加 512 字节两份镜像。两轮 CSD 均报告 98,304 个 512 字节扇区。额外一扇区在来宾可访问容量之外。Device Service 因此要求 Tab5 镜像大小是 512 KiB 的整数倍，普通 QEMU SDMMC 保留原容量规则。直接控制器负责 CSD 容量对照。另用最终 57d39746 走标准 HTTP 接口，48 MiB FAT16 完成挂载、写读和导出，增加 512 字节的种子在分配租约前返回 HTTP 400。[CSD 容量回执](evidence/tab5-sdmmc-slot0-geometry-summary.json) · [HTTP 容量对照](evidence/tab5-sdmmc-http-capacity-summary.json) · [esp-emu 1.1.0 SD 格式说明](https://github.com/espressif/esp-emulator/blob/v1.1.0/docs/guides/CLI.md#sd-card)

## 复现

固定 ESP-IDF v5.5.4 原版 SDMMC 示例及 Tab5 slot 0 BSP 设置。用 512 KiB 整数倍的 FAT16 种子，在隔离 Device Service 用标准 API 上传并导入来宾固件。配置匹配的 1.1.0 后端，按规范化固件 SHA 准入该配置，用 storage.sd_image_artifact_id 创建会话。验证实际串口和宿主镜像，再按各批次调用正常 reset 或 stop，导出并新建第二个会话。空卡和旧后端各用独立会话请求。逐一核对原 artifact、收据、ZIP、目录详情及租约。[构建与证据验证步骤](https://github.com/m5agent/m5stack-esp-emulator/tree/57d397462e661e608e7c3ae2a878e80527d08e84/tests/firmware/tab5_sdmmc)

本轮覆盖标准 API 通过原生模拟 SDMMC 控制器挂载和写读。合成 SDK 会话的 C6 证据覆盖伴生进程。C6 网络、实体硬件、热插拔、交互以及 98TAB5 正常启动仍开放。原始工作镜像、地址、进程和会话标识留在受控目录。

## 98TAB5 旧诊断的画面抄录补记

对 A10 保留的原始图片再次用 macOS Vision OCR 读取。PNG SHA-256 为 75bdb285e5c43b2252701fcbb37f43208ab12860a43d77ab386dea0af2a44250，提示准确写作 “No system disk. Insert one and reset.”。旧回执的 visually_read 字段曾写成 “No boot disk”。此前自然启动、调试时序和无启动盘诊断的结论继续沿用原始证据。[此前启动路径记录](https://github.com/m5agent/agent-work-logs/tree/bb8e4e4490c0647d1f95924b11cbe5a705649686/records/esp-emulator/2026-11-18-native-littlefs-http-diagnostics/followups/2026-11-18-98tab5-cpu1-panic/followups/2026-11-18-tab5-startup-paths)
