# English translation candidate 0.2.8

The ISO, patch reconstruction and independent binary readback pass.

Adds 397 independently reviewed battle captions at 964 occurrences to 0.2.7.
The release contains 1,000 texts at 2,312 indexed occurrences: all 877 rows in
the active/donor disagreement queue and all 123 new captions. Every occurrence,
neighboring context and slice boundary received native-source meaning review.
The 603 texts included in 0.2.7 retain their approved wording.

Corrections restore omitted conditions, reversed addressees, explicit futility,
the operator of Boss Borot, and a bridge announcement incorrectly phrased as
an order. Research identifies Sozo Haran and confirms Julie Noguchi is male.
The Daisetsuzan Oroshi shout retains its Double Reversal variant. An independent
compact review preserves the unfinished dust proverb, including uncertainty
about its ending, and the warning against carelessness around Coralians.

All 1,000 captions fit two rows at a conservative 460-unit width with quotes.
The largest converted string is 91 bytes including NUL; the native maximum
is 86. The original 96-byte buffers and display instructions remain in use.
SRVC grows from 3,420,320 to 3,466,848 bytes across 180 changed blocks. English
is appended after complete native blocks; only selected text-offset words
change. Voice metadata, original text, sequence data and opaque tails remain.

The source-scoped spelling pass corrects 45 Library fields, 15 menu fields and
seven Scenario Chart summaries. Terms include Orson, Solar Wing, Mechaboost,
Musouken and Sigma Breast. Chart summaries receive spelling changes after
their independently reviewed meaning edits; story dialogue stays excluded.
The glossary records sources, provisional translations and protected names.
Older author/review files retain their original wording and hashes.

Release input: `work/translation/en/battle_release_0.2.8.json`, SHA-256
`8e9f485557db6ebda1fb0cab600c15831f9169b0a8b956e90be5b05f72c96c8e`.
The static preview is `work/ui/english/battle-caption-layout-0.2.8.png`, with
measurements in its versioned JSON. Actual Latin atlas glyphs were inspected;
the tilde preview uses a disclosed substitute. It is not an emulator capture.

The full component dry run passes, including relocation, encoded readback,
native-byte preservation and source/review hash checks. The English segment
ends at `0x83B514`, before heap base `0x83B600`; the pool is 115,476 bytes.
Name regression checks pass.

Verified artifacts and final checks:

- ISO: 3,791,781,888 bytes; SHA-256
  `e48a969c65acf31bedf18247ae498ebb9b5369a0f076c1596c491941ecf15b51`.
- xdelta: 4,358,313 bytes; SHA-256
  `3035408e09277fcdf7cc68be40113cf6d44b2c2cc399e4a4bf39b8a9000810c0`.
  Reconstruction from the clean Special Disc BIN matches the ISO exactly.
- All 3,774,186,636 bytes outside the 41 planned writes match the clean image.
  Disc directory and runtime mappings agree. Story chunks 1-67, suspend
  messages and the native save archive remain byte-identical.
- Independent readback checks all 2,312 translated caption occurrences and
  56,950 unchanged indexed occurrences, every voice binding and the restored
  original block bytes. It also checks 4,995 Library fields and 34,956
  description lines, 724 relocated targets, 313 reference names, 395 chart
  fields, 60 recaps and ten narration entries.
- Receipt hashes match all 59 tools, 63 translation files and seven glossary
  files recorded at build time.

Artifacts: `work/output/SRW Z Special Disc English v0.2.8.*`.
Independent audit: `work/analysis/build-0.2.8-independent-audit.json`.

Remaining indexed captions: 24,522 text identities at 56,950 occurrences.
These candidates require review before release. COMPDATA battle text, suspend
messages, six deferred recaps and other Japanese artwork remain in scope.
Emulator testing stays pending by user choice; this release does not complete
the non-story translation goal. See [the scope ledger](TRANSLATION_SCOPE.md).
