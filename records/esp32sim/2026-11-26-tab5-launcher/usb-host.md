# Tab5 high-speed USB host virtual-device validation

On esp32sim `b760490f`, original Maker Fighter 1.4 enumerated a virtual
HID gamepad on P4's guest-hosted USB root port. Serial reported an HID
joystick with eight buttons. Four three-byte interrupt-IN reports moved
through the guest's descriptor DMA. The matched idle run showed PRESS
START. With the scripted button and axis reports the same application
showed ARCADE, TAG BATTLE, TRAINING and SETTING. The earlier HID attempt
enumerated and transferred its first report, then asserted because the
periodic descriptor index was reported as an early stop. The normal
completion now wraps the index to zero, while a short packet retains it.

A separate unchanged-controller path used the Arduino [MSC probe](code/msc-probe.ino)
to drive HPRT, EP0 enumeration and host QTDs directly. It read the device
and configuration descriptors, set its address and configuration, sent a
31-byte SCSI READ(10) CBW over bulk OUT, received a 512-byte sector over
bulk IN, and checked the matching 13-byte CSW. The frame turned green
and serial emitted MSC_ENUMERATED and MSC_READ_SECTOR_4_OK. A trial with
the M5Stack Arduino 3.2.5 USB Host library stopped in usb_host_install
before any HCD register traffic. MSC through that library remains
unverified. The supported target is a read-only volume.

## Reproduce

Build esp32sim-p4 at the above commit with release LTO disabled and eight
code-generation units, and build the probe using M5Stack Arduino 3.2.5,
FQBN m5stack:esp32:m5stack_tab5. Use the original m5stack-tab5 profile and
ESP32-P4 rev0 mask ROM. Pass the merged image with --flash-image and
capture --tft-png with --debug usb_otg.

- Maker Fighter paired runs use --max-seconds 7.5 and
  [gamepad.txt](code/gamepad.txt) or [gamepad-idle.txt](code/gamepad-idle.txt).
- The register-level MSC probe uses --max-seconds 4.9 and [msc.txt](code/msc.txt).

The model implements the tested P4 host descriptor-DMA routes.
Isochronous transfers, transaction translators, cycle-exact scheduling and
physical USB behavior remain outside this evidence. Revert b760490f to
remove the host implementation. Existing P4 device-mode MSC goldens are
a separate regression lane.

The pocket-tank follow-up used the hash-checked model fixture. Both
revisions executed 684,909,493 and 873,140,214 instructions and emitted
identical console bytes. Median user CPU time was 12.13 s on the baseline
and 13.24 s on the launcher build. The runs took place on a shared host
with concurrent work.
