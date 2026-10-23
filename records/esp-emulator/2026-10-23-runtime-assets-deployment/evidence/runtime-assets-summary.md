# Runtime asset baseline

- `.gitignore` excludes the complete `.work/` directory.
- `git ls-files '.work/**'` returns no tracked runtime files.
- The reference workstation currently reports `.work/` at approximately 48 GiB.
- Major contents include the patched QEMU build tree, QEMU C6 build tree,
  ESP-IDF, Python dependencies, ROM/eFuse files, firmware caches and generated
  test artifacts.
- `.work/M5StopWatch-QEMU/` is approximately 1.3 GiB in this reference tree.
- `.work/esp-idf-v5.5.4/` is approximately 3.8 GiB in this reference tree.

These files are local runtime/build state. They are not a missing Git object,
and the source repository does not provide a one-command clean-clone bootstrap
for the complete runtime.
