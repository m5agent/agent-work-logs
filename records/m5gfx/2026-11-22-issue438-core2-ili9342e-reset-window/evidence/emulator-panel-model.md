# Emulator ILI9342 panel sink: no post-reset NV reload model

Repository: `m5agent/m5stack-esp-emulator`
Model file: `hw/m5stopwatch/m5_spi_panel.c`, added by
`patches/qemu-m5stack-peripherals/0003-m5stack-shared-spi-full.patch` (line 3516)
and later refined by `0103`, `0167`, `0186`, `0187`; none of them add reset timing.

## Sleep In / Sleep Out is a boolean

`0003-m5stack-shared-spi-full.patch` (command dispatch):

```c
case 0x28: s->disp_on = false; s->dirty = true; break;
case 0x29: s->disp_on = true; s->dirty = true; break;
case 0x10: s->sleep = true; s->dirty = true; break;
case 0x11: s->sleep = false; s->dirty = true; break;
...
case 0x01:
    s->disp_on = false;
    s->sleep = true;
    s->madctl = 0;
    s->controller_invert = false;
    break;
```

Visibility is derived directly, without any time component:

```c
bool on = s->disp_on && !s->sleep;
```

## Realize starts asleep; there is no device reset callback

```c
static void m5_panel_realize(DeviceState *dev, Error **errp)
{
    M5SpiPanelState *s = M5_SPI_PANEL(dev);
    ...
    s->sleep = true;
```

`grep -c "qemu_register_reset\|DeviceReset\|dc->reset"` on the same model file: `0`.

## Consequence

- No 120 ms interval after a hardware reset during which commands are dropped.
- No "reset in Sleep Out returns to Sleep In" transition; a guest reset leaves
  `sleep`, `disp_on` and the framebuffer memory as they were.
- A Core2 firmware that resets the panel, sees its keys answer, and sends the init
  sequence is therefore always accepted by this model, independent of the elapsed
  time; the alternating blank of M5GFX#438 cannot be represented.

This is the reason no virtual-device reproduction is reported for #438. It is a
`runtime_model_gap`, not evidence that the reported hardware behaviour is wrong.
