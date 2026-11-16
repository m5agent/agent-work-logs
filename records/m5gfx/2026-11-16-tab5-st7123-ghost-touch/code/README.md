# 主机侧解析复现

`parse_check.cpp` 把 `Touch_ST7123::getTouchRaw()`（M5GFX `28d4794`）的结构体定义与
解析循环原样抽出，用报告者给出的鬼触点、真实点和窄鬼点字段构造 10 槽报表，比较三种
处理方式：

- `RULE_NONE`：当前驱动行为；
- `RULE_AREA_INTENSITY`：`area >= 30 && intensity < 25` 才丢弃；
- `RULE_INTENSITY_ONLY`：`intensity < 25` 丢弃。

构建与运行：

```bash
clang++ -std=c++17 -Wall -Wextra -O1 parse_check.cpp -o parse_check
./parse_check
```

预期输出见 [../evidence/parse-check-output.txt](../evidence/parse-check-output.txt)。本测试
只验证解析与过滤规则，不涉及 I2C、控制器时序或真实触摸，不能作为设备验证。
