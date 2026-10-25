# ESP Emulator WebBurner 能力来源与 warning 展示

- 日期：`2026-10-25`
- 结果：`PASS`（browser-ui validation；运行态与真机 `NOT RUN`）
- 工作类型：`code_change`
- 问题来源：Manifest 已有 sdkconfig detected / image observed，但 WebBurner 未展示来源
- 源码仓库：<https://github.com/m5agent/m5stack-esp-emulator>
- 基线版本：`c4d4f6afee5641dbb91b98e40f11a2c067326b1c`
- 功能与证据提交：`e759777c8c8e5203e779a76afee5b89e886bbf1d`
- CI 证据提交：`e679e303281496deb85a9ff09c8baef7cac7fdc0`
- 环境：真实本地 Device Service WebBurner 页面；公开 StickS3 Weather BIN

## 结论

WebBurner 导入结果现在分开展示：

- `SDKConfig capabilities`；
- `Image observations`，含 low-confidence signature；
- `Image scan`，含扫描状态、覆盖字节和是否截断；
- errors/warnings 的显式 severity 与 code。

真实页面显示公开 StickS3 Weather Manifest：

```text
validation       PASS
warnings         5
required         wifi
optional         display
sdkconfig        none
observed         wifi (low: esp_wifi_init)
                 display (low: lcd_panel_|m5gfx)
image scan       SCANNED · 8.00 MiB / 8.00 MiB · complete
```

## 关键证据

- 页面：`/platform/web/firmware.html`；
- screenshot：`319x864` JPEG，SHA256
  `92a126f1c8bd613675d84ce1ff889f4a9eabeb4126aba5dd4a86094ef26ecfad`；
- rendered manifest ID
  `3b6b3f71e2655860daaf380b0d03d75b0285a8b5d78652846f0802596884a9db`；
- normalized firmware SHA256
  `d291e77f782399e37fd5b464f9b206a00654b2c10556d730d1c45667156c603f`；
- Node firmware upload / SHA256：`2/2 PASS`；
- 平台测试：`413/413 PASS`；
- GitHub Actions `40147624694` 与证据提交 run `40147691797`：两个 job 均
  `PASS`。

## 文件

- `report.md`：UI 数据模型、验证过程和边界；
- `run.json`：结构化记录；
- `evidence/verification.summary.json`：脱敏验证摘要；
- `evidence/webburner-capability-observation.jpg`：真实页面截图。

## 未覆盖项

- 页面加载的是已导入 Manifest，不重新通过浏览器文件选择器上传 BIN；
- 没有创建 Device Service/QEMU session；
- 不证明 boot、UI、网络、GATT、运行时外设使用或 secure boot；
- 物理 RF、功耗、光学与真机仍为 `NOT RUN`。
