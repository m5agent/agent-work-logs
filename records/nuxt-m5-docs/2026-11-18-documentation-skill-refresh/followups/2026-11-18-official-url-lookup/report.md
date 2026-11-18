# 官网到 Markdown 的查阅路径

站点文章通常由 `static/<locale>/<route>.md` 对应到 `https://docs.m5stack.com/<locale>/<route>`。新命令 `lookup.py --url` 使用随包索引解析官网 URL，保留语言和路由大小写，查询参数、锚点和尾斜杠不参与本地查找。匹配输出含 Markdown 路径及原始 `source_url`。别名和生成页面可先打开官网确认最终路由。

在 Linux 来宾、只读 ZIP、禁用网络的环境中解包，用 `python3 scripts/lookup.py --url https://docs.m5stack.com/en/core/Tab5` 取路径，再用 `--read` 读取。分别核对 Tab5、PowerHub、Faces Keyboard3 的型号与原文标记。临时移除中日文站点语料后再次运行三个英文用例，均通过。中文打包路径、带查询参数的 URL、日文缺页、非官网域名和原有型号及 SKU 查询也经核对。

英文站点语料可覆盖样本，对英文缺页和技术内容差异需补查实际语言页面。在线样本中，Chain ENV 英文 Markdown 缺页，TimerCAM 中文页与 StackChan Core 日文页包含英文页缺少的 API 章节或附件。三语发布包的语料文件逐项与上个版本一致。本轮改动覆盖入口指南和查询工具，发布后 4,388 个文件路径和内容回读相符。
