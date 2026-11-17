import M5
import time
M5.begin()
print('SK_READY')
prev_b = False
started = None
both = False
while True:
    M5.update()
    a = M5.BtnA.isPressed()
    b = M5.BtnB.isPressed()
    if M5.BtnA.wasDoubleClicked():
        print('SK_A_DOUBLE')
    if a and b and not both:
        both = True
        print('SK_AB_OVERLAP')
    if b and not prev_b:
        started = time.ticks_ms()
    if not b and prev_b and started is not None:
        elapsed = time.ticks_diff(time.ticks_ms(), started)
        print('SK_B_RELEASE_MS', elapsed)
        if 4800 < elapsed < 5200:
            print('SK_DONE')
    prev_b = b
    time.sleep_ms(8)
