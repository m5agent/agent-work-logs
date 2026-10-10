# m5stack-linux-dtoverlays #14 aw882xx Linux 6.13+ 兼容报告

## 背景

- 来源：m5stack/m5stack-linux-dtoverlays issue #14
- 现象：较新内核下 aw882xx 模块编译失败，首先命中
  `MODULE_IMPORT_NS(VFS_internal_I_am_really_a_filesystem_and_am_NOT_a_driver)`。
- 目标：让 aw882xx 模块在当前 6.x 内核头文件下可编译。

## 结论

- 状态：`PARTIAL`（构建 PASS；运行时未验证）
- 根因：Linux 6.13 将 `MODULE_IMPORT_NS` 从自动 stringify 参数改为要求字符串
  字面量。继续向后编译还遇到旧 API 移除，需要一并处理。
- 改动范围：仅 aw882xx 模块的兼容宏和签名，不改变音频逻辑或对外接口。

## 证据

### 代码或配置

```text
- MODULE_IMPORT_NS(VFS_...)        # Linux >= 6.13 编译失败
+ MODULE_IMPORT_NS("VFS_...")      # 6.13+
+ 旧内核保留原写法
+ strlcpy -> strscpy
+ GPIOF_DIR_IN -> GPIOF_IN（6.12+）
+ devm_gpio_free 仅保留在 6.0 之前
+ i2c probe/remove 按 6.3 API 分支
```

### 执行

- 原始 6.14 失败日志见 `evidence/build-summary.txt`。
- 修复后构建：
  - Debian 6.12.111 arm64 headers：PASS
  - Ubuntu 6.14.0-37-generic arm64 headers：PASS
- 产物：`aw882xx_drv.ko`
- 未执行 `insmod` 或音频播放。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build (6.12) | PASS | 模块编译和链接完成 |
| build (6.14) | PASS | 模块编译和链接完成 |
| transport | NOT RUN | 未在目标设备加载模块 |
| device_response | NOT RUN | 未做 codec/I2C 运行时探测 |
| data_behavior | NOT RUN | 未播放音频或验证 DSP |

## 验证边界

构建使用 distro kernel headers，不是目标设备的完整 kernel build tree。没有执行
`insmod`、音频播放或中断路径验证，因此不能对外声称运行时可用。补测条件为可用的
6.12+ 目标设备和对应内核源码/头文件。

## 风险与回滚

改动只作用于旧驱动的编译兼容层；旧内核路径由 `LINUX_VERSION_CODE` 保留。回滚方式
为撤销 patch 并恢复原 `MODULE_IMPORT_NS`/旧 API。未执行不可逆操作。
