# UIFlow2 #127 battery indicator source and image comparison report

## 背景

- 来源：公开 issue [m5stack/uiflow-micropython#127](https://github.com/m5stack/uiflow-micropython/issues/127)。
- 现象：报告者称 M5Stack Core Gray（IP5306）在 UIFlow2 `v2.4.3-4MB` 上电量指示正常，从 `v2.4.4-4MB` 起直到 `v2.5.4-4MB` 电量指示为空（0%）。
- 目标：在缺少 Core Gray 真机的条件下，确认 `v2.4.3` 到 `v2.4.4` 的固件源码或镜像是否改动了 IP5306 电量路径，并给出可复现的证据边界。

## 结论

- 状态：`REVIEW`（源码与发布镜像级验证；无真机、无 UI 级复现）。
- 关键判断：`v2.4.3` 到 `v2.4.4` 的电量 UI 逻辑、M5Unified 的 IP5306 路径、分区表和整个 VFS 区都没有变化；两版官方 4 MB 镜像内嵌的 ESP-IDF 均为 `v5.5.1`。报告中的回归无法由这两版之间的固件源码变化解释，需要报告设备的运行读数继续定位。
- 根因：未定位。
- 改动范围：无源码或配置改动，仅做只读对比与虚拟设备启动尝试。

## 证据

### 代码或配置

提交范围 `2.4.3..2.4.4`（`d30cac849afb76cfa144febdc73fbc55c8c796c0` 到 `3da7e5766f866ab4eaa3d96ea02a2a0c6cb51a96`）共 16 个提交。`m5stack/modules/startup/basic/apps/dev.py` 的差异仅涉及字体：

```text
- font=Widgets.FONTS.DejaVu18
+ font=Widgets.FONTS.Montserrat18
- font=Widgets.FONTS.DejaVu9
+ font=Widgets.FONTS.Montserrat12
```

同一文件中的 `_get_battery_src()`、`_get_battery_text()` 以及 `M5.Power.getBatteryLevel()` / `M5.Power.isCharging()` 调用没有变化：

```python
def _get_battery_text(battery):
    if battery > 0 and battery <= 100:
        return "{:d}%".format(battery)
    else:
        return ""
```

M5Unified 子模块 `a852f204aa937b4e62d8700201809dbd10e83fa0` 到 `60875b040bbbc0939a80a14280839f48475d3f6f`，改动文件为 `M5Unified.cpp`、`M5Unified.hpp`、`Power_Class.cpp` 以及新增 `LED_PMIC_Class.*`。`Power_Class.cpp` 的改动只覆盖 StampS3Bat 与 StickS3 的 M5PM1 分支，`IP5306_Class` 与经典 ESP32 的 IP5306 分支未变化。

两版 4 MB 镜像的分区表完全一致：

```text
nvs       0x9000   0x6000
phy_init  0xf000   0x1000
factory   0x10000  0x360000
vfs       0x370000 0x8e000
```

VFS 区（`0x370000`，`0x8e000` 字节）两版字节完全相同：SHA256 `009c69e9ab838eda6a794d2f751cd6fb9c83d95cb4a83974c735a0e284f4e2a7`，共 581,632 字节，含 54 个 JPEG 资源；Basic 的电量图片路径与资源都在。

### 执行

- 环境：本机 UIFlow2 源码 checkout；两版官方 release 资产；Basic v2.7（`basic-v27`，ESP32-D0WDQ6-V3，`m5basic`）虚拟设备。
- 命令与输出见 `evidence/source-image-checks.txt`。
- 虚拟设备：两版官方镜像都启动到 UIFlow2 banner，串口停在同一位置，均出现相同的 I2C 初始化错误（`i2c.master: this port has not been initialized`），帧缓冲全黑，未到达 DEV 界面；两版串口日志与启动行为一致。
- IP5306 模型注入 `battery-mv=3900` 后 QOM 读到 `battery-code=8`，但官方固件未运行到 UI，无法观察到电量指示。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | 不适用 | 未构建镜像，直接使用官方 release 资产 |
| transport | `PARTIAL` | 两版镜像均在虚拟设备启动到 UIFlow2 banner，未到 UI |
| device_response | `NOT RUN` | 无 Core Gray 真机 |
| data_behavior | `NOT RUN` | 未执行 IP5306 运行读数 |
| visual_or_physical | `NOT RUN` | 未观察 DEV 界面电量指示 |

## 验证边界

- 没有 Core Gray 真机，IP5306 电量计的真实读数路径没有执行。
- 只比较了 `v2.4.3` 与 `v2.4.4`；`v2.4.5` 至 `v2.5.4` 未做镜像对比。
- 未做编译后机器码级别的 `IP5306_Class` 对比；结论基于源码、子模块范围、分区表、VFS 逐字节和镜像字符串。
- 虚拟设备的 IP5306 为寄存器模型，无电芯；虚拟结果不能当作真机电气或 UI 结论。

## 风险与回滚

- 本次为只读对比，无烧录、无仓库改动、无设备状态变更；无需回滚。
