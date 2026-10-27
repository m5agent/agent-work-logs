import M5
from M5 import *
from hardware import I2C, Pin
from unit import ENVUnit
M5.begin()
bus = I2C(0, scl=Pin(10), sda=Pin(9), freq=100000)
env = ENVUnit(i2c=bus, type=3)
t = env.read_temperature()
h = env.read_humidity()
p = env.read_pressure()
print("ISSUE4_VALUES", t, h, p)
M5.Display.fillScreen(0x101820)
M5.Display.setTextColor(0x00ff00)
M5.Display.drawString("ENV %.1fC %.0f%%" % (t,h), 8, 40)
print("ISSUE4_DONE")
