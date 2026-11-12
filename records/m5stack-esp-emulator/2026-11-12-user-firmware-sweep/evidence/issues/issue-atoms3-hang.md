## 现象

AtomS3（`m5atoms3-st7735`，128×128 ST7735）上，两款下载量靠前的公开固件启动后**停在 ROM bootloader `entry` 之后**：

| 固件 | firmware_id | SHA-256 | 串口 | 帧 |
| --- | --- | --- | --- | --- |
| ATOMS3 UserDemo | 1897200000000000938 | `2d78c3d8874eee0f…` | 225 B，停在 `entry 0x403c98c0` | 128×128 全黑 |
| Snake Game | 1897200000000003264 | `3e4fcd924596035d…` | 225 B，停在 `entry 0x403c98d8` | 128×128 全黑 |

60 s 独立复跑结果相同；同机对照 **StampFly Controller Firmware**（`1897200000000001390`）能正常出画面，说明机器/显示链路本身可用。

## 实测：guest 侧状态

用同一仓库 QEMU 运行时离线复跑 ATOMS3 UserDemo（复用 session 的 flash/efuse，`-m 0`），QMP 采样：

- `info registers` 的 `PC` 在一个窗口内**始终是 `0x4208804e`**（IROM 区，反汇编为 `retw.n`）；
- `CCOUNT` 持续增长（两秒内 `0x90278720 → 0x94f30e78`），说明虚拟时钟在走；
- 宿主 QEMU 进程 CPU 约 **6%**；换成 Snake Game 的会话则约 **102%**；
- 两款的串口都只有 ROM 输出，没有任何二级 bootloader/应用日志。

即：一个像是进入等待态不再前进，另一个像在忙等；两者都没有任何应用输出。

## 复现

```bash
# 会话创建（agent 自有 Device Service，端口 18787）
POST /api/v1/sessions {"device_id":"atoms3","firmware_id":"<uploaded merged>","runtime":"qemu","ttl_seconds":1200}
# 离线 QMP 复查
qemu-system-xtensa -M m5atoms3-st7735 \
  -drive file=<session>/virtual-flash.bin,if=mtd,format=raw \
  -serial file:serial.log \
  -qmp unix:/tmp/qmp.sock,server=on,wait=off \
  -drive if=none,id=efuse,file=<session>/efuse.bin,format=raw \
  -global driver=nvram.esp32s3.efuse,property=drive,value=efuse -m 0
# 然后 QMP human-monitor-command: info registers
```

会话：`bf707c1f56e44b958c7a64783d1bcce6`（UserDemo 复跑）、`47bc699d75344c8bb801bffe12a683f3`（离线复跑使用的会话）。

## 影响

- AtomS3 上两款常用示例/游戏固件完全不可测；由于串口无应用输出，评审侧无法区分“固件没跑”与“模拟器卡住”。
- 同机的 StampFly 只是孤例，不能推出 AtomS3 通道整体可用。

## 期望 / 验收

1. 定位两款固件在 `entry` 之后的第一个失败端点（时钟/中断/显示初始化/PSRAM 或 flash cache 配置），给出串口或 PC/寄存器级证据。
2. 验收：两款固件都能出现首帧并稳定运行 ≥120 s；同机 StampFly 与 AtomS3R 回归不退化。
3. 若根因是固件自身的特殊初始化，请附真机或其它仿真通道的正常对照。

## 边界

- virtual-device（QEMU S3）结果；不涉及真机、射频、功耗与电气测量。
- 未修改固件、flash 或设备 profile。
