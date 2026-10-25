# ESP Emulator WebBurner 能力来源与 warning 展示报告

## 背景

Manifest 已经提供 `capabilities.detected`、`capabilities.observed`、
`capabilities.observation` 和结构化 validation warnings。原 WebBurner
结果页只显示 required/optional 和整体 PASS/FAIL，审查者看不到能力来源、
扫描覆盖、low-confidence 或逐条 warning code。

本轮目标是把已有数据完整呈现，同时保持运行态与非运行态证据分离。

## 实现

新增纯渲染模块 `platform/web/firmware-report.js`：

- `capabilitySummary()` 格式化 required、optional、sdkconfig detected、
  image observed 和 image scan；
- `validationIssueRows()` 明确生成 `[error:<code>]` 与
  `[warning:<code>]`，不再把 warning 标成 info；
- `manifestNotice()` 在 PASS-with-warning 时显示 review 数量。

`firmware.js` 增加 SDKConfig capabilities、Image observations 和 Image scan
三个摘要格，并在 timeline 中记录错误、warning 和 observed 数量。

## 浏览器验证

真实本地服务导入公开 StickS3 Weather BIN 后，在 WebBurner 页面加载同一
Manifest。可见结果：

```text
FirmwareManifest 3b6b3f71e265 · 8.00 MiB · warnings 5
PASS
SDKconfig capabilities  none
Image observations      wifi (low: esp_wifi_init),
                        display (low: lcd_panel_|m5gfx)
Image scan              SCANNED · 8.00 MiB / 8.00 MiB · complete
```

warnings 逐条显示 license、security、static review、filesystem 和 SBOM code。

截图：
`evidence/webburner-capability-observation.jpg`。

## 验证

```text
platform contracts               413/413 PASS
documentation contracts          22/22 PASS
Node firmware upload/SHA256      2/2 PASS
JavaScript syntax                PASS
runtime coverage                 PASS
peripheral catalog               PASS
QEMU profiles                    PASS
project snapshot                 PASS
compileall                       PASS
selected Ruff E9/F               PASS
git diff --check                 PASS
GitHub Actions 40147624694       PASS
GitHub Actions 40147691797       PASS
```

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Node syntax、Python compile、schema/docs tests |
| browser_ui | `PASS` | real page, DOM accessibility tree and screenshot |
| manifest_contract | `PASS` | observed/scan/warnings displayed |
| runtime | `NOT RUN` | no session or guest execution |
| physical | `NOT RUN` | no hardware or RF |

## 未覆盖与风险

- 浏览器验证使用真实 API 导入后的 persisted firmware_id，再恢复页面；
  没有重新执行文件选择器的二进制上传；
- 页面展示是审查辅助，不把 observed token 升级为运行态能力；
- screenshot 只代表当前桌面 viewport；
- QEMU、boot、网络、外设、安全执行和硬件均未在本 UI 里程碑新增验证。

## 回滚

回滚 `e679e30` 后再回滚
`e759777c8c8e5203e779a76afee5b89e886bbf1d` 可移除 UI 展示、截图和测试。
变更只涉及静态浏览器资源和文档，无数据迁移或硬件不可逆操作。
