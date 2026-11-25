# 正式文档页的跨域 WASM iframe

在桌面 Chrome 158 打开 [CoreS3 产品文档](https://docs.m5stack.com/en/core/CoreS3)，在开发者工具 Console 执行下面的代码，把真实 [模拟器页面](https://m5agent.github.io/m5stack-esp-emulator/) 嵌入当前文档页。此操作只改动当前页面 DOM。

```js
const simulator = document.createElement('iframe');
simulator.src = 'https://m5agent.github.io/m5stack-esp-emulator/';
simulator.allow = 'cross-origin-isolated';
simulator.style.cssText = 'width:100%;height:800px;border:1px solid gray';
document.body.prepend(simulator);
```

等子页 Service Worker 接管并完成重载。在 Console 分别选择顶层文档与子框架上下文，执行 `[isSecureContext, crossOriginIsolated, typeof SharedArrayBuffer]`。两边均报告 `true, false, "undefined"`。文档 HTTP 200 响应未发送 COOP/COEP。子页选择浏览器工作台后，运行选择为 `model`，启动按钮禁用，Network 没有 Xtensa WASM 请求。这个阻塞发生在固件载入前。同一文档页面上的设备配置会共用这个启动前置条件。

两个独立控制组在相同工作台导出的顶层页面运行仓库的 `platform/tests/test_public_uiflow_guest.mjs`。参与执行的 Xtensa WASM SHA256 为 `96c7f8baf1d5f2fd760c560a0827ef7305ad06a1cefb28c905d05d796dc540d8`。每组都对应用就绪串口标志、同 VM Python 执行、屏幕像素、停止和所有 Worker 退出做了检查。单次冷启动从点击到解释器就绪分别为 CoreS3 11.16 秒和 Cardputer-Adv 5.74 秒。计时属于本地顶层编辑器控制组。

集成验收应在可配置响应头的预览路线打开文档，检查顶层隔离策略和子框架权限，让两个目标机型的来宾真实启动并验证输入、串口、应用画面和停止后资源回收。集成还需要检查该页面依赖的跨源脚本、字体、图片和其他可嵌内容。

[脱敏摘要](evidence/embed-and-editor-summary.json) 保留公开页面、版本、结果、哈希和回收计数。会话标识已哈希化，略去运行环境地址、Worker 标识、原始串口及像素数组。
