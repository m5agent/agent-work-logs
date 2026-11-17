# Cardputer Fn 声明识别和原版词库行为

## 背景

固件审核已能为 Cardputer 的普通 Fn+标点发送组合键。旧版审核只读取 Fn 后面的第一个键名，因此遗漏 CardputerDict 0.6.4 明确声明的 `Fn+Shift+R`。中文 `Fn+退格` 和 `Fn 单击` 也无法进入旧版计划。

审核候选在已有 `declared_complex_inputs` 中补充三种写法。三键调用含有 `keys: ["fn", "shift", "r"]`。中文退格按物理 `backspace` 映射，单独 Fn 使用语义键盘的 `click`。原有两键计划名称保持兼容。拒绝把未识别的多键组合截断后执行。168 项审核测试通过。

## 虚拟设备复现

用保存说明和匹配 SHA-256 的原版 CardputerDict 0.6.4，使用原生 Device Service 的 `qemu` 模式和文档公开的制卡工具。词库 FAT32 夹具包含三个自编词，源文件后缀为 `dictionaries/ecdict.ifo`、`.idx` 和 `.dict`，初始没有 `.cidx`。候选原生 Xtensa SHA-256、BIN、规范化 Flash 与测试介质见[摘要](evidence/execution-summary.json)。

1. 以保存快照执行旧版和新版审核，传入同一份虚拟 SD。对照 `interactions.json`。同一份 BIN 在两次审核都通过画面启动和 60 秒观察。
2. 分别创建初代 Cardputer、Cardputer ADV 的普通会话，挂载同样的原版与有词库的独占 FAT32。开启原生 `M5SW_SPI_SD_TRACE=1`，从同会话画面看到测试词条，再提交 `Fn+R → Fn+Shift+R → Fn+R`。每次等待 SPI 活动静默，按阶段统计读、写命令。屏幕和复验清单使用同一会话。
3. 在 ADV 的搜索页输入 `qu`，检查画面包含输入并在额外两秒空闲后保持相同。发送 Fn+Backspace 后，采集的 PNG SHA-256 与该会话已确认的空查询画面完全一致。首次清空测试错误地将开机后的词条列表当作预期终态，因此记为部分通过。重新对照原版清空逻辑后用空查询提示作为终态并复跑。
4. 保存通过校验的会话 ZIP，停止设备并保留历史。停机后从 SD 清单确认 `/dictionaries/ecdict.cidx`。结束时 Flash 释放且工作租约为零。

原版公开源代码把 `Fn+R` 转成 `scanSd(state.shift)`，普通读取使用有效缓存，强制重建会写回缓存。除 SPI 读写外，原版画面证明所用为同一个测试词库。原版应用日志未出现在默认串口，因此第一轮以串口标记为条件的预检超时，该轮已清理。复验以同来宾画面、SPI 跟踪和保留 SD 清单为依据。[原版键盘路径](https://github.com/RadioDisney/CardputerDict/blob/4b69cef2c59ef443eea191aa8e1b6bbef6178595/src/main.cpp#L617)

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| 静态与契约 | PASS | 168 项测试 |
| 虚拟烧录与启动 | PASS | 同一完整 Flash 启动并显示 CardputerDict |
| 输入 | PASS | 旧版对照遗漏三键，新版作为单次请求提交 |
| SPI 数据面 | PASS | 两种板型同序列达到 69/0、110/11、69/0 次读写 |
| ADV 查询清空 | PASS | 显示 `qu`，空闲保持，Fn+Backspace 后回到空查询帧 |
| 原版整体验收 | PARTIAL | 完整声明还包含网络和其他交互 |

## 验证边界和回滚

普通自动复审在重建步骤前已经按原说明打开 Wi-Fi 配置界面，保留 `E_INTERACTION_CLAIM_PARTIAL`。独立原版搜索页会话验证重建。实体设备、浏览器和外部访问未运行。所有服务为隔离实例，未提交 Burner。撤回候选提交即可恢复旧的识别规则。
