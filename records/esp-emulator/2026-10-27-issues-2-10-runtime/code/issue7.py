import M5
from M5 import *
from hardware import I2C, Pin
from unit import Joystick2Unit
M5.begin()
i2c0 = I2C(0, scl=Pin(1), sda=Pin(2), freq=100000)
print("ISSUE7_SCAN", i2c0.scan())
a = Joystick2Unit(i2c0, 0x63)
b = Joystick2Unit(i2c0, 0x64)
a_xy = a.get_axis_position()
b_xy = b.get_axis_position()
print("ISSUE7_A_XY", *a_xy)
print("ISSUE7_B_XY", *b_xy, "BUTTON", b.get_button_status())
M5.Display.fillScreen(0x101820)
M5.Display.setTextColor(0x00ff00)
M5.Display.drawString("JOY2 OK %d,%d" % b_xy, 35, 100)
print("ISSUE7_DONE")
