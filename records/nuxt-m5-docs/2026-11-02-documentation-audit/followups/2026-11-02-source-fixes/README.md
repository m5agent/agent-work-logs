# 文档Issue源码修订与人工MR准备

- 日期：2026-11-02（Asia/Shanghai）。
- 类型：code_change / review。
- 状态：REVIEW；代码和文档已修订，设备和生产服务未验收。
- 源码基线：`47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac`。
- 结果提交：`00eee6d573af4259e4fb9052b77ebef1dbe7b47e`，分支 `m5agent/fix-open-documentation-issues`。
- 范围：当前13个开放issue，4个逻辑提交、120个文件；原始源码工作区保持不变。

## 结论

修正产品规格与电气语义、教程引脚/API/采样与单位、完整示例破损和三语导航，并补齐缺失翻译。Basic的两份本地维护摘要在CSV与ESP上传时应用同一SKU澄清，对象key保持不变，实际上传内容参与哈希；没有修改被忽略的源副本或生产知识库。

## 证据与导航

- [报告](report.md)、[结构化记录](run.json)。
- [13项修订矩阵](evidence/issue-fix-matrix.json)。
- [验证摘要](evidence/validation-summary.json)：110页格式、8项新增知识库测试、官方头文件及代码/路由定向检查。
- [真实知识输入离线检查](evidence/knowledge-input-summary.json)。
- [4组变更文件](evidence/change-groups.json)。

## 验证边界

hardware validation与virtual-device validation均NOT RUN。完整Arduino/Nuxt构建、生产部署、知识库同步和线上问答复测未执行。全套知识库测试存在一个与原基线相同的旧PDF排除断言失败，详见报告。充电截止/BOM/档位映射和温度摄氏转换不填猜测值。MR交付将在后续记录回填；本记录不宣称所有issue已关闭。
