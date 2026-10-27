import M5
from M5 import *
from hardware import I2C, Pin
from unit import NFCUnit
M5.begin()
i2c0 = I2C(0, scl=Pin(1), sda=Pin(2), freq=400000)
print("ISSUE8_SCAN", i2c0.scan())
nfc = NFCUnit(i2c0)
card = nfc.detect()
uid = card.uid_str if card else "none"
print("ISSUE8_DETECT", uid)
M5.Display.fillScreen(0x101820)
M5.Display.setTextColor(0x00ff00)
M5.Display.drawString("NFC %s" % uid, 35, 100)
print("ISSUE8_DONE")
