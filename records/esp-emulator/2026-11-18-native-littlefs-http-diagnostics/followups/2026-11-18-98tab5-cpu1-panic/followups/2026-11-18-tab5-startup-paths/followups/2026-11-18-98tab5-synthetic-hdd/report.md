# 98TAB5 原版合成磁盘识别复验

## 目标与环境

确认之前只能取到无系统盘画面的原版能否通过普通 Device Service 的 Tab5 SDMMC slot 0 接入合成磁盘。六次会话均运行同一份 98TAB5 v1.3.0，未改动固件、ESP-EMU 运行时或产品源码。失败的普通冷启动单独保留。

使用 Device Service 1.90.0、esp-emu 1.1.0 和 GT911/ILI9881C 的内置识别路径。完整的原始 BIN、规范化 Flash、运行时、ROM、eFuse 和 C6 固件 SHA-256 与会话 ZIP 摘要见[验证摘要](evidence/98tab5-synthetic-hdd-recognition.summary.json)。[Device Service 源码](https://github.com/m5agent/m5stack-esp-emulator/commit/57d397462e661e608e7c3ae2a878e80527d08e84)

## 实际执行

1. 保留原始 32 MiB 空白 FAT16 作为对照。另复制其字节并加入根目录 `HDD.NHD`，长度 20,972,032 字节。512 字节头部使用 `T98HDDIMAGE.R0`，几何为 320 柱面、4 磁头、每轨 32 扇区、每扇区 512 字节。磁盘扇区全部为零。校验两份 FAT、簇链与文件摘要。原固件的首次运行默认路径为 `/HDD.NHD`。 [NHD 文件头参考](https://github.com/joncampbell123/dosbox-x/blob/fb00033436026ae5f8bf5c54536b6505e11c249b/src/ints/bios_disk.cpp)
2. 通过 `POST /api/v1/artifacts` 上传原 BIN 和 SD 镜像，`POST /api/v1/firmware/import` 导入原 BIN。通过 `POST /api/v1/sessions` 启用 Tab5 原生后端。带介质的组通过 `storage.sd_image_artifact_id` 附着独立副本。原版普通冷启动的有卡、无卡两轮均在约 31 秒内复位 16 次，均未取得完整画面。
3. 对未上传介质、空白 FAT16、含 NHD 的 FAT16 分别执行此前的只读启动诊断。CPU1 跳至原固件中的 `0x4ff00cca` 后脱离调试器，再采集同会话 DSI 帧。未上传介质和空白 FAT16 各 20 帧具有相同稳定哈希，实际原字样为 “No system disk. Insert one and reset.”。合成 NHD 的 20 个稳定帧改为另一哈希，画面不再显示该文字。启动诊断的中断时序会改变普通冷启动表现。
4. 在独立的合成 NHD 复验中，于 CPU1 跳转成功后追加硬件断点。原程序到达 FAT 挂载成功分支 `0x4003526c`，传入的设备为 `EMUSD`、32 MiB、40 MHz。随后到达 `HDD: open OK` 的调用点 `0x40021326`，参数现场读得 `/HDD.NHD`、`IDE`。断点和读取取证只观察寄存器和来宾字符串，随后脱离调试器。以实际分支与参数判定磁盘已打开。
5. 在停止前获取证据包并核对 CRC、清单及摘要。随后用 `DELETE /api/v1/sessions/<id>?purge=0` 停止，使用 `GET /api/v1/sessions/<id>/storage/sd` 和 `POST /api/v1/sessions/<id>/storage/sd/export` 核对文件、卡镜像及源镜像字节。六次会话的租约、运行进程和隔离服务均完成清理。摘要省略了原始会话标识、端点和宿主信息。

## 范围

根因仍待定位，普通冷启动没有恢复。合成空盘的挂载与打开仅验证了存储数据路径和原版选择行为。操作系统启动、实体 Tab5、触控和浏览器均未运行。没有产品改动可回滚。
