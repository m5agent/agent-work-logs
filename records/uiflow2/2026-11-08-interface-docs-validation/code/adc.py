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

import M5
M5.begin()
import machine
import hardware
from hardware import ADC as HardwareADC, Pin as HardwarePin
from machine import ADC as MachineADC, Pin as MachinePin
emit("ADC_import_class_identity", "OBSERVED", HardwareADC is MachineADC)
emit("Pin_import_class_identity", "OBSERVED", HardwarePin is MachinePin)
for namespace, ADCClass, PinClass in (("hardware", HardwareADC, HardwarePin), ("machine", MachineADC, MachinePin)):
    for setting in ("omitted", "explicit-0DB", "explicit-11DB"):
        try:
            if setting == "omitted":
                adc = ADCClass(PinClass(6))
            else:
                attenuation = ADCClass.ATTN_0DB if setting == "explicit-0DB" else ADCClass.ATTN_11DB
                adc = ADCClass(PinClass(6), atten=attenuation)
            emit(namespace + ".constructor." + setting, "OBSERVED", repr(adc))
        except Exception as error:
            emit(namespace + ".constructor." + setting, "ERROR", error=repr(error))
            continue
        for method in ("read", "read_u16", "read_uv"):
            observe(namespace + "." + setting + "." + method, getattr(adc, method))
        observe(namespace + "." + setting + ".block", adc.block)
        observe(namespace + "." + setting + ".atten_setter", lambda: adc.atten(ADCClass.ATTN_11DB))
        observe(namespace + "." + setting + ".after_setter_repr", lambda: repr(adc))
emit("ADC_method_isolation_done", "OBSERVED", True)
print("DOC_TOP3_DONE ADC")
time.sleep_ms(5000)
