# English battle-caption candidate 0.2.6

Adds 283 reviewed battle captions at 640 indexed occurrences to 0.2.5.
All 123 newly authored captions and 160 active/donor disagreements were read
against native records and separately reviewed. One compact version received
an additional meaning check. Names are normalized after editorial corrections.

All captions retain their full meaning within two rows and a conservative
460-unit width, including quotation marks. The largest converted caption uses
86 bytes including NUL, so the native 96-byte buffer and all caption display
instructions remain unchanged. Static previews use the actual Latin atlas;
they are not emulator screenshots. See [caption research](BATTLE_CAPTION_RESEARCH.md).

The SRVC archive grows from 3,420,320 to 3,434,400 bytes, with 107 blocks changed.
English is appended after each original block. Selected index offsets and the
SEG table are updated, together with both disc maps. Voice metadata, sequence
selection, native strings and opaque tails are preserved. All other 58,622
indexed occurrences remain native. The complete candidate inventory is not
automatically approved.

The actual-disc relocation tests accept much longer replacements in every
nonempty block. Generated optional buffer adapters pass MIPS instruction tests
but are not installed in this build. The separate readback auditor validates
all 59,262 indexed records and the original bytes in every block. The full
assembly dry run passes. Final ISO, patch and independent readback checks pass:

- ISO: 3,791,781,888 bytes; SHA-256
  `0ad6638f5e4ad11798316e6015a9888a26f506f49c718b29820375f9b989d55f`.
- xdelta: 4,340,681 bytes; SHA-256
  `f7c140823df55253a37ff1f55ef7427322ec1009b896efd9b3368bd074a994ac`.
  Reconstruction from the clean Special Disc BIN matches the ISO exactly.
- All 3,774,219,404 bytes outside 41 planned writes match the clean image.
  ISO and runtime mappings agree. Story chunks, suspend dialogue and the
  native save archive retain their source bytes.
- Independent readback verifies all 640 English caption occurrences, 58,622
  unchanged indexed occurrences, voice metadata and original block contents.
  Prior Library, chart, reference-name, recap and narration coverage also passes.
- Receipt hashes match the 58 tools, 46 translation files and five glossary
  files recorded at build time. Additional next-pass research is separate.

Artifacts are under `work/output/SRW Z Special Disc English v0.2.6.*`;
the independent audit is `work/analysis/build-0.2.6-independent-audit.json`.

Prior coverage remains: 4,995 Library fields, 7,883 menu/name fields, 102 Q&A
pages, 24 briefing panels, 313 reference names, 395 chart fields, 60 save/load
recaps and ten narration/journal entries. The six recap deferrals remain native.
The English segment and heap remain `0x81C970..0x83B57C` and `0x83B600`.

Story chunks 1-67 are excluded from translation. Emulator testing stays pending
by user choice. Other battle captions, suspend messages, remaining artwork,
speaker-name layout and broader inherited prose review still need work; the
[scope ledger](TRANSLATION_SCOPE.md) and overall goal remain active.
