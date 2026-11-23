# 实测记录

## StopWatch Demo Plus V0.6-OPT

基线 Reviewer 在 `board_not_advertised` 停止。独立 Device Service 接收相同原件，之后用 `qemu-wifi` 在 Linux 网络命名空间启动。A+B 长按退出首次使用引导，从首页横向切到设置，滚动到 Wi‑Fi 并打开开关。原固件显示 `Setup AP`，串口记录 AP 侧 DHCP 与 Web 服务启动。抓包中的 STA DHCP 与双向 TCP/UDP 计数均为零。

候选 Reviewer 添加带检查条件的有界拖动。对照重放时，滚动后的 Wi‑Fi 标签比首轮高 5 像素，原区域哈希拒绝放行。允许在明确的垂直范围内匹配同一 RGB 哈希后，六步在同一会话完整通过，并记录每个实际命中的区域。

热点启动仅覆盖设备侧。现有 StickS3 配网客户端针对固定热点与表单，StopWatch 原件含另一套 JSON 提交通路。原件字面量与公开组件的接口相符，组件版本身份仍未确定。[配网组件源码](https://github.com/78/esp-wifi-connect/blob/77095063d77e7705f68e95005c43ed73582233ce/wifi_configuration_ap.cc)

预置对照仅向来宾可写 Flash 的 NVS 区写入两项实验网设置。原始 16 KiB NVS 区为空，原 BIN 的摘要保持一致。六步重放后，来宾串口确认关联与 IPv4 地址。最终 Ethernet PCAP 含一次完整 DHCP、一个租用地址，双向 TCP/UDP payload 计数为零。`PARTIAL` 审查状态保留，首次热点配置及应用对端未通过此路径验证。

带同一实验 NVS 的原版也通过候选 Reviewer 本地保存快照流程。候选 Device Service 广告了 StopWatch 原生 STA，快照被 Linux worker 接收，六步输入和 UI 通过。最终抓包仍为一次 DHCP 和零双向应用流量，台账保留 `SIM_PARTIAL / E_NETWORK_PARTIAL`，提交数与剩余租约均为零。

复跑可将 [六步输入和专用选项](code/stopwatch-preconfigured-validation.json) 作为 `POST /api/reviews/{job_id}/snapshots` 的 `validation` 字段，使用原版保存快照及唯一的幂等键。目标 Linux worker 预先上传用项目 `nvs_image.py` 生成的 16 KiB 实验网镜像，并核对摘要。原版首次热点路径使用独立的无预置对照。

## 其他 ESP32-S3

- PaperDIY 原生 QEMU 以项目自有探针在隔离会话中产生关联与 DHCP 串口标记，最终抓包包含一组完整 DHCP 交换。此结果限定为板级 STA。CrossPoint 原版的网络同步未运行。
- Cardputer 的 SkyCompass 和 Cardputer ADV 的 Monster 使用各自原件及候选 Reviewer，均进入 `esp32s3_native_sta` 并完成同来宾观察和最终抓包。网络仍为 `PARTIAL`，两次会话均无 DHCP。隔离配置不连接应用公网服务。
- S3-watch 使用原件作两个 2 秒 B 长按。早期画面与第一次操作后的成熟画面显示 Web 关闭，随后长按将成熟关闭状态切到显示 Web 地址。之后 60 秒内 13 个采样保留该状态。QOM 的无线使能状态只确认控制器处于启用状态。原生运行时缺少能连接这份原版 WPA2 热点的客户端。独立 esp-emu 0.50.0 在无网卡虚拟机内运行同一原件，固定只读 HTTP 路径 26 次未返回响应，UART 出现 I²C 端口未初始化的报错。独立诊断的结果不计入原生会话。

## 复现与清理

从 [源版本与摘要](run.json) 选择同一原件或受控探针。通过 Device Service 上传原件、组合 Flash，以源表中对应的 Linux QEMU 与 ROM 启动。通用 STA 使用 `qemu-wifi` / `generic-observe`、命名空间隔离、`lab-only` 和 DNS `deny`。S3-watch 使用板级 `uiflow2-sticks3-wifi`。保留逐会话帧、输入与串口，停止前导出 ZIP，保留历史，停止后读取最终 PCAP 计数及租约清理结果。摘要保留原件、Flash、运行时、帧与 ZIP 的哈希，移除了会话与环境唯一标识。

五个独立试验实例均已正常停止并回收。候选 Reviewer 的 Opt-in Linux 分流绑定 worker、API 摘要和原件。现有审查任务以及常驻服务未迁移。本次不包含真机行为、应用外网服务或 Burner 提交。
