import M5
from M5 import *
from hardware import I2C, Pin
from hat import Servos8Hat
M5.begin()
i2c0 = I2C(0, scl=Pin(0), sda=Pin(8), freq=100000)
print("ISSUE5_SCAN", i2c0.scan())
servo = Servos8Hat(i2c0, 0x36)
servo.power_on()
servo.write_servo_angle(1, 90)
angle = servo.read_servo_angle(1)
print("ISSUE5_ANGLE", angle, "POWER", servo.get_power_state())
M5.Display.fillScreen(0x101820)
M5.Display.setTextColor(0x00ff00)
M5.Display.drawString("SERVO8 OK %d" % angle, 8, 40)
print("ISSUE5_DONE")
