# 0046 Cardputer-Adv SX1262 标准工作台双来宾

## 验证身份

| 项目 | 记录 |
| --- | --- |
| 模拟器源码 | `55d449e345417e4f0b9c6531108f48bdaf8a55db` |
| 正式 0046 补丁 | `0c7b037ed3e95102c8d588d042767a0d61591946323f21a9f87a8e02f0c90238` |
| 构建锁 | `4ba15619e4613bc886e796d6f6c6cacce7e2f1b9225e424a48c2aaea1aaa36cd` |
| 运行 WASM | `210db550d50847a3d4f66d86f81c8d1cdb2ac106ebf6bac16cccc60f4da0e211` |
| 运行物清单 | `a56410a8fb99a0e65ce7a7017c3a5ceb8ce0bd832451cbc71e12317cf614a0b9` |
| 静态站点清单 | `cec271aefa1a575d8b257ea899a8af91eb8209575202fef99fb919bab37f16ac` |
| 对应源码归档 | `cdb73af557fdedc2aee41284bf96469f4e3d0ce1d42ef6d7a9e62a87714484bf` |
| 来宾 Flash | `b6255f6af5ad10236380eae09a76b44ca174b5c4de391aef16413bdc590952bd` |
| 浏览器 | Chromium `158.0.8127.37` |

Emscripten 3.1.50 全量重新编译所有 QEMU 对象。四台测试来宾分别按选定角色启动，均使用 UIFlow2 v2.5.3、时钟除数 1 和 one-insn-per-TB。原程序通过工作台例程按钮载入并经 UART0 raw-paste 执行。复现只需要运行构建所固定的官方 UIFlow 基础镜像和 ROM。 [LoRa1262 原例程](https://github.com/m5stack/uiflow-micropython/tree/a61a29409f09f1f4bebae05e15c4bd6dcc4956b6/examples/cap/lora1262) [LoRa868 原例程](https://github.com/m5stack/uiflow-micropython/tree/a61a29409f09f1f4bebae05e15c4bd6dcc4956b6/examples/cap/lora868)

## 浏览器观测

1. 每组两标签页的初始选择均为本地 MicroPython，配对控件隐藏。测试分别明确选择发端、收端并从工作台按钮加载源码。
2. 各收端进入 SX1262 RX 后单独观察 1,800 毫秒。RX 接收次数和 FIFO 读取字节均为 0，DIO1 保持低。完成配对后，发送前再次核对零接收。
3. 发端聚焦工作台设备并通过电脑键盘输入 `w`、`a`、`s`、`m` 和 Enter。原程序在同一来宾中提交首个 TX FIFO 包 `7761736d`。两页均显示已转交 1 帧。收端的输入日志只记录一个相同的四字节包。
4. 每组均直接采样到收端 DIO1 为高、RX_DONE 为 1。随后来宾清除 IRQ，DIO1 变低，RX FIFO 的真实读取计数增至 4。相同来宾的原回调全局变量给出 `RX_WITNESS 7761736d wasm`。两种接收例程均更新 240×135 RGB565 屏幕。
5. 工作台明确断开配对，对端同步显示断开。每组两台来宾均通过页面 Stop 退出 0 并移除 iframe。浏览器上下文关闭之前，CDP 在每组独立观测到 12 个 Worker 正常回收，共 24 个。未观察到页面异常。
6. Python 平台套件 2,567 项，11 项跳过。Node 合同套件在测试夹具修正后完整通过，执行页面与运行物保持上表身份。锁定补丁、运行物及四份原始程序通过静态核对。

| 例程 | 接收画面前后摘要 | 原始报告 SHA-256 |
| --- | --- | --- |
| LoRa1262 | `d043a2d6…ed2c` → `1c27aaa9…2e4a` | `7fddd07168b91a95fce706bdf839fac6c239c2c7d0fdfcb9d56480f061fa4651` |
| LoRa868 | `d043a2d6…ed2c` → `3528b8cd…8ce5` | `03bbb8c55fdbf51c30f8f9a3936ceb396ef164f5d45ce44c052222d2f1be2fcc` |

[机器证据](evidence/sx1262-workbench-pairs.json) 记录四份源码身份、每组实际 QOM 状态、原回调输出、帧和截图哈希及退出细节。物理射频、0046 的 GNSS 再验证、单独启动裸板、文档嵌入及 Pages 部署不在此次验收范围内。

## 复现

1. 使用正式 0046 源码和 `platform/tools/bootstrap_qemu_browser_runtime.py`，在独立缓存全量构建浏览器 QEMU。使用项目的源码构建 LittleFS，运行 `platform/tools/build_public_site.py --qemu-runtime RUNTIME --littlefs-runtime LITTLEFS --base-path /showcase/ --output SITE`。
2. 保留 [回放脚本](code/run-workbench-dual-lora-0046.mjs) 的完整内容。按独立工作区调整其中的 `repo`、`lab` 和 `workspace` 变量，或使用相同工作区结构。设置 `M5_SX1262_BASE` 和 `M5_SX1262_ROM` 指向从官方来源取得的本地文件，程序会独立检查长度和 SHA-256。Node 22、Playwright 和 Chromium 路径用脚本支持的环境变量绑定。
3. 设置 `M5_SX1262_DUAL_RUN=1`，`M5_PUBLIC_SITE` 为静态导出目录，`M5_SX1262_EXPECTED_WASM` 和 `M5_SX1262_EXPECTED_SITE` 为本次构建的实际已验证哈希。分别运行 `node run-workbench-dual-lora-0046.mjs lora1262 browser-0046-workbench-lora1262-1` 和 `node run-workbench-dual-lora-0046.mjs lora868 browser-0046-workbench-lora868-1`，两次使用未占用的输出目录，等待第一组结束后再启动第二组。
4. 保留每组的独立报告原件、截图哈希与 Worker 清理后置条件。新构建的收据使用该构建产物的实际身份。
