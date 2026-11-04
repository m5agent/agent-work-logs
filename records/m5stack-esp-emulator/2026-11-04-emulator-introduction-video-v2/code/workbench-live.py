import M5
import time
M5.begin()
M5.Lcd.setRotation(1)
M5.Lcd.fillScreen(0x101B2E)
M5.Lcd.setTextSize(3)
M5.Lcd.setTextColor(0xFFFFFF)
M5.Lcd.drawString('LIVE CODE',24,30)
M5.Lcd.setTextSize(2)
M5.Lcd.drawString('UIFlow2 / RUN OK',24,72)
for i,color in enumerate([0xFF4D6D,0xFFB627,0x03C99A,0x0282CB]):
    M5.Lcd.fillRoundRect(24+i*72,120,55,78,12,color)
print('VIDEO_LIVE_CODE_READY')
while True:
    M5.update()
    time.sleep_ms(20)
