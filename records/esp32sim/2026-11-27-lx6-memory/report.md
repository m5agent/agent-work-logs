# Classic memory qualification

The native CLI and backing allocator rejected 2 MiB and 8 MiB even though the SPI ID layer already reported both sizes. The patch admits both capacities and tests the first invalid page for 2 MiB and the last valid physical page for 8 MiB.

The dual-core 2 MiB firmware passed the heap and Flash checks. The dual-core 8 MiB firmware reused one 32 KiB virtual window to read and write pages 127, 128 and 255. The same image on a 4 MiB configuration printed the detected capacity and failed its 8 MiB assertion. All runs used the native ROM boot path and a 16 MiB Flash configuration.

An earlier 2 MiB run failed the fixture's heap assumption. That build reserved eight HIMEM slots, reducing the reported heap to 1,835,008 bytes. The final 2 MiB build disables bank switching and checks an allocation against the actual allocatable heap. The 8 MiB build explicitly reserves one slot and exercises the public HIMEM API.

Commands and output requirements are linked in [run.json](run.json). The evidence contains filtered serial markers. Full SHA-256 identities and raw log digests are recorded alongside them. The branch can be rolled back by reverting the memory commit or by using the prior native CLI binary. No stock board or physical timing result is claimed.
