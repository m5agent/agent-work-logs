# Cardputer-Adv CC1101 Cap 双来宾私有 WASM 报告

## 背景

[#247](https://github.com/m5agent/m5stack-esp-emulator/issues/247) 的原始测试中，Cardputer-Adv 默认工作台按裸板启动，两份 CC1101 Cap RF 例程都在构造期间进入 `driver/cc1101.py` 的 `wait_for_idle`，观察窗内发收计数停在初值。锁定的 0043 WASM 已编入 CC1101 模型。既有的显式 Cap 启用条件可以接上对应 SPI/GPIO，但模型中的收发数据留在单个芯片实例内。另一台来宾需要独立的虚拟收包入口。

确认范围使用官方源代码修订 `a61a29409f09f1f4bebae05e15c4bd6dcc4956b6` 的两份 RF 例程。它们在原始 UIFlow2 v2.5.3 编程镜像上经 UART0 raw-paste 运行。两个来宾均采用 `cardputer-adv-wasm-uiflow-workbench-wallclock-oneinsn-candidate`、时钟除数 1 和 one-insn-per-TB。镜像输入和运行时哈希相同，大小为 8,388,608 字节。[官方发端源码](https://github.com/m5stack/uiflow-micropython/blob/a61a29409f09f1f4bebae05e15c4bd6dcc4956b6/examples/cap/cc1101/cc1101_cap_rf_tx_example.py) [官方收端源码](https://github.com/m5stack/uiflow-micropython/blob/a61a29409f09f1f4bebae05e15c4bd6dcc4956b6/examples/cap/cc1101/cc1101_cap_rf_rx_example.py)

## 改动与边界

私有预览要求显式指定 `cc1101-rf-tx` 或 `cc1101-rf-rx` 以及 `capPeer:true`，并校验原镜像和所需补丁的 SHA-256。普通 ADV 会话仍走裸板默认配置。CC1101 虚拟对端连接到 SPI2 的唯一芯片模型，通过 CC1101 CS GPIO5 和 GDO0 GPIO15 与来宾连接。保留现有 NFC 路径和原生模型的本地回环。[官方 Cap 接线](https://docs.m5stack.com/en/cap/Cap_CC1101)

C 模型在已完成的 STX 状态转换后提供 TX FIFO 的原始快照。收端只有进入 SRX 且无在途数据时才接受一个帧，检查 1 字节长度头及 64 字节 FIFO 上限。候选模型在 5 毫秒虚拟时间后置位 GDO0，由来宾读取 FIFO 数据和确定性 RSSI、LQI、CRC 状态字节。SRES 清除未交付数据与计时器。该虚拟时序和状态字节是模型参数，物理链路的空中时间、误码率和信号质量需单独测量。

私有临时补丁 `0097-cardputer-adv-cc1101-peer-preview.patch` 应用到精确 0043 QEMU 源码副本。Emscripten 3.1.50 在独立缓存中并行重编两份 C 源文件，最多使用两个编译任务，随后按原链接命令重链。其余 710 个链接输入逐项匹配锁定构建。私有站点仍保留 0043 的源码归档作为对照。候选代码身份由补丁、源文件哈希和运行物哈希独立记录，正式重新锁定及对应源码归档仍待验证。

## 执行和证据

1. 先观察已经进入 SRX 的收端，配置 1,250 毫秒无对端消息窗口。窗口结束时 `rx_armed=true`，接收、GDO0 完成、FIFO 读取及完整接收计数均为 0。
2. 启动原发端例程。取第一次完成的 TX FIFO 快照，实际发送序号为 1。首字节 `0x14`，随后 20 个字节解码为 `CC1101, SEQ=0, Hello`。21 字节帧 SHA-256 为 `fa4c8fa4968e866d6e89712e9a471696cf4a9f2e4ee2f643f70d8ceba4ef1cf1`。
3. 等收端报告 SRX 已就绪后，验证脚本经固定 QMP 属性原样转交这一个 FIFO 帧。收端记录一次接受、一次 GDO0 完成、实际读取 23 个 FIFO 字节和一次完整接收。后续用同一 REPL 只读检查原程序全局变量，收端为 `RX_WITNESS 1 0 4343313130312c205345513d302c2048656c6c6f`，发端为 `TX_WITNESS 2 2 0`。两个发端完成计数来自原脚本的周期发送，本次仅转交第一个帧。
4. 两端捕获到 240×135 RGB565 来宾帧。收端从 `190916e4c007b9ebaa621016ce4846d66978e32219e047760cc5ec701d3c3dc2` 变化为 `a472fd0a0b8dac90234b6be79f7a31e4b366b771cfdcd5650266a8d3a506d831`，发端为 `6b8a96bba694bb58daea8219a187e778744359e3f6510f1f6825308d5eb798e6`。原例程在正常运行后由验证脚本中断，以读取同一会话的变量。两台来宾各退出 0，iframe 移除，CDP 观察到 12 个 Worker 全部在上下文关闭前回收。

| 层级 | 状态 | 证据 |
| --- | --- | --- |
| build | PASS | 0043 的私有增量重链，候选 WASM `4bcb0589…c183` |
| transport | PASS | 发端实际 SPI TX FIFO 和收端实际 SPI RX FIFO |
| device_response | PASS | SRX 接受一次帧，报告一次 GDO0 完成 |
| data_behavior | PASS | 原例程解析相同载荷，RX=1、CRC=0，无对端时计数为零 |
| visual_or_physical | PASS | 仅限两台浏览器虚拟设备的来宾帧及其更新 |
| delivery | PARTIAL | 私有预览验证，标准工作台入口及正式发布构建待验证 |
| physical_rf | NOT RUN | 物理 RF、天线、射频开关电气行为、距离与信号质量 |

[脱敏证据](evidence/cc1101-dual-guest-summary.json) 逐项保留源代码、固件、WASM、站点清单、报告和截图的 SHA-256。原始输出中的主机路径、端点、会话标识及浏览器目标标识未纳入摘要。两个会话以 SHA-256 区分。

## 精确复现

在模拟器工作区保留基线 0043 完整构建 `.work/docs-wasm-cores3-camera-lab/locked-0043-build`、其静态站点 `.work/docs-wasm-cores3-camera-lab/locked-0043-site`、Emscripten 3.1.50 缓存、私有预览补丁和三个浏览器 JS 草稿文件。脚本和产物身份见 [运行记录](run.json)。原始 0043 WASM SHA-256 为 `e350ed7b2f969139803befef12757178049427058a212136868d382dfe5a5f4b`。先核对两份官方例程在源修订中的哈希。私有目录中的固件可以从已校验的官方基础镜像和历史 LittleFS 运行物重现。

```sh
cc1101_lab="$PWD/.work/docs-wasm-cardputer-cc1101-lab"
cc1101_source="$PWD/.work/docs-wasm-cardputer-cc1101-source"
node "$cc1101_lab/recompose.mjs"
python3 "$cc1101_lab/check-peer-model.py"
python3 "$cc1101_lab/build-peer-preview.py" --name peer-preview-build-replay
python3 "$cc1101_lab/stage-peer-preview.py" \
  --build peer-preview-build-replay --site peer-preview-site-replay
env M5_CC1101_DUAL_RUN=1 \
  M5_CC1101_EXPECTED_WASM=4bcb05893348b37877858b729a85d15f72bf5734ded099b0e4c3ff1cef2cf183 \
  M5_PUBLIC_SITE="$cc1101_lab/peer-preview-site-replay" \
  M5_PUBLIC_QEMU_OUT="$cc1101_lab/peer-browser-dual-replay" \
  M5_WASM_CHROME="$CHROMIUM_EXECUTABLE" \
  node "$cc1101_source/.work/cc1101-peer-pair.mjs"
```

`recompose.mjs` 仅在目标固件和凭据尚未存在时运行。保留的固件可直接用原始镜像 SHA-256 复核。工作区应已安装 Playwright，`CHROMIUM_EXECUTABLE` 指向实际 Chromium 可执行文件。重跑时为构建、站点和报告选择尚未使用的名称。预览报告会先核对站点和运行物哈希，随后验证两个真实来宾的原程序路径。

## 回滚

启动裸板无需启用 Cap 角色。撤回试验可停用私有站点，并丢弃其独立构建产物。已发布站点、默认板级配置和物理设备未在此轮操作。
