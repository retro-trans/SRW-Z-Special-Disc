# English narration candidate 0.2.5

Adds all ten episode narration/journal entries to 0.2.4. Story dialogue stays
unchanged. Emulator testing is pending by user choice.

All 130 source lines were read in their five opening/conclusion pairs. A
separate meaning review corrected one organizational descriptor. Two compact
variants received another meaning check, preserving all facts, uncertainty,
dates, signatures and the full book attribution. The shared name pass follows
meaning edits. The complete English drafts and reviews remain available.

The native archive grows from 6,592 to 7,280 compressed bytes. Decoded record
sizes are 976, 976, 992, 832, 864, 912, 928, 896, 944 and 928 bytes. Updated
size and offset tables allow native allocation to hold the expanded text.
The assembler relocates the archive and updates both disc maps. Every picture,
music, timing, modifier, clip and formatting command remains intact.

All entries retain thirteen lines at a conservative 550-unit width. Four
journal dates/signatures have dedicated rows, and the last attribution uses
two rows. Reconstructed previews are under `work/ui/english/`; they are not
emulator screenshots. See [format and renderer research](NARRATION_RESEARCH.md).

The native roundtrip, 70 expanded-record tests, 70 corrupt-record rejection
cases, translation compiler and complete assembly dry run passed. A separate
code/data review found no concrete defect. Final ISO and patch checks passed:

- ISO: `SRW Z Special Disc English v0.2.5.iso`, 3,791,781,888 bytes.
  SHA-256 `442d53e2b14aed33a56fd6ff0057a2cd10a0b138fb97f354575f18e2d366e5a8`.
- Patch: 3,166,877 bytes, SHA-256
  `d4b1719ab5c83cf240c4d07368d8dad73c9a2bb86a9e2870339670250f90c98d`.
  Reconstructs the exact ISO from the clean Special Disc BIN.
- All 3,777,655,336 bytes outside 36 planned write ranges match the source.
  Both disc maps agree. STAGE chunks 1–67, battle captions, suspend dialogue
  and the native save archive are unchanged.
- Independent finished-ISO readback passed for all ten narration entries,
  4,995 Library fields, 34,963 Library description lines, 313 reference names,
  395 chart fields, 60 English recaps and all six native recap deferrals.
  All 725 relocated English text targets pass; narration uses its own native
  loader allocations and is counted separately.
- English segment and heap remain `0x81C970..0x83B57C` and `0x83B600`.
  The loaded text pool remains 115,580 bytes.
- Receipt hashes match all 42 tool files, 28 translation files and three
  glossary files used by this build. Earlier outputs remain unchanged.

The build receipt is in `work/output/`, with the independent audit in
`work/analysis/build-0.2.5-independent-audit.json`. These checks establish
binary integrity and static layout bounds; runtime acceptance remains pending.

Six save/load recaps remain native: 2, 13, 17, 27, 44 and 53. Battle captions,
suspend messages, remaining artwork, stage UI and broader inherited prose
review remain work to do. The [translation scope](TRANSLATION_SCOPE.md) and
overall goal remain active.
