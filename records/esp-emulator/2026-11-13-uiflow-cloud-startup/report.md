# UIFlow2 原版启动与云端配对修复报告

## 背景与验收目标

用户报告刷入 UIFlow2 并联网后没有自动出现配对码。验收目标是让原版固件按其
官方启动逻辑取得云端响应并显示 Access Code，同时保留现有本地编程与任意 BIN
工作流。一次 HTTP 创建成功、REPL 就绪、`running` 或固件连接状态均不作为配对
成功的替代证据。本记录为 virtual-device validation。

## 根因与修复

旧 UIFlow2 入口实际选择本地编程环境，替换启动文件进入 UART REPL，未选择
官方云端启动配置。旧入口对照的 framebuffer 为全黑；这不能证明原版
UIFlow2 固件存在缺陷。新入口明确区分官方云端启动与本地 MicroPython 编程。

新增 `uiflow_startup={mode:"cloud",reference_sha256:<advertised SHA>}`。
服务只广告六个已准入原版镜像的精确 SHA，并在创建时重新校验。网络使用真实
`qemu-wifi`，NVS 配置完整官方字段和 typed `u8` 的 `boot_option=1`，沿用隔离
NVS overlay。官方应用、开机脚本、filesystem 和不可变原始 BIN 保持原样。
生成 NVS 与官方 `esp-idf-nvs-partition-gen 0.3.0` 逐字节相同。

原版 BIN 省略尾部擦除空间，导致初版新 API 在 CoreS3、StickS3、Core2 的完整
Flash 长度校验处失败。修复沿用已有 padding helper，只补尾部 `0xff`；原始、
规范化和 NVS artifact 均由会话引用。规范化使用独立 artifact，不调用会覆盖
同 SHA 固件元数据的 merged FirmwareStore 写入。已有 manifest 的原 metadata
和固件 bytes 均有回归保护；不通过复用其准入信息绕过调用者限制。

缺少专用 radio runtime 的 Core2 不广告 cloud 能力。调用者合法网络策略仍按
原有规则验证和执行，不扩展 egress 权限。固定 AP 与模式冲突字段被拒绝；
原请求幂等、历史恢复、双 SHA 来源和证据引用保持。服务不生成或替代云端配对码。

Core2 还接通已有真实 eFuse controller 的 drive。独立原 IDF 探针在 plain 和
Wi-Fi 两会话中通过三条 guest API 读回身份并验证 ROM CRC；该独立证据见
[Core2 身份读回](https://github.com/m5agent/m5stack-esp-emulator/blob/8598b1f603ae6638a3f6d27824431781429b9e49/tests/firmware/esp32_efuse_identity/evidence-2026-11-13-core2.json)，不把该结果转授 C6 或物理安全特性。

## 同路径执行与保留失败

[白名单摘要](evidence/validation-summary.json)保留全部可公开身份和结果：

| 阶段 | 观察 | 状态 |
| --- | --- | --- |
| 旧本地编程入口 | REPL 可用；原厂云端页面未启动，frame 全黑 | 对照保留 |
| 初版 cloud API | 三设备输入 BIN 短于物理 Flash，校验拒绝；没有应用帧 | FAIL |
| 最终原版 API | 六设备 DHCP/DNS/SNTP/MQTT 实际交换，收到六位数字配对回复，官方页面逐帧确认 | PASS |
| 最终真实网页 | CoreS3、StickS3 分别选择官方入口，实际回复和可读官方画面，页面无错误且停止 | PASS |
| 本地编程对照 | guest 实际串口 marker 与蓝底 `Local code OK` 绘图，停止完成；在最终 artifact helper 微调前 | PASS（限定阶段） |
| 清场 | 上述会话证据先于停止保存；停止、lease 释放、历史保留 | PASS |

MQTT 摘要中的 topic 检查仅表示规定下行前缀，不表示与某个设备身份逐字匹配。
代码内容、连接凭据、MAC、会话 ID、端点和原始截图均未公开。固件可能关闭 INFO
日志，因此不以缺少 `New AccessCode` marker 判失败。帧哈希本身也不替代人工
确认配对码语义。

## 复现步骤与验证层级

在有对应设备 profile、原生网络控制器和摘要固定 SHA 的原版参考 BIN 的环境中：

1. 查询 `GET /api/v1/devices/{device_id}`，取得 `uiflow_startup` 广告。
2. `POST /api/v1/sessions` 携设备、合法 TTL/幂等键和上述 cloud 对象。不要混入
   `program_mode`、`firmware_id` 或手工 `nvs`。
3. 从同会话读取 frame、串口与 evidence，检查实际配对回包及官方显示；保存
   evidence 后调用 `DELETE /api/v1/sessions/{id}?purge=0`，验证停止与 lease 释放。
4. 从真实网页重复官方模式，并切换本地编程模式执行实际绘图/串口代码。

| 验收层级 | 状态 | 依据 |
| --- | --- | --- |
| build | NOT RUN | 此记录复用精确运行时产物，未重新构建 native/WASM runtime |
| source_checks | PASS | 全平台 2098 项（1 skip）、Node contracts、四项 validators、范围检查 |
| flash | PASS | 原始 pin、仅尾部补齐、会话隔离 NVS 和完整镜像校验 |
| transport | PASS | 同 guest DHCP、DNS、SNTP、MQTT 实际交换 |
| device_response | PASS | MQTT 成功连接并收到非空六位配对响应 |
| data_behavior | PASS | 原厂路径显示真实码；独立编程路径执行应用输出 |
| visual_or_physical | PASS（virtual） | 六份官方 API 帧、两份网页入口帧及编程绘图；无物理测量 |
| delivery | PASS（限定范围） | 源码已发布 main，CI 通过，发布后原版用户路径另有独立 follow-up |

已执行最小相关回归 34 项，涵盖 NVS、cloud startup、Wi-Fi、网络执行和 API
inventory。随后在冻结的最终源码上完成全平台 2098 项：2097 通过、1 跳过、
零失败或错误，耗时 298.129 秒，Python 3.13.15；Node contracts 通过，耗时
13.107 秒；四项 validators 和范围检查通过，新增证据 36,245 字节。详见
[最终源码检查摘要](evidence/source-checks-summary.json)。

首次平台检查因未加载已有依赖及文档收尾产生 4 failure、14 error、47 skip
（2084 项）；保留为[首轮失败摘要](evidence/first-platform-check-failure-summary.json)。
加载依赖后的下一轮有 2098 项、1 failure、1 skip，唯一失败是文档全局日期
不一致；保留为[日期合同失败摘要](evidence/platform-doc-date-failure-summary.json)。
最终仅修正文档日期并再生快照后完整重跑通过，早期失败未覆盖。

## 固定源码引用

以下链接固定到已发布并回读的 main 提交；发布后行为由
[独立 follow-up](followups/2026-11-13-published-source-paths/README.md) 验收：

- [platform/tools/uiflow_cloud_startup.py](https://github.com/m5agent/m5stack-esp-emulator/blob/8598b1f603ae6638a3f6d27824431781429b9e49/platform/tools/uiflow_cloud_startup.py)：准入、NVS、真实网络默认与独立 artifact。
- [platform/tools/device_service.py](https://github.com/m5agent/m5stack-esp-emulator/blob/8598b1f603ae6638a3f6d27824431781429b9e49/platform/tools/device_service.py)：会话编排、历史和证据绑定。
- [platform/tests/test_uiflow_cloud_startup.py](https://github.com/m5agent/m5stack-esp-emulator/blob/8598b1f603ae6638a3f6d27824431781429b9e49/platform/tests/test_uiflow_cloud_startup.py)：pin、NVS、policy、幂等、恢复及 manifest 保护回归。
- [docs/evidence/2026-11-13-uiflow-cloud-startup/README.md](https://github.com/m5agent/m5stack-esp-emulator/blob/8598b1f603ae6638a3f6d27824431781429b9e49/docs/evidence/2026-11-13-uiflow-cloud-startup/README.md)：同路径证据。
- [tests/firmware/esp32_efuse_identity/evidence-2026-11-13-core2.json](https://github.com/m5agent/m5stack-esp-emulator/blob/8598b1f603ae6638a3f6d27824431781429b9e49/tests/firmware/esp32_efuse_identity/evidence-2026-11-13-core2.json)：Core2 guest 身份读回。

## 边界与回滚

仅授予摘要列出的设备、固件、运行时和路径。browser-WASM 公网数据面、物理 RF、
功耗、电气、声学、安全保证、其它固件及长期稳定性未验证。本轮没有 Burner 提交。
发布后八次配对、一轮本地编程和清理均在独立 follow-up 通过；该记录还保留首次
观察脚本失败。本轮旧入口对照、三次未补齐镜像失败和两次源码检查失败保持原样。

修复不覆写用户原版 BIN；撤回 cloud 入口和后端支持可恢复此前行为，但同时会
恢复原启动缺口。回滚须维持现有本地编程、上传固件和历史记录，不清理用户资产。
公开报告不记录常驻服务内部拓扑、端点、凭据或运维配置。

## 后续验收与 CI

[发布后复测](followups/2026-11-13-published-source-paths/report.md) 完成 main/review
两个脱敏角色上的八次原版配对、实际网页本地编程和停止/历史验收。其结果不回写
此前的 `validation-summary.json`。[固定源码 CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/43359400778)
的 platform-contracts 与 network-namespace-policy 两项作业均通过；push workflow
中的 PR-only scope step 为 skipped，本地固定 base/head 的范围检查独立通过。
