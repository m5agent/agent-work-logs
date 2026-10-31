# Native Device Service evidence

- Exact firmware was uploaded through `/api/v1/artifacts` and normalized through
  `/api/v1/firmware/import`.
- Session reached `running`.
- Serial contained `SERVO ready zeroX=460 zeroY=620 torque=1`,
  `StackChan auto-dance started` and continuous dance cues.
- Retained native frame SHA256:
  `f6f0667a6302e2d7ceeab731ad0f450adc23d3f1f30244a75826fe39586b5080`.
- Retained native evidence ZIP SHA256:
  `63a90fa8196f4a5775e82c580d01d2d23777810af422594af3b1a7c053a9e841`.
- The session was stopped with `purge=0` and terminal history was re-read.
- The native QEMU build used for this audit did not expose `/machine/scs_servo`;
  SCS presentation evidence is therefore attributed only to the matching
  browser-WASM harness.
