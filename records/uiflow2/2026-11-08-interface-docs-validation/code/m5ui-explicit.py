import time
import json

def emit(name, status, value=None, error=None):
    row = {"case": name, "status": status, "value": value}
    if error is not None:
        row["error"] = error
    print("DOC_TOP3 " + json.dumps(row))

def observe(name, fn):
    try:
        value = fn()
        emit(name, "OBSERVED", value if isinstance(value, (int, str, bool, list, tuple)) or value is None else str(value))
    except Exception as error:
        emit(name, "ERROR", error=repr(error))

import m5ui
import lvgl as lv
import M5
M5.begin()
M5.Lcd.setRotation(1)
emit("before_init_display", "OBSERVED", [M5.Lcd.getRotation(), M5.Lcd.width(), M5.Lcd.height()])
print("DOC_TOP3_M5UI_INIT_BEGIN")
m5ui.init()
print("DOC_TOP3_M5UI_INIT_RETURNED")
import M5
emit("after_init_display", "OBSERVED", [M5.Lcd.getRotation(), M5.Lcd.width(), M5.Lcd.height()])
page0 = m5ui.M5Page(bg_c=0xFFFFFF)
title = m5ui.M5Label("Title", x=10, y=10, font=lv.font_montserrat_24, parent=page0)
label = m5ui.M5Label("Text", x=10, y=50, font=lv.font_montserrat_14, parent=page0)
optional_font = lv.font_montserrat_20 if hasattr(lv, "font_montserrat_20") else lv.font_montserrat_18
value = m5ui.M5Label("123", x=10, y=80, font=optional_font, parent=page0)
page0.screen_load()
emit("label_text_readback", "OBSERVED", [title.get_text(), label.get_text(), value.get_text()])
emit("lv_display_size", "OBSERVED", [lv.display_get_default().get_horizontal_resolution(), lv.display_get_default().get_vertical_resolution()])
for _ in range(75):
    M5.update()
    time.sleep_ms(20)
print("DOC_TOP3_DONE M5UI")
time.sleep_ms(5000)
