# PocketJS 自定义触控 Applet 在 Tab5 的验证

## 目标与环境

用一款自定义触控合成器验证同一个 Applet 可同时使用 PocketJS 的辅助屏触控输入、原生界面和 PCM 输出。源码以 TypeScript 和 Solid 实现。触点改变粒子中心和配色，纵向坐标映射到五声音阶。App 为 Tab5 的原生辅助屏布局，逻辑分辨率为 640×360。

工具链使用 Bun 1.4.2、QuickJS-NG 0.14.0 和 [Pocket M5 v0.1.4](https://github.com/pocket-nexus/pocket-m5/releases/tag/v0.1.4) 锁定的 [PocketJS 源码](https://github.com/pocket-nexus/pocketjs/tree/806ac202141ece274f47c938c2899ffe8d30921d)。运行环境为隔离的 Device Service 1.99.5、esp-emu 1.1.0、Tab5 `gt911-ili9881c` 和前次复验的 GT911／codec Part。镜像、运行器与 Part 的 SHA-256 见[同会话证据](evidence/virtual-device.summary.json)。

## 构建与执行

1. 按 Pocket M5 [Tab5 host 配置](https://github.com/pocket-nexus/pocket-m5/blob/db98ac45916a8ec4a2d85fa2a7e9cb09fa95bd1c/programs/m5stack-tab5/pocket.host.config.ts)编译 Applet，目标为 `tab5-home`。输出为 257,944 字节的 `.pocket` 包。测试 Applet 源文件随本地交付保留。
2. 将 Pocket M5 原版 Tab5 BIN 扩展为 16 MiB，在副本中以 4 KiB 块、128 字节读写粒度和 512 字节缓存格式化 `storage` LittleFS 分区（偏移 `0xC10000`，大小 `0x3F0000`），将包写到 `/apps/<ID 的 SHA-256 前 16 位>/package.pocket`。原版分区表、bootloader 与应用程序字节保留。固件随后自行挂载分区，并将包迁移到 apps 分区。此条路径覆盖原版 launcher 和 Applet 运行，未覆盖联网或手机传输。
3. 通过 Device Service 上传并导入测试镜像，创建原生 Tab5 会话。将该镜像绑定到 `gt911-ili9881c`，以 `--i2s-wav <capture.wav> --i2s-instance 1` 保存本次数字音频。音频参数只对测试镜像启用。通过 GT911 点击启动器坐标 `(106,99)`，串口出现包迁移及 `PULSE_FIELD ready`。执行触摸和拖动，采集同会话串口、控制器确认、原始帧与 WAV。
4. 停止前获取会话证据 ZIP 并校验 CRC，随后通过 `purge=0` 停止会话。会话状态为 `stopped`，模拟器控制套接字和可写 Flash 未保留。

```sh
bun tools/pocket.ts compile --manifest "$APPLET/pocket.app.json" \
  --host-config "$POCKET_M5/programs/m5stack-tab5/pocket.host.config.ts" \
  --plan-dir "$BUILD/plans" --outdir "$BUILD/staging" --output "$BUILD/Pulse-Field.pocket"
```

## 结果

| 验收层级 | 状态 | 观测 |
| --- | --- | --- |
| build | PASS | 生成目标 Applet 包和 QuickJS 字节码 |
| flash | PASS | 测试镜像进入模拟会话，固件迁移预置包，点击启动器打开 Applet |
| transport | PASS | 4 次点按、2 次拖动，GT911 接收并确认 35 次报告 |
| data_behavior | PASS | 来宾串口输出 D4、D4、G4、C5、C5、E4、G4、A4。I²S1 WAV 的独立音段频谱与八个日志音符匹配 |
| visual_or_physical | PASS | 虚拟屏幕采集 56 个不同帧。亮键、粒子焦点和颜色随输入改变 |
| 无复位冷启动 | FAIL | Applet 就绪前出现 2 次 TLSF `block_locate_free` 断言重启。就绪后的采集窗口内无新增断言 |
| 真机与浏览器 WASM | NOT RUN | 本次只执行原生虚拟设备，亦未执行外置 Unit、联网安装及硬件音频测量 |

模拟器源码保持原样。隔离采集副本中的 WAV 开关、带预置包的测试镜像和临时会话都可独立移除。前次上游运行问题和修复内容见 [codec 与冷启动复验](../2026-11-20-codec-and-startup/)。
