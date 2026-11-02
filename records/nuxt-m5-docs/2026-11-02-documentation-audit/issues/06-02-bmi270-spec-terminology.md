# [文档审查] DoF6/DoF9/DoF10 的 BMI270 零偏不应标成全局测量精度

> 发布边界：本记录按用户针对本次文档工单明确批准的 REVIEW 例外发布。hardware validation 与 virtual-device validation 均为 NOT RUN。公开页面链接可能更新，源文件位置以所列提交、路径和行号为准。

## 基线与状态

文档基线：`47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac`，2026-11-02核对。资料对照为REVIEW；hardware validation / virtual-device validation均为NOT RUN。本工单只请求修正规格术语，不声称测得板级精度或超差。

## 原文位置

- [Unit DoF6 第54/57行](https://docs.m5stack.com/zh_CN/unit/Unit_DoF6)：加速度计“精度”±20mg、陀螺仪“精度”±0.5°/s。
- [Unit DoF9 第55/58行](https://docs.m5stack.com/zh_CN/unit/Unit_DoF9)：同一表述。
- [Unit DoF10 第57/60行](https://docs.m5stack.com/zh_CN/unit/Unit_DoF10)：同一表述。

## 独立依据

[Bosch BMI270 官方产品规格](https://www.bosch-sensortec.com/en/products/motion-sensors/imus/bmi270)（2026-11-02核对）将这两项明确列为 **Zero-g/zero-rate offset**，并将 **Sensitivity error** 与 **Temperature behaviour** 另列。

零输入偏置不是全量程误差上限。用户将目前“精度”理解成任何姿态、角速度、温度下的总测量误差保证，可能造成错误选型、校准目标或验收阈值。

## 建议修改

1. 三个型号及三语言统一改成“加速度计零g偏置 / 陀螺仪零速偏置”，不要把单项指标统称板级精度。
2. 引用对应版本datasheet表格，明确数值是典型值还是界限值，并带上其温度、供电、CRT等适用条件；这些条件应由硬件负责人核对后填写，不凭产品页推断。
3. 若需要提供总体测量精度，另列灵敏度误差、零偏、温漂等指标，并区分芯片规格与成品实测。

## 人工验收

- [ ] DoF6/9/10三语共九页术语一致。
- [ ] 每项数值可定位到指定版本Bosch datasheet及测试条件。
- [ ] 页面不再将零偏误写为全量程或板级精度保证。
- [ ] 如新增成品性能声明，另附匹配硬件测量证据；本次资料勘误不提供性能PASS。

## 审查记录

本文件即本次审查的归档依据；发布工单将引用本归档的完整提交永久链接。
