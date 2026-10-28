# ESP Emulator Core2 legacy dual-SPI panel routing 报告

## 背景

- 来源：`RUNTIME-03` legacy UIFlow 黑帧和 startup UI 未完成。
- 现象：legacy `m5stack` 与 `lcd` 调用正常返回，但最终帧为纯黑。
- 目标：区分 guest 显示 API、LCD 数据面和板级控制器路由。

## 结论

- 状态：`PARTIAL`
- 根因：legacy `display.TFT` 默认使用 HSPI/SPI2，UIFlow2 使用
  VSPI/SPI3；板级模型只把面板接到 SPI3。
- 修复：`0068-core2-dual-spi-panel-routing.patch` 将同一个 ILI9342
  panel sink 同时接到两个 classic ESP32 SPI controller，均使用 DC GPIO15。
- 影响：legacy LCD DMA 现在到达面板模型；原厂 startup UI 和 WDT
  生命周期仍需继续处理。

## 证据

### 代码或配置

```text
board: m5core2
panel: one M5 SPI panel object
routes:
  spi[2] / HSPI -> panel, DC15
  spi[3] / VSPI -> panel, DC15
patch: 0068-core2-dual-spi-panel-routing.patch
```

### 执行

- SPI3-only 负控启用 `M5SW_ESP32_SPI_DMA_TRACE=1`。
- 正确 LittleFS2 VFS 与 `runtime=qemu-wifi`，WDT 仅作为诊断关闭。
- 120 秒 virtual-time pause 读取双核状态和 frame。
- 原厂 startup UI 仍没有完成帧；独立 probe 只验证 legacy LCD 路由。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | QEMU 构建，平台 `1363` 项通过 |
| transport | `PASS` | 串口到达 legacy boot 与 draw 完成 marker |
| device_response | `FIXED` | legacy LCD DMA 到达 panel sink |
| data_behavior | `PASS` | frame 出现 2 色、1422 nonblack pixels |
| visual_or_physical | `PARTIAL` | probe 文字可见；原厂启动 UI 仍未完成 |

## 验证边界

- QEMU/虚拟设备结果不是物理面板或 SPI 电气测量。
- probe 修改 `/flash/boot.py` 并停留，不能替代原厂 startup UI。
- normal-WDT reset 仍存在，不能把 probe PASS 当作完整启动 PASS。

## 风险与回滚

- 路由修复只共享同一面板对象；回滚为删除 SPI2 attach 行。
- 不提交固件、原始 VFS、设备标识或运行缓存。
