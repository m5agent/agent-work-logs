# 原版 NC1020 恢复后显示复验

前次跨服务验证从实际生成的 FAT32 文件恢复 NC1020，但两份恢复帧均缺少完整图案。
本次在 Device Service 1.87.0 复用同一填充后 Flash 和保存卡，验证存储和显示是否同时复现。
原版应用仍是 Cardputer K132 的 NC1020，使用原生 QEMU 默认定时与隔离状态，不启用 NIC。
[前次执行记录](https://github.com/m5agent/agent-work-logs/blob/238021b45acdef2e6d7142c8fb0d19712833a84fa1/records/esp-emulator/2026-11-18-native-integrated-guest-validation/followups/2026-11-18-nc1020-storage-display-attribution/report.md)

## 复现步骤

1. 使用固定版本的 Device Service 和原生 Xtensa QEMU，确认 ROM、OpenAPI 和输入文件的 SHA-256。8 MiB
   原版镜像与留存 Flash 的 factory 分区从 `0x10000` 起逐字节相同。
2. 通过 `POST /artifacts` 登记留存 Flash 与 64 MiB FAT32 卡，通过 `POST /firmware/import`
   为 Cardputer 导入该 Flash。在独立状态目录创建原生会话，挂载此 SD 工件。
3. 等待来宾确认 ROM、NOR 预填充、`state restored`、`LoadNC2k() returned` 及首个心跳。
   保持零输入，通过 `frame.png?max_age_ms=0` 在约 0、2、8 秒各强制采样一次。
4. 读取同会话 `storage/sd/read-stats` 和 Flash 的 factory、ROM、NOR 分区摘要。
   停机前取证并校验证据 ZIP。使用 `purge=0&retain_flash=0` 停止，读回保留的 SD
   清单，核对状态文件哈希。确认来宾退出、租约为零并关闭独立服务。
5. 另启一份空白服务状态，用相同工件和步骤复测一次。保留两次结果。

[固定 API 说明](https://github.com/m5agent/m5stack-esp-emulator/blob/d25eae8db848918e9cafebc127a53a0f989941d4/docs/device-service-api.md) · [完整身份和时间记录](evidence/nc1020-restored-187.summary.json)

## 观察结果

| 路径 | A1 | A2 |
| --- | --- | --- |
| 同一份状态文件 | 99,384 字节，SHA-256 匹配 | 99,384 字节，SHA-256 匹配 |
| 接受 CMD17 并完整返回 | 407 | 407 |
| 来宾心跳 | 73，累计绘制 1 | 70，累计绘制 0 |
| 三次当前帧的实际像素 | 25,112 个非黑像素，3 色，作者图案 100% | 120 个非黑像素，2 色，作者图案 0% |
| 首个心跳 | 周期 164,524,339，RTC 11:14:55，绘制数增加 1 | 同周期同 RTC，绘制数增加 0 |
| 停机 | 历史保留，Flash 释放，租约归零 | 历史保留，Flash 释放，租约归零 |

两次报告相同的 `sleeping=0`、`lcdon=1`、`lcden=1` 和 `lcdbuffaddr=0x9c0`。
ROM、NOR、factory 和恢复后的状态文件字节相同。首次可观测差异出现在相等来宾周期的绘制计数。
第一轮三帧的 SHA-256 相同，第二轮的三帧也分别相同，但两轮互不相同。
画面差异与来宾绘制计数同时出现，显示问题的根因仍未定位。
前次 ESP-IDF 5.4.1 SPI 总线锁对照保留为线索，原版来宾现场归因为 `NOT RUN`。
[两轮精确哈希及串口、SPI 和画面摘要](evidence/nc1020-restored-187.summary.json)

存档恢复为 `PASS`，显示稳定性为 `PARTIAL`。本次仅执行留存状态的恢复，没有生成替换固件。
实体设备、浏览器、冷导入、重新保存、常驻服务切换和 Burner 仍为 `NOT RUN`。
