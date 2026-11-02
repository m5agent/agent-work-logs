# 补齐 LLM630 摄像头 VLM 英日教程，并审查 Gray 日文恢复固件的跨型号链接

> 发布边界：本记录按用户针对本次文档工单明确批准的 REVIEW 例外发布。hardware validation 与 virtual-device validation 均为 NOT RUN。公开页面链接可能更新，源文件位置以所列提交、路径和行号为准。

审查基线：`nuxt-m5-docs@47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac`，日期：2026-11-02。两项均为多语言内容交付不一致；Gray 固件兼容性标为 **REVIEW**，不宣称已烧录失败或硬件不兼容。

## 1. LLM630 Camera VLM：英日教程仅剩占位文字

| 页面/入口 | 基线内容 |
| --- | --- |
| [static/en/stackflow/llm630_compute_kit/stackflow_camera_vlm_demo.md:1](https://docs.m5stack.com/en/stackflow/llm630_compute_kit/stackflow_camera_vlm_demo) | 仅1行 `coming soon...` |
| [static/ja/stackflow/llm630_compute_kit/stackflow_camera_vlm_demo.md:1](https://docs.m5stack.com/ja/stackflow/llm630_compute_kit/stackflow_camera_vlm_demo) | 仅1行 `coming soon...` |
| [static/zh_CN/stackflow/llm630_compute_kit/stackflow_camera_vlm_demo.md:1](https://docs.m5stack.com/zh_CN/stackflow/llm630_compute_kit/stackflow_camera_vlm_demo) | 已包含连接摄像头、网络准备、软件包/模型安装、PC/设备两种启动路径和完整 Python 客户端 |
| 三语言 `static/platform/stackflow_directory_{cn,en,ja}.json:202` | 均将上述路径作为正常教程列入目录 |

用户在英/日目录看到 VLM 摄像头演示并进入后无法完成后续步骤，页面没有提供现有中文可操作资料入口。此结论只说明内容缺失，不证明中文示例的设备运行正确性。

### 建议方案

- 将英/日正文同步到中文现有教程的功能范围，保留软件包名、模型包名、命令、参数、客户端代码一致性。
- 如果完整翻译尚不能交付，使用清晰的“本语言教程尚未完成”提示，并提供可用中文教程入口；避免让正常导航落到单行占位页。
- 补齐脚本所需 Python 依赖、PC与设备两种运行方式、查看视频流/结果的步骤。当前中文客户端本身的运行行为应独立验证后再翻译成已验证描述，不能把“存在中文正文”当作该代码已通过运行。
- 为目录中的正式教程建立占位内容检查；即使 HTTP 200，也检查最小正文/标题与必要步骤。

## 2. Gray：日文页面的“出厂固件”链接实际指向 Fire 命名文件（REVIEW）

| 文档固定版本位置 | 链接标签 | 目标文件 |
| --- | --- | --- |
| [static/ja/core/Gray.md:259](https://docs.m5stack.com/ja/core/Gray) | Gray 工場出荷時ファームウェア Easyloader | `Fire_Factory_Firmware.exe` |
| [static/zh_CN/core/Gray.md:256](https://docs.m5stack.com/zh_CN/core/Gray) | Gray 出厂固件 Easyloader | `EasyLoader_M5Core_FactoryTest.exe` |
| [static/en/core/Gray.md:257](https://docs.m5stack.com/en/core/Gray) | Gray Factory Firmware Easyloader | `EasyLoader_M5Core_FactoryTest.exe` |
| [static/ja/core/Fire.md:288](https://docs.m5stack.com/ja/core/Fire) | Fire 出荷ファームウェア Easyloader | 与 Gray 日文完全相同的 `Fire_Factory_Firmware.exe` URL |

两个目标为官方公开下载：

- [Fire_Factory_Firmware.exe](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/656/Fire_Factory_Firmware.exe)
- [EasyLoader_M5Core_FactoryTest.exe](https://m5stack.oss-cn-shenzhen.aliyuncs.com/EasyLoader/Windows/CORE/EasyLoader_M5Core_FactoryTest.exe)

**已确认**：同一 Gray 页面跨语言恢复路径不同；日文 Gray 和日文 Fire 使用完全相同文件链接。

**尚未确认**：Fire 文件是否有意兼容 Gray、兼容哪些 Gray 硬件版本、实际包含何种固件、该版本是否能完整恢复 Gray 出厂功能。本次未下载并运行 Windows EasyLoader、未烧录设备，文件名差异本身不足以证明固件不兼容。

### 需要维护者先明确的判断

1. 如果日文是误链接：确认官方有效 Gray 恢复包后，三语言统一到该包，并说明适用硬件/版本。不要只根据英文和中文多数一致就替换。
2. 如果 Fire 包有意作为 Gray 兼容方案：列明共享实现、支持/不支持的外设、适用硬件修订与已验证版本；同步三语言说明，避免继续标为无条件的 Gray 原厂恢复包。
3. 若两个包均有适用范围：提供型号/修订选择规则和校验信息，保存包与固件散列及实际恢复证据。

## 可复现的只读检查

在基线 checkout 内检查上述三语言同一路径及目录条目；无需执行任何下载器或驱动设备：

```python
from pathlib import Path
for lang in ('zh_CN', 'en', 'ja'):
    p = Path('static') / lang / 'stackflow/llm630_compute_kit/stackflow_camera_vlm_demo.md'
    text = p.read_text()
    print(lang, len(text.encode()), len(text.splitlines()), text[:40])
    g = Path('static') / lang / 'core/Gray.md'
    for line in g.read_text().splitlines():
        if 'Easyloader' in line and ('Factory' in line or '出厂' in line or '工場' in line):
            print(lang, line)
```

## 验收清单

- [ ] LLM630 英日目录入口指向完整教程或有明确可用回退的说明，普通页面不再只有 `coming soon...`。
- [ ] 翻译中的包名、命令、模型、客户端参数与经验证基线保持一致。
- [ ] LLM630 同一摄像头→VLM→结果观察路径在匹配硬件或验证虚拟设备执行，保存运行配置与输出证据；未通过前不要宣称演示可用。
- [ ] 维护者明确 Gray 下载包选择依据，三语言采用相同且明确的适用规则。
- [ ] 若改变恢复固件链接，记录目标包/嵌入固件散列及相应 Gray 硬件修订或获准虚拟设备的恢复验证；只有真实覆盖的能力可标已验证。
- [ ] 修复后检查构建与页面导航，并重新核查在线下载目标；HTTP可达只代表能下载，不代表恢复功能正确。

## 当前验证边界

| 层次 | 当前结果 |
| --- | --- |
| 三语言文件与目录对照 | PASS：确认 VLM 两个占位正文和 Gray 下载链接差异。 |
| Gray 包/固件兼容性判断 | REVIEW：未判断为固件错误或不可用。 |
| 修复后的构建/部署/浏览器回归 | NOT RUN：未实施修复。 |
| Gray 下载器执行、烧录与恢复 | NOT RUN。 |
| LLM630摄像头与VLM实际运行 | NOT RUN。 |
| hardware validation / virtual-device validation | NOT RUN：没有硬件或虚拟设备功能验收结论。 |
