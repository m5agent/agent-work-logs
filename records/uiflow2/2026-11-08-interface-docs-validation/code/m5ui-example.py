import M5
import m5ui
import lvgl as lv

M5.begin()
M5.Lcd.setRotation(0)
m5ui.init()
page0 = m5ui.M5Page(bg_c=0xFFFFFF)

title = m5ui.M5Label("Title", x=10, y=10, font=lv.font_montserrat_24, parent=page0)
label = m5ui.M5Label("Text", x=10, y=50, font=lv.font_montserrat_14, parent=page0)

optional_font = lv.font_montserrat_20 if hasattr(lv, "font_montserrat_20") else lv.font_montserrat_18
value = m5ui.M5Label("123", x=10, y=80, font=optional_font, parent=page0)
page0.screen_load()

# Observation-only wrapper appended by dsh-docs; the example bytes above are
# unchanged.  It adds finite M5.update calls, size/text readback and a unique
# completion marker only.
import time
import json as _json

for _ in range(100):
    M5.update()
    time.sleep_ms(20)
print("DOC_TOP3 EXAMPLE " + _json.dumps({
    "case": "example_display",
    "value": [M5.Lcd.getRotation(), M5.Lcd.width(), M5.Lcd.height()],
    "status": "OBSERVED",
}))
print("DOC_TOP3 EXAMPLE " + _json.dumps({
    "case": "example_lv_display_size",
    "value": [
        lv.display_get_default().get_horizontal_resolution(),
        lv.display_get_default().get_vertical_resolution(),
    ],
    "status": "OBSERVED",
}))
print("DOC_TOP3 EXAMPLE " + _json.dumps({
    "case": "example_label_text_readback",
    "value": [title.get_text(), label.get_text(), value.get_text()],
    "status": "OBSERVED",
}))
print("DOC_TOP3_DONE M5UI_EXAMPLE")
time.sleep_ms(2000)
