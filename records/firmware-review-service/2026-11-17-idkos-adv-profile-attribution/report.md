# idkOS v1.3.0（Cardputer-ADV）启动失败归因报告

## 1. 任务与目标

固件审查任务 `job-67de39da0d65` 以 `SIM_PARTIAL` / `manual_review` / `E_SIM_MODEL_GAP`
收口，结论称“cardputer 虚拟后端仅部分覆盖，记录到异常终止（Interrupt wdt timeout on CPU1），
现有证据无法区分固件问题与模拟器模型缺口”。

目标：只读取证，判定这次启动失败是模拟器（QEMU / 外设模型）问题还是固件或设备选择问题；
仅在能归因到模拟器时提交可复现 issue。

输入：

| 项 | 值 |
| --- | --- |
| 固件 | idkOS v1.3.0（`idkOS ADV`） |
| 文件 | `idkOS-v1.3.0-Cardputer-ADV-full-0x0.bin` |
| 大小 / SHA-256 | 1,643,488 B / `c44c8f76567c3fb757be802e150ee6ef8db84bfc0c856a7b6cf880a030d2b1f9` |
| M5Burner 声明设备 | `Cardputer`，`deviceCodes=["CARDPUTER"]` |
| 声称硬件（描述页） | M5Stack Cardputer ADV |
| 版本 ID | `2122678585678315521` |
| 合成 8 MiB 镜像 | `608952df07d22addd70f29032595113f7197f9fc528bcd963a51b9bf13c529b8` |
| 审查会话 | `cbdd30535dae4562a6ca883130fcdfbb` |

## 2. 失败阶段判定

结论：失败发生在 **guest 应用初始化阶段**，不是 QEMU 断言、模型缺失、镜像/分区解析或启动竞态。

依据：

- 串口从 ROM 正常走到 app：`ESP-ROM:esp32s3-20210327` → `entry 0x403c98d0`；QEMU stderr 只有
  `Adding SPI flash device`，没有断言、非法指令或后端错误。
- 静态分析：bootloader / app0 有效，8 MiB flash 契约匹配（`declared_flash_size=8388608`,
  `partition_end=8388608`, `partitions_fit=true`）；app1 为空是合并镜像的正常形态。
- `crash-diagnostics.json`：`kind=watchdog`、`core=1`、`panic_count=2`、
  `backend_illegal_instruction=false`、`elf.status=not_uploaded`；无 QEMU 侧观测。
- 串口先出现 3 次 `i2c_set_pin(882): scl and sda gpio numbers are the same` 和
  `i2c_param_config failed`，随后才 panic；说明应用已经运行，在 I2C 初始化路径上失败。

## 3. 根因链

1. 该 BIN 是 **Cardputer-ADV 专用构建**：文件名、app descriptor `idkOS ADV`、描述页
   “for the M5Stack Cardputer ADV” 都指向 ADV；固件内含 `ADV not detected` 自检字符串。
2. M5Burner 元数据把设备字段标成 `Cardputer` / `CARDPUTER`（不是 `CARDPUTER_ADV`）。
3. 审查服务按 `deviceCodes` 映射（`CARDPUTER → cardputer`）创建了 `cardputer` 机型会话，
   使用 `m5cardputer`（K132，非 ADV）而非 `m5cardputeradv`（K132-Adv）。
4. 固件在 K132 上正确判定 `ADV not detected`，绘制
   `DEVICE CHECK / ADV not detected / Check hardware/library setup` 诊断页。
5. 随后固件进入非 ADV 回退路径，用相同的 GPIO 号初始化 I2C（`scl == sda`），
   Arduino HAL 初始化失败；审查任务随后触发 CPU1 中断看门狗 panic。

因此，**“ADV 固件 + 非 ADV 机型”是这次失败的直接原因**；模拟器的两个机型档案本身行为符合
各自硬件（K132 没有 ADV 识别上拉，K132-Adv 有）。

## 4. 机型 A/B 复现

同一源 BIN 与同一合成镜像，仅改变 Device Service 的 `device_id`：

| 会话 | 机型 | 首帧 | 串口关键行为 | 结果 |
| --- | --- | --- | --- | --- |
| `cbdd3053…`（审查任务） | `cardputer` | 174 B 全黑 | 3× `scl and sda` 同引脚，CPU1 IWDG panic ×2 | 失败（非 ADV 机型） |
| `5969a098…`（本次复跑） | `cardputer` | 649 B，固件自绘 `ADV not detected` | 同样的 `scl and sda` 错误；串口停在 NVS 错误后 | 失败（非 ADV 机型） |
| `7dba7685…`（本次复跑） | `cardputer-adv` | 9972 B / 7357 非黑 / 314 色 | 无 i2c 错误、无 panic；NVS 空、Wi-Fi 未配置、SD 无卡告警 | 启动成功，8.7 s 首帧 |
| `7c2ed46f…`（本次复跑） | `cardputer-adv` | 9972 B / 7357 非黑 / 314 色 | 同上 | 启动成功，帧 SHA-256 与上一次相同 |

ADV 首帧 SHA-256：`e85c39928e857cea1c7a071499f2a2e2319862b695b7bf6487764ef31491ec8c`
（两次会话完全一致）。画面为 idkOS 启动页。

失败机型首帧 SHA-256：
`055320a15a474a5fde6e9ce8a18e47fc4144d144493d9e0a6f094007afdffc47`
（`DEVICE CHECK / ADV not detected` 诊断页）。

## 5. 为什么不是模拟器缺陷

- `cardputer-adv` 档案被服务标记为 `peripheral_status=simulated`、`coverage.complete=true`，
  同一 BIN 在该档案上确定性启动并出帧；没有修改模拟器代码或夹具。
- `cardputer` 档案是 K132 非 ADV 机型，缺少 ADV 的 GPIO8/9 识别上拉是**正确建模**；固件因此
  走 “ADV not detected” 分支。
- 没有 QEMU 断言、后端非法指令、镜像解析错误或启动竞态；失败点在 guest 的 I2C 初始化。
- 非 ADV 分支的 `scl == sda` 是固件自身的回退实现问题；在真实非 ADV Cardputer 上也会走同一
  代码路径（真机未运行，见边界）。

## 6. 查重与未开 issue 的理由

- `gh issue list --search` 检查：无 `idkOS`、无 `i2c_set_pin` / `scl and sda` 同引脚、
  无 “ADV 固件被路由到非 ADV 机型” 的既有 issue。
- [#230](https://github.com/m5agent/m5stack-esp-emulator/issues/230)（已关闭）是 M5Unified
  运行时板型探测回退为 `board_M5StampS3(136)`，现象为 `Unsupported board type: 136` 与
  174 B 全黑帧；本任务没有该串口行，且 ADV 机型正常出帧，不是同一问题。
- [#234](https://github.com/m5agent/m5stack-esp-emulator/issues/234)（开放）是 16 MB 分区表
  镜像被 8 MB 机型接受的 intake 缺口；本 BIN 的 flash 契约是 8 MiB，匹配，不适用。
- 结论：不可归因到模拟器，**未创建 issue**，也未向任何既有 issue 追加评论。

## 7. 非模拟器侧的后续建议

1. 上游固件元数据：把 M5Burner 设备字段改为 Cardputer-ADV（或同时声明 `CARDPUTER_ADV`），
   使审查服务映射到 `cardputer-adv`。
2. 审查服务：当固件名/描述明确写 ADV、但 `deviceCodes` 只有 `CARDPUTER` 时，标记歧义并转人工，
   或在结论中写明“按非 ADV 机型运行不构成模型缺口”。
3. 固件自身：非 ADV 分支应在绘制 `ADV not detected` 后安全停机，而不是继续用相同 SCL/SDA
   引脚初始化 I2C（该路径会 panic/挂起）。

## 8. 复现步骤（不含内网端点）

1. 将源 BIN 作为 artifact 上传到本机 Device Service。
2. 以 `{"device_id":"cardputer-adv","kind":"merged","artifact_id":"<源 SHA-256>"}` 合成镜像，
   得到 `608952df…`。
3. 以 `{"device_id":"cardputer-adv","firmware_id":"608952df…","ttl_seconds":600}` 建会话，
   调用 `POST /api/v1/sessions/{id}/wait`（`frame_nonblank=true`, `frame_min_bytes=1024`），
   读取 `/serial` 与 `/frame.png`。
4. 对照：将同一 artifact 以 `device_id=cardputer` 合成并建会话，重复读取串口和帧。
5. 结束后 `DELETE /api/v1/sessions/{id}?purge=0&retain_flash=0`，保留历史证据。

## 9. 证据等级与边界

- **virtual-device validation**：QEMU 内两个机型档案的 A/B 串口、首帧、帧哈希与会话状态。
- **code-level verification**：固件字符串/描述与 `ADV not detected` 自检、审查服务
  `CARDPUTER → cardputer` 映射、镜像静态分析。
- **NOT RUN**：真实 Cardputer / Cardputer-ADV 烧录；ELF 符号化（无匹配 ELF）；
  idkOS 的 Wi-Fi/SSH/日历/主题等应用功能；60 s 采样观察协议。
- 本记录不主张模拟器缺陷，也未修改模拟器、审查服务或 M5Burner 元数据。
