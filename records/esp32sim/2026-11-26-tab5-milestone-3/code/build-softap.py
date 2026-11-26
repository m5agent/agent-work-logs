"""Extract the commented AP mode from the published STA/AP sketch."""
from pathlib import Path
import sys

source = Path(sys.argv[1]).read_text()
start = source.index("    // STA MODE")
ap = source.index("    // AP MODE", start)
end = source.index("\n}", ap)
ap_lines = source[ap:end].splitlines()
enabled = "\n".join(
    line.replace("    // ", "    ", 1) if line.startswith("    // ") else line
    for line in ap_lines[1:]
)
Path(sys.argv[2]).write_text(source[:start] + ap_lines[0] + "\n" + enabled + "\n" + source[end:])
