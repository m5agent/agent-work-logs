# Canonical native Xtensa source and build recipe

This recipe reconstructs the source used for the 2026-11-04 native build from
public sources. It does not require the locally named `75f1d24` object.
Source replay is verified; firmware execution is a separate Device Service
validation step. No C6 machine is present in this native source lane.

Public pins:

- Project: `https://github.com/m5agent/m5stack-esp-emulator.git`, commit
  `b41eba70eb61f7ddc5c41e0b981341064f9d1d1f`.
- QEMU: `https://github.com/espressif/qemu.git`, commit
  `40edccac415693c5130f91c01d84176ae6008566`.
- Project source lock: `scripts/qemu-wasm-build/sources.lock.json`, SHA-256
  `b9b137e52e77078cc67cb5b25433622f62d70cc3cbed8f92ee6699eed3389a1b`.
  Apply only its first `native_patch_count=47` entries, in listed order.
  The following WASM-only entries are excluded.
- Add board layers `0110` through `0119` in numeric order, then the 41 Unit
  layers in this exact order:
  `0120..0129, 0131, 0134, 0136, 0130, 0133, 0135, 0132, 0137..0154,
  0156, 0157, 0158, 0159, 0160, 0161`.

Use fresh, owned directories. Set `PROJECT` to the pinned project checkout,
`SOURCE` to a standalone pinned QEMU checkout, `BUILD` to a new empty build
directory, `DEPS_PREFIX` to the dependency prefix and `PYTHON_ENV` to the Python
environment. Preserve existing service state and existing source/build caches.

The published `0110` patch expects one extra blank line absent from the first
47-layer replay. The local canonical source contains that blank line. The
explicit normalization below changes no C token. Its generated empty
`subprojects/.wraplock` is also retained for exact source provenance. A full
comparison after these normalizations and `0110..0119` matched all **10,443**
canonical files, modes and symbolic-link targets, with zero differences.

```python
import hashlib, json, os, subprocess
from pathlib import Path

project = Path(os.environ["PROJECT"]).resolve()
source = Path(os.environ["SOURCE"]).resolve()
assert subprocess.check_output(
    ["git", "rev-parse", "HEAD"], cwd=source, text=True
).strip() == "40edccac415693c5130f91c01d84176ae6008566"
assert subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], cwd=source, text=True
).strip() == str(source)
lock = json.loads((project / "scripts/qemu-wasm-build/sources.lock.json").read_text())

def apply(path):
    for flags in (["--check"], [], ["--reverse", "--check"]):
        subprocess.run(["git", "apply", *flags, str(path)], cwd=source, check=True)

for row in lock["patches"][:lock["native_patch_count"]]:
    path = project / row["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
    apply(path)

path = source / "hw/xtensa/esp32s3.c"
old = "type_init(m5atoms3lite_machine_type_init);\n\n/* K130 M5Dial:"
text = path.read_text()
assert text.count(old) == 1
path.write_text(text.replace(old, old.replace("\n\n", "\n\n\n")))
(source / "subprojects/.wraplock").touch()

units = list(range(120, 130)) + [131, 134, 136, 130, 133, 135, 132]
units += list(range(137, 155)) + [156, 157, 158, 159, 160, 161]
assert len(units) == 41
for number in list(range(110, 120)) + units:
    paths = list((project / "patches/qemu-m5stack-peripherals").glob(f"{number:04d}-*.patch"))
    assert len(paths) == 1
    apply(paths[0])
```

QEMU's `.wrap` files pin its build subprojects:

| Subproject | Public repository | Commit |
| --- | --- | --- |
| dtc | `https://gitlab.com/qemu-project/dtc.git` | `b6910bec11614980a21e46fbccc35934b671bd81` |
| keycodemapdb | `https://gitlab.com/qemu-project/keycodemapdb.git` | `f5772a62ec52591ff6870b7e8ef32482371f22c6` |
| berkeley-softfloat-3 | `https://gitlab.com/qemu-project/berkeley-softfloat-3.git` | `b64af41c3276f97f0e181920400ee056b9c88037` |
| berkeley-testfloat-3 | `https://gitlab.com/qemu-project/berkeley-testfloat-3.git` | `e7af9751d9f9fd3b47911f51a5cfd08af256a9ab` |

Meson applies the checked-in `subprojects/packagefiles` overlays to the two
Berkeley projects. The recorded build reused copies of these exact commits and
overlays; all four repository worktrees had no tracked modifications.

Recorded host dependencies: Apple clang 21.0.0 on macOS arm64, Python 3.13.15,
Meson 1.12.1, Ninja 1.13.2, GLib 2.90.1, pixman 0.46.4, libslirp 4.9.5,
libgcrypt 1.11.0 and libgpg-error 1.51. The last two were reused as static
libraries from a dedicated dependency prefix; GLib/pixman/slirp were existing
host dependencies. This was a fresh QEMU object build with dependency reuse,
not a fresh build of every dependency.

```sh
export PKG_CONFIG="$DEPS_PREFIX/bin/pkg-config"
export PKG_CONFIG_PATH="$HOST_PKGCONFIG:$DEPS_PREFIX/lib/pkgconfig"
cd "$BUILD"
"$SOURCE/configure" --target-list=xtensa-softmmu --python="$PYTHON_ENV/bin/python" \
  --enable-gcrypt --enable-slirp --disable-docs --disable-werror \
  --disable-gtk --disable-gnutls --disable-nettle --disable-vnc --disable-curl \
  --disable-libssh --disable-zstd --disable-bzip2 --disable-curses \
  --disable-auth-pam --disable-dbus-display --disable-tpm \
  --disable-sdl --disable-cocoa --disable-png \
  --extra-cflags="-I$DEPS_PREFIX/include" \
  --extra-ldflags="$DEPS_PREFIX/lib/libgcrypt.a $DEPS_PREFIX/lib/libgpg-error.a"
"$PYTHON_ENV/bin/ninja" -j10 qemu-system-xtensa
xattr -c "$BUILD/qemu-system-xtensa"
codesign --force --sign - "$BUILD/qemu-system-xtensa"
codesign --verify "$BUILD/qemu-system-xtensa"
```

Recorded signed binary SHA-256:
`0e16a9bcd86b588dae6b3e3b523dfb8610a9eca37c50c141cce5f2ceb4612068`.
This identifies the actual artifact; debug paths, native toolchain and signing
can change a rebuilt binary hash. No byte-identical cross-host build guarantee
is made. Device Service should bind the binary and matching `SOURCE/pc-bios`
explicitly, then preserve firmware/session evidence and history during tests.
