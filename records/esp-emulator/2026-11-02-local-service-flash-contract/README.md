# ESP Emulator 本地服务发现与 bootloader Flash 契约

- 日期：`2026-11-02`
- 结果：`PASS`（virtual-device validation；物理硬件 `NOT RUN`）
- 工作类型：`code_change`
- 问题来源：[PR #76](https://github.com/m5agent/m5stack-esp-emulator/pull/76)、
  [PR #77](https://github.com/m5agent/m5stack-esp-emulator/pull/77)
- 源码版本：`m5agent/m5stack-esp-emulator@b4d066cfe45da81655bbbc912fad825234d8c7f8`
- 环境：macOS arm64、Python 3.12、Chromium、隔离的 QEMU Device Service

## 结论

Device Service 在 `site-config.json` 中声明自己的真实 origin；本地网页只在看到
该服务广告后连接 `/api/v1`，并在设备目录加载后显示“服务可运行”。静态 Pages
导出的 `service_url` 仍为空，不会探测服务，因此 browser-local 验收可保持
`no-device-service-requests`。

另一个失败并非舵机或应用代码把目标锁死：上传镜像的 bootloader header 声明
4 MiB SPI Flash，但其有效分区表结束于 8 MiB。服务现在会在分配 QEMU session
前返回 `409 bootloader_flash_size_too_small`。把同一镜像的完整 bootloader
flash-size 配置改为 8 MiB 后，分区验证通过并创建了 running session。

## 关键证据

- 原始合并镜像 SHA256：`1df26101dcc9d4ad20146c06472eea2b9b2b674ab7a9ee32310ac34fbef1fd29`
- 原始 bootloader header 第 4 字节：`0x2f`（Flash capacity code `2` = 4 MiB，80 MHz）
- 原分区表最高结束地址：`0x800000`
- 修复后的服务错误：`409 bootloader_flash_size_too_small`
- 8 MiB header 修正镜像创建 session 后状态：`running`，partition-table 错误未再出现
- 本地网页：正式本地服务状态为“已连接 · 22 个可运行设备”，设备行显示“服务可运行”
- PR CI：4/4 checks PASS
- 本地平台套件：1729 tests PASS，1 skipped

## 文件

- `report.md`：根因、修改、验证边界和回滚
- `run.json`：结构化记录
- `evidence/validation-summary.json`：脱敏后的关键结果

## 未覆盖项

- 物理 Cardputer-ADV 上的同镜像启动与舵机运动：`NOT RUN`
- 用户最终重新构建的 bootloader/partition image：`REVIEW`；本轮验证的是同一
  原始 artifact 的静态错误，以及仅修正 bootloader flash-size header 后的虚拟设备路径
- 网络、音频、机械和电气等价性：`NOT RUN`
