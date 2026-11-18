    static bool lp_pads_accepted(const gpio_num_t sda, const gpio_num_t scl)
    {
      if (!rtc_gpio_is_valid_gpio(sda) || !rtc_gpio_is_valid_gpio(scl)) { return false; }
 #if !defined ( LGFX_LP_GPIO_MATRIX ) && defined ( LP_I2C_SDA_IOMUX_PAD ) && defined ( LP_I2C_SCL_IOMUX_PAD )
      // Without the LP GPIO matrix the controller reaches one fixed pair only.
      if (sda != LP_I2C_SDA_IOMUX_PAD || scl != LP_I2C_SCL_IOMUX_PAD) { return false; }
 #endif
      return true;
    }
