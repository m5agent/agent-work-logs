# Controller and media readbacks

These Device Service virtual-device checks used esp32sim source
`4e257b6be8ee0ed706c2e509d8f31ef7472a424b` and the pinned native control patch.

- StickS3 received an injected NEC command `0xA3` in its original Arduino receiver. The guest reported the address with the complemented high byte and redrew its framebuffer.
- StackChan's original movement example responded to the top pad. The modeled pitch read through `device-state` moved from 0 to 45 degrees following the guest's serial servo traffic.
- AtomS3U's mic example reported a peak level of 27,989 with the PCM fixture and 300 in the idle case. These are guest values, outside physical acoustic measurement.
- Cardputer's Arduino microSD example read back its appended text and renamed the file. The stopped-session SD export returned HTTP 200.
- PaperMono redrew after NFC insert and remove. PaperColor acknowledged the SHT40 sample. The recorded interval did not establish guest SHT40 response.

[Controller and media receipt](controller-and-media-summary.json)
