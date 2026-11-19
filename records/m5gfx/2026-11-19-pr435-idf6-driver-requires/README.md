# M5GFX #435: ESP-IDF 6 下显式声明 esp_driver_gpio / i2c / spi / dma（构建级验证）

- 日期：`2026-11-19`
- 结果：`PASS`（构建级：PR 自带 CI 日志 + 组件清单核验；硬件、虚拟设备对本改动不适用）
- 工作类型：`pr`
- 条目：[m5stack/M5GFX#435](https://github.com/m5stack/M5GFX/pull/435)
  「build: require esp_driver_gpio / i2c / spi / dma on ESP-IDF 6」，作者 ainyan03，英文，OPEN
- 源码：PR head `299c52aa540555a716957eb3aa83c4490a8a4961`，base `develop`
  `5f7ad476457cd738407766c38df23620ead7baac`（#434 的 merge commit）
- 环境：GitHub Actions `ubuntu-latest` + `espressif/idf:v6.0.2` 容器（PR 自带 CI）；
  macOS arm64 本机只做只读取证，未做本地独立重建

## 结论

1. 改动只有 `CMakeLists.txt:36-38` 一处（IDF ≥ 6 分支的 `COMPONENT_REQUIRES` 末尾追加
   四个组件），没有其它文件变化；head 上 28 项检查全部 `pass`，其中 IDF 6.0.2 的
   esp32 / esp32s3 / esp32c6 / esp32p4 四个作业都成功。无阻塞问题。
2. PR 正文的依赖判断成立。6.0.2 与 6.1.1 的 `driver` 不再把 `esp_driver_*` 作为公开
   依赖：它只有 `PRIV_REQUIRES esp_driver_gpio`，公开侧是
   `REQUIRES esp_hal_i2c esp_hal_twai esp_hal_touch_sens`；而 5.4.3 / 5.5.4 的 `driver`
   注释原文写着「for backward compatibility … public dependency on other
   `esp_driver_foo` components」并逐个列出。所以「≤5.x 由 driver 兜住、6.0 起不再兜」
   属实。
3. 现状下这四个头本来就可达，只是路径依赖 `esp_lcd`：
   - `esp_lcd`（6.0.2 / 6.1.1）公开依赖 `esp_driver_gpio`、`esp_driver_i2c`、
     `esp_driver_spi`（另有 `esp_driver_parlio`、`esp_hal_lcd`）；
   - `esp_driver_dma` 在 `esp_lcd` 只是 `PRIV_REQUIRES`，`<esp_private/gdma.h>` 又只存在
     于 `esp_driver_dma/include`，base 实际是经 `esp_lcd → esp_driver_spi` 到达的，
     因为 `esp_driver_spi` 的 `REQUIRES` 公开含 `esp_driver_dma`。
   因此新增的四条今天都是「重复声明」：gpio / i2c / spi 与 `esp_lcd` 现有公开依赖重复，
   dma 与 `esp_driver_spi` 的公开依赖重复；PR 文本说的 "only reached through the public
   dependencies of esp_lcd" 对 dma 而言是间接成立。方向正确：任一层收窄公开依赖时，
   这四个头仍然在。
4. 「静默丢功能」的风险是真的，不是假想：
   `src/lgfx/v1/platforms/esp32/common.inl:125` 用
   `__has_include(<driver/i2c_master.h>)` 决定 `LGFX_LP_I2C_NUM`，:193 用
   `__has_include(<driver/lp_io.h>)` 决定 `LGFX_LP_GPIO_MATRIX`；头找不到时分别退化为 0
   与未定义，不报错，正是 PR 想堵的路径。
5. 「构建组件集合不变」有实测支撑：同一 6.0.2 镜像下 base 与 head 的
   `-- Components:` 列表逐项相同（S3 138 个、P4 137 个），构建步骤数相同
   （S3 1077、P4 1090），最终 `M5GFX-build-test.bin` 大小也相同（S3 `0x632e0`、
   P4 `0x524b0`）。base 日志里 `esp_driver_dma` 本来就在编译（S3 `[71/1077]`），
   说明这次只是把隐式依赖写实，不改变产物。
6. 组件存在性覆盖 6.0–6.1.1：`v6.0`、`v6.0.1`、`v6.0.2`、`v6.1`、`v6.1.1` 五个 tag 上
   四个组件的 `CMakeLists.txt` 都是 200；`v6.0.0` / `v6.1.0` 不是真实 tag（已知文件同样
   404）。

## 关键证据

- `evidence/ci-builds.txt`：head 28/28 检查通过；S3、P4 在 6.0.2 下 base/head 的
  `COMPONENT_REQUIRES` 打印行、组件数、构建步骤数、最终 BIN 大小；base 日志中
  `esp_driver_dma` 的编译行。
- `evidence/idf6-manifests.txt`：IDF v6.0.2 / v6.1.1 的 `driver`、`esp_lcd`、
  `esp_driver_spi` 原文片段，v5.5.4 的兼容注释，四个组件逐 tag 的 HTTP 存在性，
  五个头文件的所属组件，M5GFX 对应行号。
- `evidence/diff-scope.txt`：base/head、+6/−1 差分、`git apply --check` 通过。
- `patches/0001-build-idf6-driver-requires.patch`：PR head 的差分。
- 前序：`records/m5gfx/2026-11-19-pr434-idf6-c6-p4-ci/`（本 PR 是其直接后续）。

## 文件

- `report.md`：完整报告（背景、方法、观察表格、结论、风险）
- `run.json`：结构化记录
- `evidence/`：CI 日志摘要、IDF 清单、差分范围
- `patches/`：PR head 的差分

## 未覆盖项

- 本地独立重建：`NOT RUN`。本机 Docker 守护进程无法创建新容器（containerd 元数据
  存储只读），因此没有在 PR 之外独立跑 6.0.2 构建；结论依赖 PR 自带 CI 日志与
  IDF 源码清单，不是代码级推测，但也请注意其来源是上游 CI。
- ESP-IDF 6.1.x 构建：`NOT RUN`。M5GFX 的 `IDFBuild.yml` 没有 6.1 作业，而本改动对
  所有 6.x 生效；只做了 6.1 / 6.1.1 的组件存在性与依赖清单核对，没有编译。
- hardware validation：不适用。改动只是组件依赖声明，不改变运行时行为。
- virtual-device validation：不适用，且是结构性的：无论 base 还是 head，固件行为都
  没有可观察差异（BIN 大小已相同），任何虚拟设备都无法据此给出额外信息。
- 逐字节产物比对：`NOT RUN`。只比对到尺寸与构建步骤；CI 不保留 BIN 供下载比对。
