# Native AtomS3 family replay

The batch ports the Atom board routes onto the ESP32-S3 native CLI. The first
milestone covers AtomS3U and Atom VoiceS3R. The executable was built from
`7fb2f24d7a20c0597cdf61e3fd06bf92e6e2ed07`. The published milestone also
contains the shorter replay windows that produced clean guest exits.

| Board | Pinned Arduino cases | Stock UIFlow2 v2.5.4 |
| --- | --- | --- |
| AtomS3U | PASS button, ir_nec, mic, program, rgb_led | PASS USB CDC ID 138 and G41 press/release |
| Atom VoiceS3R | PASS button, ir, mic, program, speaker | PASS USB CDC ID 145 and G41 press/release |

AtomS3U passed through the physical G39/G38 I2S0 PDM route. The guest sketch
reported median levels of 300, 1313 and 6567 for silence and two tones.
VoiceS3R captured 4 and 7 kHz through ES8311 and the G18 amp gate. Its
record-and-play example recovered 733 and 1193 Hz after G41 input. The
silence control produced a peak of zero. IR checks decoded the transmitted
NEC address and command from the corresponding board GPIO route.

Replay with the pinned Arduino and stock images. The runner records
binary, ROM and firmware identities as SHA-256 digests.

```sh
python3 tools/run-atom-s3-docs.py BOARD SIMULATOR FIRMWARE_DIR STOCK_IMAGE ROM_ELF NEW_OUTPUT --source SOURCE_SHA
python3 tools/check-atom-s3-docs.py NEW_OUTPUT
```

Two initial AtomS3U button runs hit the host wall timeout after exercising
the guest input windows. The milestone replay retained two presses, two
releases and an idle control and completed with exit 0. Later device and
regression results are not part of this milestone. Physical validation
is NOT RUN. Revert the Atom commits or select the earlier native simulator
binary to return to the previous profile set.
