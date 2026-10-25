# ESP Emulator 镜像能力观察与 capability mismatch

- 日期：`2026-10-25`
- 结果：`PASS`（static-manifest validation；运行态与真机 `NOT RUN`）
- 工作类型：`code_change`
- 问题来源：FirmwareManifest 在没有 sdkconfig 时仍完全依赖操作者能力声明
- 源码仓库：<https://github.com/m5agent/m5stack-esp-emulator>
- 基线版本：`c36b7907b929363374fe3d2e0ba5d486a6d4fdc8`
- 功能与证据提交：`9ad3771d87acff6147714492caa84d0c288eb293`
- CI 证据提交：`c4d4f6afee5641dbb91b98e40f11a2c067326b1c`
- 环境：macOS Apple Silicon；Python 3；真实公开 StickS3 Weather BIN

## 结论

FirmwareManifest 新增独立的 `capabilities.observed`：

- 只用白名单 token 扫描规范化完整 Flash 的前 `64 MiB`；
- 每条固定为 `source=image-signature`、`confidence=low`；
- `capabilities.observation` 记录 `SCANNED`/`TRUNCATED`、总字节和扫描字节；
- observed 只产生结构化 review warning，不能单独拒绝固件；
- required capability 的 hard mismatch 仍由目标设备 profile 决定。

公开 StickS3 Weather 样本在没有 sdkconfig 时观察到 WiFi 和 display。
required wifi + optional display 为 `PASS`；错误声明 required camera 仍在
StickS3 上返回 `unsupported_capability`。两次 artifact SHA256 相同。

## 关键证据

- source BIN：8,323,072 bytes，SHA256
  `8b7b47c8d601e1821817f8d0e6b55568829913e50333dbcc15de6ffdbad1997c`；
- normalized artifact SHA256
  `d291e77f782399e37fd5b464f9b206a00654b2c10556d730d1c45667156c603f`；
- observed：`wifi` (`esp_wifi_init`)、`display` (`lcd_panel_`, `m5gfx`)；
- scan：8 MiB / 8 MiB，`SCANNED`，未截断；
- normal import：`PASS`；
- required camera：`REJECTED` / `unsupported_capability`；
- 平台测试：`413/413 PASS`；
- 文档契约：`22/22 PASS`；
- GitHub Actions `40147212974` 与证据提交 run `40147293390`：两个 job 均
  `PASS`。

## 文件

- `report.md`：数据模型、warning 语义、验证和边界；
- `run.json`：结构化记录；
- `evidence/verification.summary.json`：脱敏验证摘要。

## 未覆盖项

- token 命中不证明运行态代码路径；
- 没有新增 boot、UI、网络或 GATT 运行；
- secure boot、Flash Encryption 执行与 eFuse 真值未验证；
- 许可证/法律结论、物理 RF 和真机仍 `NOT RUN`。
