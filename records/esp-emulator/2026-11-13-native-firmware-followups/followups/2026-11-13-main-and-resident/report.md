# 最终整合与分层验收

## 根因和验证边界

Classic 原版复测保留新鲜构建 35c 的五条应用路径及 SD/IMU 控制：
Lite/Matrix 的真实中断槽位与 CPU 时钟切换修复有原始失败和同 BIN 对照。
Matrix 厂测服务器的实际 HTTP 404 仍是应用限制；Ham 只覆盖原 SD 配置及真实 B/C/B 输入。
Core2 原 UIFlow1 在本轮从主页自然到 Wi-Fi 配置页，不把早期截图时间当作固定启动行为。
35c 的历史结果不自动转移到后来的运行时；最终矩阵与部署身份另见交付门摘要。

C6 MWDT 时钟与 Nesso M5GFX 源码修复分别保留原 BIN、实际控制器和重建版身份。
Launcher 的一行触摸 bus_shared 修复只属于固定源码重建对照，原发布 BIN 仍失败；
原 BIN 所用缓存 M5GFX 版本未被精确恢复，不能宣称比特一致。
RFID 原应用的首故障包含 watchdog 订阅/喂狗路径，不能以缺少 PN532 代替根因。
MWDT 的 OFF stage 重计数有旧实现负控；零保持仅按下一真实源时钟/分频边缘量化，
不宣称物理硅片的零保持行为已经测定。
BLE 0198 证明采样时钟数据面进展，不证明 JIGGLER 应用就绪、HID 配对或 RF。

#223 两份原 BIN 仍未通过。两个加入官方 I2C 补丁的独立源码重建版，各自的
360 秒画面/触摸/UART 协议对照只属于 `e04488691fe185e9158463a01546425344754ae5966abb499a9044d9b3834cff`。
只有 UserDemo 有独立的未修源码重建负控；GPT 没有这一负控。
上游报告的硅片复现不是本次原 BIN 的真机测试。

#226 使用原 Maker Fighter BIN 的最终 ZIP 串口及真实 runtime=qemu 重新分类。
20 次 DWC 初始化断言是已有模型缺口的识别证据，不是 USB 修复。
没有捕获应用帧不能描述为测量到黑屏；未伪造 GSNPSID、端点或控制器成功。

## 最终交付门

全部状态由指定 JSON 和保留证据重新验证；缺失或身份不符时生成器拒绝输出。
矩阵执行提交 `890acf8fd4f51af400cdfa96100d5dcac7903338`，交付提交 `4f09fcba8364e02cb1f60eeec0422e3cae66db54`。
执行文件逐字相等证明用于之后仅证据/文档提交，绝不改写实际执行 SHA。
最终 Xtensa `35c35ef2427e121dcd232215339c5219b7e22bc6c63821c92e356c9573d42b26`；最终 C6 `3679e74e893670a5fd665345addcf00e0e49b9f708c6d4093960f8dc228b0db4`。
main/CI、部署状态保留、9 条部署后路径、5 条方向路径分别保存独立摘要。

## 可复现入口与证据

[Classic 原版路径](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/classic_factory/README.md)、
[MWDT 控制](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/esp32c6_mwdt_clock/README.md)、
[Launcher 源码对照](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/nesso_touch_bus_shared/README.md)、
[I2C 构建与应用对照](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/s3_i2c_lifetime/rebuild-applications.md)、
[USB 缺口](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/tab5_usb_model_gap/README.md)。

- [evidence/xtensa-originals-0194-0198.json](evidence/xtensa-originals-0194-0198.json) · SHA-256 `9c38de33068695a4379cb12890dfe6b9ae956cb2ea5254ee912fad8ac50d9368` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/classic_factory/final-0194-0198-summary.json)
- [evidence/xtensa-irq-clock-failures-and-controls.json](evidence/xtensa-irq-clock-failures-and-controls.json) · SHA-256 `587f2ea34e3c79f66d98cb79aba86c4150ad6836905ff6ee4a4a9b56a20e3702` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/classic_factory/irq-clock-recovery-summary.json)
- [evidence/xtensa-rmt-led-history.json](evidence/xtensa-rmt-led-history.json) · SHA-256 `123e9ea8877cd63edd10d153a449581f4615863a1dd5007e88a46503f66e8190` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/classic_factory/rmt-led-summary.json)
- [evidence/xtensa-wifi-history.json](evidence/xtensa-wifi-history.json) · SHA-256 `36fd4cbf6ba6abc93ef901dc3dba52fbc327d2c93a9168665205666ed2933a77` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/classic_factory/wifi-rx-summary.json)
- [evidence/xtensa-bootstrap-history.json](evidence/xtensa-bootstrap-history.json) · SHA-256 `37735f51c17d2a23434895cff57c36024b7ce2b38907ee8f35625242f51aea14` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/classic_factory/bootstrap-summary.json)
- [evidence/core2-panel-history.json](evidence/core2-panel-history.json) · SHA-256 `d1e3455864c6c844eba84d5e95eb6569b0295c12679485b6f114c773c04c411f` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/classic_panel_cs/evidence-summary.json)
- [evidence/core2-sd-history.json](evidence/core2-sd-history.json) · SHA-256 `9d3f36dc544bd16ec82a30426ed6c4bc91fb8640e5f2d5e004d7fcb8ef95ce38` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/classic_panel_cs/sd-evidence-2026-11-13.json)
- [evidence/recovery-original-failures.json](evidence/recovery-original-failures.json) · SHA-256 `da0d2d609f58fe48c4ee11ecbf7855e31a17db4ca28f69550f5dc2643f2e0f60` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/docs/evidence/2026-11-13-native-runtime-recovery/xtensa-originals-before-irq-fix.json)
- [evidence/recovery-runtime-identity.json](evidence/recovery-runtime-identity.json) · SHA-256 `7cb601d9da3a9a619ff9ba5e5e6ed3fcc8ab5cdd9a280b403431a26a504a1f96` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/docs/evidence/2026-11-13-native-runtime-recovery/runtime-identity.json)
- [evidence/c6-recovery-originals.json](evidence/c6-recovery-originals.json) · SHA-256 `a50926cfa3bd3e09a4386e72f056a16aacf4ab5c46b0b81880c86ca9c44b83d9` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/docs/evidence/2026-11-13-native-runtime-recovery/c6-originals.json)
- [evidence/c6-mwdt-clock.json](evidence/c6-mwdt-clock.json) · SHA-256 `a7938c3e6ca8ddff82c0a24da050af31d4cecd018a72f986c56f837530da9051` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/esp32c6_mwdt_clock/evidence-summary.json)
- [evidence/c6-mwdt-final-runtime.json](evidence/c6-mwdt-final-runtime.json) · SHA-256 `f53b5ea2cc0f35aca8323f2333af917e4b19a9254844f8415926d6a5478f767f` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/esp32c6_mwdt_clock/final-runtime-summary.json)
- [evidence/c6-panel-rotation.json](evidence/c6-panel-rotation.json) · SHA-256 `0f6de9ec00f4449dc4a0cd847aeaf2a1f3c0ecc53dd63bb7eeb11b0465a3351c` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/esp32c6_panel_madctl/rotation-evidence-2026-11-13.json)
- [evidence/c6-panel-dma.json](evidence/c6-panel-dma.json) · SHA-256 `33c7941d4f07c9a3ae62eda769016944e69e2f85188bce6bb872841dffb3239e` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/esp32c6_panel_madctl/dma-evidence-2026-11-13.json)
- [evidence/c6-panel-chip-select.json](evidence/c6-panel-chip-select.json) · SHA-256 `7f206fb530f2e576dc78ff23f7a1682fd8575b01a9a7880b3af989aef336c4eb` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/esp32c6_panel_madctl/chip-select-evidence-2026-11-13.json)
- [evidence/nesso-source-touch-controls.json](evidence/nesso-source-touch-controls.json) · SHA-256 `767ac6872ea2f53a1ed4ce48122af54278bef7906ba15f3bb97d423751cc5cd5` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/nesso_touch_bus_shared/evidence-summary.json)
- [evidence/nesso-source-pins.json](evidence/nesso-source-pins.json) · SHA-256 `ee36524c6bc300e83b50fcf80e85379aeff3fd9f929fb55b8f5d8d505ce40d89` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/nesso_touch_bus_shared/source-pins.json)
- [evidence/ble-0198-progress.json](evidence/ble-0198-progress.json) · SHA-256 `1a68954d07dec1f794c078d24eb58be3736fcdd42b8c4ab9f03058f3eabb5c19` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/stickc_plus2_bt_lp_clock/ble-clock-evidence-summary.json)
- [evidence/stackchan-i2c-applications.json](evidence/stackchan-i2c-applications.json) · SHA-256 `799a97367e2ee1c8a4e8ba3839d7e37e395cfef41c9ecd6a3781e19297c6c6c1` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/s3_i2c_lifetime/application-evidence-2026-11-13.json)
- [evidence/stackchan-i2c-source-pins.json](evidence/stackchan-i2c-source-pins.json) · SHA-256 `052dc289f855f0e52f81f9d4b9ded0228564a1e8d7d732d93e973a3eee02afb1` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/s3_i2c_lifetime/application-source-pins.json)
- [evidence/stackchan-i2c-minimal.json](evidence/stackchan-i2c-minimal.json) · SHA-256 `7af68ea339097d74a89382a8e2486b0afd339df9ecd8f063deaa07f118df94de` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/s3_i2c_lifetime/evidence-summary.json)
- [evidence/input-reconnect.json](evidence/input-reconnect.json) · SHA-256 `5e3c6e4a4f732bae60546f867737800f8c65efc27ea53faca6ce23f0ddc1b1d0` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/service_input_reconnect/evidence-2026-11-13.json)
- [evidence/frame-orientation-history.json](evidence/frame-orientation-history.json) · SHA-256 `51b79074aa292c2bc42a12aa8ca6a08387e9ed6f14273ab9b068f5401e12bdf5` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/docs/evidence/2026-11-13-native-frame-orientation/summary.json)
- [evidence/p4-service-boundaries.json](evidence/p4-service-boundaries.json) · SHA-256 `ce5b7a2e912a8d353ac13f2b65fa8d0b3a5b707a321a024da13edd1bd19e0cbb` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/docs/evidence/2026-11-13-tab5-service-boundaries/summary.json)
- [evidence/p4-usb-model-gap.json](evidence/p4-usb-model-gap.json) · SHA-256 `d2aebb331027d00564c1872db1cc8a0f92c4c9b0026527849edd71cc29e5017e` · [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/4f09fcba8364e02cb1f60eeec0422e3cae66db54/tests/firmware/tab5_usb_model_gap/evidence-summary.json)
- [evidence/final-deployment.json](evidence/final-deployment.json) · SHA-256 `f046bf14dc25d0dd2a70e65c68cd930174b1adf44e15796dd12a80797cde788d`
- [evidence/final-main_ci.json](evidence/final-main_ci.json) · SHA-256 `a17d829b9384bc9bbd3dbcfd218906c706d037cacba311308bba87e5e2e7525c`
- [evidence/final-matrix.json](evidence/final-matrix.json) · SHA-256 `e3c5ee570c20b69c3aaaeba8ea28ec24a5888f3cf0241d360d4b359f9051d314`
- [evidence/final-orientation5.json](evidence/final-orientation5.json) · SHA-256 `8dfda5d97770903cbba0ddf0c8a61f2272b0b2df03cecf8a71b958416056aa58`
- [evidence/final-post9.json](evidence/final-post9.json) · SHA-256 `6e98deee86a89c66b2d94af5fc8b96a5779261561c8f81c3536245211fbfb598`
- [evidence/matrix-round-1-scope-1.json](evidence/matrix-round-1-scope-1.json) · SHA-256 `44a5fe6288e128f0419f343336e940d909b50d1b0121d3fc4c8a4659add25df2`
- [evidence/matrix-round-1-scope-2.json](evidence/matrix-round-1-scope-2.json) · SHA-256 `155ae85c80316e65eb3af6f140a8fdd399c5e92e01131076f3e2a23402c9a402`
- [evidence/matrix-round-1-scope-3.json](evidence/matrix-round-1-scope-3.json) · SHA-256 `24fa7231f51f804f58d05f4aca8116d109484315788f228f47e06812ec475ae4`
- [evidence/matrix-round-2-scope-1.json](evidence/matrix-round-2-scope-1.json) · SHA-256 `b20e0a735b5c9544f024d0e7ce33dcb410da93ddecd5481203a623e4e7dcd9df`
- [evidence/matrix-round-2-scope-2.json](evidence/matrix-round-2-scope-2.json) · SHA-256 `26b45536767a9b1bb6acb6f9aaafde19f7cd199fde5e81c43c09ff8a7b01ad7c`
- [evidence/matrix-round-2-scope-3.json](evidence/matrix-round-2-scope-3.json) · SHA-256 `9e940b38ff0a5a62f85022c01523879a3a4a84b7ac8a2d1d1b37521ea8f52382`
- [evidence/optional-original-review.json](evidence/optional-original-review.json) · SHA-256 `b16572a88739a4f4190eeaafc767f937a54bb34e6ebb32e1e601ba32abd04503`
- [evidence/retained-post-deploy-01.json](evidence/retained-post-deploy-01.json) · SHA-256 `cce6fc90fd00efdeba19a200f76bf8a0a405411114ecef4538f5a16449494680`
- [evidence/retained-post-deploy-02.json](evidence/retained-post-deploy-02.json) · SHA-256 `009610946116f704f47a9e0a4b15fb6d5328eb40e1ec3a4dcf1d12eb0eac009f`
- [evidence/retained-post-deploy-03.json](evidence/retained-post-deploy-03.json) · SHA-256 `096ef2d2a65a37b2cd6dcfd2b8dddf709e994674e7a7a922993a87042a49ece3`

## 保留失败、恢复与未覆盖项

部署后验收的早期脚本失败分别保留为 INFRA_FAILED；云端成功结果与编程脚本失败逐次记录，本地编程脚本存在 preview 创建追踪、请求 intent 观察或客户端请求上下文缺口。实际已创建的预览会话经身份绑定后导出 ZIP、关闭并清理；这不是固件失败，也不是零 guest。原始 FAIL 摘要和迁移/清理证据哈希保留。最终 9 条路径只采用通过的各自独立会话，云端结果复用来源单独校验；失败的编程尝试不替代任何最终门。

旧运行时恢复失败、观察性候选、无效测试配置、初始 Ham 主机依赖失败和早期矩阵失败
均保留在历史记录/固定源码摘要；新通过不删除它们。
部署备份与原配置/历史保留经审核。回滚验证仅为 30 项隔离主机控制测试，
服务与进程生命周期使用 mock；常驻服务实际回滚为 NOT RUN。既有状态目录保持原位，
本轮未迁移状态，也不声称状态路径完全独立。内部操作明细另层记录。
此目录没有原始串口、帧、PCAP、固件、ROM、会话身份或主机路径。
物理 RF、电气、功耗、机械、光学、熵及 browser-WASM 不继承原生虚拟设备结果。

## 本次原版操作与显示复验

六款 UIFlow2 设备通过八条云端路径取得官方配对码，另有一条本地程序下发成功；九个实际 guest 画面均经过复核。八条云端结果来自第二次验收，编程项在工具修复后独立重测，三次工具失败均单独保留。

原版 Cardputer ADV MP3 Player 列出 SD 卡中的 `TEST.MP3`，真实 Enter 输入后进入播放页并产生与 524 Hz 测试音一致的 PCM。原版 Core2 2048 两轮右、左、上、下共八次输入均符合棋盘滑动、合并与单个合法新方块规则；两份原 BIN 应用字节保持一致。见[实际操作摘要](evidence/original-functional-observations-summary.json)。这些是虚拟设备数据路径验证，物理声学及真机对照未执行，未提交 Burner。

原版 Core2 for AWS 在同一 35c 运行时另行运行 90.024 秒，实际首页文字、时钟和滚动提示可见，单次启动且无致命错误。BMI270 读取错误仍保留，未授予传感器、触摸或云端功能通过；首轮工具路径解析失败亦保留。见[同原版显示复验](evidence/aws-original-final-runtime-summary.json)。
