import collections
import hashlib
import json
from pathlib import Path
import re
import sys

base, out = map(Path, sys.argv[1:3])
def identity(name):
    data = (base / name).read_bytes()
    return {'sha256': hashlib.sha256(data).hexdigest(), 'bytes':len(data)}

def markers(name, patterns):
    data = (base / name).read_text(errors='replace')
    return {label:len(re.findall(pattern, data)) for label, pattern in patterns.items()}

def profile(prefix):
    result = {}
    for mode in ('jit','interpreter'):
        name = f'{prefix}-{mode}'
        output = (base / (name+'.out')).read_text()
        clocks = re.search(r'core0 (\d+) \+ core1 (\d+) insns in [0-9.]+s wall = ([0-9.]+) Minsn/s; emulated ([0-9.]+)s', output)
        wall = re.search(r'^real ([0-9.]+)$', output, re.M)
        result[mode] = {
            'wall_seconds':float(wall.group(1)),
            'guest_instructions':int(clocks.group(1)) + int(clocks.group(2)),
            'guest_seconds':float(clocks.group(4)),
            'guest_mips':float(clocks.group(3)),
            'frame':identity(name+'.png'),
            'serial':identity(name+'.serial'),
            'profile_capture':identity(name+'.out'),
        }
    return result

starts = list(map(json.loads, (base/'reset.private.jsonl').read_text().splitlines()))
fenced = list(map(json.loads, (base/'reset-fenced.private.jsonl').read_text().splitlines()))
for row in starts + fenced:
    row.pop('serial_tail', None)

radio = base/'zigbee-pair/radio.ndjson'
packets = list(map(json.loads, radio.read_text().splitlines()))
radio_tx = collections.Counter(packet['node'] for packet in packets if packet['type']=='tx')
leds = [{k:p[k] for k in ('node','t','rgb')} for p in packets if p['type']=='leds' and p['node']==1]
tab5_trace = (base/'tab5-dsi.model').read_text()
scans, reads = map(int, re.search(r'DSI scans=(\d+) reads=(\d+)', tab5_trace).groups())
result = {
    'radio':{
        'inputs':json.loads((base/'zigbee-pair/inputs.json').read_text()),
        'trace':identity('zigbee-pair/radio.ndjson'),
        'tx_counts':radio_tx,
        'node_1_led_transitions':leds,
        'receiver_guest_markers':markers('zigbee-pair/node1.log', {
            'joined':r'Joined network successfully',
            'messages':r'Received message: endpoint\(10\), cluster\(0x6\)',
            'light_on':r'Light sets to On',
            'light_off':r'Light sets to Off',
        }),
        'receiver_serial':identity('zigbee-pair/node1.log'),
        'joined_at_guest_seconds':float(re.search(r'^([0-9.]+) .*Joined network successfully',
            (base/'zigbee-pair/node1.log').read_text(), re.M).group(1)),
    },
    'tab5_dsi':{
        'scans':scans,'reads':reads, 'trace':identity('tab5-dsi.model'),
        'file_sha256':identity('originals/tab5-v254.bin')['sha256'],
        'touch':[83,755], 'touch_guest_ms':[7000,7450], 'frame':identity('tab5-dsi.png'),
        'http_observation':'Offline home then ADC page with pin rows',
    },
    'maker_fighter':{},
    'browser_reset':{
        'site_manifest_sha256':'38cf12dcfdb8d9cdc3ecab92d7fa3cc568cf75a652a9048033031d738cadf1dd',
        'wasm_sha256':'4c61df24a2028d4d56f66c6aea599848eb5be6ad15c70a181130f6dcc257cce8',
        'first_probe':starts, 'fenced_repeat':fenced,
    },
    'cli_profile':{'cores3_doc_touch':profile('profile'), 'core2_stock':profile('core2')},
}
for arm in ('gamepad-idle','gamepad'):
    name = f'maker-{arm}'
    result['maker_fighter'][arm] = {
        'frame':identity(name+'.png'),
        'serial':identity(name+'.serial'),
        'model_log':identity(name+'.model'),
        'interrupt_endpoint_reports':markers(name+'.model',{'in_3_bytes':r'ep=1 in 3/3 bytes'})['in_3_bytes'],
        'enumeration':markers(name+'.serial',{'joystick':r'joystick connected'}),
        'observed_screen_words':(['TROPHIES'] if arm=='gamepad-idle'
                                  else ['ARCADE','TAG BATTLE','TRAINING','SETTING','TROPHIES']),
    }
paper=base/'paper-repro.private.json'
if paper.exists():
    result['paper_factory']=json.loads(paper.read_text())
out.write_text(json.dumps(result,indent=2)+'\n')
