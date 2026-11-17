# PaperDIY、Cardputer 原生审核与 Tab5 复查

## PaperDIY 卡检测与真实 SPI 数据面

PaperDIY 用 GPIO48 读取卡检测。旧 QEMU 虽有 SD SPI 路径，板级卡检测仍保持高电平。0208 在原生 QEMU 将已附加媒体的检测引脚拉低，无媒体时保持高电平。Device Service 只在 QEMU 公开只读布尔属性 `sd-card-detect-model` 后向该板宣告附卡能力。先读取设备目录，再通过 `POST /api/v1/sessions` 用显式 FAT32 artifact 创建会话。旧后端仍可创建无卡会话，附卡请求返回 `409 storage_not_supported`，未分配会话目录。 [PaperDIY 机器可读结果](evidence/paperdiy-sd-summary.json)

以 ESP-IDF `735507283d5b2f9fb363a1901172dbd9e847945d` 构建 `tests/firmware/spi_sd_media` 的 PaperDIY 探针。候选 QEMU `cbc0ea74…` 有卡时 GPIO48=0，同一来宾完成预置文件读取、写入、卸载和重挂载。无卡时 GPIO48=1、无 SPI 读取或写入。用 `POST /api/v1/sessions/{id}/reset` 对同一 QEMU 进程复位，来宾重新挂载即读到上一轮写入内容。该轮观察到 35 次 CMD17 和 14 次 CMD24。所有附卡会话源镜像 SHA 保持一致，停止后的文件内容由宿主独立校验。物理触点、电气行为、运行中热插拔和 WASM 为 NOT RUN。

## Cardputer K132 与 ADV 原生 STA

`qemu-wifi/generic-observe` 使用每个板型原生 ESP32-S3 Wi-Fi 模型。设备目录中的 `native_network.sta` 声明已验证的板级 STA 路径，同时声明 `operation_assertions=false`。完成的以太网抓包产生 `native_data_plane`，包括 SHA-256、DHCPv4 DORA、双向 TCP 或 UDP 负载地址端口对的计数。原有通用网络结论仍为 PARTIAL。 [原生 STA 摘要](evidence/native-sta-summary.json)

分别在两台原生虚拟设备中运行同一开放网络 BIN 和同一 WPA2 BIN。以固定本地 HTTP 资源为唯一允许的转发，来宾分别完成关联、租约和精确 22 字节响应正文校验。每次抓包均记录 1 次 DORA、1 对双向 TCP 流、0 对双向 UDP 流。使用相同 WPA2 BIN 配置错误凭据时，两板都发出 `NO_LEASE`，没有 HTTP 请求，最终抓包记录零包。所有捕获观察到零公网目的地。最初两次探针 FAIL，探针在抓包已收到完整响应后仍等待 TCP EOF。测试代码改为按 `Content-Length` 校验后结束，前两次固件和抓包 SHA 保留在摘要中。

自动 STA 准入还需支持 Linux network namespace 的在线 worker。macOS 隔离审核用同一开放网络 K132 BIN 执行 dry-run。目录实际声明两台板，worker 报 `worker_namespace_unavailable`，因此创建一个离线板级会话并读到 `STA_FIXTURE_BOOT`。纯串口探针产生 `E_NO_FRAME`，审核进入 `manual_review`，网络数据面为 NOT RUN。显式 `namespace` 请求返回 `503 network_isolation_unavailable`，无新增会话，原离线会话停止且释放可变 Flash。Linux 准入正向、原版应用级断言、DNS 与 UDP 应用端点、AP 和真机为 NOT RUN。 [审核准入摘要](evidence/reviewer-namespace-negative-summary.json)

## Tab5 上游 1.1.0 候选

固定上游 darwin/arm64 二进制、rev0 ROM、P4 v1.0 会话 eFuse、32 MiB PSRAM 和 C6 ESP-Hosted。通过 Device Service 上传原 BIN、导入 Tab5 固件并创建独立会话，原版无匹配 ELF。P4 增加上游 `--cosim-tcp`，以发布版 DSI 观察器订阅 VC0。取证 ZIP 通过 CRC 后停止会话。 [Espressif v1.1.0 发布记录](https://github.com/espressif/esp-emulator/releases/tag/v1.1.0) [DSI 观察器契约](https://github.com/espressif/esp-emulator/blob/v1.1.0/docs/guides/HOST-INTERFACES.md) [运行摘要](evidence/tab5-1.1.0-summary.json)

在同配置下构建 ESP-IDF 5.5.4 的独立控制固件，通过原生 `esp_lcd` DSI、DBI 和 DPI 接口绘制 128×120 RGB565 图案。观察器收到 DBI 0x11 和 0x29、视频流开始和整帧图像。PNG 逐像素核对得到红 7,680、绿 3,840、蓝 3,840，无黑像素。常驻 Tab5 的 API 画面和触摸仍依赖已验证的同镜像 GDB 参考，DSI 观察器本轮还未接入服务画面和输入实现。

使用证据中的 ESP-IDF 提交和 GCC 14.2.0 构建对照固件。

```bash
IDF_TARGET=esp32p4 idf.py -C code/dsi-control -B build-tab5-dsi build merge-bin
```

将生成的 `merged-binary.bin` 作为完整镜像导入。固件构建元数据包含时间，重建时记录重新生成的 SHA-256。 [DSI 正对照源码](code/dsi-control/main/probe.c)

三份原版各观察约 32 秒，均无 DSI 视频流起始事件或 DBI 命令。Arduventure 进入 `app_main()` 后报 `Wrong display geometry` 并返回，根因未定位。CarPlay 持续软件复位，在另一次 GDB 硬件断点观察中读到 `bsp_get_board_version` 的 BSP 断言。M5TabOS 到达应用初始化，旧版 USB 断言断点在 12 秒窗口未命中，当前停顿原因尚未定位。两个原版曾在 1.0.0 转到异常向量的 `csrr a4,0x346`，在 1.1.0 均单步到 PC+4。未写入来宾寄存器或指令。三份原版画面 FAIL，候选资格 PARTIAL。触摸控制器、USB 主机枚举、物理测试和浏览器验证为 NOT RUN。

## 交付与证据范围

所有验证使用独立服务和会话。原始固件、调试器记录、串口、抓包、ZIP、唯一标识及宿主路径保存在本地取证环境。归档保留来源及证据哈希、受控条件和结果。驻留服务切换和回滚单独取证。
