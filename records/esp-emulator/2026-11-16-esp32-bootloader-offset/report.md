# #228 引导偏移诊断

原版 `V1.4r` 镜像 1,676,320 字节，`0x1000` 的原始字节为 `40 20 20 04`。旧版在 `0x0` 识别出结构有效的 bootloader，并在缺少芯片地址检查时把该布局判为有效。独立服务接受合并和包导入，返回 HTTP 201。62.41 秒后，归档串口有 19 次 `invalid header: 0x04202040`，最终 135×240 PNG 为 174 字节且零非黑像素，SHA 与 issue 一致。观测器的 display 方向截图请求没有通过，黑帧结论来自独立解码的证据 ZIP。ESP32 ROM 的启动要求可见 [ESP-IDF ESP32 bootloader](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/bootloader.html)。

新分析优先检查芯片的 ROM 偏移，保留错放但结构有效的镜像信息用于诊断。同一 BIN 的普通合并返回 422，包导入返回含偏移诊断的 400。先前已保存的镜像重分析返回 `valid=false`，直接申请会话也返回 422。审核调用端把结构化 422 转为 `E_STATIC`，描述两个偏移。实际运行保存快照和原 BIN 的审核 worker 后，服务仍有 0 会话，提交选项为 false。

官方 UIFlow2 2.5.4 正对照分析通过，bootloader 位于 `0x1000`。第一次正对照已取得 Cloud 画面，不过串口标记使用了库名，且显示方向接口未接受请求。复验采用应用实际输出的 `Startup with network type: WIFI`，采集 panel 原生帧，并在 60.411 秒观察中获得 32,301 个非黑像素的 Cloud 画面。截图与 ZIP 哈希见结构化摘要。该对照只证明启动和页面，不覆盖配对或联网。

前后两次使用同一 Xtensa runtime 与 ROM。原始镜像没有平移或改写。停止前导出各自 ZIP，停止后保留历史状态。恢复变更可分别反向还原两个源码提交。未运行真机及 hosted/WASM 测试。

## 回归和归档

首次平台套件执行 2,237 项，其中 1 项失败、8 项跳过。失败来自 API sweep inventory 中的旧合同 SHA-256，提交 `3640cc17db5ec52fc407a38ca3f8baa1a3080bd0` 更新绑定。修订后同一套件 2,229 项通过、8 项跳过，耗时 198.616 秒。审核端在 `2846fe9b4ee73d4b4dbb9afaf31f439d0b6c34f2` 的独立套件 87 项全部通过。[平台测试摘要](evidence/platform-regression-summary.json)

三次运行的证据 ZIP SHA-256 与运行收据一致。独立逐文件校验清单、确认串口匹配次数，并对 ZIP 中的 PNG 重算 SHA-256。原始日志、归档包与固件镜像仅保存于私有证据，公开记录保留摘要和数据指纹。[归档完整性摘要](evidence/archive-integrity-summary.json)
