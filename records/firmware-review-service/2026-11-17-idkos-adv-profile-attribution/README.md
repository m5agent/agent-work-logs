# idkOS v1.3.0 启动失败归因：ADV 固件被按 Cardputer 机型审查

- 日期：`2026-11-17`
- 结果：`PARTIAL`（归因完成；真机与完整应用功能未运行）
- 工作类型：`service_debug`
- 问题来源：固件审查任务 `job-67de39da0d65`（`SIM_PARTIAL` / `manual_review` / `E_SIM_MODEL_GAP`）
- 源码版本：`m5agent/m5stack-esp-emulator @ 55e5763e`；Device Service `v1`
- 环境：macOS arm64；原生 QEMU ESP32-S3（`m5cardputer` / `m5cardputeradv`）；审查服务只读归因

## 结论

本次启动失败**不是模拟器模型缺口**。同一个 BIN 在 `cardputer-adv`（`m5cardputeradv`，K132-Adv）上
稳定启动并出现 idkOS 首帧（两次会话帧 SHA-256 完全相同）；失败发生在 `cardputer`
（`m5cardputer`，K132）机型上，因为该 BIN 是 Cardputer-ADV 专用固件，而 M5Burner 元数据把设备
标成 `Cardputer` / `CARDPUTER`，审查服务据此选择了非 ADV 机型。

在非 ADV 机型上，固件自行打印并绘制 `DEVICE CHECK / ADV not detected / Check hardware/library
setup`，随后进入非 ADV 回退路径，`i2c_set_pin` 报 `scl and sda gpio numbers are the same`，
再出现 `Interrupt wdt timeout on CPU1`（审查任务）或串口停住（本次复跑）。这是固件对不受支持
机型的回退行为，不是 QEMU 断言、外设模型缺失或启动竞态；因此未开模拟器 issue。

## 关键证据

- 审查任务串口：ROM 正常进入 app，3 次 `i2c_set_pin` 同引脚错误，随后 2 次 CPU1 中断看门狗
  panic，194 B 黑帧，`crash-diagnostics.json` 标记 `backend_illegal_instruction=false`、
  无 QEMU 断言、8 MiB flash 契约匹配。
- 机型 A/B（同一 8 MiB 合成镜像 `608952df…`，源 BIN `c44c8f76…`）：
  - `cardputer-adv` 两次：非空首帧 9972 B / 7357 非黑像素 / 314 色，帧 SHA-256
    `e85c3992…`；串口无 i2c 错误、无 panic。
  - `cardputer` 一次：同样的 `scl and sda` 错误；帧 649 B，内容为固件自绘的
    `ADV not detected` 诊断页；串口停在 NVS 错误后不再增长。
- 首帧与诊断页 PNG、审查串口和崩溃摘要均在 `evidence/`。

## 文件

- `report.md`：完整归因、A/B 方法、根因链与未开 issue 的理由
- `run.json`：结构化记录
- `evidence/`：串口、崩溃摘要、两种机型首帧 PNG、归因摘要 JSON

## 未覆盖项

- 真实 Cardputer / Cardputer-ADV 上的烧录复跑：`NOT RUN`。
- idkOS 的 Wi-Fi、SSH、日历、主题切换等应用功能：`NOT RUN`；仅确认首帧。
- 崩溃地址符号化：`NOT RUN`，审查任务与本次复跑均无匹配 ELF。
- 60 s 采样观察协议：`NOT RUN`；ADV 会话只确认首帧后无 panic，未做完整观察窗口。
- 模拟器代码、审查服务代码和 M5Burner 元数据：均未修改、未提交。
