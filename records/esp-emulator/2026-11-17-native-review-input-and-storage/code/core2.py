import M5
import time
M5.begin()
print('TS_READY')
current = False
contacts = []
while True:
    M5.update()
    pressed = M5.Touch.getCount() > 0
    if pressed and not current:
        x, y, size, touch_id = M5.Touch.getTouchPointRaw(0)
        contacts.append((x, y))
        print('TS_DOWN_RAW', x, y)
    if not pressed and current:
        print('TS_UP')
        if len(contacts) == 2 and contacts[0] == contacts[1]:
            print('TS_DONE')
            break
    current = pressed
    time.sleep_ms(6)
