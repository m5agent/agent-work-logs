# 多语查阅与产品目录复验

用户要求完整保留英文文档，并在 Skill 中查询每周维护的产品 JSON。英文站点的全部 2,013 篇 Markdown 逐份与文档提交 `fe2961505` 比对。为容纳新语料，将 2,025 篇中文站点 Markdown 按原字节放入一份有索引的 JSONL。日文支持类别为站点顶层、指南、Core 和 Unit。其他产品类语言不足时可回退到完整英文或中文。原文链接可按需读取 PDF。

同一更新流程读取同一文档提交中的 `product_collection_cn.json`、`product_collection_en.json` 和 `product_collection_ja.json`，每种语言 650 条公开记录，逐条与源数据相符。查找脚本提供精确 SKU、型号、标签和分类查询，返回原始公开字段与本地化官方页面。引脚和详细规格用设备页面交叉核对。用 `python3 scripts/products.py --sku K145 --locale en` 能定位官方 Tab5 条目，保留组合 SKU；未登记的部分 SKU 无结果。

在 aarch64 Linux 来宾中解包验证新入口。通过 `lookup.py` 实测英文 Tab5 Arduino microSD（FAT32、M5Unified 0.2.23 以上）、日文 Cardputer-Adv 恢复、缺日文页面时回退英文，以及 `--read` 读取中文 Unit ToF 的原文数据。三语 SKU 及两个负例合计六项通过。按产品页链接获取一份 VL53L0X 规格书并从第 18 页读到 0x52 与 0x53。此项是 Skill 的虚拟设备查阅验证，硬件行为和线上缓存未测。

用同一份 ZIP 发布新 ID，随后对 4,388 个文件做远端下载回读。旧分发条目保留用于兼容。再次构建逐字节一致。
