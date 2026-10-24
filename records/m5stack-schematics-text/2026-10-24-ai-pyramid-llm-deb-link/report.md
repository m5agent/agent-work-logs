# AI Pyramid llm-llm 下载链接修正报告

## 一、问题与影响

AI Pyramid 的软件包更新文档同时包含两类信息：

1. APT 源声明：`jammy ax650c`；
2. `llm-llm` 手工下载链接：`pool/jammy/ax630c/v1.9/llm-llm_1.9-m5stack1_arm64.deb`。

`ax630c` 是 LLM630 使用的组件，不是 AI Pyramid 的 `ax650c`。两个平台的包名和文件名规则相同，
错误 URL 也真实存在，因此不会报 404；用户会拿到一个架构层级不对、但表面看起来正常的 deb。

受影响页面：

```text
zh_CN/stackflow/ai_pyramid/software_update.md
```

## 二、根因

手工下载链接把平台目录硬编码成了 `ax630c`，与同一页面的 APT 源 `ax650c` 不一致；同时链接固定在
`v1.9`，而 APT 源当前索引中的 `llm-llm` 已到 `v1.12`。

## 三、修复

修改为：

```text
https://repo.llm.m5stack.com/m5stack-apt-repo/pool/jammy/ax650c/v1.12/llm-llm_1.12-m5stack1_arm64.deb
```

链接文本同时标注平台和版本，便于后续核对。

本地提交：

- 分支：`m5agent/ai-pyramid-llm-deb-link-2026-10-24`
- commit：`2aab39e`
- base：`7ae3eab`

## 四、验证

### 4.1 包索引

从 `dists/jammy/ax650c/binary-arm64/Packages` 读取到：

```text
Package: llm-llm
Version: 1.12
Architecture: arm64
Filename: pool/jammy/ax650c/v1.12/llm-llm_1.12-m5stack1_arm64.deb
Size: 28607168
SHA256: 8060a5750e6a673b953e6e324854c6c8fccc30d3d4b3c3840fd3007d5e980eae
```

### 4.2 实际下载

对目标 URL 执行 HEAD：

```text
HTTP/2 200
content-type: application/vnd.debian.binary-package
content-length: 28607168
```

实际下载后：

```text
size: 28607168
sha256: 8060a5750e6a673b953e6e324854c6c8fccc30d3d4b3c3840fd3007d5e980eae
file: Debian binary package (format 2.0)
```

大小和哈希均与索引一致。

### 4.3 类似问题审计

范围：`zh_CN/` 下全部指向 `repo.llm.m5stack.com` 的 `.deb` 链接。

| 检查项 | 结果 |
| --- | --- |
| 链接总数 | 100 |
| HTTP 非 200 | 0 |
| 平台目录错配（修复后） | 0 |
| 与当前索引版本一致 | 74 |
| 指向较旧但仍可下载的版本 | 26 |

结论：本例外没有发现第二个“AX650 页面链接到 AX630 包”的平台错配；剩余问题是版本漂移，不是坏链。
逐项结果见 `evidence/deb-link-audit.tsv`。

## 五、兼容性与影响面

- 只修改了一个文档链接，不影响源码或其他文档。
- 新链接指向 arm64 Debian 包，依赖仍为 `lib-llm (>= 1.8)`，与 APT 源当前包一致。
- 旧链接仍可下载，但对应的是错误平台，不能作为 AI Pyramid 的升级包。

## 六、未覆盖项与交付边界

- 修改仅存在于本地分支，尚未推送到 GitHub fork 或创建 PR。
- 26 个旧版本链接可能是有意固定版本，未在本轮批量更新。
- 未在 AI Pyramid 实机上执行 `dpkg -i`；本轮验收的是“文档中的下载路径是否指向正确的公开包”。

## 七、回滚

应用反向补丁或将链接恢复为原值即可；文档没有其他依赖变化。
