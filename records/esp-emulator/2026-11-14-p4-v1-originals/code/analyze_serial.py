"""Offline bounded serial summary; no guest execution or raw output publication."""
def serial_observations(serial,issue):
    import re
    result={'rom_boots':serial.count('ESP-ROM:esp32p4'),
      'dwc_identity_assertions':len(re.findall(r'assert failed: usb_dwc_hal_init[^\n]*GSNPSID',serial)),
      'old_clic_instruction_faults':len(re.findall(r'(?i)MTVAL\s*:\s*(?:0x)?34602773',serial)),
      'panic_markers':len(re.findall(r'Guru Meditation|assert failed:|panic.ed',serial)),
      'micropython_banner_observed':bool(re.search(r'MicroPython\s+v\d',serial)),
      'application_ready':'NOT_ESTABLISHED','frame_and_touch':'NOT_ESTABLISHED',
      'usb_host_enumeration':'NOT_RUN','usb_host_transfer':'NOT_RUN'}
    if result['panic_markers'] or result['old_clic_instruction_faults'] or result['dwc_identity_assertions']:
        result['result']='FAIL'
    else:result['result']='REVIEW'
    return result

if __name__ == "__main__":
    import argparse,json
    from pathlib import Path
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("serial",type=Path);p.add_argument("--issue",choices=("188","226"),required=True)
    a=p.parse_args()
    print(json.dumps(serial_observations(a.serial.read_text(errors="replace"),a.issue),indent=2))
