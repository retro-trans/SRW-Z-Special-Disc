# English test candidate 0.2.15

This build addresses the two Story Mode alignment screenshots supplied by the
user. Translation coverage stays at the v0.2.14 baseline: 1,917 battle captions
at 4,870 occurrences, all existing Library/menu/reference translations and the
pre-title demo titles/names/Rocket Punch captions. The next 236 reviewed battle
drafts are not installed in this alignment build. Story dialogue is unchanged.
Emulator testing remains pending by user choice.

## Layout changes

The original introduction starts at x=92 on the 640-unit horizontal canvas,
but the compiler allowed 560 units of text. That could extend beyond the panel.
The new shared heading/body origin is x=64, with a conservative 500-unit wrap
limit ending at x=564, inside the divider's approximately x=576 right edge.
All six pages still fit their seven body rows. No words were shortened or
removed, and the native 56-byte text cells / 57-byte stride remain unchanged.
The eighteen wider Challenge panels retain their existing content and layout.

The clear-confirmation screen previously appended markers after measuring each
label. Its original Japanese padding and English measurement differed from
the actual proportional draw advance, causing uneven columns and overlap.
A scoped helper retains the original segment creation and then sets the second
segment's x=448. It also uses unpadded CLEAR! and dash strings. Only the
confirmation mode takes this path; other reward modes tail-call the original
append function. Status flags, colors, reward logic and segment/row counts stay
native. A guard prevents repositioning when the expected second segment was
not created.

The three known questions use exact English glyph widths for their center at
x=316. Unknown text and other measurement modes fall back to the native
function. Eight executable instructions change in total: four margins, two
scoped marker calls and two scoped question-width calls. All delay slots remain
unchanged. Small helpers and strings live in the relocated English segment;
the build adjusts its memory extent and heap reservation accordingly.

## Verification

- Four test methods cover 48 cases: exact/unknown question matching, all five
  reward modes, early/late row slots, missing/extra segment guards, preserved
  flags and saved registers, and rejection of eight changed patch preimages.
- Dry-run compilation preserves the complete paragraph words on all six pages.
- Static previews were inspected using the actual Latin atlas. They are
  reconstructions, not in-game screenshots or runtime acceptance.
- Final-disc audit checks all eight patched instructions, both helpers, five
  pooled strings and all six introduction pages; it verifies that Challenge
  pages and native append/mode logic are unchanged.
- The standard build also verifies all bytes outside planned writes, text
  references, executable segment/heap bounds, and story preservation. The
  xdelta must reconstruct the exact new ISO before the build is accepted.

User references: `work/ui/reference/story-intro-before-alignment.png` and
`work/ui/reference/story-clear-before-alignment.png`. Their build version was
not supplied with this alignment request. Coordinates and reconstructed
previews are in `work/ui/story-panel-layout-0.2.15.json` and
`work/ui/english/story-panel-{intro,clear}-0.2.15.png`.

The final-disc audit passes: all six introductions retain every word from
v0.2.14 after the established glossary pass. The largest conservative line
width is 498, within the 500-unit limit. Both helpers, all five pooled strings
and all eight patched instructions read back correctly; the eighteen Challenge
panels remain unchanged. The broader readback also passes for 4,995 Library
fields, 729 relocated texts, 313 reference names, 395 chart fields, 65 recaps,
ten narration entries, 1,917 captions and all pre-title demo titles/names.

One audit-only correction was required after assembly: an older target spells
Mel Beater as Mail Beater. The compiler already applies the established
glossary correction, as it did in v0.2.14. The auditor now checks the corrected
target and the previous release's full words. The acceptance receipt records
the old/new auditor hashes; the original assembly receipt is retained as
`work/analysis/build-0.2.15-assembly-receipt.json`. This correction changes no
builder, translation, ISO or patch bytes.

All 3,773,343,084 bytes outside the 42 planned writes remain native. Among the
thirteen member payloads, only the executable differs from v0.2.14; the
introduction text also changes in VT1 chunk 40. The English pool is 115,940
bytes at 0x81F200, with segment end 0x83B6E4 below heap base 0x83C600.

Outputs use `work/output/SRW Z Special Disc English v0.2.15.*`.
ISO: 3,791,781,888 bytes, SHA-256
`2b917ceafe0239fceae2bbfb562421570e0a16b915faf3a9f27dab52e78b7966`.
Patch: 4,492,073 bytes, SHA-256
`3e99a23cc0a2f145da9d4e2e4726145ee8743b1cfdd93d4bc856be6c72e587de`.
Exact reconstruction from the clean Special Disc BIN passes.

All 236 acceptance-receipt inputs match: 90 Python tools, 128 translation
files and 18 glossaries. The snapshot contains these inputs, the acceptance
receipt, both final audits and a dependency note in 240 entries; every entry
reads back exactly. Snapshot: 10,824,067 bytes, SHA-256
`f135493c249f06a1e313d505719464977c92272dacb2d6aa7a34cf982f83a345`.
It excludes game images, donor assets, fonts and runtime dependencies.

Emulator testing remains pending by user choice. These checks establish file
integrity and the scoped layout logic, not in-game visual acceptance.
