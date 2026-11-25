# Cardputer-ADV IR timing with a private instruction-clock profile

- Date `2026-11-25`
- Result `PARTIAL` for issue #258. Both exact private controller timing checks passed.
- Work type `issue`
- Source [Emulator issue #258](https://github.com/m5agent/m5stack-esp-emulator/issues/258) and [the official IR example](https://docs.m5stack.com/en/arduino/m5cardputer/ir_nec)
- Emulator source base `a5a48eceee172be037fe7c742eeff5f529f778d5`
- Environment Apple silicon macOS, Chromium `158.0.8127.37`, Emscripten `3.1.50`, Cardputer-ADV browser WASM virtual-device validation

## Result

Two private browser guests used single-thread TCG instruction counting with shift 5. The exact original portrait firmware and the official landscape firmware both produced the expected two NEC frames on GPIO44 within the unchanged decoder tolerance. In each run, the real controller reported 136 mark and space edges and the guest emitted the matching two commands through USB Serial/JTAG. The landscape framebuffer matched the previously observed readable layout.

Both guests exited cleanly, removed their engine iframe and left zero live workers. One browser driver recorded a failure because it still required six observed workers. The runtime created four pthreads and the browser observed all five actual targets, including the engine, close. Standard public profile admission and production timing remain open.

## Files

- [Report and reproduction](report.md)
- [Structured result](run.json)
- [Bounded guest, timing and cleanup evidence](evidence/ir-icount.summary.json)
- [Unchanged strict decoder](code/check_ledc_nec.py)
