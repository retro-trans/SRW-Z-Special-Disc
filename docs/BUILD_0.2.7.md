# English translation candidate 0.2.7

Adds 320 reviewed battle captions at 708 occurrences to 0.2.6. The complete
release has 603 English texts at 1,348 indexed occurrences. All received
native-source authoring and independent meaning review, including every
occurrence, surrounding records and slice boundaries. Reuse queue 0-479 and
all 123 new captions are included; later drafts are outside this release.

Two additional compact forms preserve the entire meaning: the threat against
an Alisia family member and the refusal to abandon a rookie second lieutenant
and a frivolous first lieutenant. Rank abbreviations retain both grades.
All 603 texts fit two rows at a conservative 460-unit width, including quotes.
The largest converted string is 86 bytes including NUL, matching the native
maximum. The original 96-byte buffers and caption display instructions remain
unchanged. SRVC grows from 3,420,320 to 3,448,544 bytes across 145 changed blocks.

Names are corrected after meaning edits. Source-bound normalization fixes
148 Library fields, 52 menu/name fields and two Q&A pages. Native article owner
names identify omitted subjects in Library descriptions; complete pilot-name
records support English family/given-name reordering. The Saviour correction
explicitly protects Beam Saber, Fire Saber, Tornado Saber and Saber Claw.
The inherited Overskill Barrge typo is corrected to Overskill Barrage.

The original block data and voice metadata are preserved apart from selected
text-offset words. English is appended and all required archive/disc indexes
are regenerated. Unreviewed indexed occurrences remain native: 57,914 records
representing 24,919 text identities. Opaque tails and COMPDATA battle text need
separate work and are not counted as translated.

The versioned static preview is `work/ui/english/battle-caption-layout-0.2.7.png`.
Latin glyphs come from the actual atlas. Its tilde preview glyph is a substitute;
the game uses the verified ASCII 7E to native CP932 8160 mapping. The conservative
24-unit allowance exceeds the 13-unit ASCII advance. No punctuation is stripped.

The ISO, patch reconstruction and independent binary readback all pass:

- ISO: 3,791,781,888 bytes; SHA-256
  `71a297913402b3ca5587ab610eeef168a13cbb0a80539c4a55dc1a0c99992803`.
- xdelta: 4,348,976 bytes; SHA-256
  `9fa799713728e8d3dfee3489b7e344c797f0ce696a797ce7dda3164f1b00d160`.
  Reconstruction from the clean Special Disc BIN matches the ISO exactly.
- All 3,774,205,068 bytes outside the 41 planned writes match the clean image.
  ISO and runtime mappings agree. Story chunks, suspend dialogue and the native
  save archive retain their original bytes.
- Independent readback validates all 1,348 English caption occurrences, 57,914
  unchanged indexed occurrences, voice metadata and original block contents.
  It also reads all 4,995 Library fields and checks 34,961 description lines,
  724 relocated text targets, 313 reference names, 395 chart fields, 60 recaps
  and ten narration records. The English segment ends at `0x83B514`, before
  the unchanged heap base `0x83B600`; the pool is 115,476 bytes.
- Receipt hashes match all 59 tools, 54 translation files and seven glossary
  files recorded at build time. Later reviewed drafts are present in the
  workspace but excluded by the release input's explicit cutoff.

Artifacts are under `work/output/SRW Z Special Disc English v0.2.7.*`.
The independent audit is `work/analysis/build-0.2.7-independent-audit.json`.
Emulator testing remains pending by user choice. Binary checks and reconstructed
previews do not establish in-game playback, clipping or timing acceptance.

Existing coverage remains: 4,995 Library fields, 7,883 menu/name fields, 102 Q&A
pages, 24 briefing panels, 313 reference names, 395 chart fields, 60 save/load
recaps and ten narration/journal entries. Six recap deferrals remain native.
Story chunks 1-67 remain excluded. The [scope ledger](TRANSLATION_SCOPE.md)
lists the remaining non-story work; this build does not complete that goal.
