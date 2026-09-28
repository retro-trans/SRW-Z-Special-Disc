# Build 0.2.1 — English menus and reference text

Date: 2026-09-25. Runtime acceptance: **pending by user choice**.

Binary verification and patch reconstruction **passed**. The independent final
audit read back all 4,995 Library fields and 535 relocated text entries, and
checked 34,964 description lines against their width limits. All 12,878 final
Library, menu/name and executable text fields follow the reviewed spelling rules.

| Output | Size / SHA-256 |
| --- | --- |
| ISO | 3,791,781,888 bytes; `965cf70fdd2626f76e22a3591e84117fa14414c213b4a4a7a721e6890424065e` |
| xdelta | 3,097,777 bytes; `752973bc41b799b2f1a03eec4d268414d62c339c312fbf4619805f1a045dd530` |

The native memory ends at `0x81C600`. The English segment occupies
`0x81C970..0x822F74`, below the new heap at `0x823600`.

The current candidate translates the supplied Library screens, extracted menu
text and names, Strategy Q&A, episode selection panels and Challenge briefings.
It retains the twelve front-end buttons and adds four English mode headings.
No story, battle or suspend dialogue is translated.

## Coverage and review

| Source | Result |
| --- | --- |
| MTVZKNRT/PT/KW | 4,995 fields across 795 records; both description variants |
| COMPDATA | 5,521 name/help fields; no pending fields in the owned menu inventory |
| Executable | 2,362 menu fields; six Spirit strips handled by the compact-label compiler |
| NISVDATA | 102 Q&A pages, 264 chapter strings, shared tutorial record and six Library button labels |
| VT1 | Earlier 60 button states, four mode headings, six selection panels and eighteen Challenge briefings |

New Library material covers XAN, the standalone Vector forms, alternate
Virgolas, Lemures Test Type and alternate Denzel/Toby entries. Meaning review
examined nine new descriptions in both variants and nine name replacements,
with five adjacent character entries for context. It corrected Toby's partner
to avoid inferring gender and preserved Denzel's effort to make sound decisions.
A separate check corrected the inherited Mazinger Z launch paragraph in both
variants of the entry supplied by the user.

Q&A review covered all 22 pages differing from the main game: ten newly
translated pages, five wording adaptations and seven equivalent spelling or
punctuation changes. It also checked fifteen changed chapter strings. Special
Disc has no SR Points, sells only Parts in its Bazaar and changes replay and
completion rules. Those differences are preserved. I-Field costs 10 EN and
Barrier Field costs 5 EN in the corrected native help.

All 24 fixed panels (180 native lines) were checked for objectives, deadlines,
opponents and omissions. Another Side's chronology was corrected. Reviewed
name corrections run after editorial fixes and before layout.

## Format and memory checks

- Native font routines were matched by instruction structure before applying
  sixteen donor hook words. Reachable cave code and global references were
  relocated for Special Disc.
- The English cave and text pool use a new ELF load segment beyond native
  memory. Both startup heap address and kernel break are moved beyond it.
- Oversized menu strings use verified pointers or dedicated address-construction
  instruction pairs. Gameplay fields are protected.
- Spirit abbreviations and terrain labels use private glyph codes. Ordinary
  Japanese terrain characters retain their normal glyphs for dialogue.
- Library descriptions use actual donor glyph advances, with conservative
  limits of 560 / 280 / 544 pixels for robots / characters / glossary. Runtime
  scaling and scrolling still require emulator confirmation.
- Q&A retains its 97,776-byte decoded buffer. All pages are reparsed and text
  runs checked for bounds, overlap and preservation of words. IME data is unchanged.
- Briefings retain 56-byte text slots, 57-byte row stride, page counts, decoded
  sizes and compressed slots. The executable copies each line, terminates it
  and sends it through the menu renderer; no grid instruction changes are needed.
- Enlarged members occupy verified empty DMY disc space. ISO directory records
  and VMAP runtime entries are updated together. Disc length stays fixed.
- Verification reads all writes back and compares every other disc byte with
  the clean source. It checks final Library/help tables and modified VT1 records.
- The xdelta is decoded against the clean source; the reconstructed SHA-256
  must equal the output hash.

Machine-readable evidence: `work/output/SRW Z Special Disc English v0.2.1.json`
and `work/analysis/build-0.2.1-*.json`. The independent audit checks loaded memory,
relocated strings, every Library field, line widths and unchanged dialogue members.

## Inputs and provenance

Clean source SHA-256:
`c3bd8c1af4e411e5ab2ae2d4be877170b6ab1ea9b51fa62bc0b91a51ba1a2952`.

English donor: SRW Z English Original v0.9.85, SHA-256
`8299318b990baa3f811f3e8375b8d12315b71af350a72e01c29088584faa5f73`.
Its relocated members are read through VMAP. Library prose also uses the local
English master identified in the binding manifest. Reuse is bound to native
text identity and reviewed SP variations, not matching offsets alone.

Technical reference:
[dyzz/srwz-zh at f6673b1](https://github.com/dyzz/srwz-zh/tree/f6673b1edf697df3501fba3889e930815fd1b001/tools/special_disc).
Its archive tables, record strides, fixed-page formats and executable guards
informed this implementation. Chinese text, font and gameplay unlock patches
were not imported. The original CHD and both main-game projects are unchanged.

`work/glossary/` holds 1,078 inherited spellings with a source hash, researched
additions and reviewed corrections. Inherited entries are explicitly marked
as not fully researched. Noir 7 romanizations and several location spellings
remain provisional. Sources are linked beside the relevant terms.

## Visual evidence and remaining work

The supplied screenshots and approximate element coordinates are under
`work/ui/reference/`. English assets and text previews are under
`work/ui/english/`: **layout/asset previews, not emulator screenshots**.

Still Japanese or outside this pass:

- Story, battle and suspend dialogue, excluded from current work.
- Scenario-chart node summaries and narration in STAGE/HSFC/MTZSPROS.
- Squad-name presets and the Japanese name-entry dictionary.
- Embedded artwork outside the verified patches, including map/episode art
  and video text.

No percentage of the whole game's translation is claimed. Counts describe
bounded inventories and include aliases and variants. Donor prose has not
received a complete new meaning review.

Pending runtime checks: the supplied Library screens, font spacing, long
names, description/Q&A scrolling, briefings, Battle Viewer/Special Theater,
saves, load/continue and Data Link. The user deferred emulator testing;
this build does not claim those passed.
