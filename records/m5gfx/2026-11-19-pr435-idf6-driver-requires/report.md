# M5GFX #435 评审报告：在 IDF 6 下显式声明 esp_driver_gpio / i2c / spi / dma

## 1. 背景与目标

M5GFX 的 `CMakeLists.txt` 在 IDF ≥ 6 分支里的 `COMPONENT_REQUIRES` 一直写着 `driver`。
从前 `driver` 会把所有 `esp_driver_*` 作为公开依赖向下传递（5.5.4 的源码注释明确说这是
向后兼容），ESP-IDF 6.0 起不再这样做，于是 `<driver/gpio.h>`、`<driver/lp_io.h>`、
`<driver/i2c_master.h>`、`<driver/spi_master.h>`、`<esp_private/gdma.h>` 只在
`esp_lcd` 的公开依赖下才可达。PR #435 是 #434 的直接后续：把四个组件写进
`COMPONENT_REQUIRES`，避免 `esp_lcd` 哪天收窄依赖时，LP I2C 端口或 P4 的 LP pad 处理
通过 `__has_include` 静默消失。

评审要回答：

1. 依赖判断是否属实（6.x 的 `driver` 是否真不再公开 `esp_driver_*`）；
2. 新增四条是否覆盖了那五个头，是否有多余/遗漏；
3. 构建集合与产物是否真的不变（PR 声称 "the set of components in the build stays
   the same"）；
4. 静默降级路径是否真实存在；
5. 四个组件在 6.0–6.1.1 是否都存在。

## 2. 改动范围

`CMakeLists.txt`，+6/−1。只在 `if (IDF_VERSION_MAJOR GREATER_EQUAL 6)` 分支的
`COMPONENT_REQUIRES` 末尾追加 `esp_driver_gpio esp_driver_i2c esp_driver_spi
esp_driver_dma`，并加 4 行注释说明原因。

- base `develop` `5f7ad47`（#434 的 merge commit），head `299c52a` 单一提交。
- `MERGEABLE` / `CLEAN`；`git apply --check` 在 base 上通过。

## 3. 方法

纯构建配置改动，没有运行时行为可观测：能编过时生成的代码与 base 相同，任何模拟设备都
无法给出额外信息。因此取证分两层，不做实机与虚拟设备：

### 3.1 构建级：读 PR head 的真实 CI 结果

`gh pr checks 435` 取 head 上全部 28 项检查；对 `esp32s3 (IDF 6.0.2)` 与
`esp32p4 (IDF 6.0.2)` 拉 base（run 44438223864）与 head（run 44441797261）两侧的完整
作业日志，比较 `-- Components:` 组件列表、`M5GFX use components` 打印行、`[n/N]`
构建步骤数与最终 BIN 大小。

### 3.2 代码级：按 IDF 源码清单还原依赖图

从 `espressif/esp-idf` 的 v6.0.2、v6.1.1 取 `components/driver/CMakeLists.txt`、
`components/esp_lcd/CMakeLists.txt`、`components/esp_driver_spi/CMakeLists.txt`，
从 v5.4.3 / v5.5.4 取 `driver` 的兼容注释；用 v6.0.2 的 git tree 定位五个头所属组件；
逐 tag 用 HTTP 状态确认四个组件存在。

## 4. 观察

### 4.1 `driver` 在 6.x 确实不再公开 `esp_driver_*`

| IDF | driver 的依赖 |
| --- | --- |
| v6.0.2 / v6.1.1 | `PRIV_REQUIRES esp_timer esp_mm esp_driver_gpio esp_ringbuf esp_pm`；`REQUIRES esp_hal_i2c esp_hal_twai esp_hal_touch_sens` |
| v5.4.3 / v5.5.4 | 注释「for backward compatibility, the driver component needs to have a public dependency on other "esp_driver_foo" components」，随后逐个列出 `esp_driver_gpio … esp_driver_i2c …` |

PR 描述与源码一致。

### 4.2 四个头的实际来源

| 头 | 所属组件 | base 可达路径 |
| --- | --- | --- |
| `<driver/gpio.h>` | `esp_driver_gpio` | `esp_lcd` 公开依赖 |
| `<driver/lp_io.h>` | `esp_driver_gpio` | `esp_lcd` 公开依赖 |
| `<driver/i2c_master.h>` | `esp_driver_i2c` | `esp_lcd` 公开依赖 |
| `<driver/spi_master.h>` | `esp_driver_spi` | `esp_lcd` 公开依赖 |
| `<esp_private/gdma.h>` | `esp_driver_dma` | `esp_lcd → esp_driver_spi` 公开依赖 → `esp_driver_dma` |

`esp_lcd` 6.0.2 / 6.1.1 的公开依赖是 `esp_driver_gpio esp_driver_i2c esp_driver_spi
esp_driver_parlio esp_hal_lcd`，`esp_driver_dma` 只在 `PRIV_REQUIRES`；
`esp_driver_spi` 的 `REQUIRES` 公开含 `esp_driver_dma`，所以 gdma 头仍可达。
结论：新增的四条今天都是重复声明（dma 是间接重复），但方向正确——把「靠上层组件
转手」变成「自己声明」，任一层收窄时四个头仍然在。

### 4.3 静默降级路径是真实的

- `src/lgfx/v1/platforms/esp32/common.inl:125`：`__has_include(<driver/i2c_master.h>)`
  不成立时 `LGFX_LP_I2C_NUM` 退化为 0，LP I2C 端口静默消失；
- `common.inl:193`：`__has_include(<driver/lp_io.h>)` 不成立时 `LGFX_LP_GPIO_MATRIX`
  不定义，P4 的 LP GPIO matrix 路由静默消失；
- `src/M5GFX.cpp:13` 也用同一模式在 `i2c_master.h` / 旧 `i2c.h` 之间回退。

两处都不报错，正是 PR 要堵的路径。

### 4.4 构建集合与产物不变（base vs head，同一 6.0.2 镜像）

| 目标 | 组件数 base/head | 步骤数 base/head | BIN 大小 base/head | 四组件是否已在 base 列表 |
| --- | --- | --- | --- | --- |
| esp32s3 | 138 / 138 | 1077 / 1077 | `0x632e0` / `0x632e0` | 是（`esp_driver_dma` 在 `[71/1077]` 编译） |
| esp32p4 | 137 / 137 | 1090 / 1090 | `0x524b0` / `0x524b0` | 是 |

`-- Components:` 列表逐项 diff 为空。PR 的「组件集合不变」有实测支撑，本次改动只是把
隐式依赖写实，产物未变。

### 4.5 组件存在性

| tag | gpio | i2c | spi | dma |
| --- | --- | --- | --- | --- |
| v6.0 / v6.0.1 / v6.0.2 / v6.1 / v6.1.1 | 200 | 200 | 200 | 200 |

`v6.0.0` / `v6.1.0` 不是真实 tag（已知文件同样 404），不属于缺口。

## 5. 结论

无阻塞问题，建议合并。改动只影响 IDF ≥ 6 的组件声明，5.x 与 Arduino 路径不变；
四个组件全部存在，组件集合、构建步骤与最终 BIN 大小逐项相同，评审中未发现行为变化。
唯一值得写进评审的非阻塞事实是：这四条目前都是冗余声明，`esp_driver_dma` 经由
`esp_driver_spi` 传递可达，PR 文本对 dma 的「through the public dependencies of
esp_lcd」是间接成立。

## 6. 未覆盖项与风险

- 本地独立重建 `NOT RUN`：本机 Docker 守护进程无法创建新容器（containerd 元数据存储
  只读），只能引用 PR 自带 CI 的构建结果，没有在 PR 之外重跑 6.0.2 构建。
- ESP-IDF 6.1.x 构建 `NOT RUN`：`IDFBuild.yml` 没有 6.1 作业，而本改动对所有 6.x
  生效；只核对了 6.1 / 6.1.1 的清单与组件存在性，没有编译。
- 逐字节产物比对 `NOT RUN`：只比到尺寸与步骤数，CI 未保留可下载的 BIN。
- hardware validation：不适用（无运行时行为）。
- virtual-device validation：结构性不适用（base/head 固件无可观察差异）。
- 风险：若未来 IDF 把 `esp_driver_spi` 对 `esp_driver_dma` 的公开依赖也收窄，本 PR
  恰好覆盖；目前没有已知回归面。
