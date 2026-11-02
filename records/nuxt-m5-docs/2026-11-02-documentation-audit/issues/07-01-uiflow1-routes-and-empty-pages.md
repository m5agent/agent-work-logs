# 修复 UIFlow1 的 24 处错链入口和英日 LoRa Bus 空白正文

> 发布边界：本记录按用户针对本次文档工单明确批准的 REVIEW 例外发布。hardware validation 与 virtual-device validation 均为 NOT RUN。公开页面链接可能更新，源文件位置以所列提交、路径和行号为准。

审查基线：`nuxt-m5-docs@47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac`，观察日期：2026-11-02。此问题涉及站内导航和内容交付，不涉及设备功能结论。

## 用户可见问题

UIFlow1 目录中有 6 个教程条目的文件名被写成产品页命名，三语言累计 18 处。GoPlus2 产品页另有 3 处相同错链；PaHub 教程标题另有 3 处包含双斜杠的错链。总计 **24 个错误入口，对应 21 个不同错误 URL**。线上请求错误 URL 均返回 HTTP 404；本文表中列出的正确目标均返回 HTTP 200。

英、日 LoRa Bus 目录项可以进入页面，但 Markdown 正文为 0 字节。仅检查 HTTP 200 会漏掉该问题。

## 完整 HTTP 复核表

观察时间：2026-11-02 16:28（Asia/Shanghai）。域名统一为 `https://docs.m5stack.com`，下表 URL 为该域名下的绝对路径。状态为跟随正常 HTTP 重定向后的最终结果。源文件链接固定到上述审查提交；线上结果是观察时刻快照，并不保证线上部署提交与本地基线相同。

| 错误入口位置 | 当前链接 | 当前HTTP | 修复目标 | 目标HTTP |
| --- | --- | ---: | --- | ---: |
| [zh_CN目录：Unit Joystick2](https://docs.m5stack.com/platform/uiflow_directory_cn.json) | `/zh_CN/uiflow/blockly/unit/Unit_Joystick2` | 404 | `/zh_CN/uiflow/blockly/unit/joystick2` | 200 |
| [zh_CN目录：Unit Joystick](https://docs.m5stack.com/platform/uiflow_directory_cn.json) | `/zh_CN/uiflow/blockly/unit/Unit_Joystick` | 404 | `/zh_CN/uiflow/blockly/unit/joystick` | 200 |
| [zh_CN目录：Unit Makey](https://docs.m5stack.com/platform/uiflow_directory_cn.json) | `/zh_CN/uiflow/blockly/unit/16-Key_Capacitive_Touch` | 404 | `/zh_CN/uiflow/blockly/unit/makey` | 200 |
| [zh_CN目录：Unit Trace](https://docs.m5stack.com/platform/uiflow_directory_cn.json) | `/zh_CN/uiflow/blockly/unit/Unit_Trace` | 404 | `/zh_CN/uiflow/blockly/unit/trace` | 200 |
| [zh_CN目录：Module13.2 GoPlus](https://docs.m5stack.com/platform/uiflow_directory_cn.json) | `/zh_CN/uiflow/blockly/module/Module_GoPlus` | 404 | `/zh_CN/uiflow/blockly/module/goplus` | 200 |
| [zh_CN目录：Module13.2 GoPlus2](https://docs.m5stack.com/platform/uiflow_directory_cn.json) | `/zh_CN/uiflow/blockly/module/Module_GoPlus2` | 404 | `/zh_CN/uiflow/blockly/module/goplus2` | 200 |
| [en目录：Unit Joystick2](https://docs.m5stack.com/platform/uiflow_directory_en.json) | `/en/uiflow/blockly/unit/Unit_Joystick2` | 404 | `/en/uiflow/blockly/unit/joystick2` | 200 |
| [en目录：Unit Joystick](https://docs.m5stack.com/platform/uiflow_directory_en.json) | `/en/uiflow/blockly/unit/Unit_Joystick` | 404 | `/en/uiflow/blockly/unit/joystick` | 200 |
| [en目录：Unit Makey](https://docs.m5stack.com/platform/uiflow_directory_en.json) | `/en/uiflow/blockly/unit/16-Key_Capacitive_Touch` | 404 | `/en/uiflow/blockly/unit/makey` | 200 |
| [en目录：Unit Trace](https://docs.m5stack.com/platform/uiflow_directory_en.json) | `/en/uiflow/blockly/unit/Unit_Trace` | 404 | `/en/uiflow/blockly/unit/trace` | 200 |
| [en目录：Module13.2 GoPlus](https://docs.m5stack.com/platform/uiflow_directory_en.json) | `/en/uiflow/blockly/module/Module_GoPlus` | 404 | `/en/uiflow/blockly/module/goplus` | 200 |
| [en目录：Module13.2 GoPlus2](https://docs.m5stack.com/platform/uiflow_directory_en.json) | `/en/uiflow/blockly/module/Module_GoPlus2` | 404 | `/en/uiflow/blockly/module/goplus2` | 200 |
| [ja目录：Unit Joystick2](https://docs.m5stack.com/platform/uiflow_directory_ja.json) | `/ja/uiflow/blockly/unit/Unit_Joystick2` | 404 | `/ja/uiflow/blockly/unit/joystick2` | 200 |
| [ja目录：Unit Joystick](https://docs.m5stack.com/platform/uiflow_directory_ja.json) | `/ja/uiflow/blockly/unit/Unit_Joystick` | 404 | `/ja/uiflow/blockly/unit/joystick` | 200 |
| [ja目录：Unit Makey](https://docs.m5stack.com/platform/uiflow_directory_ja.json) | `/ja/uiflow/blockly/unit/16-Key_Capacitive_Touch` | 404 | `/ja/uiflow/blockly/unit/makey` | 200 |
| [ja目录：Unit Trace](https://docs.m5stack.com/platform/uiflow_directory_ja.json) | `/ja/uiflow/blockly/unit/Unit_Trace` | 404 | `/ja/uiflow/blockly/unit/trace` | 200 |
| [ja目录：Module13.2 GoPlus](https://docs.m5stack.com/platform/uiflow_directory_ja.json) | `/ja/uiflow/blockly/module/Module_GoPlus` | 404 | `/ja/uiflow/blockly/module/goplus` | 200 |
| [ja目录：Module13.2 GoPlus2](https://docs.m5stack.com/platform/uiflow_directory_ja.json) | `/ja/uiflow/blockly/module/Module_GoPlus2` | 404 | `/ja/uiflow/blockly/module/goplus2` | 200 |
| [zh_CN GoPlus2 产品页](https://docs.m5stack.com/zh_CN/module/Module13.2_GoPlus2) | `/zh_CN/uiflow/blockly/module/Module_GoPlus2` | 404 | `/zh_CN/uiflow/blockly/module/goplus2` | 200 |
| [en GoPlus2 产品页](https://docs.m5stack.com/en/module/Module13.2_GoPlus2) | `/en/uiflow/blockly/module/Module_GoPlus2` | 404 | `/en/uiflow/blockly/module/goplus2` | 200 |
| [ja GoPlus2 产品页](https://docs.m5stack.com/ja/module/Module13.2_GoPlus2) | `/ja/uiflow/blockly/module/Module_GoPlus2` | 404 | `/ja/uiflow/blockly/module/goplus2` | 200 |
| [zh_CN PaHub教程标题](https://docs.m5stack.com/zh_CN/uiflow/blockly/unit/pahub) | `/zh_CN//unit/pahub` | 404 | `/zh_CN/unit/Unit_PaHub` | 200 |
| [en PaHub教程标题](https://docs.m5stack.com/en/uiflow/blockly/unit/pahub) | `/en//unit/pahub` | 404 | `/en/unit/Unit_PaHub` | 200 |
| [ja PaHub教程标题](https://docs.m5stack.com/ja/uiflow/blockly/unit/pahub) | `/ja//unit/pahub` | 404 | `/ja/unit/Unit_PaHub` | 200 |

| LoRa Bus正文 | HTTP | 响应体字节数 | 本地基线正文 |
| --- | ---: | ---: | ---: |
| `/en/uiflow/blockly/advanced/lora_bus.md` | 200 | 0 | 0 |
| `/ja/uiflow/blockly/advanced/lora_bus.md` | 200 | 0 | 0 |
| `/zh_CN/uiflow/blockly/advanced/lora_bus.md` | 200 | 6288 | 6288 |

英、日目录入口分别位于 [static/platform/uiflow_directory_en.json:404](https://docs.m5stack.com/platform/uiflow_directory_en.json)、[static/platform/uiflow_directory_ja.json:404](https://docs.m5stack.com/platform/uiflow_directory_ja.json)。空白文件分别为 [static/en/uiflow/blockly/advanced/lora_bus.md](https://docs.m5stack.com/en/uiflow/blockly/advanced/lora_bus)、[static/ja/uiflow/blockly/advanced/lora_bus.md](https://docs.m5stack.com/ja/uiflow/blockly/advanced/lora_bus)。

## 源码依据

- components/DirectoryItem.vue:78（源码 `components/DirectoryItem.vue`，提交 `47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac`，L78） 将目录字符串直接拼为 `/{language}/{path}`。
- libs/markdown-loader.js:30（源码 `libs/markdown-loader.js`，提交 `47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac`，L30） 按请求路径读取同名 `.md`，不将 `Unit_Joystick2` 自动改为 `joystick2`。
- middleware/redirect.js:9（源码 `middleware/redirect.js`，提交 `47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac`，L9） 的现有规则未覆盖这些 UIFlow1 错误文件名或 PaHub 双斜杠地址。
- pages/document.vue:244（源码 `pages/document.vue`，提交 `47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac`，L244） 读取后直接渲染正文，当前没有空白正文的提示或回退路径。

因此，此处不是大小写兼容路由或产品 SKU 别名造成的扫描误报。

## 具体修复方案

1. 在三语言 `uiflow_directory_*.json` 将这 6 个教程路径改为表中的短文件名，保持实际 `.md` 路径不变。
2. 将三语言 GoPlus2 产品页的 UIFlow1 链接改为 `/{lang}/uiflow/blockly/module/goplus2`。
3. 将三语言 PaHub 教程标题链接改为 `/{lang}/unit/Unit_PaHub`。
4. 对已公开的旧错误 URL 增加精确兼容重定向，覆盖三语言；避免用过宽的全局替换影响产品页名称。
5. 补齐英日 LoRa Bus 正文并与中文 API/代码对齐。若暂不能翻译，显示明确的语言缺失提示并链接到可用中文资料，不继续发布无提示的空白页。
6. 在内容发布检查中校验已列目录目标存在且正文非空。动态页面（产品对比、SKU 跳转、协议等）须按真实路由规则处理，避免将它们当作缺少 `.md`。

## 可复现方式

在该基线 checkout 中读取表列源文件；对 URL 发起 GET，而不是仅检查本地文件名。例如：

```python
from urllib.request import urlopen
from urllib.error import HTTPError
for path in (
    '/zh_CN/uiflow/blockly/unit/Unit_Joystick2',
    '/zh_CN/uiflow/blockly/unit/joystick2',
    '/en/uiflow/blockly/advanced/lora_bus.md',
):
    try:
        with urlopen('https://docs.m5stack.com' + path, timeout=20) as response:
            print(path, response.status, len(response.read()), response.url)
    except HTTPError as exc:
        print(path, exc.code)
```

基线结果依次为 `404`、`200`、`200且0字节正文`。其余 URL 按表遍历即可。

## 验收清单

- [ ] 三语言 18 个目录入口、3 个 GoPlus2 产品页入口、3 个 PaHub 标题入口均指向存在且正文非空的正确资料。
- [ ] 21 个已公开错误 URL 的兼容跳转到正确目标，不形成循环，不改变查询参数/锚点需要的阅读语义。
- [ ] 英日 LoRa Bus 展示完整正文或明确可用的语言回退，普通页面和原始 `.md` 均不再静默为空。
- [ ] Nuxt 生成/发布流程通过，浏览器从目录实际点击后显示对应教程标题和代码。
- [ ] 重新保存修复后的 HTTP 状态与正文长度，确保测试针对修复提交/部署。

## 验证范围

- **PASS（观察基线）**：静态文件/路由交叉检查；表内错误与正确 URL 的实际线上 HTTP 请求；三语言 LoRa Bus 原始正文长度。
- **NOT RUN**：修复代码、修复后的构建/部署/浏览器点击回归。
- **NOT RUN**：硬件/虚拟设备外设运行；本 issue 不据此推断任何 LoRa、GPIO 或模块运行结果。
