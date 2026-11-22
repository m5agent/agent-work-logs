# M5GFX `28d4794` (v0.3.0) code snippets

Collected 2026-11-22 from a clean clone of `m5stack/M5GFX` at
`28d47949bdc84f30881623476f555398e2194313` with `git show`. Line numbers are
the pristine file's.

## src/board_detect/m5/esp32_d0wdq6.inl:58-72 (Core2 descriptor, i2c_reset(1, 10))
```cpp
  static constexpr board_desc_t desc_core2 = {
    { id(lgfx::board_M5StackCore2), "M5StackCore2", 0 },
    i2c_power(400000, core_pmic_variants, pmic_ops::core2_devices, 5, 20), i2c_reset(1, 10),
    shared_sd(wiring::core2::shared_sd_sclk, wiring::core2::shared_sd_mosi,
              wiring::core2::shared_sd_miso, wiring::core2::shared_sd_sd_cs,
              wiring::core2::shared_sd_other_cs),
    display_pins(wiring::core2::display_sclk, wiring::core2::display_mosi,
                 wiring::core2::display_miso, wiring::core2::display_dc,
                 wiring::core2::display_cs, wiring::core2::display_rst,
                 wiring::core2::display_busy),
    pins(wiring::core2::hold),
    internal_i2c(wiring::core2::internal_i2c_sda, wiring::core2::internal_i2c_scl,
                 wiring::core2::internal_i2c_port),
    options(generated_options::core2::names), pins(wiring::core2::hold),
  };
```

## src/board_detect/m5/esp32_d0wdq6.inl:486-517 (observe_core_panel)
```cpp
      ESP_LOGD("board_detect_m5", "Core panel observation after SD SPI preparation");
      const auto& display = desc_core2.display;
      const std::int8_t signals[] = {
        display.dc, display.sclk, display.mosi, display.miso
      };
      prepare_detail::pin_level(display.cs, true);
      prepare_detail::pin_level(desc_core2.sd.sd_cs, true);
      soft_spi_t bus(display.sclk, display.mosi, display.mosi, display.dc);
      bus.init();
      // Without reset, leave the same 120 ms window for a waking panel.
      variant = identify_panel_variant(bus, display.cs, keys,
                                            ctx.allow_reset ? 1 : 120);
      if (ctx.allow_reset)
      {
        prepare_detail::i2c_scope_t i2c(*ctx.transaction, ctx.probe_port,
                                         desc_core2.internal_i2c);
        if (!i2c.opened || !prepare_reset(desc_core2, result, ctx, i2c.port))
        {
          ctx.transaction->restore_to_snapshot(signals);
          return false;
        }
        std::uint32_t after_keys[4] = {};
        const auto after = identify_panel_variant(bus, display.cs, after_keys,
                                                  120, variant != panel_variant_t::e);
        if (after != panel_variant_t::unknown)
        {
          variant = after;
          for (int i = 0; i < 4; ++i) { keys[i] = after_keys[i]; }
        }
      }
      return true;
    }
```

## src/board_detect/m5/board_registry.inl:170-183 (poll is a ceiling)
```cpp
    panel_variant_t identify_panel_variant(soft_spi_t& bus, int pin_cs,
                                           std::uint32_t keys[4], std::uint32_t poll_ms,
                                           bool try_c_key = true)
    {
      auto variant = probe_panel_variant(bus, pin_cs, keys, try_c_key);
      const auto started = io::millis();
      while (variant == panel_variant_t::unknown && poll_ms)
      {
        io::delay_ms(1);
        variant = probe_panel_variant(bus, pin_cs, keys, try_c_key);
        if (io::millis() - started >= poll_ms) { break; }
      }
      return variant;
    }
```

## src/board_detect/prepare.inl:505-513 (post-release delay)
```cpp
          ESP_LOGW("board_detect",
                   "reset_release stopped after board confirmation: op=%u status=%u native=%d",
                   static_cast<unsigned>(release_result.failed_index),
                   static_cast<unsigned>(release_result.status), 0);
        }
        if (ok || retain_confirmed_board) { io::delay_ms(reset.post_ms); }
      }
      if (retain_confirmed_board) { ok = true; }
    }
```

## src/M5GFX.cpp:997-1003 (no second reset)
```cpp
  bool M5GFX::_init_adopted_panel(bool use_clear)
  {
    // Detection and preparation have already handled reset. Construction
    // and panel initialisation must not pulse it again.
    if (false == LGFX_Device::init_impl(false, use_clear)) {
      return false;
    }
```

## src/lgfx/v1/panel/Panel_ILI9342.hpp:86-101 (ILI9342E init list)
```cpp
      static constexpr uint8_t list0[] =
      {
          CMD_SETEXTC_E, 1, 0x01,          // Turn on the external command
          0xD5       , 1, 0x00,
          0xB1       , 1, 0x22,
          0xC8       , 1, 0x38,            // Power Control 3 (VCOM)
          0xCB       , 1, 0x1C,
          0xC9       , 1, 0x1A,
          0xCA       , 1, 0x1A,
          0xB7       , 4, 0x5A,0x41,0x11,0x19,
          CMD_GMCTRP1_E,15, 0x04,0x08,0x11,0x06,0x12,0x07,0x3A,0x76,0x47,0x07,0x0F,0x0A,0x11,0x19,0x05,
          CMD_GMCTRN1_E,15, 0x02,0x03,0x07,0x06,0x12,0x07,0x36,0x5F,0x48,0x06,0x10,0x0C,0x16,0x14,0x09,
          CMD_IDMOFF , 0,
          CMD_DISPON , 0,
          CMD_SLPOUT , 0 + CMD_INIT_DELAY, 120,    // Exit sleep mode
          0xFF,0xFF, // end
```

## src/lgfx/v1/panel/Panel_Device.inl:196-218 (delay is after the command)
```cpp
    {                // For each command...
      uint8_t cmd = *addr++;
      uint8_t num = *addr++;   // Number of args to follow
      if (cmd == 0xFF && num == 0xFF) break;
      writeCommand(cmd, 1);  // Read, issue command
      _bus->flush();
      uint_fast8_t ms = num & CMD_INIT_DELAY;       // If hibit set, delay follows args
      num &= ~CMD_INIT_DELAY;          // Mask out delay bit
      if (num)
      {
        do
        {                   // For each argument...
          writeData(*addr++, 1);  // Read, issue argument
          _bus->flush();
        } while (--num);
      }
      if (ms)
      {
        ms = *addr++;        // Read post-command delay time (ms)
        delay( (ms==255 ? 500 : ms) );
      }
    }
  }
```
