# 鹈鹕骑行 SVG 动画报告

## 背景与结论

用户要求全新绘制鹈鹕骑自行车的 2D SVG 动画，并明确不参考历史。绘制从空白开始，采用暖色海岸场景、白色鹈鹕、绿色围巾和珊瑚红自行车。无既有作品输入；没有上游代码缺陷或根因适用。

## 改动与运行路径

SVG 使用原生 path、use、animate 和 animateTransform，不含脚本或外部资源。踩踏周期 `1.6 s`，车轮周期 `1.2 s`；双踏板相差半圈。以固定腿长的逆运动学生成 97 个姿态，脚掌和曲柄使用相同相位；身体起伏也进入髋部计算。地面重复图案使用匹配的平移周期，避免循环跳变。

初次内联预览发现生成器将根 SVG 尺寸替换同时作用于裁剪矩形，导致画面空白；已将替换限制到第一次匹配。初次验证脚本对只读 animVal 调用 consolidate，改为读取 getItem(0)。最终数据和截图来自修正后的执行。车把与翼尖已对齐，并删除靠近后轮的多余货架。

## 可重建执行

环境为 Python 3.13.15、Playwright 1.63.0、Chrome 156.0.8078.80。进入记录根目录后运行：

```sh
python3 -m pip install playwright==1.63.0
python3 -m playwright install chromium
python3 code/work/build_pelican.py
python3 code/work/verify_pelican.py
```

若使用独立 Chrome，通过 `PELICAN_BROWSER_EXECUTABLE` 指定本机可执行文件。上述默认安装的 Chromium 可能与本次实测的 Chrome 版本不同；复测以输出 JSON 中实际版本为准。公开源码仅将输出路径改为记录目录下的相对路径，浏览器路径改由环境变量提供；矢量源和运动计算不变。

## 验证结果

| 层级 | 状态 | 证据 |
| --- | --- | --- |
| build | PASS | XML 解析，19 个动画元素，独立文件 30,118 bytes |
| data_behavior | PASS | 9 个相位的脚掌和髋部附着误差检查；首尾姿态匹配 |
| visual_or_physical | PASS | 浏览器运行，1120/736/320 CSS px 的截图与无横向溢出检查 |
| cross_browser | NOT RUN | 未启动 Safari 或 Firefox |
| flash / transport | NOT RUN | 无固件与嵌入式设备，不适用 |

这是同一交付 SVG 的浏览器运行验证，不属于 MCU 硬件验证或虚拟设备验证。没有对真实机械运动、RF、电气或物理测量作出声明。浏览器错误和外部网络请求均为零。视觉检查是所保存帧的人工检查，不代表逐帧像素级审查或无限时长播放测试。

## 证据、边界与回滚

产物 SHA256：`81babc991aa1b6159b953a76efc438276a2d2edddfc06bc1e8003aa48b52c79d`。原始浏览器采样数据、两个骑行相位和窄屏截图见 `evidence/`。截图不包含宿主路径、凭据或设备标识。未部署服务，无设备状态变更。回滚只需删除本次新增文件；公开记录提交保留为可追溯存档。
