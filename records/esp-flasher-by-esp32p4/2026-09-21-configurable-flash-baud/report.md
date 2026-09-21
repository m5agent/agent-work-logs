# ESP32-P4 Flasher 可配置 DUT 烧录波特率报告

## 背景

- 来源：用户反馈 DUT 烧录速度很慢，UIFlow 等接近 8 MiB 的镜像等待时间很长。
- 现象：现有固件连接 ROM loader 后始终以 115200 baud 传输镜像，没有暴露烧录速率给中台或 Agent。
- 目标：固件、中台和 `device-test-center` skill 同时支持可配置烧录速率；默认 1,500,000 baud；
  旧设备失败时 Agent 可以显式回退低速率。

## 结论

- 状态：`PARTIAL`
- 关键判断：慢的原因是 loader 会话在 115200 同步后没有切换速率，而不是网络下载或 Flash 擦写阶段。
- 改动范围：
  - 固件 `flash` command 接受 `baud`，范围 9600-3,000,000；连接成功后调用
    `esp_loader_change_transmission_rate()` 切换主机与目标 loader 速率。
  - 中心 `TargetProfile` 新增 `flash_baud`，默认 1,500,000；task 的 `firmware.flash_baud`
    可覆盖 target 默认值，显式 plan 使用 `flash.args.baud`。
  - Web 配置页和任务创建页新增烧录波特率字段，并与 Monitor 波特率分开显示。
  - API 文档和 `device-test-center` skill 增加默认值、字段位置和回退顺序。

## 证据

### 代码或配置

```text
app_flasher_session_set_baud():
  esp_loader_change_transmission_rate(loader, baud)

center:
  TargetProfile.flash_baud = 1500000 by default
  firmare.flash_baud override -> plan flash.args.baud
  explicit plan flash.args.baud validation: 9600..3000000

fallback order:
  1500000 -> 921600 -> 460800 -> 230400 -> 115200
```

### 执行

- 环境：Apple Silicon macOS；Docker `espressif/idf:v5.5.4`；target `esp32p4`。
- 命令：使用受控 ESP-IDF Docker 构建器执行 `idf.py build`。
- 结果：构建成功；应用镜像 1,211,648 bytes。
- 中心服务：`python -m unittest discover -s center_server/tests -t center_server -v`，84 项通过。
- 静态检查：center Python `py_compile`、Web `node --check app.js ota.js`、`git diff --check`
  全部通过。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | ESP-IDF v5.5.4 构建成功，生成 app bin |
| transport | NOT RUN | 没有真实节点观察 1.5 Mbaud UART loader 收发 |
| device_response | NOT RUN | 没有真实 DUT 完成 ROM loader 切换与 flash |
| data_behavior | PASS | 中心 task plan 默认/覆盖/越界测试通过 |
| visual_or_physical | NOT RUN | 没有实机吞吐和稳定性证据 |

## 验证边界

- 115200 仅用于 ROM loader 同步或旧设备回退；默认烧录速率为 1,500,000。
- 本次没有执行实机烧录，因此无法证明所有目标芯片、线缆长度和 USB-UART 桥接芯片都支持
  1,500,000 baud。
- M5Stack 旧设备应先尝试默认值；仅在失败或校验异常时按回退顺序逐级降低，并保留失败证据。
- 如果目标芯片或桥接芯片不支持速率切换，固件会返回 `flash_baud_failed` 或
  `flash_baud_unsupported`，不应把它误判成应用固件故障。

## 风险与回滚

- Patch 使用零上下文格式以移除公开记录中的内网端点上下文；验证命令为
  `git apply --check --unidiff-zero`。

- 风险：高速 UART 对线缆、夹具和时钟误差更敏感；1,500,000 默认值可能提高部分旧夹具的失败率。
- 缓解：target 可持久设置较低 `flash_baud`，单次 task 也可覆盖；无需重新烧录 P4 才能回退 DUT 速率。
- 回滚：把 target 或 task 的 `flash_baud` 设为 115200，或 revert 本次 patch；没有执行不可逆
  P4 OTA、擦除或分区迁移。
