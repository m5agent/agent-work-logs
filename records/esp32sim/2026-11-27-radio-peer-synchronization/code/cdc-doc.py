"""Generate an esp32sim USB host script for an exact UIFlow2 example."""
from hashlib import sha256
from pathlib import Path
import sys

source = Path(sys.argv[1]).read_bytes()
assert sha256(source).hexdigest() == sys.argv[2], "Unexpected UIFlow2 source hash"
print("attach", "cdc 3000", "cdc 300 \x03", "cdc 150 \x01", "cdc 20 src=bytearray()", sep="\n")
for i in range(0, len(source), 120):
    print(f"cdc 20 src.extend(bytes.fromhex('{source[i:i + 120].hex()}'))")
print("cdc 10 print('DOC_EXEC_BYTES',len(src));exec(src)\x04", "cdc 6500", sep="\n")
