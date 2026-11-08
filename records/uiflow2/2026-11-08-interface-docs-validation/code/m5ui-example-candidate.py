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
