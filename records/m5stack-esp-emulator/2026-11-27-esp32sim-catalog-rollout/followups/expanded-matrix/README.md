# Expanded Device Service matrix

Virtual-device validation exercised both runtimes on 322 Arduino docs
images and 31 checked-in UIFlow2 fixture images. These counts describe
the sampled boot and stop behavior. The Dial encoder sketch changed its
frame with three detents through either runtime. Keeping the existing
defaults reflects the remaining case-specific and deterministic repeat
checks.

The legacy Tab5 lane passed startup and cleanup after provisioning its
existing assets. Both AtomS3 GC9107 variants and the Core2 AXP192 variant
completed separate esp32sim stock sessions. The two AtomS3 frames changed
after their GPIO button input. Core2's recorded touch sample left the
frame unchanged.

[Per-device table](per-device.md) · [Run manifest](run.json)
