# 文档 Skill 构建过滤与分发验证

生成器原先把符合来源条件的 Markdown 写入正文包和查询索引。部分待发布页面的正文含 Coming Soon，另一些仅通过 `coming-soon.png` 显示徽标。构建器现在在写入正文和索引前检查整篇 Markdown，匹配忽略大小写，并兼容空白、连字符、下划线和源码中的常见 Markdown 或 HTML 标记。

相同的规则用于主语料、补充目录、英日文语料和 ESPHome 下载文档。过滤按单篇文档生效，产品目录仍独立从文档仓库刷新。对比前一版分发包，6 份 Skill 说明及运行文件逐字节一致。

在源码提交 `74ccbb789062fc43b74e2673b115fbeb0c19af87` 上运行 `tools/knowledge/update_docs_skill.py` 生成分发 ZIP。20 项回归测试通过。两次构建得到相同 SHA-256，包大小为 15,695,463 字节。主语料排除 23 篇，英语排除 15 篇，日语排除 7 篇。本次 ESPHome 来源排除 0 篇。

Linux 虚拟机使用只读块设备挂载归档，校验 ZIP 中的 4,401 个文件，解析读取 6,410 篇索引正文，包括 2,022 篇合并存储的正文，未再发现 Coming Soon 标记。虚拟机从归档中解包并运行 `scripts/lookup.py --url https://docs.m5stack.com/en/core/Tab5`，返回英文 Tab5 文档。执行 `scripts/products.py --sku K145 --locale en` 返回 Tab5 和对应官网链接。虚拟机检查退出码为 0。

Skill Hub 发布后重新下载归档，校验了 4,401 个文件的路径和内容，更新计数为 4。本地安装与同一归档逐文件一致。可从前一版构建归档恢复 Skill 分发包，如需恢复旧构建行为可回退本条记录中的流程提交。未执行生产反馈、终端问答和实机固件流程。
