# Build 0.3.17

Local test candidate based on v0.3.16. Fixes the reported Back Log overlap and renames the Gabthley's weapon to Fedayeen Rifle.

## Back Log

The Back Log draws the raw story strings; it never passes them through the MessageWindow converter that v0.3.1 enabled for the dialogue box. Its row renderer treats bytes 0x2E-0x3D as control codes before any ASCII handling, so every `.` (0x2E) acted as a line break and digits, `:`, `;` and `/` corrupted rows. English rows broke at their first period and overprinted the next row, as in the reported screenshot. The SRW Z main game found and fixed the same engine fault (SRW-Z `tools/patch_backlog.py`).

Special Disc already carries that fix's converting copy and its path-A sprite-width stub in the ported English runtime; the width stub was already hooked. `tools/backlog_runtime.py` changes six instruction words:

| Change | Special Disc address |
| --- | --- |
| Converting copy table pointer: donor 0x78A1BC -> 0x81CABC | 0x81E424 / 0x81E428 |
| Back Log row copy 1 and 2: `jal 0x1A5640` -> `jal 0x81E3F0` | 0x2263C4, 0x2263D8 |
| Source-length terminators (would cut the converted string): NOP | 0x2263F0, 0x2263F4 |

The copy helper 0x1A5640 matches the main game's 0x1A1190 over 16 words; the surrounding row-copy code is the main game's with frame offsets shifted by 0x10. Converted text is at most 265 bytes, inside the 0x210-byte row buffers. ASCII becomes the installed two-byte glyph codes; Shift-JIS, control bytes and already-converted text pass through unchanged, so the dialogue box path is unaffected. `build_story.py` now applies this patch with the story runtime.

`tools/test_backlog_runtime.py` executes the installed routine with branch delay slots: both screenshot rows, all printable ASCII, mixed Japanese/English, empty input, already-converted input, idempotence and the preimage guard. No control byte 0x2E-0x3D survives conversion.

## Fedayeen

COMPDATA weapon names フェダーイン・ライフル and its 連射 variant read "Fedain"; they now read Fedayeen Rifle and Fedayeen Rifle (Rapid), in their native 24- and 32-byte fields. A scan of every English-bearing disc member (raw and decompressed) found no other "Fedain". The glossary (`english.json`) records the spelling correction and term; both compdata translation files are updated. COMPDATA grows by 5 compressed bytes and moves into empty reserved space (LBA 1,811,148) with its ISO extent and VMAP entry updated.

## Verification

- Every other disc byte equals v0.3.16; EXE and COMPDATA read back identically through the ISO directory and runtime VMAP.
- ISO SHA-256 `d99e0f0b6a232a043ad7995e8e7a1e182e0f9a04f0feac1ed85cc9d25a298ad0`.
- Clean-disc xdelta 16,456,740 bytes, SHA-256 `d4cfaf96cfcef2328163550d12f3a9a65fda6438da62af130444f19586b5168a`; reconstruction verified.

Build: `python -B tools/build_backlog_fedayeen.py --write --patch` (dry run without flags).

## Not yet verified in game

Cold boot v0.3.17 (do not load an older save state), open the Back Log after several English lines, and check rows with periods, digits and commas; check the Gabthley weapon list.
