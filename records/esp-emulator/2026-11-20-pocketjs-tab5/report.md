# PocketJS Tab5 兼容性复验

## PocketJS 主仓库

构建 [PocketJS v0.17.0 `prebuilt` ESP-IDF 示例](https://github.com/pocket-nexus/pocketjs/tree/83c6cac996237968785125118b543cd4e339254c/tests/esp-idf/examples/prebuilt)。使用 ESP-IDF `v6.0.2`、Bun `1.4.2`、Rust `1.93.0` 和 QuickJS-NG `0.14.0`。构建产物的 SHA-256 为 `a82b994aca1aa1ee1de94ef6c7d585ac0637f51c99bc61ef1462ff8cbff8928e`。

- 用 `bun install --frozen-lockfile` 安装依赖。运行 `bun tools/pocket.ts host export --config tests/esp-idf/examples/prebuilt/pocket.host.config.ts --out "$PROFILE"`。运行仓库的 `bun tools/packaging/esp-idf/native.ts --target esp32p4 --cargo "$PINNED_CARGO" --archiver "$RISCV_AR"`。
- 在 `tests/esp-idf/examples/prebuilt` 按 `esp32p4` 构建，传 `-DPOCKETJS_RUST_FROM_SOURCE=OFF -DPOCKETJS_PROFILE_EXPORT_DIR="$PROFILE"`。在 `sdkconfig.defaults` 之后合入 `CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y`、`CONFIG_ESP32P4_SELECTS_REV_LESS_V3=y`、`CONFIG_ESP32P4_REV_MIN_100=y`，对应本次虚拟板的 Flash 容量与 v1.0 revision。
- 保留默认构建的 `pocket_memory_package.flags` 缺少显式初始化诊断。用 ESP-IDF 的 `EXTRA_CFLAGS=-Wno-error=missing-field-initializers` 重新配置并构建，源码使用 tag 原样内容。用 `idf.py merge-bin` 合并完整镜像。
- 独立会话的串口结果为 `PASS target=idf-smoke hash=4a36c3de04507602 flush=15 buffers=2 bytes=20480`。示例使用自身的 RGB565 内存传输校验，不初始化 Tab5 面板。真实 DSI 帧和触摸来自下面的独立固件验证。

## Pocket M5 原版 Tab5 固件

[上游 Pocket M5 v0.1.4](https://github.com/pocket-nexus/pocket-m5/releases/tag/v0.1.4) 使用 PocketJS `806ac202`。发布 BIN SHA-256 为 `26d7bb07fc3e35b759d5a1f2acddef675957d808bf7130b3eb975c6a36f2b99e`，Device Service 规范化至 16 MiB 后为 `814ffdcc234d60f951c34c39cb1830bc4b6b5497ba209f0dc0463dc79f3ea593`。无对应 ELF，使用 [Device Service `cc25a8a8` 的原生 DSI 及 GT911 入口](https://github.com/m5agent/m5stack-esp-emulator/blob/cc25a8a8ac083e00608d591281289f1452cc75ac/docs/device-service-api.md)。

1. 将发布 BIN 提交给 `/api/v1/artifacts`。通用 `/api/v1/firmware/import` 在可打印字符串的 URL 静态扫描步骤返回 HTTP 400 `Invalid IPv6 URL`。完整镜像入口 `POST /api/v1/firmware` 接受同原始文件，请求字段为 `device_id: tab5`、`kind: merged`、`artifact_id: <发布文件 SHA-256>`。
2. 在独立 Device Service 配置 `M5_TAB5_DSI_EMULATOR`、`M5_TAB5_GT911_PART`、`M5_TAB5_DSI_BOARD=gt911-ili9881c` 和 `M5_TAB5_DSI_FIRMWARE_SHA256S`。使用摘要中的运行时和 Part 哈希，准入表填规范化镜像的 SHA-256。对每个镜像用 `POST /api/v1/sessions` 创建 Tab5 会话，指定 `runtime: qemu` 和已登记 `firmware_id`。
3. 从同一会话读串口和 720×1280 原生 DSI 帧。显示桌面后用 `/input` 发送 `kind: touch`，按原生面板坐标依次点击 `(99,959)`、`(42,120)`、`(360,72)`。GT911 分别确认 8/8、7/7、7/7 份事件。串口记录 `unit-swap worker: porta node declared`，画面依次显示 `Unit Swap`、`EXT 5V off` 和恢复的 Pocket Shell。该观测覆盖 GUI 状态，外接 Unit 与真实供电未测量。
4. 第二个同配置新会话点击 `(97,1175)`。控制器确认 8/8，串口记录 `slot e6868f6a5616c4fe did not boot`。音频在两个会话启动时均报告 codec 初始化失败。ESP-Hosted 记录 host `3.0.10` 和 coprocessor `2.12.6` 的版本差异。联网数据面未执行。
5. 停机前收集 evidence ZIP。以 `purge=0` 停止，检查终态为 `stopped`，独立可写 Flash 和 companion socket 已释放。ZIP 和原始帧的哈希保留在[脱敏摘要](evidence/virtual-device.summary.json)。

本次属于 `virtual-device validation`。浏览器 WASM、物理硬件、其他主机和外接 Unit 为 `NOT RUN`。源码和常驻服务均无改动。
