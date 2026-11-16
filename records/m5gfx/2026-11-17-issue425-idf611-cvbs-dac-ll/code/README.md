# 复现工程：ESP-IDF v6.1.1 + M5GFX（esp32 目标）

最小 ESP-IDF 应用，只把 M5GFX 作为组件编译，用于复现 m5stack/M5GFX#425。

## 目录

```text
CMakeLists.txt        IDF 工程入口
.esp-build.yml        记录本次使用的 IDF 版本与目标（可选，供构建调度器读取）
main/CMakeLists.txt   main 组件，REQUIRES M5GFX
main/main.cpp         仅实例化 M5GFX，确保组件参与编译与链接
components/M5GFX/     放入 M5GFX 源码（未提交）
```

## 重建

```bash
git clone https://github.com/m5stack/M5GFX.git components/M5GFX
git -C components/M5GFX checkout b48dce04c80d3e3c9874b7ba946c43d672129c28
# 未打补丁：应当出现 5 条 dac_ll_* 编译错误
# 打补丁：git -C components/M5GFX apply /path/to/0001-panel-cvbs-idf611-dac-ll.patch
docker run --rm -v "$PWD":/project -w /project espressif/idf:v6.1.1 \
  bash -lc 'idf.py set-target esp32 && idf.py build'
```

`main.cpp` 用 `extern "C"` 声明 `app_main`，这是 IDF 的 C 入口约定；与应用层用法无关。
