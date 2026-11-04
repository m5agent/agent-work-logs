import M5
import time
import math
M5.begin()
M5.Lcd.setRotation(0)
if M5.Lcd.width() != 320:
    M5.Lcd.setRotation(1)
M5.Lcd.setBrightness(255)
c = M5.Lcd.newCanvas(w=320, h=240, bpp=16, psram=True)
mode = 0
frame = 0
last_touch = False
print('M5_VIDEO_READY', M5.Lcd.width(), M5.Lcd.height())
while True:
    M5.update()
    touch = M5.Touch.getCount() > 0
    if touch and not last_touch:
        mode = 1 - mode
        print('M5_VIDEO_TOUCH', M5.Touch.getX(), M5.Touch.getY(), 'MODE', mode)
    last_touch = touch
    c.fillRect(0, 0, 320, 240, 0x081019)
    c.fillRect(0, 0, 5, 240, 0x0282CB)
    c.setTextSize(1)
    c.setTextColor(0x85A3B8, 0x081019)
    c.drawString('M5STACK / CORES3', 18, 14)
    c.fillCircle(285, 18, 3, 0x55E0BB)
    c.drawString('LIVE', 250, 14)
    c.setTextSize(2)
    c.setTextColor(0xFFFFFF, 0x081019)
    c.drawString('VIRTUAL DEVICE', 18, 34)
    c.drawLine(18, 59, 300, 59, 0x234253)
    color = 0x0282CB if mode == 0 else 0x52E0B5
    cx, cy = 86, 126
    for r in (30, 44, 58):
        c.drawCircle(cx, cy, r, 0x18374A)
    for n in range(16):
        a = n * math.pi / 8 + frame * 0.035
        x = cx + int(math.cos(a) * 44)
        y = cy + int(math.sin(a) * 44)
        c.fillCircle(x, y, 3 if n % 4 else 5, color)
    c.fillCircle(cx, cy, 21, color)
    c.setTextColor(0xFFFFFF, color)
    c.setTextSize(2)
    c.drawString('M5', cx-12, cy-8)
    c.setTextColor(0x85A3B8, 0x081019)
    c.setTextSize(1)
    c.drawString('DEMO SIGNAL', 166, 78)
    for x in range(120):
        if x % 30 == 0:
            c.drawLine(166+x, 95, 166+x, 151, 0x132C3C)
        if x:
            y0 = 122 + int(20 * math.sin((x-1) * .11 + frame * .10))
            y1 = 122 + int(20 * math.sin(x * .11 + frame * .10))
            c.drawLine(165+x, y0, 166+x, y1, color)
    c.drawLine(166, 151, 286, 151, 0x234253)
    c.drawString('INPUT', 166, 163)
    c.setTextColor(color, 0x081019)
    c.drawString('TOUCH ACTIVE' if mode else 'READY', 166, 177)
    c.fillRoundRect(18, 205, 282, 23, 6, 0x16324A if mode == 0 else 0x185546)
    c.setTextColor(0xD7EAF7, 0x16324A if mode == 0 else 0x185546)
    c.drawString('TAP TO CHANGE / UIFlow2', 45, 213)
    c.push(0, 0)
    frame += 1
    time.sleep_ms(40)
