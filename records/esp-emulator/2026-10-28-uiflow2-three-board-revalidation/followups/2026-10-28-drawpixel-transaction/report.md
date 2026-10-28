# Display.drawPixel framebuffer transaction 报告

## 背景

StopWatch UIFlow2 的 `M5.Display.drawPixel(x,y,color)` 返回成功，但 standalone
调用后 framebuffer capture 中没有目标像素。先前 trace 只看到 CO5300
CASET/RASET/RAMWR 窗头，且 `Panel_AMOLED` 要求偶数窗口，因此曾误判为
单像素模型限制。

## 根因

StopWatch `M5GFX::begin()` 在 PSRAM framebuffer 创建成功后会切到
`Panel_AMOLED_Framebuffer`。该 panel 的 `_auto_display` 只在
`Panel::endWrite()` 且嵌套计数归零时提交 dirty range。

Python `gfx_drawPixel()` 原实现：

```cpp
auto gfx = getGfx(...);
gfx->drawPixel(x, y);
return mp_const_none;
```

没有事务。因此 standalone 调用只修改 framebuffer，没有触发 display。显式
`startWrite()/endWrite()` 批次能够显示，证明 CO5300 本身和偶数窗口不是根因。

## 修复

`0024-display-draw-pixel-transaction`：

```cpp
gfx->startWrite();
gfx->drawPixel(x, y);
gfx->endWrite();
```

嵌套计数保证已有用户事务不会被提前 flush。

## 验证

同一程序：

1. 显式 `startWrite()`；
2. 写红/绿像素；
3. `endWrite()`；
4. 在事务外写青/白 standalone 像素。

StopWatch preimage 最终帧：

- 红/绿显式事务像素出现；
- 青/白 standalone 像素缺失；
- 相邻背景未改变。

三台候选最终帧均为 `FRAME_PASS`，检查 standalone 奇/偶像素、颜色和相邻
背景。StopWatch 实际中心颜色受面板色彩变换影响，但仍在 tolerance 8。

| 设备 | base SHA256 | status | frame SHA256 |
| --- | --- | --- | --- |
| StopWatch | `e13f7217…58ba` | `FRAME_PASS` | `d458f649…c974` |
| StickS3 | `2a20c3cf…ccb1` | `FRAME_PASS` | `2696612f…3858` |
| Core2 | `6ab3b5c7…c826` | `FRAME_PASS` | `dd42971e…49b3` |

Patch SHA256：
`18d55fc29f92bc701e6a9019aebe10d147e662488bbb8276198fc769589895e3`

Compiled source SHA256：
`d66d11b7748cf80714f59a0c7943aa2c4bbb15488acedd9d7df69af64e8fbca9`

## 回归

```text
PYTHONPATH=platform/tools:.work/py python3 -m unittest discover -s platform/tests -p 'test_*.py'
Ran 1347 tests in 113.841s
OK (skipped=1)

runtime_coverage / peripheral_catalog / qemu_profiles / project_snapshot: PASS
actionable contracts: 30/30 PASS
git diff --check: PASS
```

## 边界与回滚

候选为 incremental application relink，不是冷构建。物理屏幕、功耗、光学和
长期 DMA soak 未验证。回滚为撤销 `0024` candidate，不改默认 reference。
