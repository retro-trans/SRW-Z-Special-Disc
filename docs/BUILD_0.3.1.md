# v0.3.1 — story layout runtime test candidate

The reported chapter-7 Eiji line breaks into overlapping text in v0.3.0. Its stored text already has three explicit body lines. The English font port provides ASCII glyph drawing, but omitted the main-game story setText hook that converts ASCII into two-byte glyph codes before the native story layout sees it.

This candidate enables that conversion globally for MessageWindow story text. It preserves the original reviewed text, punctuation, line breaks, source archives, font artwork, English memory segment and heap allocation. It changes 13 instruction words in the executable.

| Purpose | Special Disc address |
| --- | --- |
| MessageWindow setText | `0x2112D0` |
| Existing reserved converter | `0x81C970` |
| Expansion-context lookup | `0x205490` |
| Macro expansion | `0x2056E0` |
| Plain string copy | `0x1A5238` |

The three helper calls are confirmed in the native setText function. All four routines match the main-game native instruction signatures over their first 24 words. The converter's complete 83-word control-flow graph has only those three external calls; absolute jumps and its 95-entry table pointer are relocated. Relative branches stay internal. The table and existing glyph code remain unchanged.

Six regression tests execute the relocated instructions with MIPS branch delay slots, including the actual screenshot text, all printable ASCII, null input, mixed Shift-JIS and control bytes, and a Japanese name returned by the macro-expansion helper. Helper behavior is simulated; this is not a full PS2 emulator test. All 7,509 ordinary dialogue rows fit the 1,024-byte conversion scratch bound, with a maximum converted size of 265 bytes; both separately stored silent dialogue occurrences are tested too. Register restoration, object-prefix preservation, guarded writes and applying the patch twice are checked.

Build: `python -B tools/build_story_runtime.py --write --patch`, after inspecting its dry run. The builder verifies the exact v0.3.0 source hash, reads the new executable through both disc mappings, compares every output byte against the base plus the 13 planned words, and reconstructs the target from the clean-disc xdelta.

**Runtime visual confirmation remains pending.** Cold boot v0.3.1 and load an in-game save. Loading a PCSX2 save state can restore v0.3.0 code and reproduce the old problem. Recheck the pictured Eiji line, another long dialogue line, a thought box and a name-expansion line. The public v0.3.0 release is unchanged.

## Completed verification

- Six converter regression tests passed. Normal story-builder preflight installs all 45 chunks with no skipped chunks and includes the 13-word runtime patch.
- Finished disc: ISO/runtime executable readback passed; every byte outside the planned 13 words equals v0.3.0.
- ISO: 3,791,781,888 bytes; SHA-256 `c1ae1dc250ac687188d8ed6380751686bb47010fbaf60f44028c7ce9ece5d174`.
- Clean-disc xdelta: 4,643,993 bytes; SHA-256 `326f6a3ee37dc13ff982955c987d658c22bf3a9f88f3dd6d8707a5d739eb137f`. Full reconstruction passed.
- Candidate files: `work/output/SRW Z Special Disc English v0.3.1.iso`, `.xdelta` and `.json`. No public release was changed.
