print("M5EMU_API_SWEEP_READY")
import sys, time, json, hashlib, binascii, io
import M5
CONFIG = {'lane': 'compatible', 'case': 'embedded-7e-epc'}
M5.begin()
def emit(label, value):
    print(label + " " + json.dumps(value))
def source_record(module):
    path = getattr(module, "__file__", None)
    if not path or not path.startswith("/flash/"):
        raise RuntimeError("subject module did not select VFS source: " + str(path))
    with open(path, "rb") as handle:
        data = handle.read()
    return {"path": path, "sha256": binascii.hexlify(hashlib.sha256(data).digest()).decode()}
if CONFIG["lane"] == "baseline":
    sys.path.insert(0, "/flash")
    for name in ("unit.uhf_rfid", "unit", "driver.jrd4035", "driver"):
        sys.modules.pop(name, None)
    from unit import UHFRFIDUnit
    import unit.uhf_rfid as wrapper_module
    import driver.jrd4035 as driver_module
    sources = {"driver": source_record(driver_module), "wrapper": source_record(wrapper_module)}
else:
    sys.path.insert(0, "/flash")
    import maintainer_candidate as candidate_module
    from maintainer_candidate import UHFRFIDUnit
    sources = {"candidate": source_record(candidate_module)}
emit("UHF_SOURCE", {"lane": CONFIG["lane"], "sources": sources, "sys_path": list(sys.path),
                    "class_module": getattr(UHFRFIDUnit, "__module__", None)})
unit = UHFRFIDUnit(1, (1, 2), verbose=True)
emit("UHF_CONSTRUCTED", {"lane": CONFIG["lane"], "case": CONFIG["case"]})
time.sleep_ms(3000)
for index in (0, 1):
    emit("UHF_CALL_BEGIN", {"index": index})
    started = time.ticks_ms()
    try:
        value = unit.inventory()
        emit("UHF_CALL_RESULT", {"index": index, "kind": "return", "value": value,
                                 "elapsed_ms": time.ticks_diff(time.ticks_ms(), started)})
    except Exception as error:
        trace = io.StringIO()
        sys.print_exception(error, trace)
        emit("UHF_CALL_RESULT", {"index": index, "kind": "exception", "error": str(error),
                                 "error_type": type(error).__name__,
                                 "trace": trace.getvalue(),
                                 "elapsed_ms": time.ticks_diff(time.ticks_ms(), started)})
emit("UHF_QUERIES_FINISHED", {"count": 2})
time.sleep_ms(1000)
print("UHF_CASE_DONE")
