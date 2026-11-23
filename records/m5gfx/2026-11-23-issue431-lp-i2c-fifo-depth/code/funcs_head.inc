    static inline bool isLpPort(int i2c_port)
    {
#if LGFX_LP_I2C_NUM > 0
      return i2c_port >= LGFX_LP_I2C_PORT;
#else
      (void)i2c_port;
      return false;
#endif
    }

    /// Hardware FIFO depth of this port. The low power I2C has a shallower FIFO than the
    /// normal one, so this cannot be a single constant for the whole chip.
    /// ESP-IDF 6.0 moved the depths from soc_caps.h (SOC_*) to hal/i2c_ll.h (I2C_LL_*).
    static inline uint32_t getFifoLen(int i2c_port)
    {
#if LGFX_LP_I2C_NUM > 0 && defined ( SOC_LP_I2C_FIFO_LEN )
      if (isLpPort(i2c_port)) { return SOC_LP_I2C_FIFO_LEN; }
#elif LGFX_LP_I2C_NUM > 0 && defined ( I2C_LL_LP_FIFO_LEN )
      if (isLpPort(i2c_port)) { return I2C_LL_LP_FIFO_LEN; }
#elif LGFX_LP_I2C_NUM > 0
      // Falling back to the HP depth would overrun the shallower LP FIFO without any error.
 #error "LP I2C FIFO depth is unknown: neither SOC_LP_I2C_FIFO_LEN nor I2C_LL_LP_FIFO_LEN is defined"
#else
      (void)i2c_port;
#endif
#if defined ( SOC_I2C_FIFO_LEN )
      return SOC_I2C_FIFO_LEN;
#elif defined ( I2C_LL_FIFO_LEN )
      return I2C_LL_FIFO_LEN;
#else
      return 32;
#endif
    }
