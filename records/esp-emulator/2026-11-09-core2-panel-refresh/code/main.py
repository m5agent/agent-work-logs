import M5
import time

M5.begin()
M5.Lcd.fillScreen(0x112244)
M5.Lcd.drawString("Core2 touch probe", 8, 8)
print("CORE2_TOUCH_PROBE_READY", M5.Lcd.width(), M5.Lcd.height())
previous = None
while True:
    M5.update()
    count = M5.Touch.getCount()
    state = (count,)
    if count:
        raw = M5.Touch.getTouchPointRaw()
        state += (raw[0], raw[1], M5.Touch.getX(), M5.Touch.getY())
    if state != previous:
        print("CORE2_TOUCH_PROBE", time.ticks_ms(), *state)
        previous = state
    time.sleep_ms(10)
