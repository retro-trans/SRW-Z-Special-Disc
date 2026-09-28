# English translation candidate 0.2.10

Fixes the supplied pre-title Mazinger Z demo screenshot from v0.2.9:
**Mazinger Z**, **Koji**, and **"Great Wheel Rocket Puuunch!"**.
The title and name are stored separately from the regular battle UI.

All 20 series-title graphics and 61 speaker-name fields across the three demo
banks are translated. Names reuse the exact already released pilot/display
identities; titles reuse established Library PRDC wording. Independent review
checks all 81 mappings against native source and records the short-title
localization choices. Titles are authored into the original 512-by512 indexed
atlases with their original palettes. The twenty-byte name fields are inside
thirty-two-byte crew records; adjacent IDs and commands are preserved.

Three attack-call variants received independent contextual meaning review.
They use Great Wheel Rocket Punch, following the
[Mazinger Wiki terminology](https://mazinger.fandom.com/wiki/Mazinger_Z_(Robot)/TV),
with extended delivery and native punctuation preserved. Total battle
coverage is 1,003 identities at 2,315 occurrences. The earlier 1,000 entries are
identical, and the remaining 56,947 indexed occurrences stay native.

Dry-run validation confirms only `BTL/OP.BIN`, `BTL/SRVC.BIN` and
`BTL/SRVC.SEG` differ from the v0.2.9 component payloads. The executable and
English memory pool are unchanged: 115,476 bytes, ending at 0x83B514 below
heap 0x83B600. No movie files are changed. Existing Library, chart, recap,
menu and narration coverage remains installed; separate story and suspend
translation drafts are not newly installed by this build.

Static atlas previews were visually inspected. Every title fits within its
512-by40 cell; the pictured caption uses 321 of 460 font units in one row.
Independent demo readback checks names against regular battle display fields
and all permitted pixel/name ranges against native data. Fault checks reject
changes to the next crew's ID, a name, a palette and an event command.
Existing scoped-name regression tests pass.

Emulator acceptance remains pending by user choice. The artwork and caption
previews are static reconstructions, not evidence of emulator playback.
Other demo battle dialogue is not claimed complete.

Outputs: `work/output/SRW Z Special Disc English v0.2.10.*`.
Build receipt and final-disc audit record artifact hashes, patch reconstruction,
preservation checks and source/translation/tool dependencies.

Final validation passed:

- ISO: 3,791,781,888 bytes, SHA-256
  `b29b5803630fe004e3dad3837ece33b5d0248d480887217328742f797ec93c43`.
- xdelta: 4,473,642 bytes, SHA-256
  `16671f6bf7166ef450dac65e9a09336964e20f83a87a9000ffb4f309ea150793`.
  Reconstruction from the clean Special Disc BIN matches the ISO exactly.
- All 3,773,388,140 bytes outside 42 planned writes match the clean image.
  Disc directory and runtime mappings agree. Native story chunks, suspend
  dialogue and save archive remain unchanged.
- Independent finished-disc readback passes for all 20 demo titles, 61 demo
  names and 2,315 English caption occurrences, as well as existing Library,
  reference, chart, recap and narration coverage. Native voice metadata and
  all 56,947 unapproved indexed caption occurrences are preserved.
- All 73 Python tools, 82 top-level translation files and 12 glossary files
  recorded in the receipt match their build-time hashes.

Reports: `work/analysis/build-0.2.10-independent-audit.json` and
`work/analysis/build-0.2.10-input-verification.json`.

See [demo format research](ATTRACT_DEMO_RESEARCH.md) and
[remaining translation scope](TRANSLATION_SCOPE.md).
