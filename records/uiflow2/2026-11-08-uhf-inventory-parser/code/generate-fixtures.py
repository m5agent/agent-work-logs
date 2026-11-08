"""Prepare synthetic UART vectors without running firmware or a device."""
import binascii
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def tag_crc(pc, epc):
    return binascii.crc_hqx(pc.to_bytes(2, 'big') + epc, 0xffff) ^ 0xffff


def frame(frame_type, command, payload):
    body = bytes((frame_type, command)) + len(payload).to_bytes(2, 'big') + payload
    return b'\xbb' + body + bytes((sum(body) & 255, 0x7e))


def inventory_frame(epc, pc=0x3000, rssi=0xc5):
    crc = tag_crc(pc, epc)
    return frame(2, 0x22, bytes((rssi,)) + pc.to_bytes(2, 'big') + epc + crc.to_bytes(2, 'big'))


def decode(raw):
    assert raw[0] == 0xbb and raw[-1] == 0x7e
    size = int.from_bytes(raw[3:5], 'big')
    assert len(raw) == size + 7
    assert sum(raw[1:-2]) & 255 == raw[-2]
    payload = raw[5:-2]
    value = {'frame_type': raw[1], 'command': raw[2], 'payload_length': size,
             'checksum_verified': True}
    if len(payload) >= 5:
        epc = payload[3:-2]
        pc = int.from_bytes(payload[1:3], 'big')
        crc = int.from_bytes(payload[-2:], 'big')
        value.update(rssi_raw=payload[0], pc=pc, epc_hex=epc.hex(),
                     crc_field=payload[-2:].hex(), tag_crc_verified=crc == tag_crc(pc, epc))
    return value


normal_epc = b'\x11' * 12
normal = inventory_frame(normal_epc)
embedded_epc = b'\x33' * 5 + b'\x7e' + b'\x33' * 6
embedded = inventory_frame(embedded_epc, pc=0x3400)
crc_epc = None
for suffix in range(65536):
    trial = b'\x55' * 10 + suffix.to_bytes(2, 'big')
    if tag_crc(0x3000, trial) >> 8 == 0x7e and b'\x7e' not in trial:
        crc_epc = trial
        break
assert crc_epc is not None
crc_frame = inventory_frame(crc_epc)
short = frame(2, 0x22, b'\x01\x02\x03\x04')
bad_checksum = normal[:-2] + bytes((normal[-2] ^ 1, normal[-1]))
error = frame(1, 0xff, b'\x15')
truncated = embedded[:14]
assert truncated[-1] == 0x7e

cases = [
    {'id': 'normal-inventory', 'response_hex': normal.hex(), 'expected_epc': normal_epc.hex(),
     'expected_baseline': 'EPC_MATCH', 'expected_candidate': 'EPC_MATCH', 'decoded': decode(normal)},
    {'id': 'embedded-7e-epc', 'response_hex': embedded.hex(), 'expected_epc': embedded_epc.hex(),
     'expected_baseline': 'ValueError buffer too small predicted from source, must observe',
     'expected_candidate': 'EPC_MATCH', 'decoded': decode(embedded),
     'issue_relation': 'Same declared length17 and first0x7e at wire index13 as the reported third-read shape. EPC bytes are synthetic repeated0x33.'},
    {'id': 'embedded-7e-crc', 'response_hex': crc_frame.hex(), 'expected_epc': crc_epc.hex(),
     'expected_baseline': 'ValueError buffer too small predicted from source, must observe',
     'expected_candidate': 'EPC_MATCH', 'decoded': decode(crc_frame)},
    {'id': 'synthetic-truncated-prefix', 'response_hex': truncated.hex(), 'expected_epc': '',
     'expected_baseline': 'ValueError buffer too small predicted from source, must observe',
     'expected_candidate': 'EMPTY_TIMEOUT', 'declared_payload_length': 17,
     'actual_received_bytes': len(truncated), 'complete_frame': False},
    {'id': 'short-valid-payload', 'response_hex': short.hex(), 'expected_epc': '',
     'expected_baseline': 'ValueError invalid format or buffer size predicted from source, must observe',
     'expected_candidate': 'EMPTY_NO_EXCEPTION', 'decoded': decode(short)},
    {'id': 'bad-checksum', 'response_hex': bad_checksum.hex(), 'expected_epc': '',
     'expected_baseline': 'EMPTY_NO_EXCEPTION', 'expected_candidate': 'EMPTY_TIMEOUT', 'checksum_valid': False},
    {'id': 'module-error-response', 'response_hex': error.hex(), 'expected_epc': '',
     'expected_baseline': 'EMPTY_NO_EXCEPTION', 'expected_candidate': 'EMPTY_NO_EXCEPTION', 'decoded': decode(error)},
    {'id': 'noise-before-valid', 'response_hex': '00117f' + normal.hex(), 'expected_epc': normal_epc.hex(),
     'expected_baseline': 'EPC_MATCH', 'expected_candidate': 'EPC_MATCH', 'leading_noise_hex': '00117f',
     'decoded_frame': decode(normal)},
]
for row in cases:
    row.update(recovery_response_hex=normal.hex(), recovery_expected_epc=normal_epc.hex(),
               initial_responses_hex=row['response_hex'] + ';' + normal.hex(),
               maximum_driver_wait_ms=5000, expected_inventory_command_hex='bb00220000227e', queries_per_session=2)

result = {'schema_version': 1, 'kind': 'prepared-not-executed', 'epc_origin': 'All EPC bytes synthetic, no issue reporter tag identity copied.',
          'normal_api': 'UHFRFIDUnit.inventory()',
          'constructor': 'UHFRFIDUnit(1, (1,2), verbose=True) on CoreS3 PORT.A; machine.UART id1 tx2/rx1',
          'fixture_semantics': 'One semicolon-separated chunk is injected atomically into UART RX FIFO for each complete guest command. Second chunk is next-query recovery, not timed fragmentation.',
          'crc_scope': 'Module8bit checksum independently summed. Synthetic PC+EPC tagCRC uses CRC16/GENIBUS (poly1021 initffff xoroutffff) via hostbinascii.crc_hqx. This is protocol fixture consistency, no physical RF measurement.',
          'constructor_wire_commands_expected': 0,
          'constructor_source_basis': 'JRD4035.__init__ only saves UART and allocates buffers; UHFRFIDUnit.__init__ creates real machine.UART and calls super().__init__; neither invokes command/_send.',
          'cases': cases,
          'blocked_cases': [{'id': 'timed-fragmented-frame', 'status': 'BLOCKED_FIXTURE',
                             'reason': 'Current UHF model injects one chunk atomically per command. Live responses-hex only replaces the pending queue and does not inject delayed continuation. A semicolon waits for another command and cannot prove same-query fragmentation.'}]}
a = bytes((68,)) * 12
b = bytes((85,)) * 12
c = bytes((102,)) * 12
first = inventory_frame(a) + inventory_frame(b)
next_response = inventory_frame(c)
cases.append({'id': 'queued-complete-frames', 'response_hex': first.hex(),
              'expected_epc': a.hex(), 'recovery_response_hex': next_response.hex(),
              'recovery_expected_epc': b.hex(),
              'initial_responses_hex': first.hex() + ';' + next_response.hex(),
              'expected_pending_after_first': 24})
if __name__ == '__main__':
    print(json.dumps({'synthetic_data_only': True, 'cases': cases}, indent=2))
