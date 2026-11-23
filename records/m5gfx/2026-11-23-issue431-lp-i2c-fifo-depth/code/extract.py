import os
import subprocess

# Point this at a local M5GFX checkout.
REPO = os.environ.get('M5GFX_REPO', '/path/to/M5GFX')
INL = 'src/lgfx/v1/platforms/esp32/common.inl'


def src(ref):
    return subprocess.check_output(['git', '-C', REPO, 'show', f'{ref}:{INL}'], text=True)


def extract(ref):
    lines = src(ref).splitlines()
    start = next(i for i, l in enumerate(lines)
                 if l.strip() == 'static inline bool isLpPort(int i2c_port)')
    ret32 = next(j for j in range(start, len(lines)) if 'return 32;' in lines[j])
    end = next(k for k in range(ret32, len(lines)) if lines[k].strip() == '}')
    return '\n'.join(lines[start:end + 1])


for ref, name in (('452c15b', 'base'), ('origin/develop', 'head')):
    body = extract(ref)
    with open('funcs_%s.inc' % name, 'w') as f:
        f.write(body + '\n')
    print(ref, 'extracted', len(body.splitlines()), 'lines')
