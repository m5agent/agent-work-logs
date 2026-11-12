## 现象

所有模拟设备的 efuse 镜像都是**全 0**（会话目录 `efuse.bin` 4096 字节全零），因此 guest 读到的 WiFi/BT MAC 是 `00:00:00:00:00:00`。依赖 efuse MAC 的固件会走进异常路径：

```
E (648) phy_init: load_cal_data_from_nvs_handle: calibration data MAC check failed:
        expected 00:00:00:00:00:00, found dc:54:75:cb:b6:60
```

本轮矩阵中至少 6 个样本命中（atoms3r / sticks3 / nanoc6 / dial / papercolor），其中：

- **Evil-Parasite（AtomS3R，fw 1897200000000002572）**：串口停在上述 MAC 失败后，60 s 无首帧；
- **StickS3 Evil-StickS3（fw 1897200000000003468）**：同样报错，但后面能出 UI，说明影响取决于固件对 WiFi 初始化的依赖程度；
- 其它命中样本均在 WiFi/PHY 初始化阶段。

## 证据

- efuse：`session.json` 同目录的 `efuse.bin` 全零（`xxd` 前 48 字节全 `00`）。
- 串口：`phy_init ... MAC check failed`、`phy_init: failed to load RF calibration data (0x1102), falling back to full calibration` 12 次。
- 会话示例：`c558fb72089144a3b598eef5cb1de95a`（matrix-b/atoms3r-1897200000000002572）等。

## 分析

真实 ESP32 出厂 efuse 含唯一 MAC；NVS 里的 RF 校准数据按该 MAC 绑定。模拟器给全 0 MAC 后，凡是校验 MAC 的代码都会失败。部分固件会回退到全量校准并继续，部分（尤其是语音/联网固件）会在 WiFi 初始化失败后停留在启动页。

目前没有发现设备 profile 提供 MAC 注入口，也没有框架级说明“MAC 固定为全 0”。

## 期望 / 验收

1. 为每个设备/会话提供确定性的本地管理 MAC（如从 session id 派生，和现有 WiFi fixture 的 `locally-administered MAC` 规则一致），并写入 efuse 镜像或 guest 可见的对应字段。
2. 或者在运行时显式声明 `mac: unprovisioned`，让固件/评审能区分“模拟器没有 MAC”与“固件 WiFi 坏了”。
3. 验收：Evil-Parasite 串口不再出现 MAC 校验失败并出首帧；StickS3 等既有通过样本不退化。

## 边界

- virtual-device；不涉及真实 MAC 分配、RF 校准精度、射频或电气测量。
- 不要求模拟器提供真实厂商 OUI，只需稳定、非零、会话隔离的 MAC。
