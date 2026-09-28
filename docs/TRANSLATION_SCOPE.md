# Translation scope and remaining work

Objective: **translate everything to English except story dialogue**.
This ledger is a progress record, not a narrower replacement for the objective.
The goal remains active until the in-scope Japanese surfaces are handled.
Emulator testing is pending by the user's explicit choice; this does not block
translation or binary checks.

| Surface | Current state | Remaining work |
| --- | --- | --- |
| Library and standard menus | Included since 0.2.0; 4,995 Library and 7,883 menu/name fields | Broader editorial review and runtime acceptance |
| Strategy Q&A | 102 pages and 264 chapter fields included in 0.2.1 | Runtime layout acceptance |
| Selection and Challenge briefings | All 24 fixed panels included in 0.2.1; introduction/Story Mode alignment in 0.2.15; shared Challenge confirmation translated and centered in 0.2.22 | Runtime layout acceptance |
| Squad-name presets | All 113 included in 0.2.2 | Runtime acceptance |
| Deployment/squad UI | 96 late-table entries, 12 tournament roster names, four word sprites and compact heading in 0.2.18; all five deferred composed-help fragments plus nine related text fixes and two confirmation word sprites in 0.2.24 | Runtime layout acceptance for naming, formation, Join reports and shared button states |
| Tactical counters and movement footer | Five Sq suffixes, A/G/S terrain cells, corrected movement templates, Will label and seven spacing adjustments in 0.2.20 | Runtime acceptance; 44 related formation/help/header selector targets independently verified |
| Terrain-rating labels | All 11 rows use the donor AIR/GND/SEA/SPC micro-glyphs and full-width blank cells in 0.2.21 | Runtime acceptance on pilot, mech, weapon and equipment screens |
| Intermission and Bazaar artwork | 26 reviewed word tiles, 12 scrolling-fragment layouts and all three pictured Bazaar slogan fields in 0.2.23; source-matched image reuse from SRW Z | Runtime acceptance, especially the composed SETUP heading, highlighted/disabled colors and scrolling banner |
| Mission conditions | All 60 distinct texts / 114 pointers in 39 modules in 0.2.19; victory, defeat and extra tables, including 18 Challenges | Runtime phase-selection and layout acceptance; 38 hidden “???” placeholders intentionally native |
| Map labels | All 200 slots included in 0.2.2 | Many are development labels rather than normal player-facing text |
| Globe location cards | All 13 native captions included in 0.2.16 after independent meaning review | Runtime legibility/timing acceptance; see WORLD_MAP_TITLES.md |
| Episode-entry title cards | All 21 native selector slots covered in 0.2.17; 20 translated images, one native English image, shared Ep. number heading | Runtime layout/animation acceptance; see EPISODE_TITLES.md |
| Scenario Chart overlay | 131 titles, 128 labels, all 131 summaries and five key hints in 0.2.3 | Audit two terminator text fields and chart artwork; runtime layout acceptance |
| Save/load summaries (HSFC chunk 0) | 65 of 66 records included in 0.2.9 after independent full-meaning and compact-layout reviews | ID 27 retains native text until full meaning fits; runtime acceptance; see SAVE_SUMMARY_RESEARCH.md |
| Narration (MTZSPROS) | All ten entries included in 0.2.5 after full meaning and compact-layout review | Runtime layout/timing acceptance; all nontext commands retained; see NARRATION_RESEARCH.md |
| Battle captions (SRVC and COMPDATA battle text) | 0.2.15 retains 1,917 reviewed SRVC captions at 4,870 occurrences | 23,605 indexed identities / 54,392 occurrences remain native, including the statically suppressed placeholder at 382 occurrences. COMPDATA battle text, speaker-name layout and 180 unbound tail identities need audit; see BATTLE_CAPTION_RESEARCH.md |
| Pre-title battle demo | All 20 series-title graphics and 61 separate speaker-name fields in 0.2.10; pictured Rocket Punch call and two variants included | Other demonstration battle captions remain subject to SRVC coverage above; emulator layout/timing acceptance pending; see ATTRACT_DEMO_RESEARCH.md |
| Suspend messages | All 296 unique texts / 379 occurrences in 57 scenes have independently reviewed English drafts | Prove encoding, buffer ownership, display layout and relocation before installing; currently native in ISO; see SUSPEND_RESEARCH.md |
| Embedded text in artwork | Front-end, Library buttons, shared art, four headings, globe and episode title cards included | Audit remaining KVMAP/MAPMODEL, logos, credits and video text |
| Stage-contained UI or instructions | Chapter 13's 12 tournament squad/ship names and all bound mission-condition tables included through 0.2.19 | Inventory other instruction categories; separate UI from excluded story dialogue before patching |
| Japanese input dictionary | Unchanged functional data | Audit visible name-entry labels and Latin input; do not count internal kana data as untranslated prose |
| Story dialogue | 0.3.0 installs all 45 chunks: 7,511 rows, 71 captions, chunk-66 scene; labels native | In-game rendering check; label usage audit |

Story protection through 0.2.17 was verified at **chunk** level: only the chart
overlay in STAGE chunk 0 changed. Version 0.2.18 also redirects 27 typed roster
name pointers in chapter 13. All other decoded bytes in that chapter, including
dialogue and gameplay data, remain identical. The other 66 story chunks remain
compressed-byte identical. Version 0.2.19 adds 114 typed condition pointers in
39 modules. Restoring those and the 27 roster pointers reproduces every native
decoded story/gameplay byte; the other 28 story chunks remain compressed-byte
identical. Calling the whole STAGE member unchanged is inaccurate.

The inherited Library prose is translated but has not all received a fresh
meaning review. Known terminology corrections are applied by the glossary
script after editorial review. Runtime testing and a visual inventory may find
additional Japanese surfaces; add them here rather than redefining completion.

Version 0.2.24 translates all five previously deferred naming/formation help
fragments as complete compositions with their colored overlays. It repairs
the related label, two descriptions, two Join headers and four report fields,
and replaces the shared OK/Cancel word tiles. All other 0.2.23 data is retained.

Version 0.2.23 applies indexed-image replacements to the reported intermission,
Bazaar and status/banner graphics. It preserves Special Disc-only mission
artwork that occupies space used by the main game's English patch. Three
fixed Bazaar banner fields also receive the reviewed English slogan. These
are UI fields inside stage records, not dialogue; all other decoded bytes
remain protected by the existing checks.

Version 0.2.22 translates the one shared question used by all 18 Challenge
briefings: “Attempt this mission?” Its late COMPDATA pointer slot was outside
the earlier menu pass. One text slot and one x-position word change; all
other decoded menu data, executable bytes and archives match 0.2.21.

Version 0.2.21 applies the main game's terrain micro-glyph technique to all 11
native Air/Ground/Sea/Space rating rows. The existing private glyphs now replace
the ordinary ASCII words, and full-width blank cells restore the native rating
spacing. These are exact donor images, with no changes to rendering code,
rating values, coordinates or movement-only A/G/S labels. See TERRAIN_ROWS.md.

Version 0.2.20 addresses the four tactical UI screenshots. It repairs a fixed-byte
movement formatter corrupted by shorter ASCII template substitutions and adds
the small labels skipped by the earlier minimum-length text scan. The 44 related
formation, settings-help and list-heading texts already existed in 0.2.18; the
new audit follows their native selectors to English memory. The screenshot build
was not confirmed during this pass. No new alternate Japanese dispatch path was
found. The five deferred COMPDATA naming fragments are separate from the five
executable squad suffixes translated here. See TACTICAL_UI.md.

Version 0.2.19 covers the complete native mission-condition tables found across
all 67 non-chart modules. The scan binds 61 unique texts: 60 are translated;
the remaining identity is the hidden “???” placeholder. Every full translation
and the 14 compact/layout variants received independent meaning review. The
English preserves turn limits, funds earned, damage/kill thresholds and all
exceptions; it does not infer missing turn phases or attack mechanics.
Story dialogue, event logic and pending battle/suspend drafts remain untouched.
See MISSION_CONDITIONS.md for native ownership and four-row layout evidence.

Version 0.2.18 covers the reported deployment hint, tournament squad names,
Reserve button and overlapping Squad Setup heading. Its 113 entries passed
meaning review before compact layout and glossary checks. Five dynamic naming
fragments remain deferred; sort/sub-info “positions” retain the literal source
meaning pending runtime confirmation. All prior translations are retained.

Version 0.2.17 covers every episode-entry title selector, the shared ordinal
heading and the native duplicate-image defect on Prologue. Full title meanings
match the independently reviewed Scenario Chart wording. Story dialogue and
pending battle/suspend drafts stay unchanged; emulator testing is pending.

Version 0.2.16 adds all 13 globe location-title images, preserving every other
map byte and all earlier translations. The pending battle/suspend drafts remain
outside this location-only update. Emulator testing remains pending.

Version 0.2.15 fixes the reported Story Mode introduction overflow, aligns
clear-status markers in one column, and centers the confirmation questions
using the English font advances. All paragraph words and translation coverage
are retained. Static previews and binary checks do not replace the pending
emulator test. Separately, IDs 960-1199 have 236 new reviewed drafts at 694
occurrences and four exact baseline retentions; these drafts are not installed
in this alignment build. The next unauthored consecutive range begins at 1200.

Version 0.2.14 adds 239 reviewed captions from native IDs 720-959 at 547
occurrences. One baseline identity is retained exactly, as are all earlier
release entries. Three compact versions have separate meaning approval;
the spelling pass makes no changes. Only SRVC caption/segment payloads change
from 0.2.13. The next consecutive range begins at 960.

Version 0.2.13 adds 215 reviewed captions from native IDs 480-719 at 427
occurrences. Twenty-four baseline identities are retained; caption 600 stays
native pending supported spelling of Gain's birth name. The next range begins
at 720. Three Library meaning fixes precede scoped spelling corrections in
16 Library and two menu fields. The Meteor song title is preserved.

Version 0.2.12 adds 231 reviewed captions from native IDs 240-479 at 467
occurrences. Seven baseline identities are retained. Caption 323 remains
unresolved; 444 is preserved as a production placeholder with positive native
suppression evidence in `work/analysis/battle-placeholder-444-audit.json`.
Neither counts as translated. The next consecutive range begins at 480.
Asakim Dowen and Raster Edge follow researched, source-bound spelling rules;
the Library also receives seven previously pending Domepolis corrections.

Version 0.2.11 adds 229 reviewed caption identities from consecutive native
IDs 0-239 at 1,114 occurrences. Eleven earlier identities fall within those
slices; only caption 169 changes through an explicit reviewed amendment.
Existing weapon and settlement spellings stay consistent across battle,
Library and menu text. IDs 240-479 were completed in the next release under
`BATTLE_CANDIDATE_NEXT_BATCH.md`.

Version 0.2.10 fixes the separate OP demo title atlases and name records and
adds three reviewed Rocket Punch shout variants. The previous 1,000 caption
entries retain exact wording and layout. No PSS movies are altered.

Version 0.2.9 adds five independently approved save summaries and corrects
Takeshi Tsukikage in two native-bound Library fields. All earlier 60 approved
recaps and 1,000 battle-caption entries retain their wording. Suspend drafts
are consolidated separately in `work/translation/en/suspend_reviewed.json`;
this is meaning coverage, not installed English coverage.

Version 0.2.7 corrects known names and ability terms in 148 Library fields,
52 menu/name fields and two Q&A pages. Corrections use native field or owner
identity, with explicit protection for ordinary saber weapons. The dry runs
caught and rejected Fire Saber, Tornado Saber and Saber Claw false matches.
Version 0.2.8 adds source-scoped corrections in 45 Library fields, 15 menu
fields and seven chart summaries. All 877 caption disagreement rows and 123
new captions are now reviewed and included; the other candidates remain
unapproved. The largest caption uses 91 of the native buffer's 96 bytes.

The 110 main-game chart summaries were bound by byte-exact native text and
reviewed for 0.2.3. Some donor translations have moved: follow the donor's
pointer table, never assume English remains at the Japanese source offset.
The compiler redirects SP pointers at `0x14864` to new English memory while
preserving the native string bytes. Those unreachable old strings are not a
remaining player-facing translation surface. The unrelated `stage_synopsis.json`
export contains short HSFC save summaries, including visibly truncated entries,
and must not replace the full chart texts.
