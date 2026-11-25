# 0045 Cardputer-Adv CC1101 Cap 工作台双来宾

## 验证身份

| 项目 | 记录 |
| --- | --- |
| 模拟器源码 | `06e629a3a77be5d004be5968145ac028d0d3bdb4` |
| 模拟器基线 | `a7fd5b3856d6937adecc3ce274d0f5c58c2b8532` |
| 0045 源码补丁 | `feeae444d6f29dce4780b366759d66a727a850f22daf12012e37c31ba80381a2` |
| 构建锁 | `99fb46c2ef68a535be48e5edda0074be0abd0ee6d11abcfc9085230bb3f3aee2` |
| QEMU WASM | `dca8fddbbff5cdce16d08f6de529ad96e221bc227eaf9250b4e3514a4dfd9772` |
| 对应源码归档 | `c8ab2594c71062fe502384527a9e72f4dfd0d726dca4ed152762e5235c85fb72` |
| 静态站点清单 | `3c1cb794316e471c9e0e3af319853ff45b24339c34ba9abdfee334cb1810d09f` |
| 两端固件 | `b6255f6af5ad10236380eae09a76b44ca174b5c4de391aef16413bdc590952bd` |

两台来宾使用官方 UIFlow2 v2.5.3 的同一校验镜像、时钟除数 1 和 one-insn-per-TB。工作台从已校验的官方基础镜像组合启动固件，随后经 UART0 raw-paste 运行两份原例程。Emscripten 3.1.50 在新缓存中重建所有 QEMU 对象。现有 USB Serial/JTAG 输出能力保留在两端实际收据中，单芯片本地回环通过同一 C 源码的主机行为检查。[官方发端源码](https://github.com/m5stack/uiflow-micropython/blob/a61a29409f09f1f4bebae05e15c4bd6dcc4956b6/examples/cap/cc1101/cc1101_cap_rf_tx_example.py) [官方收端源码](https://github.com/m5stack/uiflow-micropython/blob/a61a29409f09f1f4bebae05e15c4bd6dcc4956b6/examples/cap/cc1101/cc1101_cap_rf_rx_example.py)

## 验收

1. 两个普通工作台标签页初始选择本地 MicroPython，配对控件隐藏。测试分别选择 CC1101 Cap 发送端和接收端，启动固件后用例程按钮载入各自的官方源码，核对编辑器中的实际字节。
2. 运行收端并观察 1,250 毫秒。CC1101 进入 SRX，接收次数、GDO0 完成次数、RX FIFO 读取字节数和完整接收次数均为零。
3. 同一浏览器上下文中生成配对码并在两标签页连接。两端显示配对成功，发端尚未启动原脚本时收端仍保持零接收。
4. 发端运行原程序，第一帧完成时 SPI FIFO 快照为 `144343313130312c205345513d302c2048656c6c6f`。页面通过 BroadcastChannel 转交这个 21 字节帧，经固定 QOM 属性送入收端芯片模型。收端产生一次 GDO0 通知，原程序读出 23 字节，包括帧和两个状态字节。接收程序报告 `RX_WITNESS 1 0 4343313130312c205345513d302c2048656c6c6f`，两端页面均显示已转交一帧。测试脚本读取实际来宾状态和输入记录。
5. 收端 240×135 RGB565 帧从 `190916e4…dc2` 更新为 `a472fd0a…831`，发端帧为 `53332b18…7ec04`。通过页面断开配对，对端同步显示断开。两端通过页面 Stop 退出 0，移除 iframe。CDP 在浏览器上下文关闭前观测到 12 个 Worker 全部回收，未发生回退终止。
6. Python 平台套件 2,566 项，11 项跳过。受影响的 Node 合同、静态来源与导出检查及四个项目校验器通过。

原始报告 SHA-256 为 `621f6192ebaa43de4edbc49d198c83d4cf3c73def6180d7388852dc2e3bd4e1a`。完整截图、帧、脚本和产物哈希见 [脱敏证据](evidence/cc1101-workbench-pair.json)。

## 复现

1. 从包含正式 0045 补丁的模拟器源码构建独立浏览器 QEMU，使用其 `platform/tools/bootstrap_qemu_browser_runtime.py` 和固定的 3.1.50 SDK。用 `platform/tools/build_public_site.py --qemu-runtime RUNTIME --littlefs-runtime LITTLEFS --base-path /showcase/ --output SITE` 导出普通工作台并校验站点清单。
2. 将 [工作台回放脚本](code/cc1101-workbench-pair.mjs) 放在模拟器源码工作树的 `.work/cc1101-workbench-pair.mjs`，保留它相对 `platform/tests` 的导入。将 `lab` 和 `sourceRoot` 指向独立的复现目录和官方例程目录。准备官方 UIFlow 基础镜像与经工作台验证的组成镜像，并按程序中的文件名放入该目录。原始 ESP32-S3 ROM 从运行时配置所固定的官方源获取。回放用固定的本地 ROM 和基础镜像答复相应浏览器请求，页面执行原有哈希验证。
3. 启动该脚本前设置 `M5_CC1101_DUAL_RUN=1`，填写 `M5_CC1101_EXPECTED_WASM` 为本次已验证静态导出的 WASM SHA-256，`M5_CC1101_ROM` 为本地校验 ROM，`M5_PUBLIC_SITE` 为独立静态站点，`M5_PUBLIC_QEMU_OUT` 为尚未创建的证据目录，`M5_WASM_CHROME` 为 Chromium 可执行程序。用 Node 22 运行脚本，Playwright 从 `M5_WASM_NODE_MODULES` 或工作区安装目录加载。
4. 使用独立构建产物重跑时保留自己的源码锁、站点和 WASM 哈希。当前收据属于上表所列产物。

## 覆盖范围

两台浏览器虚拟设备、工作台角色选择与配对、实际 SPI/GDO0/FIFO、原程序有效载荷、来宾帧和清理均有记录。普通工作台的初始默认选项与配对控件隐藏已验证。单独启动裸板的浏览器运行、物理 RF、NFC、文档嵌入和 Pages 部署未纳入此次收据。
