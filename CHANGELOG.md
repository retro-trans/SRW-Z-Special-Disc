# Changelog

## Publication packaging — 2026-09-28

- Prepare v0.3.0 for the SRW-Z-Special-Disc GitHub repository with installation instructions, coverage, limitations and release notes modeled on the main SRW-Z project.
- Publish English-only review exports, excluding original script corpora, extracted assets, local receipts and private caches. Add an index audit and publication workflow.
- Document both DVD and single MODE1/2048 data-track CHD extraction; the local source uses the latter container.
- Match the catalog importer's core-file checksum scope; verify optional documentation assets separately on upload.
- Use Retro Trans canonical release metadata, full patch reconstruction and raw-image hash aliases. The v0.3.0 game bytes are unchanged; the distributed patch is re-encoded without local paths.

## 0.3.0 — 2026-09-27

- First build with English story dialogue, on top of 0.2.24 (all its
  non-story work retained). All 45 story chunks installed: 7,511 dialogue
  rows, 71 scene captions and the chunk-66 demo scene. See docs/BUILD_0.3.0.md.
- Text is packed inside each chunk's native Japanese text region and every
  pointer repointed and read back; 796 rows use independently reviewed
  shorter fits (86 review corrections) to keep boxes at three lines and
  chunks within budget. Labels that may be lookup keys stay native.
- STAGE.BIN grows to 548,272 bytes and moves to reserved disc
  space (ISO directory + VMAP updated); HB.BIN's chunk table is rewritten.
  Every other ISO byte equals 0.2.24. xdelta reconstruction verified.
- Rank titles follow the SRW Z rulings; name rules now also apply to fits.
- In-game rendering of story text is not yet verified.

## 0.2.24 — 2026-09-27

- Replace the shared squad Confirm/Cancel artwork with OK/Cancel image tiles.
- Translate the missing composed naming and formation help, preserving red
  emphasis and reserving measured gaps between the colored text pieces.
- Shorten two naming descriptions and both Join headers to fit their panels.
  Separate Sq from the live squad number and use action wording in the
  confirmation/cancellation report.
- Pass 16-entry independent meaning review, bounded component preflight and
  finished-disc audit. Verify exact patch reconstruction and all 313 recorded
  inputs; freeze a 317-entry input archive. Emulator testing remains pending.
  Story dialogue and game logic stay unchanged. See BUILD_0.2.24.md.

## 0.2.23 — 2026-09-27

- Apply SRW Z's indexed-image replacement method to 26 intermission, Bazaar,
  status-bar and scrolling-banner tiles. Reuse 15 matching donor tiles;
  preserve native palettes, button tinting and all unrelated graphics.
- Relocate the banner's English fragments into unused Special Disc texture
  space and align all 12 sprite records, titles and three digit styles.
  Keep the MISSION portion of both intermission headings in its native suffix
  region for composed headings; its in-game appearance remains unverified.
- Translate all three copies of the pictured Bazaar slogan to “Does willpower
  decide the outcome?” Preserve all other stage dialogue and gameplay bytes.
- Pass independent meaning review, component preflight and finished-disc audit.
  Verify exact patch reconstruction and all 308 recorded inputs; freeze a
  312-entry input snapshot. Emulator testing remains pending by user choice.
  See BUILD_0.2.23.md.

## 0.2.22 — 2026-09-27

- Translate the shared Challenge briefing confirmation to “Attempt this
  mission?” after independent meaning review. This late-table field was outside
  the earlier menu inventory and is shared by all 18 Challenge briefings.
- Center the question using the installed English font's 210-unit width.
  Change one 32-byte text slot and one final x-position instruction; preserve
  pointer selection, measurement/draw calls, Yes/No controls and all other data.
- Pass four focused checks covering the English selector target, centering,
  rejection of the original Japanese prompt and protection of adjacent bytes.
  Emulator testing remains pending by user choice. See BUILD_0.2.22.md.
- Verify the finished ISO and exact reconstruction from the 5,052,921-byte
  patch. The independent audit confirms the two intended changes and all
  earlier translations. Verify all 298 recorded inputs and preserve the
  302-entry input archive with exact readback.

## 0.2.21 — 2026-09-26

- Apply SRW Z's terrain micro-glyph technique to every one of the 11 native
  Air/Ground/Sea/Space rating rows. Replace ordinary-text labels with the
  existing AIR/GND/SEA/SPC full-width image cells, separated by full-width
  blank cells. Preserve the original seven-cell structure and 16-byte slots.
- Reuse the exact donor artwork and installed glyph renderer. Keep rating
  values, drawing coordinates, Japanese story glyphs, movement-only A/G/S
  fields and all other translations unchanged. No new code or art is injected.
- Independently approve all four meanings and validate exact donor pixels,
  empty spacer artwork, complete row coverage and protected executable bytes.
  Add six focused regression tests and an exact-art static preview. Emulator
  testing remains pending by user choice; see BUILD_0.2.21.md.
- Verify the finished ISO and exact reconstruction from the 5,052,912-byte
  patch. Only the eleven approved text slots differ from v0.2.20; every other
  translated archive and all VT1 textures match. Verify all 292 build inputs
  and preserve the 296-entry input snapshot with exact readback.

## 0.2.20 — 2026-09-26

- Translate five standalone squad suffixes to Sq and three fixed-width terrain
  markers to A/G/S (Air/Ground/Sea). Use Will for the cramped Morale footer label.
  Independently review all 13 text/template entries, including their encodings.
- Repair movement templates shortened by an earlier in-place translation.
  Preserve the native two-byte cells, four-byte number insertion, byte-eight
  terminator and six-byte terrain placeholder. Keep AirOnly/GndOnly/AirSea.
- Adjust seven coordinate words to separate the Forces count, slash, enemy
  count, Move label, movement value and Pilot label. Preserve count values,
  comparison colors, sorting, terrain eligibility and every gameplay instruction.
- Trace five native selector routines and verify 44 existing English labels:
  three formation names, three diagram labels, 22 settings descriptions,
  15 list headings and the Group Formation hint. These were already translated
  in 0.2.18; retained Japanese source strings are not active display targets.
- Pass seven focused regression tests, including all 1,101 movement/terrain
  combinations and rejection of the old shortened templates. Add a measured
  static preview. Story dialogue stays unchanged; emulator testing remains
  pending by user choice. See BUILD_0.2.20.md for finished-artifact verification.
- Verify the finished ISO and exact reconstruction from the 5,052,908-byte
  patch. Only the 20 approved executable spans differ from 0.2.19; every other
  translated member and all VT1 textures match. Verify all 285 build inputs and
  preserve the 289-entry input snapshot with exact readback.

## 0.2.19 — 2026-09-26

- Translate the reported victory and defeat conditions: “Defeat all enemies”
  and “An allied battleship is shot down”. Cover all 60 distinct condition
  texts at 114 pointer sites in 39 modules, including all 18 Challenges and
  the developer test module. Preserve 38 hidden “???” placeholders.
- Bind the category to native victory/defeat/extra table assignments, not
  dialogue punctuation. Redirect display pointers to persistent English
  memory, retaining all source strings, event commands and mission logic.
- Review every full translation before shortening; independently approve
  14 compact/layout variants, then apply glossary spelling. Preserve funds
  earned, deadlines, thresholds, reinforcement rules and deployment limits.
- Keep every group within four renderer rows and each line within 460 font
  units. Recompress all affected modules inside their original allocations.
- Add six scope/encoding/layout tests, final-disc pointer and glyph readback,
  and 39 static layout previews. Keep story dialogue unchanged and emulator
  testing pending by user choice. See BUILD_0.2.19.md for release validation.
- Verify the finished ISO and exact reconstruction from the 5,052,893-byte
  patch. Only STAGE and the executable differ from v0.2.18; all previous
  English-pool bytes and the entire VT1 texture archive match. Verify all
  277 build inputs and preserve the 281-entry input snapshot with readback.

## 0.2.18 — 2026-09-26

- Translate the pictured deployment hint and 95 related late-table menu entries.
  Five dynamic naming fragments remain native until their composition is verified.
- Translate all 12 names in the tournament roster: QF Group 1–8, Round 1 Losers,
  Argama, Minerva and King Beal. Redirect only 27 typed display-name pointers;
  preserve all dialogue, squad membership, positions and event commands.
- Translate New Squad, To Reserve, To Squads and Deployed in the squad word
  sheet. Preserve palette banks, all other sprites and archive geometry.
- Shorten only the squad screen heading to Squads, leaving space for NEXT.
  The Squad Setup menu command retains its existing wording.
- Independently review all 113 entries, including 20 approved compact forms.
  Apply glossary spelling after meaning review and freeze the rendered tiles.
- Add five negative/ownership tests and an independent final-disc audit.
  Verify exact reconstruction from the 4,815,171-byte patch and retain every
  VT1 byte from v0.2.17. The longest new hint is within the 560-unit limit.
  Verify all 263 receipt-listed inputs and freeze the 267-entry input snapshot.
  Emulator testing remains pending by user choice. See BUILD_0.2.18.md.

## 0.2.17 — 2026-09-26

- Translate all 21 episode-entry title slots: author 20 English images and
  preserve the already-English “at the risk of pride” image exactly.
- Translate the shared episode-number heading to “Ep.” while preserving all
  ten native digit tiles. Keep title/number selection and animation data intact.
- Independently review all 21 titles across 24 active stage bindings. Correct
  the native duplicate image for Prologue using its COMPDATA selector binding.
- Preserve full wording and center title images with the native pixel aspect.
  Keep original palettes, texture sizes, archive allocations and runtime tables.
  Two small allocations use fewer antialias shades without changing the words.
- Add independent artwork readback, pixel/overflow/compression guards, and a
  comparison with the previous release outside the 21 new texture spans.
- Verify the finished ISO and exact reconstruction from the 4,801,254-byte
  patch. All 254 receipt-listed inputs match; freeze and read back the
  258-entry, 10,864,640-byte input snapshot.
- Keep story dialogue and pending caption/suspend drafts untouched. Emulator
  testing remains pending by user choice. See BUILD_0.2.17.md for validation.

## 0.2.16 — 2026-09-26

- Translate all 13 globe location cards shown before dialogue, including
  Western Gallia Continent and the three Special Disc base/region additions.
  Bind every caption to its native image hash and reviewed full English text.
- Review all 13 native images independently; use Federation Forces for the
  general military term and apply the locked Domepolis spelling afterward.
- Center each full caption within its native 512×32 image. Preserve original
  palettes, English subtitles, map geometry, offsets, archive size, all other
  decoded bytes and all 188 unrelated compressed map members.
- Add pixel-orientation, packing and overflow guards plus independent final
  disc readback. Keep earlier translations and panel alignment unchanged.
- Verify the finished ISO, exact reconstruction from the 4,781,579-byte patch,
  and all 247 build inputs. Freeze a 10,843,583-byte input snapshot. A whole-disc
  comparison confirms only MAPMODEL differs from v0.2.15.
- Story dialogue and pending battle/suspend drafts remain untouched. Emulator
  testing remains pending by user choice. See BUILD_0.2.16.md for verification.

## 0.2.15 — 2026-09-26

- Align the episode-introduction and cleared-stage panels from the user's
  screenshots. Move headings and body labels to a shared left margin, and
  rewrap all six introduction pages within 500 units. Preserve every word,
  the nine-row page format and all eighteen Challenge briefings.
- Place the cleared-stage dashes and CLEAR! markers in a fixed column.
  Keep their native status logic, colors and row ownership. Other reward
  modes retain the original append path.
- Center the three known English confirmation questions using actual glyph
  advances, with native measurement as the fallback for other text or modes.
- Pass 48 bounded instruction-model and negative-guard cases across four test
  methods. Inspect two reconstructed previews using the actual Latin atlas.
  Final ISO/patch readback passes, including all six full paragraphs and the
  unchanged Challenge panels. Correct the auditor's comparison to use the
  established glossary spellings and previous-release words; preserve the
  original assembly receipt and record the verification-only hash change.
- Verify all 236 acceptance-receipt inputs and freeze them with the receipt
  and audits in a 10,824,067-byte snapshot. Exact patch reconstruction passes;
  all bytes outside planned writes remain native. Details are in BUILD_0.2.15.md.
- Keep the v0.2.14 translation coverage, including the pre-title demo fixes.
  The 236 newly reviewed caption drafts remain separate for the next translation
  build. Story dialogue is unchanged; emulator testing remains pending.

## 0.2.14 — 2026-09-26

- Add 239 independently reviewed battle captions at 547 occurrences from IDs 720-959.
  Retain caption 807 and every v0.2.13 release entry exactly. Coverage reaches
  1,917 identities / 4,870 occurrences; the translation remains incomplete.
- Approve three compact captions separately after full meaning review. All new
  captions fit two rows and the existing buffers; inspect actual-atlas previews.
- Pin independent review and compact-approval bytes, and reject malformed,
  empty or oversized layouts. All 56 independent preflight cases pass.
- Build the ISO and 4,491,757-byte patch. Exact reconstruction and independent
  final-disc readback pass. All 3,773,343,084 bytes outside planned writes remain
  native. Only SRVC caption and segment payloads differ from v0.2.13.
- Verify all 219 receipt-listed inputs and preserve them with the receipt and
  audits in a 10,599,960-byte snapshot. Story dialogue is unchanged; emulator
  testing remains pending by user choice.
- Establish the native suspend display path and parser limits in a read-only
  audit. Confirm that the existing English font hooks serve it and pass 419
  bounded spacing checks. Storage, visible capacity and integration remain unfinished.

### Unreleased drafts after 0.2.14

- Save two 80-ID slices for 960-1119: 157 new full drafts and three exact
  retentions across 458 assigned occurrences. Source, baseline and literal
  break checks pass. Independent meaning review now passes all 160 IDs;
  separate compact reviews approve 967, 980 and 1116 without losing meaning.
- Research the scoped Orguss addresses and King Gainer startup interference.
  Preserve caption 1104's omitted agents and full caption 1116 for review.
  All 219 receipt-listed v0.2.14 inputs remain unchanged after these saves.
- Author and independently review 1120-1199: 79 new full translations at
  243 occurrences, plus exact retention 1174 at two occurrences. Approve a
  separate compact 1122; preserve musical notes in 1145/1146 for font checking.
- Record sourced Detector II, Vascud Crisis and Gagundura terms, corrected
  Anemone/Dominic profile notes, and the scoped Library spelling follow-up.
  The combined unreleased batch has 236 new texts at 694 occurrences.
- Add a reproducible suspend substitution audit. All 296 encoded drafts omit
  the dollar byte used by all fourteen native dictionary keys; none expands
  under that dictionary. The 174-byte peak remains a requirement, not an
  approved storage capacity. Visible layout and installation remain pending.

## 0.2.13 — 2026-09-26

- Add 215 reviewed battle captions at 427 native occurrences from IDs 480-719.
  Preserve 24 baseline translations exactly. Total installed coverage reaches
  1,678 identities / 4,323 occurrences; the translation remains incomplete.
- Keep caption 600 native pending verified spelling of Gain's birth name.
  Earlier deferred captions 323 and 444 remain native.
- Apply three independently reviewed Library meaning fixes and six approved
  Overfrozen forms before the source-bound Overfreeze, METEOR and Hughes Gauli
  spelling pass. Compare all 4,995 Library fields against frozen v0.2.12:
  only the 16 intended fields change. Two menu terms change; Meteor music is
  protected. Narration wording and layout are unchanged.
- Preserve all pre-title demo fixes, including Koji's pictured Rocket Punch
  shout. Inspect reconstructed caption layouts using the actual Latin atlas;
  the complete release still fits the existing 96-byte caption buffers.
- Add guarded release merging, persistent reviewed Library corrections and
  receipt-input verification. Story dialogue is unchanged; emulator testing
  remains pending by user choice.
- Build the ISO and 4,486,385-byte xdelta. Exact patch reconstruction and
  independent final-disc readback pass; all 3,773,353,324 bytes outside planned
  writes remain native. Demo and narration archives match v0.2.12 exactly.
- Verify all 82 tool / 109 translation / 15 glossary input hashes and preserve
  them with the receipt and audits in a 10,036,282-byte input snapshot. Every
  archive member reads back exactly; external game/font dependencies stay external.

### Unreleased caption drafts after 0.2.13

- Save three 80-ID author slices for 720-959: 239 new full drafts and one exact
  retention across 550 native occurrences. Root source, baseline and literal
  break checks pass. Subsequent independent reviews are incorporated in 0.2.14.
- Keep full drafts754/768 for later compact-layout review and retain documented
  ambiguity and wordplay limitations. Add sourced terminology notes without
  changing the frozen release. All 206 v0.2.13 receipt inputs still match.

## 0.2.12 — 2026-09-26

- Add 231 independently authored and reviewed battle captions at 467 native
  occurrences, covering consecutive IDs 240-479 in three 80-row slices.
  Seven previously approved identities are retained. Installed coverage is
  1,463 identities / 3,896 occurrences; the translation remains incomplete.
- Keep caption 323 native because its coined term lacks a substantiated
  rendering. Preserve all 382 copies of production placeholder 444: both
  native caption fill paths skip it before reading its text. This static
  finding does not claim the prior caption clears or replace emulator testing.
- Apply Asakim Dowen and Raster Edge after meaning review: four prior caption
  identities, four Library fields, three menu fields, nine system labels and
  one narration record. Seven other Library fields adopt settled Domepolis.
  Source bindings protect unrelated names; all other words are retained.
- Replace one unsupported colon in caption 270 through an independently
  reviewed punctuation supplement. Full wording and the question are retained.
- Keep all pre-title demo fixes. Unrelated Library edits refresh dependency
  hashes only; every approved demo label, source binding and layout field must
  still equal the original reviewed manifest.
- Add frozen-baseline and unhandled-amendment guards for the next caption
  batch. Historical authors, reviews, release inputs and ISO files remain
  unchanged. Story dialogue is unchanged; emulator testing remains pending.
- Build the ISO and 4,482,107-byte xdelta; exact patch reconstruction and
  independent final-disc readback pass. All 3,773,363,564 unplanned bytes
  remain native, and all 76 tool / 99 translation / 14 glossary input hashes
  match the receipt. The pre-title demo archive is unchanged from v0.2.11.

### Battle-caption preparation after 0.2.12 (released in 0.2.13)

- Independently author and review the next three 80-ID slices, 480-719,
  covering all 496 native occurrences and their complete sequence context.
  Preserve 24 existing translations exactly. The consolidated candidates
  contain 215 new English captions at 427 occurrences; caption 600 remains
  native pending substantiated spelling of Gain's birth name.
- Preserve missing ranks, relationships, unfinished clauses and support
  direction. Resolve late-DESTINY Mu's native rank as Captain, and record
  METEOR / Overfreeze terminology with sources and a whole-corpus scan.
  Existing Library/menu spelling follow-ups are recorded, not applied yet.
- Independently review a compact version of caption 604 retaining the
  Citizens' Charter, Article 9 and Exodus Law alias. All 215 candidate texts
  pass two-row layout and encoding readback; the longest needs 89 of the
  existing 96 buffer bytes. The tilde uses the verified native glyph exception.
- Save the reviewed candidates separately from the release. They are not
  installed in v0.2.12. Preserve that build's receipt-listed inputs and final
  audits in a verified 9,536,238-byte input snapshot ZIP; external game/font
  dependencies are not bundled. Story dialogue and emulator status are unchanged.
- Check 15 distinct malformed/stale input scenarios. Fix compact approval
  validation to reject a string-valued false; boolean false also rejects.
  The real reviewed output remains unchanged after the guard correction.

## Unreleased — story dialogue translation (started 2026-09-26)

- Story dialogue is now in scope at the user's request. `tools/extract_story.py`
  exports 7,509 dialogue rows from STAGE chunks 1-67 (44 non-empty scenario
  chunks) into 117 slices of up to 80 rows, bound by chunk, native offset,
  source SHA-256 and absolute pointer sites (base 0x8045F0). Offset order
  matches script order in every chunk. Japanese source stays in the ignored
  cache; 773 other referenced strings (scene captions, conditions, map names)
  are exported separately for a later pass.
- `tools/story_glossary.py` merges all project glossaries (1,177 terms) for
  translators; `work/translation/en/story_speakers.json` maps all 277 speaker
  lines, with six generic-role overrides.
- `docs/STORY_TRANSLATION_BRIEF.md` defines the agent contract; outputs go to
  `work/translation/en/story/`. `tools/check_story.py` validates coverage,
  placeholders, ASCII and length. No ISO is built yet: relocation, wrapping
  and dialogue-box layout still need implementing and verifying.
- All 7,509 rows drafted in 117 slices (0 unresolved) by source-bound agents;
  `check_story.py` passes coverage, placeholder, `{tm}` and ASCII checks.
  Fourteen native runtime-value tags (＜ｔｍ＞…) are kept as `{tm}` markers and
  must be restored verbatim by the build.
- Independent meaning review of every row (`docs/STORY_REVIEW_BRIEF.md`):
  28 corrections, including reversed subjects, a conditional read as past,
  an invented condition, the colony-drop allusion, plural address, a
  misgendered group, and compact variants for seven overlong rows.
  `apply_story_review.py` rejects stale `was` values and writes
  `work/translation/en/story_reviewed/`; drafts stay immutable. One review
  file that covered 66 of 80 rows was rejected and redone.
- Terminology research (`work/glossary/story-research.json`): 108 terms, six
  rank recommendations and 277 speaker records (160 with established
  gender, 117 left unknown rather than guessed). Two proposals rested on
  katakana absent from the game text; Poe Aijee and Luzianna were re-verified
  against Gundam sources. The Saint Reagan proposal was not adopted: the
  reviewed glossary spelling Saint Regan stands.
- Name pass `tools/story_names.py` (after review, as BASE_RULES requires):
  reviewed spelling corrections plus 21 source-scoped rules in
  `work/glossary/story-name-rules.json`; each fires only when the native row
  contains the named term. 58 rows changed; output in
  `work/translation/en/story_final/`. Rank titles are unchanged pending a
  project decision.
- Rank titles follow the SRW Z rulings (E:/Projects/SRW Z name_sweep.py):
  大尉 Captain per character with Lt. Quattro/Lt. Amuro, 中尉 Lt. before a
  name, 少尉 Ensign, 准将 General. Scoped rules in story-name-rules.json;
  110 rows changed in total by the name pass.
- `tools/extract_story_extra.py` exports the remaining story text: 376
  unique strings at 621 occurrences (71 scene captions, 66 conditions and
  keyword descriptions, 190 labels, 46 inline-speaker lines of the chunk-66
  demo/Kanada tribute scene, 2 choice lists and the silent `$n` row the
  dialogue filter missed at two sites); 29 binary false positives excluded.
  All 376 translated (`work/translation/en/story_extra/A.json`, `B.json`,
  brief `docs/STORY_EXTRA_BRIEF.md`); keyword links written `{{Term}}` and
  matched to their label entries. Independent review checked every row
  (all 57 B conditions number by number): four corrections, including
  新西暦 as New Western Calendar (wiki) and the exact Lemures Test Type
  unit name. Reviewed output: `work/translation/en/story_extra_reviewed/`.
- Still pending: dialogue-box width measurement and
  wrapping, and the STAGE relocation writer. No story build exists yet.

## 0.2.11 — 2026-09-26

- Add 229 independently authored/reviewed battle captions at 1,114 native
  occurrences, after checking consecutive native IDs 0-239 and their full
  containing sequences. Total installed coverage: 1,232 identities / 3,429
  occurrences. The remaining 55,833 indexed occurrences stay native.
- Correct the earlier caption 169 from "ZAFT scum" to "ZAFT weaklings" through
  an explicit source-bound amendment. New drafts repair reversed support
  direction, bailout wording, a prized-asset idiom and stolen-machine wording.
- Bind candidate author/reviewer/source/glossary hashes before compilation;
  apply researched, source-scoped names after meaning review and preserve
  complete text during two-row layout. Document the workflow in
  `docs/BATTLE_CANDIDATE_BRIEF.md`.
- Preserve established Mach Band Shaker and Domepolis spellings after a
  whole-project scan. Normalize one earlier chart synopsis from "Dome Polis
  Katez" to "Domepolis Katez" and rewrap its complete prose.
- Retain v0.2.10's pre-title demo fixes. Story dialogue stays excluded from
  this active build; separate story drafts are preserved. Emulator acceptance
  remains pending by user choice. See `docs/BUILD_0.2.11.md` for final checks.

## 0.2.10 — 2026-09-26

- Fixes the separate pre-title battle-demo text reported on v0.2.9. Its
  series titles are TIM2 graphics in `BTL/OP.BIN`, and its speaker names are
  local crew records; changing regular COMPDATA names does not update them.
- Translates all 20 series-title graphics and 61 demo speaker-name fields
  using existing Library titles and exact pilot/display identities. Keeps
  native palettes, crew IDs, commands, animation data and segment offsets.
- Adds three independently reviewed Great Wheel Rocket Punch shout variants,
  including the pictured "Great Wheel Rocket Puuunch!". Battle coverage is
  now 1,003 captions at 2,315 occurrences. The previous 1,000 entries are
  unchanged; English captions remain relocated outside native strings.
- Adds demo parsing, source-bound translation data, static atlas previews
  and an independent final-disc preservation/readback audit. The name field
  is 20 bytes within a 32-byte crew record; numeric fields are not text padding.
- ISO and xdelta build pass final readback and exact patch reconstruction.
  All 3,773,388,140 bytes outside the 42 planned writes remain native; build
  dependencies match their recorded hashes. Earlier v0.2.9 outputs are retained.
- Emulator testing remains pending by user choice. Other unreviewed battle
  captions remain Japanese. Story translation work above is separate and
  is not installed by this non-story build.

## 0.2.9 — 2026-09-25

- Adds five independently reviewed save/load summaries, bringing coverage
  to 65 of 66 records. The remaining entry 27 preserves full meaning in its
  English draft but still needs four rows; the build retains native text.
- Corrects Takeshi Tsukikage in two Library fields using Ashi Productions'
  English cast. Whole-corpus scanning precedes native-scoped replacement.
  Previously released 60 recaps and 1,000 battle-caption texts are unchanged.
- Drafts and independently reviews all 296 suspend messages at 379 occurrences
  across 57 scenes, including seven Special Disc variants. Matches 289 native
  texts to main-game STAGE chunk 0 through typed command pointers. Preserves
  gameplay tips, prophecy clauses, character jokes and military-drill glosses.
- Adds source-bound extraction and review consolidation, terminology sources,
  and format notes. Suspend messages are not yet installed: buffer, encoding
  and display contracts still need verification. Story dialogue stays excluded.
- Save-summary follow-up merge rejects duplicate proposal IDs, stale reviews,
  bad correction preimages, unapproved edits and incorrect archive hashes.
  Emulator testing remains pending by user choice.
- Builds the ISO and 4,358,034-byte xdelta with exact patch reconstruction.
  All 3,774,186,636 unplanned bytes match the source; story chunks, native
  save data and all 57 suspend scenes are preserved. Build input hashes match
  all 63 tools, 77 translations and eight glossary files.
- Independent ISO readback passes for all 65 English recaps, 4,995 Library
  fields, 729 relocated targets and 2,312 translated caption occurrences.
  All 56,950 unreviewed caption occurrences and voice metadata remain native.

## 0.2.8 — 2026-09-25

- Adds the remaining 397 conflicting battle captions at 964 occurrences.
  The release contains all 877 disagreement rows and 123 new captions:
  1,000 texts at 2,312 occurrences. All fit the measured two-row layout.
- Restores omitted conditions, corrects reversed speakers and commands,
  preserves the full Double Reversal attack variant, and verifies Julie's
  gender and Sozo Haran's identity. The long unfinished proverb received an
  independent compact-wording review without losing its uncertainty.
- Applies source-scoped terms to 45 Library fields, 15 menu fields and seven
  chart summaries, including Orson, Solar Wing, Mechaboost, Musouken and
  Sigma Breast. Historical drafts and previous versioned build inputs are
  retained. The original 96-byte caption buffers remain sufficient.
- Built and independently verified the ISO and 4,358,313-byte xdelta. Exact
  patch reconstruction passes. All 3,774,186,636 unplanned bytes match the
  source; 56,950 unreviewed indexed captions and all voice metadata retain
  native data. Existing Library, menu, chart, recap and narration checks pass.
- Story dialogue remains excluded. Emulator testing remains pending by
  user choice. Other captions, suspend messages, recaps and artwork still
  require work; the full non-story goal remains active.

## 0.2.7 — 2026-09-25

- Adds 320 independently reviewed captions at 708 occurrences. Total English
  caption coverage is now 603 texts / 1,348 occurrences, with no layout deferrals
  in the reviewed release. Story dialogue remains excluded.
- Corrects reversed addresses, missing qualifications, atonement, reprimands
  and ambiguous referents. Two compact forms preserve full meaning and ranks;
  an ordinary Japanese farewell is translated as Goodbye.
- Applies researched names and ability terms to 148 Library fields, 52 menu/name
  fields and two Q&A pages. Corrects the inherited Barrge typo. Preserves the
  native identity of saber weapons and English family/given-name reordering.
- Adds regression checks for source-scoped names and records the native glyph
  mapping for the tilde vocal inflection. Versioned caption input and preview
  preserve the previous release's artifacts.
- Built and independently verified the ISO and 4,348,976-byte xdelta. Exact
  reconstruction passes. All 3,774,205,068 unplanned bytes match the clean disc;
  57,914 unreviewed caption occurrences and all voice metadata remain unchanged.
  Existing Library, menu, chart, recap and narration checks pass.
- Emulator testing remains pending by user choice. The full non-story goal
  remains active; other captions, suspend messages and artwork still need work.

### Drafts prepared after this release

- Reuse queue 480-639 has native-source authoring and independent reviews:
  160 captions at 437 occurrences. One cross-review correction restores the
  singular next opponent. These drafts are outside the 0.2.7 release and were
  subsequently normalized, laid out and included in 0.2.8.
- Follow-up research records Ray Beams versus Rey, Orson, Pain Shouter,
  Vegan Empire, Harry's named rank and the Chaos Leo spoken attack declaration.
  Whole-corpus variant scanning found further Library/menu candidates;
  native identity checks and the spelling pass were completed for 0.2.8.

## 0.2.6 — 2026-09-25

- Adds 283 reviewed battle captions at all 640 matching occurrences: 123 new
  captions and 160 reuse disagreements. Independent reviews check every native
  occurrence with adjacent context.
- Corrects missing facts and reversed support commands, then applies researched
  names. One compact taunt received another meaning check; every released
  caption fits two rows in full, without truncation.
- Appends English after native SRVC blocks and updates their index/SEG tables
  and both disc maps. Preserves voice metadata and all original block bytes
  except selected text-offset words. Unreviewed captions stay native.
- Adds format, relocation and independent readback checks, a corpus spelling
  inventory and static layout previews. Optional larger-buffer adapters pass
  instruction tests but are not installed: current captions fit 96 bytes.
- Emulator testing stays pending by user choice. Story dialogue is excluded;
  other captions, suspend messages and remaining artwork still need work.
- Built and independently verified the ISO and 4,340,681-byte xdelta. Exact
  patch reconstruction passes. All 3,774,219,404 unplanned disc bytes match
  the source; 58,622 unapproved indexed captions and all voice metadata remain
  unchanged. Existing Library, menu, chart, recap and narration checks pass.

## 0.2.5 — 2026-09-25

- Adds all ten English episode narration and journal entries. Full drafts
  were checked against all 130 native lines and paired context. Corrected
  ZEUTH's descriptor to "independent mobile force"; two compact variants
  received a further meaning check. Names are normalized after meaning edits.
- Expands length-delimited text and updates native allocation/offset tables,
  preserving every picture, music, timing, modifier and clip command. All
  entries retain thirteen lines; dates, signatures and attribution are intact.
- Adds strict container tests, source/review bindings, finished-ISO checks,
  a terminology supplement and ten reconstructed layout previews. Emulator
  testing remains pending by user choice. Story dialogue stays excluded.
- Built and independently verified the ISO and 3,166,877-byte xdelta. Patch
  reconstruction is exact; all ten narration texts read back with every
  nontext command intact. All 3,777,655,336 unplanned disc bytes match the
  clean image. Existing coverage, six native recap deferrals and story
  protection pass their checks. Older builds are unchanged.

## 0.2.4 — 2026-09-25

- Adds 60 English save/load summaries, including challenge objectives and
  literal developer placeholders. All 66 full drafts and compact alternatives
  received independent native-source meaning review. Applied nine corrections
  after the compact pass, then checked glossary spelling and display bounds.
- Six records remain native: IDs 2, 13, 17, 27, 44 and 53. Their full meanings
  exceed the three-row limit; they are explicitly deferred without truncation.
- Replaces the recap getter with a guarded 67-entry table in loaded English
  memory, and changes the two line strides to 256 bytes. Native fallback cells
  are preserved in the same wider record shape. HSFC and save-file layouts
  are unchanged; story dialogue remains excluded.
- Added exhaustive low-16-bit lookup tests, independent finished-ISO recap
  checks, a UI width profile, review hashes and glossary provenance notes.
- Built and independently verified the ISO and 3,161,438-byte xdelta. Patch
  reconstruction is exact; all 60 English recaps and six native deferrals
  read back correctly. All story chunks, HSFC and unplanned disc bytes are
  unchanged. Emulator acceptance remains pending by user choice.

## 0.2.3 — 2026-09-25

- Added all 110 main-game Scenario Chart summaries, completing the 131-summary
  chart. Reused donor candidates by complete native-text identity and followed
  the donor's relocated pointers instead of assuming matching byte offsets.
- Meaning reviewers checked all 110 entries and adjacent context. Applied 78
  corrections, including missing facts, reversed actions, mistaken characters,
  misgendered referents, and unsupported claims that characters had died.
- Applied names after meaning review. Corrected 129 Library fields and 36
  COMPDATA fields; protected unrelated actors and characters from ambiguous
  name replacements. Source-specific rules distinguish Freeden/Freedom,
  Four/Fa, Mel/Black Mail and fictional Ameria/real-world America.
- Relocated every new summary to loaded English memory. All fit eleven lines
  at the existing 560-unit limit. Native main-summary bytes remain preserved;
  only their typed pointer table is redirected. Story chunks 1–67 are retained.
- Saved the review notes, name research and binding metadata. Emulator
  testing remains pending by user choice; other in-scope surfaces remain work
  to do and are tracked in the scope ledger.
- Built and independently verified the ISO and 3,157,348-byte xdelta. Patch
  reconstruction is exact; 395 chart fields and 665 relocated texts read back
  correctly, with all story chunks and unplanned disc bytes unchanged.

## 0.2.2 — 2026-09-25

- Added 113 squad-name presets, preserving every squad's membership data.
- Added all 200 map labels. Reused 74 only after exact native-source matching;
  authored Special Disc changes and preserved SP future-map variant numbers.
- Added Scenario Chart text: 131 titles, 128 episode labels, 21 SP summaries and
  five control hints. Three route-node labels are intentionally empty.
- Relocated the complete English summaries to the loaded English segment,
  with a conservative 560-unit line width and eleven-line limit. Retained the
  native chart buffer, archive slot, and every byte of story chunks 1–67.
- Reviewed all 21 new summaries, 113 squad presets and six authored map labels
  for meaning. Corrected ambiguous referents and an unsupported fatal outcome.
- Applied glossary corrections across generated text: Earthgertz, Meeya,
  Medaiyu and Mischa, plus squad/map terminology. English chapter titles now
  use Wings to Dry Tears and Rosary of Grief instead of romanized Japanese.
- Clarified the active scope: only story dialogue is excluded. Battle captions
  and suspend messages remain work to do. Emulator testing stays pending.
- Inventoried 110 additional main-game summaries in the chart overlay; they
  remain native and are explicitly tracked for the next translation pass.
- Built and independently verified the ISO and 3,133,784-byte xdelta. The patch
  recreates the exact ISO; all 598 new fields and 555 relocated text targets
  read back correctly, with story chunks and unplanned disc bytes unchanged.

## 0.2.1 — 2026-09-25

- Added all 102 Strategy Q&A pages and 264 chapter/keyword fields, plus the
  shared tutorial record. Reviewed 22 changed pages against Special Disc.
- Corrected the help for absent SR Points, Parts-only Bazaar, replay rules,
  Extra Stage Continue, completion bonuses, and barrier EN costs.
- Translated all 24 fixed selection and briefing panels: Data Link, five
  episode introductions and eighteen Challenge Battle briefings. Preserved
  every objective, deadline, page size and archive slot.
- Reviewed newly authored Library entries and briefings for meaning. Corrected
  Mazinger Z's launch description, Toby's unspecified partner gender, and
  Another Side's chronology. Applied reviewed name spellings across components.
- Added a local glossary snapshot (1,078 inherited terms), researched additions,
  provisional-name notes, source links and spelling rules.
- Added screenshot measurements and clearly marked English asset/layout
  previews. Emulator validation remains pending by user choice.
- Built the ISO and 3,097,777-byte xdelta. Patch reconstruction matched the ISO
  hash; independent checks passed for 4,995 Library fields, 535 relocated text
  entries, 34,964 description lines and English segment/heap separation.
- Recorded remaining chart/narration, squad-name and embedded-artwork coverage
  explicitly. This candidate is not a claim that every Japanese surface is gone.

## 0.2.0 — 2026-09-25

- Added the supplied Library screenshots as UI references.
- Bound existing English robot, character, and keyword entries by native field
  identity. Reviewed Special Disc wording changes and translated new entries.
- Completed 4,995 Library text fields across 795 records, including both
  description variants. Story dialogue remains excluded.
- Ported the existing English menu glyph renderer using verified native code
  correspondence, relocated references, and separate heap space. Runtime testing
  remains pending at the user's request.
- Translated 5,521 menu/name fields and 2,362 executable UI fields, including
  Battle Viewer, Special Theater, unit/pilot/weapon names and music names.
- Reused verified Library and shared UI graphics, authored four mode headings,
  and added English compact Spirit/terrain labels with separate private glyphs.
- Built and verified the versioned ISO and xdelta patch. Relocated enlarged
  archives into verified empty disc space and updated ISO/VMAP entries together.
- Preserved story, battle and suspend dialogue, original font archive and all
  disc bytes outside the planned text/graphic changes.

## 0.1.0 — 2026-09-25

- Started English work with front-end graphics only, following the instruction
  to leave story dialogue for later.
- Translated 12 buttons in the title, Extra Stage, and Battle Viewer menus,
  covering all 60 native highlight/transition images.
- Reused SRW-Z's MIT-licensed ISO reader and Banpresto compression libraries.
  Added a separate Special Disc source contract and native TIM2 authoring.
- Added English label JSON, measured text bounds, source/font/asset hashes,
  frozen indexed pixels, and native/English atlas previews.
- Built a versioned ISO and xdelta patch. Verified strict decompression, native
  palettes and texture frames, fixed archive capacity, all protected disc bytes,
  unchanged ISO layout, and patch reconstruction of the exact output hash.
- Kept the executable, original font, story and battle dialogue, and gameplay
  behavior data unchanged. No upstream unlock/reward/skip modifications applied.
- Prepared an isolated PCSX2 instance without existing memory cards or texture
  replacements. Runtime validation is pending: Windows input failed with
  `GetCursorPos failed: Access is denied. (0x80070005)` and captures were black.
- Restricted native texture export to the three visually checked 512x512
  atlases; smaller heading texture layouts remain to be researched.

## Initial assessment — 2026-09-25

- Inspected the Special Disc workspace, local SRW Z projects, and dyzz/srwz-zh
  at commit `f6673b1edf697df3501fba3889e930815fd1b001`.
- Extracted the supplied CHD into a local MODE1/2048 source image and verified
  its whole-image SHA-256 and all 65 members against the upstream inventory.
- Added a read-only audit tool and reports for source identity, compression,
  original font compatibility, and English battle-caption reuse candidates.
- Recorded glossary disagreements, stale caption exports, and differing story
  exports without changing the original SRW Z projects.
- Documented Special Disc format differences and the recommended implementation
  order. No translation, runtime patch, playable build, or emulator test was made.
- Reserved **0.1.0** for the first actual test build; this audit is not a build.
