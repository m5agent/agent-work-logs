## 现象

Core2（`m5core2`）上若干固件串口显示 LCD/触摸初始化成功，但**面板模型完全没有收到像素**：320×240 帧全黑，QOM 导出 `m5-panel` 的 GDDRAM 也几乎全 0。

| 固件 | firmware_id | 矩阵结果 | 帧 | 串口 |
| --- | --- | --- | --- | --- |
| Core2_For_AWS | 1897200000000000568 | PARTIAL/application_frame_not_ready | 全黑 nb=0 | `LCD: FT6336 ... old panel detected`、HOME 欢迎文本 |
| UIFlow_Core2 | 1897200000000002280 | 同上 | 全黑 | 507 B |
| M5HamRadio Core2 | 1897200000000001395 | 同上 | 全黑 | 617 B |
| **Core2FactoryTest（对照）** | 1897200000000000926 | **UI 正常**（nb=76800，242 色） | 正常 | Axp 初始化 |

## 证据：同一机器上的 GDDRAM 对照

用同仓库 QEMU 运行时离线复跑，`qom-set /machine/m5-panel dump-path=...` + `refresh-now` 导出面板 GDDRAM：

| 固件 | GDDRAM 非零字节 | screendump 非黑像素 |
| --- | ---: | ---: |
| Core2_For_AWS（失败） | **15 / 230415** | 0 |
| Core2FactoryTest（对照） | **229551 / 230415** | 有画面（242 色） |

即：失败的固件根本没有把像素写进面板模型，而不是“画了但取帧坏了”。

## 复现

```bash
# 16 MiB flash 补零后用 m5core2 机器直接跑
truncate -s 16777216 flash.bin
qemu-system-xtensa -M m5core2 -drive file=flash.bin,if=mtd,format=raw \
  -accel tcg,thread=single,tb-size=128 -icount shift=5,align=off,sleep=off \
  -display none -serial file:serial.log \
  -qmp unix:/tmp/qmp.sock,server=on,wait=off -m 8
# QMP: qom-set /machine/m5-panel dump-path /tmp/gddram.bin
#      qom-set /machine/m5-panel refresh-now true
```

## 影响

- Core2 上这批固件在模拟器里“能启动、有日志、黑屏”，容易被误判为固件问题；实际是显示写入没有到达面板。
- Core2 是主力机型，黑屏会直接阻断社区固件的评审和截图证据。

## 期望 / 验收

1. 定位这批固件的 SPI 事务为何未被面板模型消费（重点：`old panel` 初始化序列、命令/数据切换、DMA 写入长度、CS/DC 时序）。
2. 验收：Core2_For_AWS 能出现非黑帧且 GDDRAM 非零；Core2FactoryTest 与 UIFlow2 既有显示用例不退化。
3. 负控：同机同镜像重跑，结果稳定。

## 边界

- virtual-device；不涉及真机面板、亮度、色偏或光学测量。
