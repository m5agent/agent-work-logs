"""Check Tab5 guest captures and emit a verdict for every matrix case."""
import array
from collections import Counter
import json
from pathlib import Path
import re
import statistics
import struct
import subprocess
import sys
from tempfile import TemporaryDirectory
import wave
import zlib

root = Path(__file__).resolve().parent
runs = root / "runs"
verdicts = []

def ensure(condition, detail):
    if not condition:
        raise ValueError(detail)

def runfile(label, file):
    return runs / label / file

def log(label):
    return runfile(label, "model.log").read_text()

def console(label):
    return runfile(label, "console.log").read_text()

def frame(label):
    path = runfile(label, "frame.png")
    png = path.read_bytes()
    ensure(struct.unpack_from(">II", png, 16) == (720, 1280), "wrong native dimensions")
    ensure(re.search(r"DSI scans=([1-9][0-9]*)", log(label)), "no DSI scanout")
    return path, png

def clip(label, degrees=0):
    path, _ = frame(label)
    with TemporaryDirectory() as d:
        preview = Path(d) / "capture.png"
        if degrees:
            subprocess.run(["sips", "-r", str(degrees), str(path), "--out", str(preview)], check=True, capture_output=True)
        else:
            preview = path
        return subprocess.check_output([sys.argv[1], str(preview)], text=True).split("\t", 1)[-1].strip()

def normalize(s):
    return re.sub("[^a-z0-9]", "", s.lower())

def screen(label, rotation, *want):
    seen = normalize(clip(label, rotation))
    ensure(all(normalize(msg) in seen for msg in want), f"{label}: absent expected text {want!r}")
    return f"{label}: " + ", ".join(want)

def case(name, check):
    try:
        verdict = dict(case=name, status="PASS", evidence=check())
    except (AssertionError, OSError, ValueError, subprocess.SubprocessError) as error:
        verdict = dict(case=name, status="FAIL", evidence=str(error))
    verdicts.append(verdict)
    print(json.dumps(verdict), flush=True)

def pixels(label):
    _, data = frame(label)
    part = data[8:]
    payload = bytearray()
    while part:
        n = int.from_bytes(part[:4], "big")
        if part[4:8] == b"IDAT":
            payload.extend(part[8:8+n])
        part = part[12+n:]
    return zlib.decompress(payload)

def button():
    for label, expected in [('idle', 'Button Released'), ('press', 'Button Pressed'), ('release', 'Button Released')]:
        screen("final-gt-" + label, 0, expected)
    pressed = pixels("final-gt-press")
    ensure(all(pressed != pixels("final-gt-" + state) for state in ("idle", "release")), "press did not change display pixels")
    return "GT911 press and release redraw the button"

def stock(version):
    label = f"stock-final-25{version}"
    screen(label + "-home", 90, "Offline", "WEB IDE", f"V2.5.{version}")
    ensure("[ppa] SRM " in log(label + "-home"), "missing guest SRM trace")
    screen(label + "-adc", 90, "PIN: 54", "PIN: 53", "OPEN")
    ensure(frame(label + "-home")[1] != frame(label + "-adc")[1], "ADC frame equals home")
    ensure(all(x in log(label + "-adc") for x in ("Touch(83, 755, true)", "Touch(83, 755, false)")), "missing touch markers")
    return "stock home and ADC control after touch"

def repl(version):
    label = f"final-25{version}-release"
    markers = ("TAB5_REPL_DRAW 22", "TAB5_REPL_TOUCH 1 233 456", "TAB5_REPL_UP 0")
    ensure(all(m in console(label).splitlines() for m in markers), "missing REPL or touch marker")
    ensure(pixels(label) == (b"\0" + bytes((16, 52, 82))*720)*1280, "unexpected REPL fill pixels")
    if version == 3:
        for reg, value in enumerate(("98", "81", "0c")):
            ensure(f"[dsi] read vc=0 dt=0x06 cmd=0x{reg:02x}: [{value}]" in log(label), "ILI9881C RX FIFO ID mismatch")
    return "exact full framebuffer and down/up" + ("; ILI9881C ID 98 81 0c" if version == 3 else "")

def pcm(path):
    with wave.open(str(root / path)) as file:
        out = array.array("h", file.readframes(file.getnframes()))
        ensure(file.getnchannels() == 1 and file.getsampwidth() == 2, "unexpected WAV format")
        return file.getframerate(), out

def speaker():
    screen("speaker-final-full", 0, "Speaker Test")
    rate, data = pcm("speaker-1-corrected/final-full.wav")
    ensure(rate == 48000 and len(data) >= 5*rate, "complete speaker PCM sequence missing")
    step = rate//100
    observed = []
    for second in range(5):
        votes = Counter()
        for offset in range(second*rate, (second+1)*rate, step):
            window = data[offset:offset+step]
            if sum(sample != 0 for sample in window) >= 225:
                votes[100*sum(a <= 0 < b for a, b in zip(window, window[1:]))] += 1
        most_common = votes.most_common(1)
        ensure(most_common and most_common[0][1] >= 4, f"second {second}: no sustained speaker tone")
        observed.append(most_common[0][0])
    ensure(observed == [10000, 8000, 6000, 4000, 2000], f"unexpected speaker tone sequence {observed!r}")
    return "five ordered speaker tones from 10 kHz to 2 kHz through codec-gated 48 kHz PCM"

def microphone():
    screen("mic-final-tone", 0, "REC", "Touch screen to play the record")
    ensure(frame("mic-final-tone")[1] != frame("mic-final-silence")[1], "tone and silence frames match")
    rate, data = pcm("mic-final-play.wav")
    freq = []
    for i in range(0, len(data) - rate//10, rate//10):
        window = data[i:i+rate//10]
        if max(map(abs, window)) > 300:
            freq.append(sum(x <= 0 < y for x, y in zip(window, window[1:])) * 10)
    ensure(len(freq) >= 10 and abs(statistics.median(freq)-733) <= 10, "playback lacks the injected 733 Hz tone")
    return "recording reacts to the input and reproduces 733 Hz on touch playback"

def raw_speaker():
    build = json.loads((root / "firmware/speaker-1/result.json").read_text())
    ensure(build["exit_code"] == 0, "original ##include fails compilation")
    return "unmodified documentation sketch compiled"

def rtc():
    values = re.findall(r"RTC\s+UTC\s+:2021/12/31 \(Fri\)\s+12:34:(\d+)", console("tab5-rtc"))
    ensure(len(set(values)) >= 2, "guest did not read a ticking RTC")
    return "RTC found and time advanced from the written date"

def wake(label, minimum_duration):
    trace = log(label)
    ensure("Touch(360, 640, false)" in trace, "missing sleep gesture")
    reached = re.search(r"emulated ([0-9.]+)s", trace)
    ensure(reached and float(reached[1]) >= minimum_duration, "wall-clock limit before the expected wakeup window")
    reset = re.findall(r"rst:(0x[0-9a-f]+)", console(label))
    ensure(any(r != "0x1" for r in reset) or len(reset) > 2, "no guest reboot after sleep gesture")
    return "guest restarted after sleep gesture"

def msc_sdk():
    trace = console("msc-final-sdk")
    ensure("MSC_PROBE_BEFORE_HOST" in trace, "probe stopped before the host installation call")
    ensure("MSC_PROBE_READY" in trace, "SDK host installation did not return")
    ensure("MSC_ENUMERATED" in trace and "MSC_READ_SECTOR_4_OK" in trace, "SDK MSC enumeration or sector read failed")
    return "SDK host stack enumerated and read MSC"

def sd():
    screen("tab5-sd", 90, "SD card detected", "write success", "PNG file 01 detected", "PNG file 02 detected")
    readback = subprocess.check_output(["mtype", "-i", str(root/"tab5-sd-run.img")+"@@1048576", "::WriteTest.txt"])
    ensure(readback == b"Hello, world! \nSD card write success! \n", "incorrect image bytes")
    for label, rgb in (("tab5-sd-render", (32, 89, 205)), ("tab5-sd-render-second", (180, 72, 32))):
        expected = (b"\0" + bytes(rgb)*720)*1280
        ensure(pixels(label) == expected, f"{label}: wrong PNG pixels")
    return "SPI SD mount, exact WriteTest.txt bytes, and two full-frame PNGs"

def rails():
    expected = ["TAB5_RAIL both PA=1 USB=1", "TAB5_RAIL no-pa PA=0 USB=1", "TAB5_RAIL neither PA=0 USB=0"]
    observed = [line for line in console("tab5-rail-output").splitlines() if line.startswith("TAB5_RAIL ")]
    ensure(observed == expected, "invalid expander-controlled PA/USB states")
    return "guest M5Unified power API observes both, USB only, and neither"

def wifi_scan():
    ensure("Wi-Fi sta scan done" in console("tab5-scan-ap"), "C6 did not complete the station scan")
    screen("tab5-scan-ap", 90, "Scan done")
    return "C6 scan results reached the Tab5 application screen"

def sdmmc():
    label = "tab5-sdmmc"
    ensure("TAB5_SDMMC_SPI_FILE_OK" in console(label), "SDMMC could not read the exact file written through SPI")
    reads = re.search(r"\[sdmmc\] [0-9]+ commands \(.*?\), ([0-9]+) bytes read", log(label))
    ensure(reads and int(reads[1]) >= 512 and "CMD17" in log(label), "no SDMMC sector read")
    frame(label)
    return f"same SPI-written card, read through SDMMC with {reads[1]} controller bytes"

def antenna():
    text = log("tab5-antenna")
    ports = re.findall(r"start addr 0x43 read=false\n\[i2c\]   write 0x05\n\[i2c\]   write (0x[0-9a-f]+)", text)
    ensure(ports and int(ports[-1], 16) & 1 == 0, "no internal-antenna select on expander P0")
    return "firmware selects internal antenna through expander P0"

def maker():
    screen("maker-final-prompt68", 90, "PRESS START")
    idle = normalize(clip("maker-final-idle", 90))
    ensure("trophies" in idle and "arcade" not in idle and "training" not in idle,
           "idle control is absent or has already entered the menu")
    screen("maker-final-gamepad", 90, "ARCADE", "TAG BATTLE", "TRAINING", "SETTING")
    for label in ("maker-final-idle", "maker-final-gamepad"):
        ensure("joystick connected:" in console(label), "HID was not enumerated")
    ensure(pixels("maker-final-idle") != pixels("maker-final-gamepad"), "input left the frame unchanged")
    ensure(log("maker-final-gamepad").count("ep=1 in 3/3 bytes") >= 4, "four HID reports were not transferred")
    return "HID enumeration, interrupt transfers and application menu change"

def msc():
    ensure("MSC_ENUMERATED" in console("msc-final-register") and "MSC_READ_SECTOR_4_OK" in console("msc-final-register"), "MSC enumeration/read marker absent")
    ensure(all(x in log("msc-final-register") for x in ('ep=2 out 31/31 bytes', 'ep=1 in 512/512 bytes', 'ep=1 in 13/13 bytes')), "missing BOT data phase")
    ensure(b"\0"+bytes((0,255,0))*10 in pixels("msc-final-register"), "missing green result frame")
    return "MSC descriptor enumeration, READ(10), sector and command status"

case("touch button", button)
case("touch multi ST7123", lambda: screen("final-st-multi", 0, "Point 1 X:0160 Y:0400", "Point 2 X:0540 Y:0880"))
case("touch multi GT911", lambda: screen("tab5-multi", 0, "Point 1 X:0160 Y:0400", "Point 2 X:0540 Y:0880"))
case("BMI270", lambda: screen("tab5-imu", 270, "Acc X = 0.50", "Acc Y = -0.25", "Gyr X = 125.00"))
case("microphone and replay", microphone)
case("speaker original build", raw_speaker)
case("speaker corrected", speaker)
case("battery and charging", lambda: screen("tab5-power", 270, "Bat Charging: Yes", "Bat Voltage: 7980mv", "Bat Level: 86"))
case("RTC local", rtc)
case("RTC SNTP", lambda: screen("tab5-sntp-ap", 90, "RTC found", "RTC UTC"))
case("wakeup five seconds", lambda: wake("tab5-wake-5s", 10))
case("wakeup next minute", lambda: wake("tab5-wake-min-retry", 65))
case("microSD", sd)
case("microSD native SDMMC", sdmmc)
case("Wi-Fi station", lambda: screen("tab5-wifi-ap", 90, "Connected to", "IP address"))
case("Wi-Fi scan", wifi_scan)
case("expander PA and USB rails", rails)
case("antenna select", antenna)
for version in (3, 4):
    case(f"UIFlow2 2.5.{version} stock", lambda version=version: stock(version))
    case(f"UIFlow2 2.5.{version} REPL", lambda version=version: repl(version))
case("Maker Fighter HID", maker)
case("MSC register probe", msc)
case("MSC SDK probe", msc_sdk)
sys.exit(any(c["status"] != "PASS" for c in verdicts))
