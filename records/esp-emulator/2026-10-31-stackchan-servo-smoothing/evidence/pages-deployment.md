# Pages deployment evidence

```text
URL: https://m5agent.github.io/m5stack-esp-emulator/
release: pages-preview-20261031-stackchan-smoothing
asset: public-site-preview-live.tar.gz
asset bytes: 151913554
asset SHA256: 1565afc97085cfa4f33760bf7655d9d19d43897f742f1615fca57dda62be2e5a
deployment run: 41158906682
deployment result: success

manifest SHA256: 22b90111ae80080ea5b7e9e73ae140af758a4ef60cfb4bd3286c0b61d4be4ae8
public.js: e89d98c4c83df2eed442c36ffcbb5dceaf0398b0cea5b9751592a3acce29bb8d
public-qemu-servo.js: 250e7229509a2a8f844087ad218e4b508def7af9e002b427336cbc0b903020ca
public-qemu-runtime.js: e4e8801cebaceebb24c3e317b072d9a0764ac6fbb377cc62580a69d4c3034741
public-qemu-instance.js: 04d360cfeb299bab3eaf7adb6f16e3f6f39832306cc2fdbb1e29de808e13d00c
WASM: 5d6c36bdafc1129c2652b5ba9422f3deb5ab170475748cea96fdc4cf9520a993
```

Public HTTPS CoreS3 guest:

```text
checks: 30/30 PASS
renderer: ANGLE (Apple, ANGLE Metal Renderer: Apple M4)
JavaScript errors: 0
service or local emulator requests: 0
```

The regular source-build workflow was invoked twice on the same main commit and
failed before browser acceptance at an upstream dependency download:
`The handshake operation timed out`. The prepared-site deployment is separately
recorded and is not presented as a regular source-build PASS.
