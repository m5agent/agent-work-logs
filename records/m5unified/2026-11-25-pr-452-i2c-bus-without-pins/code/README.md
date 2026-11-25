# 探针工程

`probe-main.cpp`、`app-CMakeLists.txt`、`sdkconfig.defaults` 组成最小 ESP-IDF 探针工程，
链接 M5Unified（develop 或 PR head）与 M5GFX `28d4794`。

重建步骤：

1. 建工程目录：`app/main/main.cpp`（用 `probe-main.cpp`）、`app/main/CMakeLists.txt`
   （`idf_component_register(SRCS "main.cpp" INCLUDE_DIRS "." REQUIRES M5Unified)`）、
   `app/CMakeLists.txt`（用 `app-CMakeLists.txt`，`EXTRA_COMPONENT_DIRS` 指向 `../components`）、
   `app/sdkconfig.defaults`。
2. `components/M5Unified` = 目标 M5Unified 检出；`components/M5GFX` = M5GFX `28d4794`。
   本地 ESP-IDF v6.1 需要把两个组件的 `CMakeLists.txt` 换成 `idf_component_register()` 包装，
   并删除 `idf_component.yml`（否则会去 registry 拉 m5gfx 0.3.0）。库源码不改。
3. `idf.py set-target esp32s3 && idf.py build`，再按 `build/flasher_args.json` 合并
   `0x0` bootloader、`0x8000` 分区表、`0x10000` app 为单镜像。
4. 用本机 Device Service 上传并创建会话，串口读到 `P2 MARK_DONE`。

探针输出前缀统一为 `P2`，字段见 README 的对照表。两个版本只有 `BUILD_TAG`
（`pre`/`post`）不同。
