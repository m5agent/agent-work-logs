# Issue #234 常驻审核服务交付

## 常驻变更与回读

先用 macOS 系统 Python 3.9.6 启动隔离 Reviewer，核对 0.29.0、原有 macOS 后端和零活动，再执行带空闲检查和有界备份的切换。常驻 Reviewer 源码从 `37d7675dced42b2b932c51d1ca21bbb8ccfdf7e1` 更新到 `69386c6a162a1c786d6745c46eaa330c14558d3c`。安装的运行代码只更新 `app.py`，切换成功，无需回退。

独立回读核对实际 Reviewer HTTP 200 就绪、0.29.0 和 macOS 后端。切换前后的 130 条任务、批次和事件表、API 统计及抽样证据 ZIP 保持一致。工作台和审核设备 Device Service 继续运行 `c9ec0f274579b78d87a4a301147f351e8b7a48fa`。两套角色均以 HTTP 200 提供完整 OpenAPI 1.99.1，逐字节匹配已发布契约。Reviewer 的 OpenAPI 摘要来自仓库。常驻 Reviewer 回读的是版本与就绪状态。

## 保留旧库存时的验证

将早前由原版问题 BIN 产生的规范化 Flash 和历史库存记录按原字节复制到独立状态。使用普通会话创建请求引用已存在的固件条目。当前 Device Service 在申请来宾前返回 HTTP 409，代码为 `firmware_flash_contract_mismatch`。目标为 8,388,608 字节，镜像要求、启动头声明及分区结束地址均为 16,777,216 字节。调用后对照两份库存文件，内容未变，没有会话，租约为零，独立服务进程正常退出。

[先前候选复验](../../README.md)以同一原版 BIN 验证保存快照审核的结构化回执，并用官方 8 MiB UIFlow2 对照验证原生来宾启动和出帧。本次常驻回读覆盖服务状态和历史保留。生产固件会话、实体硬件与 Linux 路由未执行。Issue #234 的状态回读为 `CLOSED / COMPLETED`，没有新增回复。Burner 未提交。
