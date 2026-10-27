import M5
from M5 import *
from hardware import I2C, Pin
from unit import EncoderUnit, Servos8Unit
M5.begin()
enc_i2c = I2C(0, scl=Pin(1), sda=Pin(2), freq=100000)
srv_i2c = I2C(1, scl=Pin(8), sda=Pin(9), freq=100000)
print("ISSUE6_PORT_A", enc_i2c.scan())
print("ISSUE6_PORT_B", srv_i2c.scan())
encoder = EncoderUnit(enc_i2c, 0x40)
servos = Servos8Unit(srv_i2c, 0x25)
servos.set_mode(3, 0)
servos.set_servo_angle(90, 0)
angle = servos.get_servo_angle(0)
print("ISSUE6_ENCODER", encoder.get_rotary_value(), "ANGLE", angle)
M5.Display.fillScreen(0x101820)
M5.Display.setTextColor(0x00ff00)
M5.Display.drawString("8SERVOS OK %d" % angle, 40, 100)
print("ISSUE6_DONE")
