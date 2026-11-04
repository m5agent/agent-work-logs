# M5Stack 模拟器介绍视频制作与验证报告

## 背景

用户要求直接交付一支符合 M5Stack 视觉习惯、具有科技感的中文介绍视频，并授权自主决定其它细节。成片规格为 74 秒、1080p、30 fps。内容包含产品外观、真实虚拟设备演示及开发验证工作流。

本任务没有待定位的软件故障。关键判断是将介绍性的产品图片、工作流示意与真正运行的客体画面分开标明，避免把视觉模型或营销图形当作固件验证证据。

## 结论与改动范围

CoreS3 原生 QEMU 路径的演示部署、连续画面、触摸输入、串口反馈、状态变化和停止清理为 `PASS`，分类为 **virtual-device validation**。成片全流解码、浏览器播放与关键帧跳转、画面/字幕检查均通过；整体为限定任务范围内 `PASS`，未执行项保持独立。

没有修改模拟器源码、上游固件或用户服务配置。新增的是介绍片素材、单独的 UIFlow2 演示程序和本记录。产品参考图用于外形展示；图形化流程用于解释操作；演示屏幕来自实际 guest framebuffer。画面上的 `DEMO SIGNAL` 为合成波形，不是传感器测量。

## 精确执行身份

| 对象 | 身份 |
| --- | --- |
| 源码 commit | `b41eba70eb61f7ddc5c41e0b981341064f9d1d1f` |
| CoreS3 基础固件 SHA256 | `1324f12d3ddd5392f47a9eff537f9ce0b01a8e6e36d829b6bd22cdf82d2c1264` |
| 合成后固件 SHA256 | `0ede40601c1e37b7ba32c87a3ca55e4da7a448f6cf52957f005763bc7c7c78e8` |
| QEMU SHA256 | `6d9af027e2f744208fc2503128f1772f436d7ca7358f9e53be597bc76800f39d` |
| 实际演示源码 SHA256 | `f4dfef69d5272a8bbebce849acbfdbbd459c4a73fb38742d3a962e452435e776` |
| 数据面 | `m5cores3` / native QEMU / Device Service `/api/v1` / `uiflow-live` |
| 屏幕 | `320×240`，guest rotation `1` |

程序于 `2026-11-04T08:36:03.677810+00:00` 提交。运行时未显式设置 icount 或替代加速器；其它参数见[运行摘要](evidence/runtime-summary.json)。服务源码关键文件哈希与当前工作树、上述 commit 均一致；运行时可执行文件、固件会话、合成元数据、138 张帧的时间清单及 ZIP 哈希均已独立复核。

原始 Python 文件哈希与服务的程序包哈希使用不同格式：后者对 `main.py` 到源码的 canonical JSON 映射取 SHA256。两者已经通过[完整性摘要](evidence/archive-integrity-summary.json)核对，不能把两种格式混为同一个哈希。

## 执行与复现

使用上述固定源码版本，按该版本的 [Device Service API](https://github.com/m5agent/m5stack-esp-emulator/blob/b41eba70eb61f7ddc5c41e0b981341064f9d1d1f/docs/device-service-api.md) 准备独立服务与匹配资产。精确复现需要相同的固件与运行时哈希；这些二进制未在本公开记录重新分发。

1. 创建 `device_id=cores3`、`runtime=qemu`、`program_mode=uiflow-live` 的专用会话，使用上述已接纳的 UIFlow2 合成固件。
2. 通过该会话的程序接口，将 [demo.py](code/demo.py) 作为 `main.py` 提交到同一客体的 UART REPL。等待 `M5_VIDEO_READY 320 240`。
3. 读取同会话 `frame.png`；实际采样请求使用 `max_age_ms=125`，连续采集约 24 秒。采样数量或更新数不表示完整应用 FPS。
4. 采样开始约 `10.1514 s` 后请求同会话输入：

```json
{"kind":"longpress","x":160,"y":214,"hold_seconds":1.0,"settle_seconds":0.2}
```

5. 确认串口 `M5_VIDEO_TOUCH 160 214 MODE 1`，屏幕的 `READY` 切换为 `TOUCH ACTIVE`，蓝色图形变为绿色。
6. 在停止前请求同会话 evidence ZIP；停止时保留历史、释放可变 Flash；确认 QEMU 进程被回收，随后停止自建服务。

两张公开 PNG 分别来自捕获 `9.9989 s` 与 `11.5563 s`，保留原始字节和像素。输入调用包含约 1.2 秒 hold/settle；该过程不是触摸延迟基准。运行摘要保留第一次方向识别调整与超出 API 超时上限的请求拒绝，不将它们擦除或改写为从未失败。

## 独立后续执行：网页工作台本地上传

第二次执行由当前 `platform/web/index.html` 工作台选择本地完整镜像上传，并通过原生 Device Service 运行 CoreS3。它属于 **browser UI → native Device Service → QEMU**，不是浏览器内 WASM 客体。

两次固件必须分别绑定：

| 执行 | 固件 SHA256 | 程序进入方式 |
| --- | --- | --- |
| 连续帧 / UART live | `0ede40601c1e37b7ba32c87a3ca55e4da7a448f6cf52957f005763bc7c7c78e8` | 同 guest UART REPL 部署 |
| 当前网页工作台 | `a31ba1df11e7e2e0309fd71a8e58765ea26449c32b80f02f366a5d952fecf9ea` | 完整 16 MiB 合成 Flash 本地上传，`main.py` 已写入文件系统 |

两者都使用本文所列 `b41eba70…` 源码与 `6d9af027…` QEMU，以及同一 `f4dfef69…` 演示源码。第二次固件本体、会话与合成 manifest 的哈希已交叉核对；不把首次会话的 marker 或帧移作第二次会话证据。

原始工作台 PNG 为 `1920×1200`、190,313 字节，SHA256 为 `06333790a618f9b6dbb47d48b78aa62e5a655eeee02f5613317aac5bd6e432c4`。其与成片素材文件字节相同；未替换 framebuffer、未添加虚构控制台输出。影片 35–46 秒使用该截图的中心列裁切。公开记录只归档截图身份，不包含整张截图。

截图显示“固件运行中”“实际会话屏幕已更新”及实际 3D CoreS3 guest 画面。之后输入 `longpress (160,214)`、hold `1 s`，原始 guest 前后帧分别显示蓝色 `READY` 与绿色 `TOUCH ACTIVE`。ZIP 在停止前获取，SHA256 为 `1699e615fc1e24df65ad0113c0b3ad867cd71aa61f8b9cc23c5eb1659a715e43`。本组创建的两个会话均停止且 runtime reaped，专用服务也已停止。

保留首次网页自动化等待应用 UART marker 超时：该固件控制台只有启动串口，客体实际仍在运行，之后单独停止。最终 readiness 由实际 guest framebuffer 建立。启动输出含一次 I2C 初始化提示，本记录没有授予“串口完全无错误”。网页目录计数只表示目录模型，不代表完整支持。详情见[工作台摘要](evidence/workbench-summary.json)与[独立完整性复核](evidence/workbench-integrity-summary.json)。

## 素材来源与呈现边界

M5Stack 横向标志来自 [官方品牌规范](https://m5stack.com/brand-guidelines) 提供的 Brand Kit，使用其原始白色及蓝黑版本，保持比例和颜色。产品图来自模拟器仓库已存在的 `platform/web/assets/reference-cutout/`，仅用于外形展示。实录段落需标注 `virtual-device validation` / 原生虚拟设备；产品矩阵及工作流图形需标明展示或示意。

成片标明 `M5AGENT PROJECT SHOWCASE`，不表示 M5Stack 官方发布。中文神经旁白配原创合成电子乐，按实际语音窗口压低音乐。字幕嵌入画面。最终媒体身份与自动播放、响度和视觉 QA 见 [media-summary.json](evidence/media-summary.json)。未将自动响度检查称为人工全片听审。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | NOT RUN | 使用既有固定哈希资产；未新建固件或运行时 |
| transport | PASS | 同 guest UART REPL 提交确认及两个串口 marker |
| device_response | PASS | 实际 longpress 进入虚拟触摸控制器，guest 检测 MODE 1 |
| data_behavior | PASS | 连续帧和输入后状态变化，138 帧 / 137 不同 SHA256 |
| visual_or_physical | PASS（virtual only） | 原始 framebuffer 显示蓝色 READY 到绿色 TOUCH ACTIVE |
| web native workbench | PASS | 独立上传镜像、真实工作台 guest 画面、触摸后状态变化、两会话及服务清理 |
| browser-WASM | NOT RUN | 两次运行都使用 native Device Service；网页界面不等于 WASM 客体 |
| hardware validation | NOT RUN | 未使用物理设备，未测物理属性 |
| delivery / media QA | PASS | 74.000s / 1920×1080 / 30fps / 2220帧；H.264与AAC；全流解码、Chromium播放/9次seek、关键帧视觉检查及最终AAC响度 |

## 脱敏、风险与回滚

公开摘要未包含服务端点、认证数据、本机路径、session 或 process 标识。原始完整响应、证据 ZIP、固件、运行时二进制、完整帧序列和成片不提交到本记录；仅保留哈希、限定结论和两张无敏感信息的原始画面。完整性摘要说明了公开材料与本地原始材料的对应关系。

本次仅新增可删除的媒体及记录文件，没有不可逆设备写入，也没有更改项目实现或他人服务。上述两份镜像以外的固件、设备、网络、外设或 browser-WASM 能力不继承这些演示的 PASS。本记录通过仓库 `scripts/publish.sh` 发布到两个归档远端，视频本体本地交付。

## 成片验收与精确身份

文件 `M5Stack-Emulator-Intro-1080p.mp4`，`9225412` bytes，SHA256 `504eec4151b63cff0ded05b1312127ea98573546d05784471616516ccc5b7e5c`。H.264/yuv420p，AAC 48 kHz 双声道，两条媒体流均为 74.000 秒。封装包含八个章节，最终编码后的响度为 −16.23 LUFS、真峰值 −1.37 dBTP。

FFmpeg 完整解码没有错误。Chromium 实际播放推进约 0.61 秒，随后在 3、11、21、28、30、40、51、61、70 秒完成 seek 与解码截图。检查全部八段构图及字幕，没有发现文本重叠；28/30 秒保留真实输入前后蓝绿变化。首次 QA 像素断言误采固定装饰条，第二次误采深色背景，产生两个测试探针 FAIL；改为真实 guest 状态区域后 PASS，视频文件本身未改变。

35–46 秒使用第二次主工作台截图的中心列裁切并轻微缩放，未替换其中 framebuffer。工作台截图与前段连续帧分别绑定自己的固件 SHA；不将两份素材拼接为一个会话。
