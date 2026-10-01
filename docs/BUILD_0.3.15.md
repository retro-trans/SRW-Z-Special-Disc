# Build 0.3.15

Local test candidate based on v0.3.14. This completes the indexed battle-caption translation set and the separate Battle Theater speaker-name bank.

## Coverage

- 23,359 newly installed source strings at 53,252 indexed occurrences; 23,357 reuse English matching the SRW-Z donor, and two have explicit source-reviewed edits.
- 58,880 final player-facing indexed caption records, representing 25,521 unique native sources, checked for remaining Japanese.
- 352 caption banks checked, with 267 changed. Existing English translations remain intact.
- 382 occurrences of source 444 remain native because the verified game pipeline suppresses this internal production note. Its suppression instructions are rechecked; it is excluded from player-facing coverage.
- 4,297 speaker-name cells in 1,031 Battle Theater scenes across 28 banks. The parser validates both sides, all eight unit slots per side, every variable crew list and the exact scene/event boundary. Names match existing pilot translations by ID and source hash; eight AI labels are translated explicitly.

Roger's reported line is "I'll have to get a little rough!" The other edited caption reads "Newtype... Power sealed in the Black History's darkness... What is it?!" It retains the source's question, which the inherited long version omitted, while fitting two rows.

## Preservation and checks

New captions use the current Latin encoding and at most two rows, 460 conservative width units per row and 96 encoded bytes including the terminator. No display-buffer or font changes are needed. English strings are appended to their existing banks, and only selected caption offset words change. Voice metadata, existing captions and opaque tails are preserved and compared. The final indexed readback checks all player-facing captions for remaining Japanese.

Battle Theater names occupy existing 20-byte cells. The archive length and segment table stay unchanged. Every byte outside these cells is restored and compared, protecting pilot IDs, units, weapons and battle events. The title-screen attract demo's previously translated name bank remains unchanged.

`python tools/build_complete_battle.py --write --patch` creates the ISO and clean-source xdelta in `work/output`, compares the full disc with planned writes, checks ISO/runtime reads, and reconstructs the exact image from the patch. The English-only translation inventories are `work/translation/en/battle_complete.json` and `battle_theater_names.json`; no Japanese dialogue corpus is exported. Static layout evidence is `work/ui/battle-complete/preview-0.3.15.png`.

## Verification limit

Inherited SRW-Z English is source-matched and checked for glossary spelling, encoding, capacity and layout; this is not a fresh manual proofreading pass over all 23,357 inherited translations. The preview is reconstructed from the installed font atlas. Emulator playback, name display and timing checks remain pending. Cold boot the new ISO and restart the Battle Theater scene rather than loading an old emulator state.
