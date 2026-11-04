import M5
import time
M5.begin()
M5.Lcd.setRotation(1)
M5.Lcd.setBrightness(255)
c=M5.Lcd.newCanvas(320,240,16,True)
colors=[0xFF4D6D,0xFFB627,0x03C99A,0x0282CB,0x9A65E8]
color=3
count=0
last=False
px=py=0
c.fillRect(0,0,320,240,0xF6F8FB)
c.fillRect(0,0,320,36,0x122434)
c.setTextColor(0xFFFFFF,0x122434)
c.setTextSize(2)
c.drawString('TOUCH STUDIO',12,11)
c.setTextSize(1)
c.setTextColor(0x526574,0xF6F8FB)
c.drawString('DRAW / COLOR / CLEAR',12,44)
for i,col in enumerate(colors):
 c.fillCircle(34+i*51,76,16,col)
c.fillRoundRect(274,61,35,30,5,0xDCE6EF)
c.setTextColor(0x30475A,0xDCE6EF)
c.drawString('CLR',281,72)
for x in range(14,310,16):
 for y in range(110,230,16):c.drawPixel(x,y,0xD7E2EA)
c.drawCircle(34+color*51,76,20,colors[color])
c.push(0,0)
print('TOUCH_STUDIO_READY 320 240')
while True:
 M5.update()
 touch=M5.Touch.getCount()>0
 if touch:
  x=M5.Touch.getX();y=M5.Touch.getY()
  if not last:
   count+=1
   print('TOUCH_STUDIO_INPUT',count,x,y)
  if y<100 and not last:
   if x>270:
    c.fillRect(0,101,320,139,0xF6F8FB)
    print('TOUCH_STUDIO_CLEAR')
   else:
    c.drawCircle(34+color*51,76,20,0xF6F8FB)
    color=max(0,min(4,(x-9)//51));c.drawCircle(34+color*51,76,20,colors[color]);print('TOUCH_STUDIO_COLOR',color)
  elif y>=105:
   if last and py>=105:
    for j in range(1,9):c.fillCircle(px+(x-px)*j//8,py+(y-py)*j//8,6,colors[color])
   else:c.fillCircle(x,y,6,colors[color])
  px=x;py=y;c.push(0,0)
 last=touch
 time.sleep_ms(10)
