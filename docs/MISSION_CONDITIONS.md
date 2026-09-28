# Mission-condition text

The supplied Operation End screenshot reads “Defeat all enemies” and “An allied
battleship is shot down”. These are stage-owned UI strings, separate from the
story dialogue. Version 0.2.19 translates their entire native table category.

## Coverage and review

Scan all 67 non-chart STAGE modules. There are 39 modules with three condition
tables: 20 story combat modules, 18 Challenge modules (39–56) and developer
module 66. The other 28 contain no such initializer. The tables have 152 pointer
entries: 43 victory, 70 defeat and 39 extra. Of 61 unique native strings, 60 are
translated at 114 sites. One fullwidth “???” identity remains native at 38 sites.
The developer module's “No special requirements” extra condition is translated.

The full draft and compact layout each received an independent 61/61 meaning
review. Fourteen variants shorten or format the approved full wording. The
compact reviewer restored “funds earned” to four loss conditions to distinguish
earnings from the current balance. Bandock's five-turn deadline applies to both
the initial enemies and Bandock. Assault Aquarion's destruction is a defeat
trigger. Glossary canonicalization runs after these meaning fixes.

Where the source omits a turn phase, exact one-attack mechanics or how the
deployment limit is enforced, English does not invent that information.

## Native ownership

`DATA/STAGE.BIN` has 68 compressed chunks. `HEDBDY/HB.BIN` at `0x5170` contains
69 boundary words. Chunks load at `0x8045f0`; chunk 0 is the already-translated
Scenario Chart. The archive is 527,552 bytes and retains all original offsets.

The initializer loads a table address through a MIPS LUI/ADDIU pair and stores
it to one of these globals:

| Global | Meaning |
| --- | --- |
| `0x61e1b0` | Victory pointer table |
| `0x61e1b8` | Defeat pointer table |
| `0x61e1c0` | Extra condition pointer table |

`inspect_mission_conditions.py` verifies the exact instruction pattern, address
bounds and source-string hashes. `work/ui/mission-conditions/native-inventory.json`
freezes all code/table/text bindings. It exports only this UI category, no story
dialogue. The compiler changes only those bound display pointer words. It keeps
the native strings and the phase-selection mapping at global `0x61e1c8` intact.

Restoring the 114 condition pointers plus the 27 previously translated chapter
13 roster-name pointers yields byte-identical native decoded story modules.
All other 28 modules retain their exact compressed bytes. The chart chunk is
covered by its existing independent audit. English lives in the persistent pool
and adds 3,352 bytes; no new executable rendering hook is needed.

## Layout evidence

Native printer selection is at executable addresses `0x37fa68` and `0x37fa78`;
the text row counter at `0x3d4af0` returns newline count plus one. Victory text
pointers occupy four words at window offsets `+0x80..+0x8c`, followed by their
row/color data. Defeat occupies `+0xa0..+0xac`. Body loops at `0x3801f0..0x380244`
and `0x380258..0x3802ac` each render four rows. More rows could overwrite the
adjacent fields, so the compiler rejects an entire table needing over four rows,
even when a stage normally selects only a subset of its entries.

Body text starts at logical x=118; a conservative 460-unit line ends at x=578,
inside the panel. Width comes from the installed 69-glyph Latin advance table,
plus native punctuation fallback. Rows advance 14 native field units. All 117
table groups satisfy the four-row bound; the longest line is 460 units.

The funds comparison `<350,000` is a displayed less-than glyph, encoded as
fullwidth CP932, not a numeric angle-bracket command. Final-disc readback checks
the displayed glyphs, all thresholds, punctuation and full reviewed words.

`preview_mission_conditions.py` writes 39 reconstructed pages and four contact
sheets. Latin glyph masks/advances match the installed atlas; frames and native
punctuation use approximations. They are not emulator captures. The original
screenshot is `work/ui/mission-conditions/reported-operation-end.png`.

## Build and checks

Run each author/compiler/preview script dry before using `--write`. Reviewed
targets are in `work/translation/en/mission_conditions.json`; both reviews and
their drafts remain alongside it. The compression cache is keyed by complete
decoded bytes plus native flags, and every reuse strictly decodes to the expected
data. All 39 updated streams fit their original allocations (minimum headroom
81 bytes); all original table bounds and decompressed lengths are unchanged.

Six read-only tests cover allowed display pointers; rejected opcode, native
text, hidden pointer and roster-member edits; less-than glyph encoding; damage
threshold punctuation; all reviewed layouts; and rejected overflow/truncation.
The independent finished-disc audit reads every translated pointer and string,
checks source/review ancestry and preserves all hidden placeholders. Earlier
component audits continue to run. See BUILD_0.2.19.md for verified output hashes.

Emulator testing remains pending by user choice. When it resumes, check
Operation End and mission-status windows, phase changes, the four-row Challenge
rules and comparison symbols. Binary/static checks do not establish runtime
acceptance.
