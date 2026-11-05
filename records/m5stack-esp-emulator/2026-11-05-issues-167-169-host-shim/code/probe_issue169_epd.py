import M5

M5.begin()
d = M5.Display
print("ISSUE169_ENUM", d.EPDMode.EPD_QUALITY, d.EPDMode.EPD_TEXT,
      d.EPDMode.EPD_FAST, d.EPDMode.EPD_FASTEST)
print("ISSUE169_ISEPD", d.isEPD())
print("ISSUE169_MODE_AFTER_BEGIN", d.getEpdMode())
d.setEpdMode(d.EPDMode.EPD_QUALITY)
print("ISSUE169_MODE_AFTER_QUALITY", d.getEpdMode())
d.setEpdMode(d.EPDMode.EPD_FASTEST)
print("ISSUE169_MODE_AFTER_FASTEST", d.getEpdMode())
d.setEpdMode(0)
print("ISSUE169_MODE_AFTER_ZERO", d.getEpdMode())
print("ISSUE169_EPD_DONE")
