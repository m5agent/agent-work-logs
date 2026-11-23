# Run inside an AIFlow StickS3 guest (MicroPython), where m5sync is a frozen module.
# Requires: the guest REPL and the m5sync module from the AIFlow firmware.
#
# This script keeps m5sync's real filesystem, MD5 and retry logic; only the HTTP
# transport is replaced with an in-memory response so the case is deterministic.
#
# Case A: duplicated devicePath (the AIFlow #6 symptom) -> ENOENT x3, Failed 50%.
# Case B: corrected devicePath                   -> downloaded, Success 100%.
#
# Set CASE and run the script once per capture. Case A removes the target app
# file first so the duplicated parent path is genuinely absent (ENOENT); running
# Case A after Case B would otherwise give ENOTDIR instead.
CASE = "A"  # "A" or "B"

import binascii
import hashlib
import os
import m5sync.sync as s

APP_NAME = "My_Project_1795168094430.py"
OTA_PATH = "main_ota_temp.py"
DUP_PATH = "apps/%s/%s" % (APP_NAME, APP_NAME)
FIXED_PATH = "apps/%s" % APP_NAME

OTA = b"# ota placeholder\n" * 114 + b"#" * 13          # 2065 bytes
APP = b"# sync probe\n" * 158 + b"#" * 11                # 2065 bytes
H_OTA = binascii.hexlify(hashlib.md5(OTA).digest()).decode()
H_APP = binascii.hexlify(hashlib.md5(APP).digest()).decode()


class _Raw:
    def __init__(self, data):
        self.data = data
        self.offset = 0

    def read(self, size):
        chunk = self.data[self.offset:self.offset + size]
        self.offset += len(chunk)
        return chunk


class _Response:
    status_code = 200
    headers = {"Content-Length": str(len(APP))}
    raw = _Raw(APP)

    def close(self):
        pass


def _fake_get(url, stream=False):
    print("PROBE_GET", url)
    return _Response()


def run_case(label, app_device_path):
    print("PROBE_CASE", label, app_device_path)
    records = [
        {
            "devicePath": OTA_PATH,
            "url": "http://fixture.invalid/" + OTA_PATH,
            "name": OTA_PATH,
            "md5": H_OTA,
            "size": len(OTA),
        },
        {
            "devicePath": app_device_path,
            "url": "http://fixture.invalid/" + APP_NAME,
            "name": APP_NAME,
            "md5": H_APP,
            "size": len(APP),
        },
    ]

    view = s.M5Sync()
    view._view.set_total_size(len(OTA) + len(APP))
    view._view.on_view()
    error = view.process_files([], records)
    print("PROBE_ERR", repr(error))
    if error:
        view._view.on_failed()
    else:
        view._view.on_success()


# Make the first record "already present" so progress reaches 50% before the
# app record is processed, matching the reported log (2 files, 4130 bytes).
handle = open("/flash/" + OTA_PATH, "wb")
handle.write(OTA)
handle.close()

if CASE == "A":
    try:
        os.remove("/flash/apps/" + APP_NAME)
    except OSError:
        pass

s.requests.get = _fake_get
if CASE == "A":
    run_case("A-duplicated", DUP_PATH)
else:
    run_case("B-corrected", FIXED_PATH)
