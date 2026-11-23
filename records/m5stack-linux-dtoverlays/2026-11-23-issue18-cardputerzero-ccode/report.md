# CardputerZero 12/13 信道问题：根因、修复位置与验证边界

## 1. 问题与来源

- Issue：[m5stack/m5stack-linux-dtoverlays#18](https://github.com/m5stack/m5stack-linux-dtoverlays/issues/18)
- 作者：cjct-dev；语言：英文；状态：OPEN；评论：0；关联 PR：无
- 设备：CardputerZero（CM0，CYW43439，SDIO `brcmfmac`）
- 系统：Debian 13，kernel `6.18.39+rpt-rpi-v8`，Wi-Fi country 设为 GB
- 现象：2.4 GHz 12/13 信道上的网络在扫描和启动器 Wi-Fi 列表中都看不到；同房间其他
  设备能看到。`iw reg set GB` 后 `iw list` 有变化，但扫描仍无结果；NVRAM 里的
  `ccode=` 被 Raspberry Pi 内核拦截。
- 报告者日志：`brcmf_translate_country_code No country codes configured for device`
- 报告者建议：给 Wi-Fi 节点加 `brcm,ccode-map-trivial`，让驱动把 ISO 国家码直接交给
  固件。

本记录的目标不是复跑报告者的真机结果，而是确认「这个属性是否真的能让驱动把国家码写到
固件」以及「在这个仓库里应该加在哪里」。

## 2. 驱动链路与根因

### 2.1 属性读取

Raspberry Pi 6.18.y（`d4addd158e6e06df12e4ccaf95ba699a9ed047b2`）的
`drivers/net/wireless/broadcom/brcm80211/brcmfmac/of.c`：

- `brcmf_of_probe()` 先做 compatible 检查：

  ```c
  if (!np || !of_device_is_compatible(np, "brcm,bcm4329-fmac"))
          return 0;                                    /* of.c:124-125 */
  err = brcmf_of_get_country_codes(dev, settings);     /* of.c:127 */
  ```

- `brcmf_of_get_country_codes()` 先数 `brcm,ccode-map`；属性不存在时读
  `brcm,ccode-map-trivial` 布尔值：

  ```c
  count = of_property_count_strings(np, "brcm,ccode-map");   /* of.c:26 */
  if (count < 0) {
          settings->trivial_ccode_map =
                  of_property_read_bool(np, "brcm,ccode-map-trivial"); /* of.c:31-32 */
          return (count == -EINVAL) ? 0 : count;
  }
  ```

`of.c` 是 `brcmf_get_module_param()` 的一部分：`common.c:604` 在没有 board platform
data 时调用 `brcmf_of_probe(dev, bus_type, settings)`。SDIO 路径传入的是 SDIO function
设备（`sdio.c:4204`），其 `of_node` 由 `sdio_bus.c:362` 的
`mmc_of_find_child_device(host, func->num)` 取得；MMC 核心按子节点 `reg == func_num`
匹配（`drivers/mmc/core/core.c:1113-1127`）。因此 func 1 拿到的是 `wifi@1`（`reg = <1>`），
它带有 `compatible = "brcm,bcm4329-fmac"`，上面的 compatible 门会通过。

### 2.2 失败点

同一个 6.18.y 的 `cfg80211.c`：

- `brmcf_use_iso3166_ccode_fallback()`（`:8266-8280`）在 `trivial_ccode_map` 为真时
  返回 true；否则只对 43430 / 4345 / 4356 / 43602 返回 true。**43439 不在列表里**。
- `brcmf_translate_country_code()`（`:8282`）在既没有 `country_codes` 表、又不能走
  ISO 回退时打印 `No country codes configured for device`（`:8308`）并返回 `-EINVAL`。
- `brcmf_cfg80211_reg_notifier()`（`:8561`）拿到 `-EINVAL` 后直接 `return`
  （`:8606-8608`），后面的 `brcmf_fil_iovar_data_set(ifp, "country", ...)`
  （`:8610`）不会执行。

所以即使用户设置了 GB，固件从未收到 country 设置；报告者观察到它仍按默认国家 US
（只允许 1–11）工作。`iw reg set` 改变的是内核/cfg80211 的监管域，不能替代这次 iovar
写入。报告者关于 `iw list` 的观察（内核侧有变化但扫描无结果）与本失败点在 iovar 写入
之前一致；本记录不把 `iw list` 的具体输出当作固件已接受 GB 的证据。

### 2.3 属性打开后的行为

同一 `cfg80211.c`：

```c
if (drvr->settings->trivial_ccode_map)
        return true;                                   /* :8268-8269 */
...
ccreq->country_abbrev[0] = alpha2[0];
ccreq->country_abbrev[1] = alpha2[1];
ccreq->ccode[0] = alpha2[0];
ccreq->ccode[1] = alpha2[1];
return 0;                                              /* :8300-8305 */
```

随后 `:8610` 才会写入 `country` iovar；报告者的真机结果是在此之后 12/13 可见。binding 对属性的
定义是 `cc -> { cc, 0 }`，即假定 CLM 使用 ISO3166 国家码且 revision 为 0；如果同时
存在 `brcm,ccode-map`，后者优先（`brcm,bcm4329-fmac.yaml:91-99`）。

## 3. 仓库内应加在哪里

### 3.1 源文件

- `modules/CardputerZero/cardputerzero-v3-overlay.dts`：426 行，最后一个 fragment 是
  `fragment@6`（407 行）。
- `modules/CardputerZero/cardputerzero-v5-overlay.dts`：502 行，最后一个 fragment 是
  `fragment@6`（486 行）。
- 两个文件当前都没有 `ccode` / `brcm,ccode-map` 相关属性。

建议在两者末尾追加：

```dts
    fragment@7 {
        target-path = "/soc/mmcnr@7e300000/wifi@1";
        __overlay__ {
            brcm,ccode-map-trivial;
        };
    };
```

路径 `/soc/mmcnr@7e300000/wifi@1` 已核对：

- 内核 DT 源：`arch/arm/boot/dts/broadcom/bcm270x.dtsi:50` 定义
  `mmcnr: mmcnr@7e300000`；`arch/arm/boot/dts/broadcom/bcm2710-rpi-cm0.dts:144-155`
  打开 `&mmcnr` 并定义 `brcmf: wifi@1 { reg = <1>; compatible = "brcm,bcm4329-fmac"; }`。
- 实际基础 DTB：`raspberrypi/firmware` 的 `boot/bcm2710-rpi-cm0.dtb`
  （SHA256 `1ef5ed4a...71edb08`，33740 字节）解编译后存在
  `/soc/mmcnr@7e300000/wifi@1`，compatible 相同。
- 把上面的片段单独编译后 `fdtoverlay` 到该 DTB，属性落在 `wifi@1` 节点上。

补丁见 `patches/0001-cardputerzero-ccode-map-trivial.patch`，对 base `a3fd3e8`：
两个文件各 +7 行，`git diff --stat` 为 `2 files changed, 14 insertions(+)`。

### 3.2 预编译 dtbo

`firmware/CardputerZero/config.txt:58` 是 `dtoverlay=cardputerzero-overlay`，而仓库内的
`firmware/CardputerZero/overlays/cardputerzero-overlay.dtbo`（6535 字节，最后变更
`db765d2a70`，2026-02-08）解编译后没有 `mmcnr` fragment，也没有
`brcm,ccode-map-trivial`。如果 stock image 直接使用这个预编译文件，只改 `.dts` 不会
改变已发布镜像；需要从更新后的 overlay 重新生成该 dtbo。该预编译文件与当前 v3/v5 源
也不是逐字节/逐结构一致，重生成时应明确选用哪个 revision 的源。

## 4. 验证

### 4.1 编译与应用

环境：macOS arm64，`dtc` 1.8.1，Apple clang 21；命令与仓库 Makefile 一致：

```sh
gcc -E -nostdinc -undef -x assembler-with-cpp <overlay>.dts -o <overlay>.tmp
dtc -@ -I dts -O dtb -o <overlay>.dtbo <overlay>.tmp
fdtoverlay -i bcm2710-rpi-cm0.dtb -o out.dtb <overlay>.dtbo
```

结果：

- v3 补丁编译、应用到 CM0 DTB：成功（`fdtoverlay` 退出 0）。
- v5 补丁编译、应用到 CM0 DTB：成功（`fdtoverlay` 退出 0）。
- 两者生成的 `wifi@1` 节点均包含 `brcm,ccode-map-trivial;`，`reg` 与 compatible 不变。
- 补丁 `git apply --check` 通过。
- 产物 SHA256：
  - v3 补丁 dtbo：`66abb56c386643343884406cf958b278abc3714848fe60f136c7c6f3e9e40239`
  - v5 补丁 dtbo：`941594104b6f72e67445c11aa9ec8caf74e9d45ee8ec7d7a842b3828a4974129`
  - 基础 CM0 DTB：`1ef5ed4abcb860a6b97efd31c4104a57e1ccc8d0dcec71834a3ac82ff71edb08`

这是主机侧的编译/应用验证，不是运行时验证：它证明 DT 片段语法正确、目标路径在 CM0
基础 DTB 中存在、属性会落到 `wifi@1`，但不证明 `brcmfmac` 在该板上实际拿到 GB 或
扫描到 12/13。

### 4.2 未执行

- hardware validation：`NOT RUN`。本机没有 CardputerZero；未申请硬件台验证。
- virtual-device validation：`NOT RUN`。本机 Device Service 的 `cardputer-zero` profile
  是 `supported=false`、`creatable=false`、`backend_ready=false`，缺少
  `__missing_qemu__` / `__missing_rom__`，后端为 Linux ARM64；`device_service_specs.py`
  明确把该机型排除为 “separate Linux backend”。ESP32 模拟器没有 CYW43439 SDIO Wi-Fi
  模型，也没有 Raspberry Pi 固件/NVRAM/CLM 流程，无法验证这个行为。
- 端到端：`NOT RUN`。未在真机上设置 GB 后扫描/连接 12/13，也未验证重启、挂起恢复和
  运行时切换国家。
- 其他国家码：`NOT RUN`。trivial map 固定 revision 0；GB 由报告者验证，但其他 ISO 码
  是否被对应 CLM 接受未覆盖。

## 5. 风险与兼容性

1. **revision 固定为 0**：`brcm,ccode-map-trivial` 对所有国家使用 `{cc, 0}`。如果某个
   国家在 CLM 中需要非 0 revision，固件可能拒绝；现场应看
   `dmesg` 是否出现 `Firmware rejected country setting` 或
   `No country codes configured for device`。
2. **`brcm,ccode-map` 优先**：如果基础 DT 或别的 overlay 同时提供显式 map，trivial
   属性会被忽略。当前 CM0 基础 DTB 没有 `brcm,ccode-map`。
3. **路径适用范围**：`/soc/mmcnr@7e300000/wifi@1` 适用于 CM0/CM4；CM5 的 WiFi 节点是
   `/axi/mmc@1100000/wifi@1`。CardputerZero 是 CM0，不受影响；如果同一 overlay 被
   复用到 CM5，target-path 不会匹配。
4. **预编译产物**：仓库内 dtbo 需要和 `.dts` 一起更新，否则 stock image 不会生效。
5. **NVRAM `ccode=`**：Raspberry Pi 下游会在 `firmware.c:572-586` 拦截 `ccode=` 并
   comment out；它不能替代 cfg80211 的国家设置。该属性修的是“设置能到达固件”，不是
   “NVRAM 自动设置国家”。

## 6. 回滚

删除两个 overlay 中的 `fragment@7`，重新编译并安装 dtbo 即可；不涉及内核或固件二进制，
回滚只影响 country iovar 的映射方式。

## 7. 结论

- 报告者的根因与代码一致；`brcm,ccode-map-trivial` 是正确且最小的修复。
- 建议加到 v3 和 v5 两个 overlay；若 stock image 使用预编译 dtbo，同步重生成。
- 本记录没有发现需要阻塞该方案的问题；真机 12/13 扫描/连接和重启持久性仍由报告者/维护者
  在 CardputerZero 上确认。
