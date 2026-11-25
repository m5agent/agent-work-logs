# M5GFX #447 评审报告

## 1. 条目与改动

- PR：[m5stack/M5GFX#447](https://github.com/m5stack/M5GFX/pull/447)，
  `PaperDIY: stop driving G45 as the EPD OE; catalog its FPC connectors instead of a Grove port`
- 作者：ainyan03；状态：OPEN、非 draft、`MERGEABLE`；评审前无评论、无 review。
- 源码版本：head `a5fdf82cae2ebf3385f622302a1ffe917b197fdc`，
  base `72001da0fdd7232a8a8ac77cd84120801f879496`（develop）。
- 改动 7 文件 `+203/-30`：
  - `extras/board_spec/boards/m5paperdiy.json`：删去 `bus:epd_bus.oe` 与 `port_a`，
    新增 `fpc_i2s` / `fpc_spi` 两个 `logical_terminals_12` 连接器，补齐 FPC 端子对应 GPIO；
  - `extras/board_spec/connector_types/logical_terminals_12.json`：导轨枚举新增 `3v3_au`；
  - `dist/board_spec_editor.html`、`generated/m5unified_pin_table/*`、
    `src/board_detect/m5/generated/esp32s3_board_data.hpp`：重新生成；
  - `test/board_spec.test.js`：PaperDIY 的期望 `oe` 改为 `-1`，PaperS3 不变。

## 2. 事实核验（数据手册层）

### 2.1 面板 XOE 的归属

K159-B 原理图第 4 页（`EPD1 AXE544127`）逐脚抽取：

| pin | net | signal |
| --- | --- | --- |
| 7 | EPD_PWR | VDD |
| 12 | EPD_PWR | XOE |
| 23 | EPD_PWR | TEST |

即 XOE 直接接 `EPD_PWR`，与面板 VDD 同一网络，不由 G45 驱动。同一张图里
FPC-I2S 的 JP2 写作 `MCLK EXT_G45`（pin 10）。完整抽取见
`evidence/schematic-nets.txt`；PDF 为
<https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1288/K159-B_PaperDIY_sche.pdf>
（SHA256 `d3dbc90ac64058a16e9a4426e8924b8f9a51dabac255f450bb91a478af2c6760`，4 页）。

### 2.2 官方 PinMap 与 catalog 逐项对照

官方页 <https://docs.m5stack.com/en/core/PaperDIY_Complete_Kit>：

- FPC-I2S：1 G5(SCLK)、2 GND、3 PY_G0、4 G41(SYS_SDA)、5 G42(SYS_SCL)、6 GND、
  7 G2(LRCK)、8 G1(DSDIN)、9 G0(DOUT)、10 G45(MCLK)、11/12 3V3_AU
- FPC-SPI：1 G39(SCK)、2 GND、3 G21(CS)、4 G38(MOSI)、5 G40(MISO)、6 GND、
  7 PY_G4(RST)、8 G43(BUSY)、9 G44(IRQ)、10 PY_G1(SW)、11/12 3V3_L2

PR 的 `fpc_i2s` / `fpc_spi` positions 与 pin roles 完全一致；PMIC 侧分别映射到
`pmic.gpio0`、`pmic.gpio4`、`pmic.gpio1`，与页面的 PYG0/PYG4/PYG1 对应。

页面原文同时说明：电子纸与其驱动电路的供电由 M5PM1 的 `PYG2 (EPD_PWR)` 控制，
G46 (`BST_EN`) 控制升压使能。这与库内 `pmic_ops.hpp:192` 的
`// PaperDIY: M5PM1 GPIO2 drives EPD_PWR` 及 `paperdiy_power_on` 一致。

页面全文没有出现 `Grove` 或 `HY2.0`（0 次），与「PaperDIY 没有 Grove 口」相符；
`port_a` 的删除有依据。

## 3. 代码路径核验

| 事实 | 位置（PR head） |
| --- | --- |
| `Bus_EPD` 只在 `powerControl`/`init` 使用 `pin_oe` | `src/lgfx/v1/platforms/esp32/Bus_EPD.inl:86,96,123` |
| `gpio_hi/gpio_lo` 对负引脚直接跳过 | `src/lgfx/v1/platforms/esp32/common.hpp:240-241` |
| `pinMode` 对越界/负引脚提前返回 | `src/lgfx/v1/platforms/esp32/common.inl:665-668` |
| PaperDIY 的 EPD bus 传入生成值 | `src/board_detect/m5/esp32s3_construct.inl:653` |
| PaperDIY 的 `display_oe` 已生成 `-1` | `src/board_detect/m5/generated/esp32s3_board_data.hpp:437` |
| PMIC GPIO2 = EPD_PWR 的上电序列 | `src/board_detect/m5/pmic_ops.hpp:192-199` |

结论：`-1` 不会写到 GPIO 寄存器，也不会进入 IO_MUX 配置；`powerControl` 只是不再切换
OE，而 OE 在硬件上跟随 EPD_PWR。PaperS3 的 `display_oe` 仍为 45，行为未变。

## 4. 生成物与 host 检查

在 PR head 上：

```
node cli/spec.js check                 -> check passed: 63 board(s), 90 resolved combination(s)
node cli/spec.js emit-pintable         -> 55 boards / 4 targets
node cli/spec.js emit-wiring           -> 57 boards
git status --porcelain                 -> 空（生成物可逐字节重建）
npm run bundle                         -> git status 仍为空
npm test                               -> 221 tests / 221 pass / 0 fail / 0 skip
node cli/spec.js compare-pintable --m5unified <M5Unified#451>
                                       -> 55 board(s), 2750 value(s), 4 target(s) 全部一致
```

`npm test` 的 5 个 M5Unified 相关用例在未提供检出时会 skip；本次把 M5Unified#451 head
放在 `../../../M5Unified`，所以 221 项全部执行并通过（含 pin table 对比）。

生成表变化只有 PaperDIY 一行：`port_a_pin1/2` 42/41 → 255/255，`in_i2c_*` 仍为 42/41；
`esp32s3.inl` 对应 `{ board_M5PaperDIY, 42, 41, 255, 255 }`。

## 5. 虚拟设备 A/B 复现

目的：验证 `display_oe = -1` 在真实的 `Bus_EPD` 面板路径上不会破坏初始化、绘制与
`sleep()`/`wakeup()` 后的重绘。

- 工程：`code/`，ESP-IDF v6.1，esp32s3，16 MiB flash，8 MiB OPI PSRAM；
  程序打印编译期的 `wiring::paperdiy::display_oe`，绘制一页，`display.sleep()`，
  1 秒后 `wakeup()`，再绘一页，并在每步后输出标记。
- 镜像：base `6de3b51b…`（firmware `4aedcb74…`），PR head `6ee10a40…`
  （firmware `0187379a…`），均合并为 16 MiB 镜像后由 Device Service 写入 `paperdiy`。
- 结果（两次会话，同一程序）：

```
PR447 BOOT
I (190) M5GFX: [Autodetect] board_M5PaperDIY
PR447 init=1 board=34 width=540 height=960 display_oe=-1   # base 为 display_oe=45
E (230) gdma-link: gdma_link_mount_buffers(204): lli full start=0 need=1 avail=0
PR447 DRAW1_DONE
PR447 SLEEP_DONE
PR447 WAKE_DONE
PR447 DRAW2_DONE
```

- 末帧 PNG 两次完全相同：
  `b2e0d50618711095bb5366143a4709d432020275094e2af01bb29125d124d75e`（540x960，3599 B），
  画面为 sleep/wakeup 之后的 `AFTER WAKE` 页。
- QOM 面板计数一致：`scan-frames=73`、`latched-lines=39959`。
- `gdma-link ... lli full` 在 base 与 head 都出现一次（首次 flush 前），随后绘制和
  sleep/wakeup 重绘均完成，因此与本 diff 无关；本次未进一步定位（IDF v6.1 不在该 PR
  的 s3 CI 矩阵内）。

会话与证据：head `5fb2634c1ded482c89def0a1263c85a1`、base
`fa5ba15cd71f40bf849e4c74dbf13905`，均以 `purge=0` 停止并确认清理；证据 ZIP 的
SHA256 记录在 `evidence/virtual-device.txt`。原始 ZIP 与完整串口日志保留在评审机，
本记录只归档派生摘要、末帧和哈希。

## 6. 兼容性与影响面

- PaperS3：catalog 与生成值均未改动，`display_oe=45`。
- M5Unified：PaperDIY 的 `Ex_I2C` 消失、`In_I2C` 移到 port 1，是 M5Unified#451 的内容；
  M5GFX 侧只改变生成 pin table 的 `port_a_pin1/2`，两仓库被 `compare-pintable` 绑定。
  **合入顺序要求**：两边必须一起合；只合一边时该对比会不一致，而 M5GFX CI 在缺少
  M5Unified 检出时跳过对比，不会拦住。作者已在正文写明。
- 其他 board：`logical_terminals_12` 仅新增一个合法导轨值 `3v3_au`，不改变既有板子的
  端子编号或生成值；`check` 与全量测试均通过。
- 页面/编辑器：bundle 可从源重建，diff 为空；未在真实浏览器里点开验证。

## 7. 非阻塞建议

`m5paperdiy.json` 的 pin `5`（`conn:fpc_i2s.1`，G5/SCLK）是本次新增 FPC 引脚中唯一没有
`verified` 注解的一个；其余十个新引脚都写了 `roles: "datasheet"`。如果 G5-SCLK 与其它
引脚取自同一份官方 PinMap，建议补上以保持 provenance 一致。仓库里存在不带 `verified`
的 connector-only 引脚先例，所以这只是注解层面的建议，不影响生成结果。

## 8. 未覆盖项与风险

- 没有实体 PaperDIY 操作；作者自述的真机 sleep/wakeup 检查未由本次评审复跑。
- 虚拟设备不建模 `XOE` / `EPD_PWR` 网络、灰度波形和面板光学，因此无法在仿真中观测
  「G45 之前是否真的切换过 OE」；该结论来自原理图与官方 PinMap。
- 本机无 arduino-cli，Arduino 目标未本地复跑；仅引用上游 CI（40/40 pass）。
- 未在真实浏览器验证 board_spec editor 的分组展示（两个 FPC 共用 `group: "fpc"` 会在
  工具里作为一个连接器组展示）；这是展示层选择，不影响生成物。
- 上游 CI 结果取自 `gh pr checks` 汇总，未逐 job 复跑。

## 9. 回滚

改动是纯数据/生成物 + 一行生成常量；回滚即 revert 这一个 commit，
`display_oe` 回到 45，`port_a` 回到 Grove 定义。与 M5Unified#451 分开回滚会重新引入
pin table 不一致，需成对处理。
