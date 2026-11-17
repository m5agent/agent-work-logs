# 保存快照审核与 Tab5 写入分类复验

## Dial 原版 U197 音频审核

用同一 vinylM5Dial 1.0 R1F30 镜像、保存快照描述和 16 kHz 单声道 WAV 工件，运行原生 Dial 和 Port B U197。审核等待实际 440 Hz 自播基线，然后发出 +1 的编码器输入。用基线留下的字节游标约束后续窗口，再从同会话 ZIP 原始 PCM 回核各窗口。初版给基线 3 秒，首次正向和错误频率对照都在取得可用基线前返回 `E_SIM_AUDIO_PARTIAL`。后续将 Unit 基线超时调整为 20 秒并保留该记录。

Reviewer `6402b43a6134778ee70f09e2cce1aec0658b43ba` 的正向案例取得 440 Hz 输入前基线和两个连续的曲目 2 样本窗。故意要求 1,318 Hz 后，在 24 个窗口中没有匹配，返回 `E_SIM_AUDIO_ASSERTION_FAILED`。实际样本中仍能找到夹具的曲目 2。关闭 `audio.read` 时预取返回 HTTP 403，ZIP 省略 PCM，保留 `PARTIAL` 与 `E_SIM_AUDIO_PARTIAL`。

集成 Reviewer `30524015c15ead7940a66b53f496e1cd5f1cea07` 独立重跑正向，基线为 440.000 Hz，字节游标 6,648。+1 后在偏移 35,320 和 39,416 分别取得 4,096 字节的连续窗，两个都逐字节匹配曲目 2 工件，独立估算主频均为 524.069 Hz。原版虚拟会话观察超过 60 秒，最终为 `done`。实际 ZIP、报告、基线前缀和目标样本均按同会话独立回核。 [正向、错误频率与权限对照](evidence/dial-u197-review-summary.redacted.json)

## 保存快照 SD 写入取证准入

集成 Reviewer 的 PaperDIY 保存快照规划能识别 `PAPER_DIY` 和 `PAPERDIY`，选择原生 QEMU 整机计划，并根据所配置的写入采样能力准入。另一个直接 Device Service 用例用固定 PaperDIY 探针完成插卡、六次 SPI CMD24、拔卡、重插和文件回读。PaperDIY 本次验收覆盖实际 Reviewer 规划和准入，以及独立的来宾存储用例。完整 PaperDIY Reviewer 任务为 `NOT RUN`。

原版 PaperS3 Factory V0.5 完成隔离 Reviewer 任务，观察超过 60 秒，按键 A 已接受，启动与界面通过。计划因未声明 `sd_write_stamp` 在准入阶段保留采样 `NOT RUN`，该审核会话发出零次自动采样请求。另一次独立路由探测返回 HTTP 409 和 `sd_write_stamp_unsupported`。整单保留 `E_SIM_SD_WRITE_PARTIAL`。早期脚本曾把 PaperDIY 拔卡产生的 409 计入 PaperS3 窗口，后来按会话归属核对并重跑。

独立的旧 Device Service 对照用同一 CardputerDict 原版完成保存快照审核，兼容的 SPI 路径仍可核对保留文件 `/dictionaries/ecdict.cidx` 的实际 68 字节和摘要。SD 项通过，整单因交互声明仍为 `E_INTERACTION_CLAIM_PARTIAL`。三项证据均按各自执行范围归档，检测结束后隔离进程退出、活动租约为零。 [准入、拒绝与旧服务回归](evidence/reviewer-sd-admission-summary.redacted.json)

## Tab5 历史原版的写入报告冲突

Tab5 诊断分类把同一次 core dump 写入的失败行与随后出现的保存行绑定。98TAB5 历史原版串口共有 31 组冲突，当前分类为 `write_failed`，同时记录 `saved_reported=true` 和 `conflicting_reports=true`。旧版把末尾保存文案汇总成 `flash_reported_saved`。当前分类保留了更早的失败依据。CarPlay 对照无写入报告，M5TabOS 历史文件仍为 `flash_check_failed`。

输入为同一批历史证据 ZIP。只对已停止的 98TAB5 与 CarPlay 副本执行 GET，新的 HTTP 诊断和 ZIP 输出一致。集成 Device Service 1.81.0 再次完成这两个只读 GET/ZIP 验证，公开 OpenAPI 响应与源码逐字节一致。M5TabOS 仅执行解析器回放，HTTP 为 `NOT RUN`。三份原始 UART 摘要核对一致，旧记录的其他诊断保留。此次启动零个来宾，也没有重新判断复位根因、启动就绪或实体 Flash 写入。 [三份历史证据](evidence/tab5-stock-write-report-summary.redacted.json)

实机、浏览器和常驻服务部署为 `NOT RUN`。本轮未提交 Burner。


## 源码与校验

模拟器主线为 `b92d7b5630687cb7d7142346a39839ef61bd0116`，Device Service API 为 1.81.0。最终平台套件执行 2,416 项，跳过 10 项，其余通过。运行覆盖、外设目录、QEMU 配置、项目快照与变更范围通过。Reviewer 主线为 `30524015c15ead7940a66b53f496e1cd5f1cea07`，API 0.11.0，210 项本地测试通过。归档时模拟器远程 CI 仍在进行。可分别撤销相关提交以回滚。 [模拟器主线](https://github.com/m5agent/m5stack-esp-emulator/commit/b92d7b5630687cb7d7142346a39839ef61bd0116)
