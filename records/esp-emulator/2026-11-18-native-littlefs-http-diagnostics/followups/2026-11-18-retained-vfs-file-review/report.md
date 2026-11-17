# 原生 VFS 留存清单与文件摘要审核

## Device Service 比较契约

Device Service 1.83.0 的内部文件系统清单接口继续读取结束并保留 Flash 的同会话分区。选择 `include_source=1` 后，服务额外核验已应用的源夹具摘要、分区尺寸和文件系统几何，并返回源夹具清单供调用方对照。会话需已停止、租约已释放，并满足既有 `storage.read` 与 `flash.read`。两个清单均包含有界元数据和文件摘要。源夹具缺失或摘要不符时，对照路径返回 409，常规清单仍可读取留存 Flash。

初版 `9db66ecb` 使用默认 URL 查询解析，空值会被忽略。`bb94ea01` 对此端点保留空值再严格验证，实际 HTTP 的空值、重复值和其他无效值均被拒绝。省略选项仍返回原形状，导出仍限定于已应用的分区。

## 原生 Device Service 实测

以 Cardputer ADV 的 ESP-IDF 6.1.1 LittleFS 夹具和固定原生 QEMU 执行。第一会话通过串口确认读取种子、写入并重新挂载读回。停止并重启 Device Service 后仍能读取源与留存清单，导出限定在 1 MiB 分区。第二会话复用该导出并观察到先前文件。第三会话重用原种子，来宾报告起初没有前一会话的输出。三份 ZIP 均核对了同会话串口、来源身份和实际 Flash 分区摘要。分区以外字节保持不变，结束后 Flash 已释放，活动租约为零。 [Device Service 三会话](evidence/device-service-littlefs-comparison.summary.json)

## 保存快照 Reviewer 实测

使用 Device Service `bb94ea01e65da8c94c709960fbf4c05fc6ea261f`、Reviewer `4ffd5d951d42bab8e3c0834bbd01a0b1820073b0` 和相同 QEMU。Cardputer ADV 使用 ESP-IDF 6.1.1 LittleFS，Cardputer 使用 ESP-IDF 5.5.4 SPIFFS。Reviewer 在同一会话停止后读取两份清单，随后释放 Flash。六份断言收据与报告一致，ZIP 的原始虚拟 Flash 分区摘要与停机后回执一致。 [Reviewer 六个终态](evidence/reviewer-vfs-file-digest.summary.json)

| 文件对照 | 结果 |
| --- | --- |
| LittleFS 新文件，实际摘要符合请求 | PASS |
| LittleFS 实际写入，预期摘要故意不符 | FAIL |
| LittleFS 未生成指定路径 | FAIL |
| LittleFS 源夹具已有相同文件，留存仍相同 | PARTIAL，无法证明新增或改写 |
| LittleFS 源夹具已有请求内容，来宾随后覆盖为不同内容 | FAIL，停机后实际摘要不符 |
| SPIFFS 新文件，实际摘要符合请求 | PASS |

六次观察均保留无画面夹具的整单 `manual_review / E_NO_FRAME`。首轮直接实验的启动包装器板型名有误，两个早期审核预检也缺少冻结 Flash 辅助程序。三次均在来宾执行前终止。修正实验环境后的结果见对应终态证据。

## 源码与未覆盖项

模拟器主分支 `dacf6efbb7c7836821874916ff704ba6b96a2e49` 的产品代码和 OpenAPI 与实际来宾检查使用的版本字节一致。首轮本地套件发现旧 API sweep 摘要和项目快照需要更新，修正后完整重跑 2,418 项，跳过 10 项，零失败。Reviewer 225 项通过。文档 51 项、生成校验和改动范围检查通过。归档时准确提交的 GitHub CI 尚未完成。 [已发布原生证据](https://github.com/m5agent/m5stack-esp-emulator/blob/dacf6efbb7c7836821874916ff704ba6b96a2e49/tests/firmware/littlefs_partition/reviewer-output-summary.json) · [持续集成](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/44192637455)

实机、浏览器、常驻部署、Pages 部署和 Burner 提交均为 `NOT RUN`。
