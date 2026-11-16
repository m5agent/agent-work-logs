# Cardputer 原版复现与修复

## #229

原版 M5Apps 2.7 的 SHA-256 为 04a87f9352ad402ede9a7f683ccd657dc6b2ff7339aa9b0895fe69f01c47348f。旧运行时在 ROM 轮询占用完成位时停滞，串口停在 Multicore app、帧全黑。只补 DONE 的对照越过轮询却在写缓存 SRAM 时崩溃。

ROM 实际请求地址 0x3c000000、32 字节行长、0x200 个块，控制值 0x9，首次映射页有效。原 ESP-IDF 16 KiB 设置利用统一 MMU 在数据视图保留该 16 KiB，指令视图仍使用原映射。0203 提供读写 SRAM 和 ENA/DONE，并保持普通 Flash/PSRAM 的映射及访问权限，首个 MMU 页重映射和复位撤销保留区。缓存测试 27 项通过。早期全黑结论一度误用于最终候选，实际 PNG 复核及后续两次运行纠正了该判断。

在干净重建的 06db397c… 上，以同一原 BIN 两次独立验证。4 秒采样能看见启动提示，36 和 61 秒样本为黑。无论启用 SPI 跟踪，A 唤醒启动页，Enter 进入 SETTINGS / INSTALLER / FDISK，最终 31,935 个非黑像素，PNG SHA 一致。原版设置默认约 30 秒空闲进入渐暗，首键只负责唤醒。串口仍有 ST7789V2 ID 0，启动和输入验证通过。这个现象未扩大到存储、联网或全部应用功能。

## #230

四份样本在旧运行时 61 秒均全黑并报板型 136。旧实现没有沿着 GPIO 读回面板 ID。0204 复用既有 GPIO SPI 适配器与面板命令游标，并把 ADV GPIO 8/9 连接到真实的模拟 TCA8418 总线。仅修面板的中间结果已有画面，ADV 按键仍无响应。

组合版本的四个原版应用都获得非黑帧并响应输入。Tiny Journal 输入 x 后笔记长度改变，MacroCard Enter 显示未分配，Frequency and Noise Generator Enter 进入播放状态，CapLab Enter 进入采集页面。MacroCard 沿用原 app-only 组合镜像。两份 ADV 原版经真实 GPIO I2C 看到 0x34 ACK，并从键盘事件寄存器收到 Enter 按下/松开的 0xc3/0x43。显示 qtest 在 Cardputer、ADV、StickC Plus2 分别 14/14，Core2 负控 13/13。

## 候选构建和保留边界

从已验证 0202 源码按顺序应用 0203 和 0204，核对 152 个源文件并重新编译 1,529 步。沿用固定依赖，未复用 QEMU 对象。组合定向执行使用同一实际二进制，6 份 ZIP 逐项校验并清理。上传和组合保留原版应用字节。此处物理真机及 browser-WASM 未执行。应用的 ADC 校准或存储日志独立保留。

早期与其他设备关联的问题见 [#228](https://github.com/m5agent/agent-work-logs/blob/e6eb65e47fcf94077409f0cf9e37f6ffc13ed707/records/esp-emulator/2026-11-16-esp32-bootloader-offset/report.md) 和 [Tab5 #226/#227](https://github.com/m5agent/agent-work-logs/blob/e6eb65e47fcf94077409f0cf9e37f6ffc13ed707/records/esp-emulator/2026-11-14-p4-v1-originals/followups/2026-11-16-tab5-touch-usb-csr/report.md)。


## 完整原生矩阵与代码门禁

70 个用例均首轮通过，286 项检查，零重试。应用分区对照均相等，所有所属 guest 均退出。矩阵执行使用相同 Xtensa 06db397c…、未更新的 C6 69493c4e… 及各自固定 ROM。各用例证据哈希见 [矩阵摘要](evidence/matrix-summary.json) 与同目录分片。

平台套件共 2237 项，2229 项通过、8 项跳过。PR 232 的精确 head 同时通过 platform-contracts 和 network-namespace-policy。此前的本地文档检查因新增索引、状态页行数及评审日期条件失败过，已修正文档并复验，测试条件保留。#228 已独立进入模拟器与审核服务主分支，模拟器主分支 CI 通过，审核服务以 87 项本地测试及原版 E_STATIC 取证。
