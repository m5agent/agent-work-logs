# Issue #234 固件容量准入复验

## 原因与改动

同一份问题原版 BIN 长 2,041,968 字节。其启动头声明 16,777,216 字节，分区结束地址为 16,777,216 字节，目标 Cardputer ADV 提供的 Flash 容量为 8,388,608 字节。Device Service 1.99.1 报 `firmware_flash_contract_mismatch`，发送镜像的文件长度无法代替所需 Flash 布局。

候选 Reviewer `69386c6a162a1c786d6745c46eaa330c14558d3c` 保留 Device Service 提供的结构化拒绝原因，在 HTTP 审核详情及对应静态证据中写入 `static_effective.admission`。结构包含失败阶段、原因、板型、固件摘要和四项数值。整体状态仍为 `failed / E_STATIC`，人工详情继续显示「Flash 容量」。候选 OpenAPI 契约版本为 0.29.0。系统 Python 3.9.6 下 301 项测试通过。

## 执行

1. 使用 Device Service 1.99.1 `c9ec0f274579b78d87a4a301147f351e8b7a48fa` 的冻结源码和同一原生 QEMU，分别启动隔离的 Reviewer 基线与候选。
2. 上传同一原版 BIN，向 `/api/v1/firmware` 与 `/api/v1/firmware/import` 提交同一板型。两种入口均返回 HTTP 409。确认审核前没有虚拟来宾、固件注册或租约。
3. 通过标准保存快照重试路径观察 terminal 审核状态，并读回静态证据。基线 `37d7675dced42b2b932c51d1ca21bbb8ccfdf7e1` 保留文字归因。候选保留同样的分类和四项整数。两种运行中的审核固件均与原上传字节一致，问题固件未进入虚拟写入。
4. 将官方 Cardputer ADV UIFlow2 原版交给同一 Device Service，取得 8,388,608 字节规范化 Flash，并创建不带虚拟网卡的标准 QEMU 会话。通过原生进程身份、串口与 240×135 非黑帧验证启动。回读同会话证据 ZIP，独立校验 CRC、成员大小和摘要。停机后检查进程退出、可写 Flash 释放和租约归零。

## 边界

此记录覆盖虚拟容量准入、保存快照审核归因和官方 8 MiB 对照的原生启动。首批测试夹具异常的回执保留作执行记录，最终证据来自精确版本的完整重跑。候选生产切换、真机烧录、实物 16 MiB 板型、联网和配对均为 `NOT RUN`。未提交 Burner。
