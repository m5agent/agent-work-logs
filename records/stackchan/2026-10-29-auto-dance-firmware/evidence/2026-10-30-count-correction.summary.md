# 2026-10-30 StackChan SCS count correction

The original public record reported 1006 matching SCSCL `SYNC_WRITE` packets in a
96-second native QEMU run. The retained record contains a derived text summary
and an unpublished raw evidence ZIP digest, but not the raw SCS trace itself.

Therefore the value is retained as:

- historical reported count: `1006`;
- independent reverification: `NOT RUN`;
- current status: `PARTIAL`.

A later browser-QEMU test of the same full-flash SHA observed 30 accepted SCS
packets with yaw present/goal `307..613` and pitch present/goal `677..850`.
That test used a different execution profile and time window. It proves the
current browser path consumes servo position changes, but it does not replace or
recount the earlier 96-second native run.

Follow-up record:
[ESP Emulator StackChan dance and Cardputer-ADV all-key validation](../../../esp-emulator/2026-10-30-stackchan-dance-cardputer-adv-all-keys/).
