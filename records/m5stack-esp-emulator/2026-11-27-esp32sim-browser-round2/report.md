# Browser WASM board parity

The candidate extends the service-parity pin 1bde80f2 with board construction and browser protocol changes. It uses the licensed Espressif ROM lock. The test binaries and sidecar are supplied to Chrome at run time. Public site exports omit those firmware images.

## Reproduction

Build the pinned runtime with `platform/tools/bootstrap_browser_runtime.py` and use `platform/tools/build_public_site.py` for an isolated mixed export. Pass the export URL through `M5_BROWSER_SITE` and run `node platform/tests/test_public_esp32sim_board_guest.mjs` for fixed fixtures. For additional local or uploaded fixtures, use the firmware environment variables and digests in that runner. It records guest output and actual Chrome DedicatedWorker targets before and after Stop. Start and capture values in these functional runs may reflect ordinary host load.

## Findings

- AtomS3R requires the LGA56 package value in the ESP32-S3 eFuse for M5GFX to select the AtomS3R panel path. Nesso N1 requires its QFN40, external Flash eFuse. Nesso verifies the touch read and native-sized panel update.
- PaperColor initially stalled within the old test budget. The extended run reaches ready, reports a 16,995 ms guest refresh and repaints after an input.
- The 2 and 8 MiB classic configuration passes the StickC Plus2 and Core2 fixed cases. Atom Matrix and Matrix v1.1 pass the 25-LED uniform-color sequence. Per-LED spatial order is outside that fixture.
- StamPLC A goes through the front I2C expander. StickT2 uses I2C encoder input, and M5Stick OLED pixels travel through SPI. The diagnostic images are distinct from stock.
- The camera fixtures observe five unique guest captures and a camera preview. VoiceS3R emits nonzero PCM. The Core2 fixture reads nonzero PCM after upload to the modeled I2S source.
- The Tab5 stock rev0 launcher receives the pinned C6 sidecar. The ADC selection marker changes after the GT911 tap. The P4 rev3 factory pairing is implemented. The rev3 stock launcher is NOT RUN.
- ADV completes 11 physical keyboard press and release pairs through the original KeyboardI2C FIFO decoder. This is evidence for the default esp32sim engine. The hosted QEMU UIFlow IRQ refusal remains a diagnostic.
- StackChan observed UART servo reads and writes before an intermittent servo Y write failure. The three body touch zones use a separate original-driver Si12T fixture.
- The AtomU and Echo diagnostic UIFlow2 images stalled near 0.5 guest seconds. Both Stop checks are recorded in the matching attempts. The original launcher defect is independent.

The summary files retain batch-specific hashes and include earlier failures. They omit raw UART logs, rendered images, Chrome target identifiers and local endpoints. Rollback is selecting the retained QEMU-WASM engine on a dual-engine board or redeploying the preceding immutable Pages artifact.
