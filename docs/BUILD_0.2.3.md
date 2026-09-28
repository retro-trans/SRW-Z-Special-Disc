# English reference-screen candidate 0.2.3

Adds the 110 main-game Scenario Chart summaries, completing all 131 summaries.
The full chart now contains 395 translated fields. Story dialogue remains
unchanged; emulator testing is pending by user choice.

## Source and review

The preparer compares complete native NUL-terminated strings against the
main-game archive and follows its English donor pointer table. Reading English
at the old Japanese offset is unsafe: several donor paragraphs were relocated.
Two reviewers examined all 110 assigned rows, 113 including their adjacent
context, and supplied 78 meaning corrections. The merge applies those edits
first and glossary rules afterward, preserving review-input hashes.

Corrections restore missing plot facts, distinguish Edel from The Edel,
correct the destination of the rescue at Heaven's Base, identify Kihel rather
than Kira as Dianna's successor, and avoid converting risk or injury into death.
Notes retain uncertainty about Auel's memories, the recipient of Asakim's fear,
and Leele's injury mechanism. Edel's station recapture is stated as an objective,
without claiming its success. Heizaemon is named without the source's disputed
kinship implication.

## Binary preservation and layout

- Main synopsis pointer table: `0x14864`, 110 entries, overlay base `0x8045F0`.
- All new paragraphs use the loaded English ELF segment. No source-byte budget
  truncation is used. All paragraphs fit eleven rows at 560 font units per row,
  with the wider bold advance included.
- Native main-summary strings are preserved. Packed words before the text
  region can numerically resemble pointers; only the known typed table changes.
- The decoded chart buffer and its 44,016-byte compressed slot stay fixed.
  All non-text chart bytes and all compressed story chunks 1–67 are preserved.
- Inherited Library/name fields are regenerated after the glossary pass.
  Context rules protect Banjou Ginga, Masako Katsuki, George Glenn, Black Mail
  and Freedom Gundam while fixing the intended references.

The structure follows the verified Special Disc overlay identified in
[dyzz/srwz-zh](https://github.com/dyzz/srwz-zh/blob/f6673b1edf697df3501fba3889e930815fd1b001/tools/special_disc/writeback/write_frame_text.py).
No Chinese translation, font or unlock changes are imported.

Name sources include [Orguss](https://en.wikipedia.org/wiki/Super_Dimension_Century_Orguss),
[King Gainer](https://en.wikipedia.org/wiki/Overman_King_Gainer),
[Rena](https://en.wikipedia.org/wiki/List_of_Genesis_of_Aquarion_characters),
[Kihel](https://gundam.fandom.com/wiki/Kihel_Heim), and
[Heizaemon](https://srw.wiki.cre.jp/wiki/神北兵左衛門).
The glossary contains the detailed references and context rules.

## Validation

The ISO and 3,157,348-byte xdelta are in `work/output/` as
`SRW Z Special Disc English v0.2.3`.

- ISO SHA-256: `75a149cf6e71d997193824eeae535f0e29717da3da469ea94261ebcf812228f7`.
- Patch SHA-256: `9a5b4474b3b5e1be69e02a726e636f0c23766e67118c5c00930f55d9c5e09c8b`.
- Patch reconstruction matches the full ISO. All 3,777,704,512 bytes outside
  the 32 planned write ranges match the clean source.
- Independent readback passed: 4,995 Library fields, 313 reference names,
  395 chart fields and 665 relocated text targets. All 34,963 Library description
  lines and all chart paragraphs pass their configured width checks.
- English segment `0x81C970..0x831570` is above native memory and below the
  adjusted heap at `0x831600`. The text pool occupies 74,608 bytes.

The receipt and independent audit are recorded in `work/analysis/` and
`work/output/`. Runtime layout and gameplay acceptance remain pending.
See [the scope ledger](TRANSLATION_SCOPE.md) for save/load summaries, narration,
battle captions, suspend messages, artwork and stage UI still requiring work.
