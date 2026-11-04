import M5
import time
from hardware import MatrixKeyboard
M5.begin()
M5.Lcd.setRotation(0)
if M5.Lcd.width()!=240:M5.Lcd.setRotation(1)
M5.Lcd.setBrightness(255)
k=MatrixKeyboard()
c=M5.Lcd.newCanvas(240,135,16,True)
px=100;bx=120;by=80;vx=2;vy=-2;score=0;frame=0;flash=0
blocks=[1]*24
colors=[0xFF4E6A,0xFFB53D,0x00D1B4]
print('ARCADE_READY',M5.Lcd.width(),M5.Lcd.height())
while True:
 M5.update()
 while k.is_pressed():
  key=k.get_key()
  if key in (97,106):px=max(0,px-26)
  if key in (100,108):px=min(200,px+26)
  print('ARCADE_KEY',key,'PADDLE',px)
 bx+=vx;by+=vy
 if bx<4 or bx>236:vx=-vx
 if by<22:vy=abs(vy)
 if by>117:
  if px-5<bx<px+45:vy=-abs(vy);score+=1;flash=5
  elif by>139:bx=px+20;by=102;vy=-2
 for j in range(24):
  if blocks[j]:
   x=6+(j%8)*29;y=29+(j//8)*13
   if x-3<=bx<=x+25 and y-3<=by<=y+10:
    blocks[j]=0;vy=-vy;score+=10;flash=4;break
 if not sum(blocks):blocks=[1]*24
 c.fillRect(0,0,240,135,0x101B2E)
 c.fillRect(0,0,240,20,0x1C2D46)
 c.setTextSize(1);c.setTextColor(0xFFFFFF,0x1C2D46)
 c.drawString('M5 ARCADE',8,6);c.drawString('SCORE %03d'%score,164,6)
 for j in range(24):
  if blocks[j]:c.fillRoundRect(6+(j%8)*29,29+(j//8)*13,25,9,2,colors[j//8])
 c.fillCircle(int(bx),int(by),4,0xFFFFFF)
 c.fillRoundRect(px,119,40,6,3,0xFFFFFF if flash else 0x0282CB)
 c.setTextColor(0x7892AA,0x101B2E);c.drawString('A / D : MOVE',82,129)
 c.push(0,0)
 flash=max(0,flash-1);frame+=1
 time.sleep_ms(24)
