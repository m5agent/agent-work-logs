# Flash 容量复验报告

原记录中的 BIN 文件只有 2,041,968 字节。镜像头声明 16 MiB，分区末尾同样为 16 MiB。历史服务将这份镜像写入 8 MiB 的虚拟 Flash 后才出现 probe 失败。Device Service 的[容量检查改动](https://github.com/m5agent/m5stack-esp-emulator/commit/6c28cbb59641d02b0dcdc892488e6868bc4b0ea9)在镜像合成或导入时检查声明容量和分区末尾。本轮复验范围是当前主线和常规审核路径，代码改动不适用。

## 执行

1. 在隔离状态目录启动固定源码版本的 Device Service，使用冻结的原生 Xtensa QEMU，启动 Cardputer ADV 档案时关闭网卡。使用保留的发布者原始 BIN 并验证大小及 SHA-256。
2. 经 `POST /api/v1/artifacts` 上传原件，从常规 `POST /api/v1/firmware` 合成和 `POST /api/v1/firmware/import` 两路均复现拒绝。检查错误中的模型容量、镜像头声明值和分区末尾，检查无新会话和租约。
3. 使用同一原版 SHA 在隔离 Reviewer 对保存快照调用 `POST /api/reviews/{job_id}/retry`，请求含 `sourceMode=saved_snapshot`、`useAgentReview=false` 和 `submit=false`。入口返回 202，任务收口为 `failed / E_STATIC`。静态结果给出 `Flash 容量`，没有进入虚拟 Flash 检查，前后无来宾会话。
4. 用基线中冻结的同设备官方 8 MiB UIFlow2 BIN 做正对照。正常合成并在 `POST /api/v1/sessions` 启动实际 QEMU，核对所用可执行文件、规范化 Flash、串口及 `GET /api/v1/sessions/{id}/frame.png`。该帧为 240×135，超过 1,000 个非黑像素，串口无原容量不匹配的 probe 信息。
5. 停机前获取会话 ZIP，核对 CRC、原始固件来源和全部成员的清单哈希。归档帧为同会话稍后的一张快照，独立解码得到 240×135 和 32,400 非黑像素。串口与直接采样逐字节一致。停止后确认来宾进程退出、可写 Flash 和租约释放。

## 对照与限制

先前两轮均稳定获得两条 Device Service 容量拒绝。A1 漏挂冻结的 `esp-emu` 能力配置，未形成完整 Reviewer 对照。A2 的私有离线包装器校验了错误的 QEMU machine 名称，Reviewer 已终止于预期 `E_STATIC`，正对照为配置失败。A3 修正两项试验设置，完整链路通过。三轮原始摘要的完整 SHA-256 和字节数见[证据摘要](evidence/replay.summary.json)。

该结果覆盖 16 MiB 镜像在 8 MiB 档案上的服务准入和匹配固件的虚拟启动。真机烧录、其他 Flash 配置、按键、云端配对和联网仍未执行。测试使用新建的隔离服务及状态目录，结束后关闭测试进程并保留只读取证。无生产部署或回滚，无 Burner 提交。
