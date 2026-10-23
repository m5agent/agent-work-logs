# ESP Emulator ESP32-C6 单 guest WiFi + BLE 报告

## 背景

- 来源：用户要求将 WiFi/BLE 移植推广到热门 M5Stack 设备，先不做 Tab5。
- 现象：C6 QEMU 能完成板级外设和 UART1 HCI BLE，但 WiFi 只到 scan；
- 目标：在同一个 C6 guest 和同一个 Device Service lease 内打通板级外设、
  WiFi 数据面和外部 BLE GATT。

## 结论

- 状态：`PASS`，范围为 virtual-device validation；
- 关键判断：不是固件兼容性问题，而是 QEMU C6 WiFi 寄存器窗口、DMA 完成和
  802.11 管理帧实现不完整；
- 改动范围：C6 QEMU WiFi 模型、NanoC6/Nesso unified probes、Device Service
  profile、HTTP fixture 和目录状态。

## 根因

1. `MODEM_SYSCON` 位于 `0x600a9800`，private RF window 位于
   `0x600af000`。缺少这两个区域时，固件无法退出 scan mode，只发送 Probe
   Request，不发送 Authentication。
2. TX-done 只抬中断还不够。固件还会读取 MAC TX queue state；缺少队列完成
   位及 clear 语义时，第二个 TX descriptor 永远不会被提交。
3. Association Response 的 Frame Control、status、AID 和 supported-rate IE
   必须符合 802.11 格式；错误帧会让 station 反复重连。
4. C6 TX 帧长度是 32 位，不是首字节。按 8 位读取会把 DHCP 帧截断。
5. SLiRP 需要有效的 Ethernet source address；全零 source 会导致 Discover
   被丢弃。

## 修复

- 增加 C6 MAC/PHY/AGC/MODEM_SYSCON/RF 寄存器窗口；
- 实现 RX descriptor ring、92-byte C6 RX control header 和 IRQ 回注；
- 实现 TX descriptor 解析、TX queue completion/clear 和 TX-done IRQ；
- 构造 open AP 的 Probe Response、Authentication Response 与 Association
  Response；
- 在 802.11 data frame 与 Ethernet frame 之间转换，并接入 QEMU user net；
- 为 NanoC6/Nesso unified probes 增加 WiFi DHCP、受控 HTTP 和 BLE 共存；
- 为 Nesso N1 和 StickS3 unified runner 增加可选公网 DNS/HTTP 验收；
- 将两者注册到 Device Service unified profile，并启动受控 HTTP fixture。

## 执行与证据

- 公网探针：DNS `example.com` PASS，TCP HTTP 收到 `HTTP/1.1 200 OK`；
- NanoC6 unified：板级外设、WiFi DHCP/HTTP、BLE NUS 全部 PASS；
- Nesso N1 unified：显示/触摸、设备外设、公网 DNS/HTTP、BLE NUS 全部 PASS；
- StickS3 unified：显示/电源/IMU/音频/按键、公网 DNS/HTTP、BLE NUS 全部 PASS；
- Device Service：StickS3 使用一个 `qemu-unified` lease PASS，serial 与 frame
  同时就绪，evidence ZIP 含 network/BLE/QOM/audio；
- 平台：173/173 unit tests、runtime coverage、peripheral catalog PASS；
- full peripheral matrix：使用含 S3 QIO 修复的新 QEMU 二进制完成 67/67 PASS；
- 两个 QEMU patch 均通过 reverse-apply 和重建检查。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | S3/C6 QEMU、UIFlow2 NanoC6/Nesso/StickS3 镜像构建通过 |
| transport | PASS | S3/C6 WiFi MAC/DMA、SLiRP、UART1 H4 BLE |
| device_response | PASS | AP/station 管理帧、DHCP、公网 DNS/HTTP、BLE GATT notification |
| data_behavior | PASS | DHCP lease、DNS/HTTP、GATT write → guest receive → ACK |
| visual_or_physical | PASS | Nesso 和 StickS3 framebuffer/输入重绘 PASS；NanoC6 无显示 |
| delivery | PASS | 源码、最小 QEMU patch、Device Service 和本文档 |

## 验证边界

- 仅验证 QEMU virtual device，不是真机、RF、PHY、天线或电气测量；
- virtual AP 为 open、单固定信道；WPA2/WPA3 未实现；
- BLE 是 UART1 HCI offload 到 Bumble，不是原生 C6 Bluetooth radio；
- 公网 HTTP 依赖宿主网络；重复回归使用受控本地 HTTP fixture；
- Tab5 未实施；CardputerZero 不在本路径。

## 风险与回滚

C6 WiFi 设备仅在 `-nic user,model=misc.esp32c6.wifi` 时实例化，不影响无网络
启动。回滚可撤销 `0025` QEMU patch，并移除 NanoC6/Nesso unified profile 的
WiFi marker、NIC 与 HTTP fixture。
