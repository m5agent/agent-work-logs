# 可复现的 Markdown 文档 Skill 更新

每次在独立文档检出上生成 Skill。构建复用既有的 Markdown 筛选规则，保留原文和外链，临时 CSV 随构建退出清理。构建读取 3,275 份文档及补充资料、701 份 ESPHome 资料。GitHub、原理图和 UIFlow2 补充语料沿用本轮已验证输入快照。需要规格书或原理图时从 Markdown 的原链接取回单份 PDF。

构建和发布是两个入口。用 `tools/knowledge/update_docs_skill.py` 指定文档检出、补充语料和目标 ZIP。脚本先生成并校验新包，再原子替换旧包。同一输入重复构建的 SHA-256 相同。故意省略补充语料导致失败，已有 ZIP 保持原字节。16 项仓库现有测试通过。

虚拟设备验证在 aarch64 Linux 来宾、Python 3.12.3 上执行。使用 `python3 -m zipfile -e` 解包后运行 `m5stack-docs-local/scripts/lookup.py`。用 `K128`、`StickS3 PWR_BTN --category schematic --text`、`Unit ToF --category unit`、`ToFUnit --category uiflow2-docs --text`、`VL53L0X --category esphome`、`CardputerZero` 和 `Unit Accel --category unit` 检查查阅路径。两个最新改动页面与源提交的原文字节相符。从 Unit ToF 文档只获取关联的 VL53L0X 规格书，读取第 18 页，找到写入和读取地址字节 0x52、0x53。

通过 `tools/knowledge/publish_docs_skill.py --archive` 发布经过验证的原 ZIP，读取远端详情和下载包，对 3,981 个文件逐一比对路径和 SHA-256。再次运行普通发布识别到内容相同，更新计数保持 1。回滚可用通过验证的历史 ZIP 再次发布。实机和固件状态、线上问答缓存未在本轮验证。
