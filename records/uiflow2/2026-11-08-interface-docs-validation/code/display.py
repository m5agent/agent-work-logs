import M5
import time
import json
M5.begin()
M5.Lcd.setRotation(0)
lcd = M5.Lcd

def emit(case, status, value=None, error=None):
    row = {"case": case, "status": status, "value": value}
    if error is not None:
        row["error"] = error
    print("DOC_TOP3 " + json.dumps(row))

CASES = [{'method': 'setTextColor', 'required': ['fgcolor'], 'full': {'fgcolor': 255, 'bgcolor': 16777215}}, {'method': 'setTextScroll', 'required': ['scroll'], 'full': {'scroll': False}}, {'method': 'setCursor', 'required': ['x', 'y'], 'full': {'x': 8, 'y': 8}}, {'method': 'clear', 'required': [], 'full': {'color': 16777215}}, {'method': 'fillScreen', 'required': [], 'full': {'color': 16777215}}, {'method': 'drawPixel', 'required': ['x', 'y'], 'full': {'x': 8, 'y': 8, 'color': 255}}, {'method': 'drawCircle', 'required': ['x', 'y', 'r'], 'full': {'x': 18, 'y': 18, 'r': 8, 'color': 255}}, {'method': 'fillCircle', 'required': ['x', 'y', 'r'], 'full': {'x': 18, 'y': 18, 'r': 8, 'color': 255}}, {'method': 'drawEllipse', 'required': ['x', 'y', 'rx', 'ry'], 'full': {'x': 18, 'y': 18, 'rx': 10, 'ry': 6, 'color': 255}}, {'method': 'fillEllipse', 'required': ['x', 'y', 'rx', 'ry'], 'full': {'x': 18, 'y': 18, 'rx': 10, 'ry': 6, 'color': 255}}, {'method': 'drawLine', 'required': ['x0', 'y0', 'x1', 'y1'], 'full': {'x0': 8, 'y0': 8, 'x1': 25, 'y1': 22, 'color': 255}}, {'method': 'drawRect', 'required': ['x', 'y', 'w', 'h'], 'full': {'x': 8, 'y': 8, 'w': 18, 'h': 16, 'color': 255}}, {'method': 'fillRect', 'required': ['x', 'y', 'w', 'h'], 'full': {'x': 8, 'y': 8, 'w': 18, 'h': 16, 'color': 255}}, {'method': 'drawRoundRect', 'required': ['x', 'y', 'w', 'h', 'r'], 'full': {'x': 8, 'y': 8, 'w': 20, 'h': 18, 'r': 4, 'color': 255}}, {'method': 'fillRoundRect', 'required': ['x', 'y', 'w', 'h', 'r'], 'full': {'x': 8, 'y': 8, 'w': 20, 'h': 18, 'r': 4, 'color': 255}}, {'method': 'drawTriangle', 'required': ['x0', 'y0', 'x1', 'y1', 'x2', 'y2'], 'full': {'x0': 18, 'y0': 5, 'x1': 8, 'y1': 23, 'x2': 28, 'y2': 23, 'color': 255}}, {'method': 'fillTriangle', 'required': ['x0', 'y0', 'x1', 'y1', 'x2', 'y2'], 'full': {'x0': 18, 'y0': 5, 'x1': 8, 'y1': 23, 'x2': 28, 'y2': 23, 'color': 255}}, {'method': 'drawArc', 'required': ['x', 'y', 'r0', 'r1', 'angle0', 'angle1'], 'full': {'x': 18, 'y': 18, 'r0': 12, 'r1': 8, 'angle0': 0, 'angle1': 90, 'color': 255}}, {'method': 'fillArc', 'required': ['x', 'y', 'r0', 'r1', 'angle0', 'angle1'], 'full': {'x': 18, 'y': 18, 'r0': 12, 'r1': 8, 'angle0': 0, 'angle1': 90, 'color': 255}}, {'method': 'drawEllipseArc', 'required': ['x', 'y', 'r0x', 'r1x', 'r0y', 'r1y', 'angle0', 'angle1'], 'full': {'x': 18, 'y': 18, 'r0x': 12, 'r1x': 8, 'r0y': 10, 'r1y': 6, 'angle0': 0, 'angle1': 90, 'color': 255}}, {'method': 'fillEllipseArc', 'required': ['x', 'y', 'r0x', 'r1x', 'r0y', 'r1y', 'angle0', 'angle1'], 'full': {'x': 18, 'y': 18, 'r0x': 12, 'r1x': 8, 'r0y': 10, 'r1y': 6, 'angle0': 0, 'angle1': 90, 'color': 255}}, {'method': 'drawQR', 'required': ['text', 'x', 'y', 'w'], 'full': {'text': 'D5', 'x': 8, 'y': 5, 'w': 24, 'version': 1}}, {'method': 'drawJpg', 'required': ['img'], 'full': {'img': '/flash/doc-fixture.jpg', 'x': 8, 'y': 8, 'maxW': 8, 'maxH': 8, 'offX': 0, 'offY': 0, 'scaleX': 1.0, 'scaleY': 1.0}}, {'method': 'drawPng', 'required': ['img'], 'full': {'img': '/flash/doc-fixture.png', 'x': 8, 'y': 8, 'maxW': 8, 'maxH': 8, 'offX': 0, 'offY': 0, 'scaleX': 1.0, 'scaleY': 1.0}}, {'method': 'drawBmp', 'required': ['img'], 'full': {'img': '/flash/doc-fixture.bmp', 'x': 8, 'y': 8, 'maxW': 8, 'maxH': 8, 'offX': 0, 'offY': 0, 'scaleX': 1.0, 'scaleY': 1.0}}, {'method': 'drawImage', 'required': ['img'], 'full': {'img': '/flash/doc-fixture.bmp', 'x': 8, 'y': 8, 'maxW': 8, 'maxH': 8, 'offX': 0, 'offY': 0, 'scaleX': 1.0, 'scaleY': 1.0}}, {'method': 'drawRawBuf', 'required': ['buf', 'x', 'y', 'w', 'h', 'len'], 'full': {'buf': '__RAW_RGB565_4X4__', 'x': 8, 'y': 8, 'w': 4, 'h': 4, 'len': 16, 'swap': False}}, {'method': 'print', 'required': ['text'], 'full': {'text': 'A', 'color': 255}}, {'method': 'newCanvas', 'required': ['w', 'h'], 'full': {'w': 8, 'h': 8, 'bpp': 16, 'psram': False}}]
emit("display_size", "OBSERVED", [lcd.width(), lcd.height(), lcd.getRotation()])
for case in CASES:
    name = case["method"]
    full = dict(case["full"])
    if name == "drawRawBuf":
        full["buf"] = bytearray([0xE0, 0x07] * 16)
    for missing in case["required"]:
        arguments = dict(full)
        arguments.pop(missing)
        try:
            getattr(lcd, name)(**arguments)
            emit(name + ".missing." + missing, "UNEXPECTED_ACCEPTED")
        except TypeError as error:
            emit(name + ".missing." + missing, "EXPECTED_TYPEERROR", error=repr(error))
        except Exception as error:
            emit(name + ".missing." + missing, "OTHER_ERROR", error=repr(error))
    try:
        result = getattr(lcd, name)(**full)
        emit(name + ".complete", "CALL_RETURNED", str(result))
        if name == "newCanvas":
            result.fillScreen(0x0000FF)
            result.push(8, 8)
    except Exception as error:
        emit(name + ".complete", "ERROR", error=repr(error))
    minimum = {key: full[key] for key in case["required"]}
    try:
        if "color" in full and name not in ("clear", "fillScreen", "print"):
            lcd.drawPixel(1, 1, 0x00FF00)
        result = getattr(lcd, name)(**minimum)
        emit(name + ".required_only", "CALL_RETURNED", str(result))
        if name == "newCanvas":
            result.fillScreen(0x00FF00)
            result.push(40, 8)
    except Exception as error:
        emit(name + ".required_only", "ERROR", error=repr(error))
# Deterministic final framebuffer for the four issue representative methods.
lcd.fillScreen(0xFFFFFF)
lcd.fillRect(20, 20, 80, 50, 0x0000FF)
lcd.drawPixel(130, 30, 0xFF0000)
lcd.drawPixel(131, 30)
lcd.drawCircle(180, 50, 20, 0x00FF00)
lcd.setTextColor(0x000000, 0xFFFFFF)
lcd.setCursor(20, 100)
lcd.print("DOC27")
emit("frame_oracle", "OBSERVED", {"blue_rectangle": [20,20,80,50], "red_pixels": [[130,30],[131,30]], "green_circle": [180,50,20], "label": "DOC27"})
print("DOC_TOP3_DONE DISPLAY")
time.sleep_ms(5000)
