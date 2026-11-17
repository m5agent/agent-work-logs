import M5
import time
from hardware import Keyboard
M5.begin()
kbd = Keyboard()
print('KB_READY')
combination = False
while True:
    kbd.update_key_list()
    kbd.update_keys_state()
    state = kbd.keys_state()
    if state.fn and len(state.word) and state.word[0] == 59 and not combination:
        combination = True
        print('KB_FN_SEMICOLON')
    if combination and not kbd.is_pressed():
        print('KB_DONE')
        break
    time.sleep_ms(12)
