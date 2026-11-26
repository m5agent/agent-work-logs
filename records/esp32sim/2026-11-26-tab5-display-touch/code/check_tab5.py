"""Check the native documentation and firmware runs. Uses macOS Vision OCR."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zlib

root = Path(__file__).resolve().parent / "runs"
for label, text in {
    "final-gt-idle": ["Button Released"],
    "final-gt-press": ["Button Pressed"],
    "final-gt-release": ["Button Released"],
    "final-st-multi": ["Point 1 X:0160 Y:0400", "Point 2 X:0540 Y:0880"],
}.items():
    run = root / label
    png = run / "frame.png"
    data = png.read_bytes()
    assert (int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")) == (720, 1280)
    model = (run / "model.log").read_text()
    scans = re.search(r"DSI scans=(\d+)", model)
    assert scans and int(scans[1]) > 0, label
    ocr = subprocess.check_output([sys.argv[1], str(png)], text=True).split("\t", 1)[-1].strip()
    normalized = [re.sub(r"[^a-z0-9]", "", s.lower()) for s in text]
    document = re.sub(r"[^a-z0-9]", "", ocr.lower())
    assert all(s in document for s in normalized), (label, ocr)
    print(json.dumps({"case": label, "scans": int(scans[1]), "png_sha256": hashlib.sha256(data).hexdigest(),
                      "ocr": ocr.splitlines()}))
for label in ("final-253-release", "final-254-release"):
    run = root / label
    serial = (run / "console.log").read_text().splitlines()
    for marker in ("TAB5_REPL_DRAW 22", "TAB5_REPL_TOUCH 1 233 456", "TAB5_REPL_UP 0"):
        assert marker in serial, (label, marker)
    data = (run / "frame.png").read_bytes()
    assert data[37:41] == b"IDAT"  # esp-soc PNG writer emits one IDAT with filter 0
    raw = zlib.decompress(data[41:41 + int.from_bytes(data[33:37], "big")])
    expected = b"\x00" + bytes((16, 52, 82)) * 720
    assert raw == expected * 1280, label
    if label == "final-253-release":
        trace = (run / "model.log").read_text()
        for register, value in enumerate(("98", "81", "0c")):
            assert f"[dsi] read vc=0 dt=0x06 cmd=0x{register:02x}: [{value}]" in trace
    print(json.dumps({"case": label, "png_sha256": hashlib.sha256(data).hexdigest(), "rgb": [16, 52, 82],
                      "repl": [x for x in serial if x.startswith("TAB5_REPL_")]}))
