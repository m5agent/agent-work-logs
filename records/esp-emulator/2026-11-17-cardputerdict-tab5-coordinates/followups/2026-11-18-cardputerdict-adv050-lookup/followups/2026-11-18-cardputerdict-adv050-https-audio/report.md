# 原版 ADV 的联网、缓存和数字音频

同一原版用 Flash 擦除填充至声明大小，原版字节保留。原生 Linux arm64 Device Service 通过受控 DNS 和仅限授权目标的策略运行。保留常规 SNTP 和 HTTPS 端口，网络 namespace 默认拒绝其他目标。确切服务、QEMU、ROM、原 BIN、填充后 Flash 和 SD 种子身份见[回执](evidence/adv050-https-audio-summary.json)。[固定 Device Service 源码](https://github.com/m5agent/m5stack-esp-emulator/tree/13df3b8a7ab197df14f57d2ca8bc58919a7eb666)

等待原版词典页面就绪，以实际键盘输入进入 Wi-Fi 页面并确认保存画面。匹配原版 hello 释义，再以 Fn+P 触发发音。共 18 个设备动作被接收，词典就绪、Wi-Fi 页面、设置已保存、词义和发声提示分别绑定截图身份。PCAP 见一轮 DHCP DORA、两次解析成功、一对 SNTP 交换和双向 TLS 负载。Guest 在存储中生成 10,605 字节 MP3；默认 I²S 采样的同会话 live PCM 为 60,928 字节，峰值 7,051，RMS 2,258.77。分别保留停止前 ZIP 和停机后 PCM 的采样范围及哈希。

首次在词典尚未就绪时提交 Fn+W，后续仅看到离线提示。第二次把窄字体的 W 识别成 U，测试编排器超时。第三次以实际词典画面限定输入窗口后完成一轮。停止前 ZIP 验证 CRC，15 项证据成员核对，原始 pcap 与停止后的 API 导出一致。guest 停止、工作 Flash 释放、租约归零，清除了本次 namespace 与临时 NAT，自建服务及容器退出。

## 复现

1. 从已发布的 0.5.0 获取与回执同哈希的 ADV 原版 BIN 和同 SHA 的 SD 种子，在指定原生 Device Service 建立独占会话。观察原版词典界面出现后执行 Fn+W，完成隔离 Wi-Fi 夹具输入和保存。
2. 仅按授权配置固定 DNS、校时与发音的真实服务目的地。在会话中输入 hello，等待原版词义，再按 Fn+P，对照画面、封存链路、缓存文件和默认音频导出。
3. 核验 ZIP、PCM 采样窗口及终态，再停止并确认资源释放。报告只发布计数和哈希，地址、凭据、原始包和音频均留在受控目录。

本轮范围为一次直接 Device Service 的应用功能通过。Reviewer ADV 类型入口、设备注册或云端配对、实体声音及射频、浏览器和额外重复次数均为 NOT RUN。无需回滚产品源码。
