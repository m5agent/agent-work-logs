# NC1020 原版在 Device Service 1.99.0 上的配对回放

## 目标和执行条件

以相同的 Cardputer K132 原版 NC1020 1.1 工厂应用及已导入 ROM/NOR 的 Flash，在两个独立工作器验证真实 G0 存档、停机后 FAT 读回、整卡导出和冷启动恢复。同时检查存档成功是否伴随可用的完整应用画面。原版工厂应用区与已导入 Flash 的工厂应用区逐字节相同。原版、导入 Flash、FAT32 种子、QEMU、SoC ROM 和在线 OpenAPI 的完整身份见 [证据摘要](evidence/nc1020-199-cold-restore.summary.json)。

执行使用两个新的隔离 Device Service 1.99.0 工作器、Python 3.13.15 和 Pillow 11.3.0。Cardputer 为原生 QEMU `qemu` 运行时，普通时序、无指令追踪，透过启动参数 `-nic none` 保持离线。由系统进程接口核验运行中的 QEMU 可执行文件。每个会话从同一份 Flash 快照创建。运行时没有源代码或固件改动。

## 复现步骤

1. 启动独立服务，调用 `GET /api/v1/health` 与 `GET /api/v1/openapi.yaml`。使用二进制 `POST /api/v1/artifacts` 上传固定 Flash 和历史 FAT32 镜像。调用 `POST /api/v1/firmware/import`，设备为 `cardputer`，Flash 的 `artifact_id` 为其内容 SHA-256。
2. 以 `POST /api/v1/sessions` 新建会话，运行时为 QEMU、租期 180 秒，将卡的 SHA-256 传入 `storage.sd_image_artifact_id`。轮询 `GET /api/v1/sessions/{id}/serial` 直到出现 ROM/NOR 就绪、`LoadNC2k() returned`、`state restored: /sd/nc1020.state` 和应用心跳。
3. 在初次采样及其后约 2、8 秒调用 `GET /api/v1/sessions/{id}/frame.png?max_age_ms=0`。按发布者的 160×80 逻辑 LCD 图案映射到 240×135 帧，以每个逻辑像素类别的主色命中率判定，完整图案须两种颜色不同且较低的类别命中率达到 0.99。读取 `GET /api/v1/sessions/{id}/storage/sd/read-stats`，将计数绑定到实际会话、固件、运行时和源介质。
4. 对 A 先读取 `GET /api/v1/sessions/{id}/storage/sd/write-stamp`，再通过 `POST /api/v1/sessions/{id}/input` 发送下方 G0 动作。读取动作后串口和相同介质的写入戳，再取帧、计数、Flash 与 ZIP。

   ```json
   {"kind":"button","control":"boot","action":"hold","seconds":0.85,"settle_seconds":0.3}
   ```

5. 从 `GET /api/v1/sessions/{id}/evidence?include=manifest,serial,frames,logs,storage` 取会话 ZIP 后调用 `DELETE /api/v1/sessions/{id}?purge=0&retain_flash=0`。核对工作器归零、进程退出和历史可访问。用 `GET /api/v1/sessions/{id}/storage/sd` 读取停机后的 FAT 清单，再用 `POST /api/v1/sessions/{id}/storage/sd/export` 导出整卡。启动新工作器 B，重复步骤 1–3 和只读取证，使用 A 导出卡与相同的导入 Flash。这一轮无 G0 输入。

[固定版本 API](https://github.com/m5agent/m5stack-esp-emulator/blob/597e03214dc5f442787cec52f1720567e4ed2a00/docs/device-service-api.md) · [原版测试路径](https://github.com/m5agent/m5stack-esp-emulator/tree/597e03214dc5f442787cec52f1720567e4ed2a00/tests/firmware/cardputer_k132_stock)

## 观察结果

| 观察 | A，恢复旧卡后写入 | B，导出卡冷启动 |
| --- | --- | --- |
| 恢复串口与初次 SD 单块完整读取 | `state restored: /sd/nc1020.state`，407 | 同一恢复标记，410 |
| G0 和写入 | `G0 pressed`、`state save /sd/nc1020.state: ok`，同一介质的写入戳前进 | 无输入 |
| 停机文件（字节） | 99,384 | 99,384 |
| 停机文件 SHA-256 | `fce26ec044ba72ea8ccfe83ad9abd63977bac29cb6cac44bfe56830dd20bdbd8` | 完全一致 |
| 帧结果 | 21623/32400 非黑像素，最佳命中率 86.4021%，三张定时样本与一次动作后样本相同 | 13565/32400 非黑像素，最佳命中率 54.2036%，三张定时样本相同 |
| 应用心跳 | 87，循环计数增加，绘制增量合计 0 | 86，循环计数增加，绘制增量合计 0 |

B 的初始 SD 字节与 A 停机导出逐字节一致。B 停机后整卡有两个扇区共三个字节发生变化，存档文件哈希保持一致。两轮的工厂应用、ROM 和 NOR 分区在运行前后均逐字节一致。两份 ZIP 的 CRC、清单、串口长度与哈希、Flash 和源卡 SHA-256 已复核。证据为脱敏摘要，省略本地路径、会话标识和原始数据，仅保留内容哈希、计数、协议结果以及帧与串口特征。

## 归因和边界

1. 范围内的存档链路通过。画面停刷与两次成功恢复并存，B 回读的状态文件与 A 写入的文件一致，两个会话的残留帧哈希与画幅不同。
2. 1.87 的历史原版双核追踪曾观测到一次 SPI 总线锁交接漏唤醒。另一次停刷未确认同样的时序。本次正常时序复测仍出现不完整画面，指令级锁归因未执行。 [此前原版追踪](../2026-11-18-nc1020-dual-core-cas/report.md)
3. 原版和 Flash/SD 源种子保持不变。实验结束已停止两个会话和工作器。实体设备、浏览器 WASM、云审查和修订后的发布镜像属于本次未执行项。
