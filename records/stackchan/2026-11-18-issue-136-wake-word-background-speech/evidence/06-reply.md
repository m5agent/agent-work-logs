Thanks for the detailed report. I checked the published V1.6.0 firmware source (`m5stack/StackChan` @ `94856a7`); the observations are consistent with two separate parts of the AI.AGENT audio path rather than a single wake-word defect.

**Conclusion**

1. **Wake detection.** The wake word is a fixed, pre-trained WakeNet model (`CONFIG_SR_WN_WN9_HISTACKCHAN_TTS3`) run through the AFE with the ES7210 reference channel (`AUDIO_INPUT_REFERENCE true`). Detection parameters come from the model/AFE configuration, not from a user setting, and the wake-word audio is not uploaded (`CONFIG_SEND_WAKE_WORD_DATA=n`), so the server never receives the sample and cannot verify the detection.
2. **Why a conversation can continue.** When the server sends `tts stop`, the device goes straight back to `Listening` unless the session was started in manual-stop mode. While listening, wake-word detection is off by default, so any microphone audio is treated as the next user turn; there is no fixed device-side listening timeout. The device returns to standby only when the server closes the audio channel (or on a user action/error). One false wake is therefore enough to chain: reply → listen → TV speech accepted as a follow-up → reply → listen. That matches the repeated follow-ups, the several-minute duration, and the response after the assistant said it was ending: a spoken goodbye is model output, not a command that closes the session.

**Evidence class: code-level verification** (source-level; runtime not reproduced).

**Code locations (V1.6.0 source)**

- `firmware/repos.json`: AI.AGENT is xiaozhi-esp32 `v2.2.4`.
- `firmware/sdkconfig.defaults:15-16`: `CONFIG_SEND_WAKE_WORD_DATA=n`, `CONFIG_SR_WN_WN9_HISTACKCHAN_TTS3=y`.
- xiaozhi `v2.2.4` `main/audio/wake_words/afe_wake_word.cc:73-75`: `afe_config_init(..., AFE_TYPE_SR, AFE_MODE_HIGH_PERF)`, AEC enabled from the reference input; no user threshold is read anywhere.
- `main/application.cc:531-539`: on `tts stop`, non-manual-stop sessions return to `Listening`; `:950-951` selects that mode; `:708-709` a screen tap while listening closes the audio channel.
- `main/Kconfig.projbuild:732-740`: wake-word detection in listening is disabled by default.
- `firmware/main/hal/board/stackchan_display.cc:256-266`: screen tap → `ToggleChatState()`.

**Answers to your questions**

1. *Known issue?* I did not find a separate report of this specific false-activation pattern. The closest thread is #94, which covers the fixed pretrained wake model and the lack of custom wake phrases — not this behaviour. I cannot confirm a tracked defect entry for your case.
2. *Configurable sensitivity / timeout / reactivation?* Not on V1.6.0. The on-device AI.AGENT settings only expose idle movement frequency and idle auto power-off (`app_setup/workers/ai_agent.cpp`); volume, brightness and timezone are separate. AEC is a build-time option (`CONFIG_USE_DEVICE_AEC`, see #85), not a user setting. The same is true on V1.6.2.
3. *Recommended mitigation without custom firmware?* Keep the device away from the TV speaker and lower the direct TV level; for a fixed acoustic model, distance and level are the only effective knobs. A screen tap while the device is in `Listening` closes the audio channel and returns it to standby, which ends a chain that started with a false wake. (Tapping while it is speaking aborts the reply and starts listening again, so use the listening state.) The idle auto power-off only applies while idle and does not interrupt an active conversation.
4. *Planned improvements?* I cannot confirm a planned change. V1.6.2 (current main, PR #128) moves to xiaozhi `v2.5.2` / esp-sr `2.4.7` and changes the model from WN9 to WN9L (`CONFIG_SR_WN_WN9L_HISTACKCHAN_TTS3`), but the post-reply re-listen behaviour is unchanged in `v2.5.2` and I have no measurement showing a lower false-accept rate, so I would not present it as a fix for this report. User-configurable wake phrases remain unsupported (#94); discussion #133 is the right place to track that request.

**Not covered**

- No hardware and no virtual-device validation. Why virtual-device validation was not used: the local StackChan QEMU profile covers display, touch and Wi-Fi and models the ES7210 codec, but AI.AGENT requires a bound device with a live AI-service session, which the emulator does not provide; and a false accept is a statistical property of the acoustic model against your actual room and TV audio, which a synthetic PCM fixture cannot establish. I also did not build the factory image (ESP-IDF 6.1 and the fetched xiaozhi components are not installed here).
- The repository README notes that published source can lag the released firmware, so the factory image may differ in details from `94856a7`.
- The server-side listening/VAD timeout is not in this repository, so I cannot state when the server closes the channel.

If you can capture a USB serial log around one incident, the `Wake word detected: ...` lines and the following `tts`/`stt` messages would show whether each turn came from a new false wake or from the automatic listening window. That is the one piece of information that would let us separate the two causes for your unit.

Full analysis and code excerpts: {{RECORD_URL}}
