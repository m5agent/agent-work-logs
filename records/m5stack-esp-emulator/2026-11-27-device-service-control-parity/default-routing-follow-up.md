# Remaining consumer gaps and StickC Plus SE

2026-11-27. Virtual-device validation through the exact release binary built
from the `9c0447e8` fork pin.

StickC Plus SE passed both of its selected display oracles in both trials
on esp32sim. The frozen QEMU path missed those two oracles in both trials.
The checked-in UIFlow2 fixture passed both trials per runtime. It observed
the guest button press/release and green pixel at (3, 3). The original stock
firmware reached a rendered frame and accepted the same input on each
runtime. These stock results alone do not establish a guest screen transition.
The shared watcher compatibility probe passed both trials on both runtimes,
including QOM and Flash snapshots and diffs, the frame, crash receipt,
and evidence ZIP hashes. The proposed default is esp32sim.

For each QEMU-default profile with registered device state probes, the
test issued `GET /device-state` through the service on its checked-in fixture.
QEMU returned HTTP 200. Eighteen esp32sim sessions returned HTTP 409, while
StackChan returned its servo components and lacked the legacy components
returned in the QEMU snapshot. The Atom VoiceS3R QEMU fixture returned no
components despite the legacy provision for the route. NanoC6 and Nesso N1
advertise separate legacy network profiles. An esp32sim lease with the same
profile fails admission with `409 not_supported_on_runtime`.

- [Expected state names and virtual-device receipts](evidence/remaining-consumer-gaps.json)
- [StickC Plus SE trial scopes and hashes](evidence/stickc-plus-se-follow-up.json)
