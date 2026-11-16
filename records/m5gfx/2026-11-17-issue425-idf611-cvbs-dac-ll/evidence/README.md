# 证据说明

| 文件 | 来源 | 说明 |
| --- | --- | --- |
| `issue-425.json` | `gh issue view 425` | 条目元数据（标题、作者、状态、时间、评论数）；不含正文副本 |
| `build-unpatched-fail-idf611-esp32.log` | 本机一次性容器构建 | M5GFX `b48dce0` 未打补丁，IDF v6.1.1 / esp32，完整 1057 步日志 |
| `build-unpatched-errors.txt` | 同上 | 失败 TU 的编译命令与 5 条错误（日志 1438-1472 行） |
| `build-patched-pass-idf611-esp32.log` | 本机一次性容器构建 | 同一工程打 `patches/0001` 后的完整日志 |
| `build-artifact.txt` | 构建产物 | `m5gfx425.bin` 大小与 SHA-256 |
| `idf-v611-dac-ll-names.txt` | ESP-IDF 仓库 v6.1 / v6.1.1 / master | `dac_ll.h` 新旧函数对照 |
| `idf-dac-driver-mapping.txt` | ESP-IDF v6.1.1 源码 | 驱动侧对 data source、clock invert、power 的使用 |
| `m5gfx-cvbs-source-refs.txt` | M5GFX `develop` / `master` | DAC LL 调用点、`.inl` 包含关系与目标守卫 |
| `m5gfx-ci-matrix.txt` | M5GFX `.github/workflows/IDFBuild.yml` | 现有 IDF 版本矩阵 |
| `patch-apply-check.txt` | `git apply --check` | 补丁对 `b48dce0` 的可应用性 |

日志中的 `ext_password.c` 等是 ESP-IDF 自带源文件名，不是凭据；日志中没有内网地址、设备标识或令牌。
容器内路径 `/project`、`/opt/esp` 是镜像内路径，不指向本机或内网。
