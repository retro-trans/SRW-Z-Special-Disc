# Special Disc tools

## Current build: 0.2.24

Use Python 3.11+ with the dependencies below. Run each tool without `--write`
first and inspect its samples. `--write` saves targets/reports or, for the
assembler, creates a new versioned ISO. Never overwrite an existing build.

The current pipeline also reads the verified local v0.9.85 English donor,
native main-game extraction, and Library English master. See
`docs/BUILD_0.2.24.md` and the component reports for identities and scope.

For this release, dry-run `squad_followup.py`, then dry-run
the main builder before `--write --patch`. Dry-run
`audit_nonstory_build.py --version 0.2.24`,
`verify_build_inputs.py --version 0.2.24 --previous 0.2.23`, and
`snapshot_build_inputs.py --version 0.2.24` before their `--write` steps.
The component-specific examples below retain their original release versions.

`squad_followup.py --prepare` inventories the 14 text fields and two indexed
word tiles; `--prepare --write` saves bindings, draft and atlas preview after
dry-run inspection. Independent review is mandatory before building.
`audit_squad_followup.py` checks the final installed text and pixels, verifies
font widths and overlay gaps, and restores only approved spans before the
historical whole-file audits run. No story fields or executable instructions
change in this component.

Mission conditions use `inspect_mission_conditions.py` to bind native table
assignments, `prepare_mission_conditions.py` for full drafts, independent meaning
review, `prepare_mission_layout.py` for compact layout proposals, and a second
independent review. `mission_conditions.py --prepare --cache` defaults to a
read-only plan; inspect text/coverage before `--write` freezes targets and
verifies compression caches. `preview_mission_conditions.py` similarly defaults
to dry run. Run `test_mission_conditions.py`, then dry-run `build_nonstory.py`
before `--write --patch`. The final-disc audit calls `audit_mission_conditions.py`.
Dry-run `audit_nonstory_build.py --version 0.2.19`,
`verify_build_inputs.py --version 0.2.19 --previous 0.2.18`, and
`snapshot_build_inputs.py --version 0.2.19` before their `--write` steps.
See `docs/MISSION_CONDITIONS.md` for ownership, layouts and preserved bytes.

Episode title cards use `inspect_episode_titles.py` for native image/selector
bindings, an independent meaning review, then `episode_titles.py --prepare`
to freeze all 21 targets and layouts. Run dry before `--write`, inspect the
title and number-atlas previews, and run `test_episode_titles.py`. The build
includes the writer and `audit_episode_titles.py` checks final-disc pixels.
After assembly/audit, dry-run `verify_build_inputs.py --version 0.2.17
--previous 0.2.16` and `snapshot_build_inputs.py --version 0.2.17` before their
`--write` steps. See `docs/EPISODE_TITLES.md` for the complete sequence.

For globe location cards, dry-run `prepare_world_map_titles.py`, inspect all
13 full names, then use `--write`. It binds native artwork and applies glossary
spelling after independent review. Dry-run `world_map_titles.py` before its
`--write` preview/component step. `build_nonstory.py` includes the same writer;
the final-disc auditor includes `audit_world_map_titles.py`. After build and
audit, dry-run `verify_build_inputs.py --version 0.2.16 --previous 0.2.15` and
`snapshot_build_inputs.py --version 0.2.16` before their `--write` steps.
The snapshot also preserves the location-image bindings.

Battle captions use `prepare_battle.py` for candidate bindings,
`prepare_battle_review.py` for the disagreement queue, and independently
authored/reviewed slices. `review_battle_batch_00720_00959.py` applies meaning changes,
source-scoped spelling and full-word layout. Run it dry, inspect samples, then
use `--write`. `compile_battle.py` is a read-only component dry run;
`build_nonstory.py --write --patch` assembles the reviewed release. Never import
the complete candidate inventory as approved English.

`inspect_battle_runtime.py`, `preview_battle.py` and `audit_battle_names.py`
default to dry runs; `--write` saves their reports/previews. The finished ISO
auditor includes an independent SRVC pass. See `docs/BATTLE_CAPTION_RESEARCH.md`
for native format, preserved bytes, layout and remaining work.

Consecutive native candidate ranges use the contract in
`docs/BATTLE_CANDIDATE_BRIEF.md`. For IDs 240-479 run
`review_battle_batch.py --candidates` dry, inspect samples, then add `--write`.
Run `review_battle_batch.py` dry and inspect before its `--write` release step.
The first batch's `review_battle_candidates.py` and
`review_battle_release.py` remain historical workflows. Both source and independent review bindings are
mandatory. Candidate inventory alone does not authorize an ISO change.

For v0.2.13, run `prepare_reference_0_2_13.py` dry and inspect its complete
field comparison before `--write`. It needs the frozen v0.2.12 input ZIP,
applies the independent Library meaning review before spelling, and refreshes
narration metadata. Then dry-run and refresh `reuse_compdata.py --write`.
Keep versioned review/release files immutable. After assembly, run
`verify_build_inputs.py --version 0.2.13 --previous 0.2.12` and inspect before
`--write`; `snapshot_build_inputs.py --version 0.2.13` similarly preserves the
receipt-listed inputs after both final audits exist.

For v0.2.14, the reference components are unchanged. Dry-run
`review_battle_batch_00720_00959.py` and `review_battle_release_0_2_14.py`, inspect
their samples, then use their guarded `--write` steps only for new outputs.
The frozen author, review and compact-approval hashes are mandatory. After
assembly and the independent final-disc audit, run
`verify_build_inputs.py --version 0.2.14 --previous 0.2.13`, inspect, then
`--write`. Dry-run `snapshot_build_inputs.py --version 0.2.14` before its
`--write` step. Versioned outputs and snapshots must not be overwritten.

Version 0.2.15 retains the 0.2.14 translation inputs and fixes Story Mode
panel alignment. `align_story_panels.py` supplies guarded, scoped helpers;
`compile_briefings.py` wraps the six introductions to their narrower bounds.
`test_story_panel_alignment.py` checks the helper instructions and native
fallbacks. Dry-run `preview_story_panels.py` before `--write` to save the
reconstructed previews. The final-disc auditor includes
`audit_story_panel_alignment.py`. After assembly and that audit, dry-run
`verify_build_inputs.py --version 0.2.15 --previous 0.2.14` before `--write`,
then do the same with `snapshot_build_inputs.py --version 0.2.15`.

The current battle release input is `battle_release_0.2.14.json`, assembled by
`review_battle_release_0_2_14.py`. The older `battle_release_0.2.13.json`,
`battle_release_0.2.12.json`,
`battle_release_0.2.11.json`, `battle_release_0.2.10.json`,
`battle_release_0.2.8.json`, `battle_release.json` and earlier build outputs are
retained. Name corrections also run after editorial changes in the Library,
COMPDATA, Q&A, system UI, narration and Scenario Chart compilers;
inspect their source-bound differences before writing. `test_scoped_names.py`
protects weapon names, unrelated identities and both line-break encodings.

`battle_placeholder.py` rechecks the pinned analysis of hidden production
caption 444 against native metadata and executable instructions. The compiler
and final audit require those suppression guards to survive. Its 382 original
records remain byte-identical and do not count as English translations.

The pre-title battle demo has separate text and graphic assets. Run
`attract_demo.py --prepare` to inspect the exact pilot/display and Library-title
reuse bindings; add `--write` to save the manifest. Its independent meaning
review is required by `attract_demo.py`, whose dry run compiles the three
native-palette atlases and twenty-byte name fields. `--write` saves previews
and layout metadata. The build includes this component, and the finished ISO
audit runs `audit_attract_demo.py` for independent crew-ID, command, palette,
pixel and regular-name readback checks. See `docs/ATTRACT_DEMO_RESEARCH.md`.

Initial preparation, already performed in this workspace:

```powershell
python -B tools/inspect_english_runtime.py --write
python -B tools/port_menu_runtime.py --write
python -B tools/prepare_glossary.py --write
python -B tools/library_text.py --write
python -B tools/complete_library.py --write
python -B tools/compile_library.py --write
python -B tools/reuse_menu_graphics.py --write
python -B tools/reuse_compdata.py --write
python -B tools/reuse_system_text.py --write
python -B tools/port_compact_labels.py --write
python -B tools/reuse_help_book.py --write
python -B tools/author_headings.py --write
python -B tools/compile_briefings.py --write
python -B tools/preview_nonstory.py --write
```

The front-end indexed assets from 0.1.0 are also inputs. The assembler rebuilds
components from native sources and English targets. Refresh `reuse_compdata`
after changing its targets: its cached menu pool is a checked prefix for the
system pool. `complete_library` applies meaning fixes and glossary spellings
before measuring and reflowing text.

The 0.2.2 components `compile_reference_names.py` and `compile_chart.py` have
their own dry runs. The assembler invokes them after the help archive and
compact-label pool are ready. `review_reference_batch.py` records the bounded
meaning corrections from this pass, then applies glossary spellings to its
authored files. Its operation is idempotent. After glossary changes, regenerate
`complete_library` and `reuse_compdata` before assembly. The chart's long
summaries join the same loaded pool; final addresses are in the versioned
build report, not the standalone translation export.

For the main-game chart, `prepare_main_chart.py` follows native and donor
pointer tables and exports source-bound candidates. `review_main_chart.py`
requires both complete meaning-review files before applying the global and
row-specific glossary rules. Run its dry run, then `--write`, whenever those
inputs or the glossary change. The compiler rejects stale review hashes.
Do not overwrite the review files with an unreviewed donor export.

For save/load recaps, `review_save_summaries.py` requires both the full-draft
and compact-layout meaning reviews. It applies corrections before names and
recomputes the three-row fit. Run its dry run, then `--write` after review or
glossary changes. `compile_save_summaries.py` similarly has a dry run and a
`--write` binding export; its final pointers are assigned during assembly.
Entries that fail the layout gate retain native strings in the widened cells
and are listed explicitly in reports. `test_save_summary_hook.py` is a
read-only instruction-level test covering every 16-bit lookup index.

The 0.2.9 recap follow-up uses `review_save_summary_followup.py` to retain the
earlier reviewed input and merge only independently approved changes into
`save_summaries_release_0.2.9.json`. It has the same dry-run/write flow. Do not
overwrite the base review while its follow-up is bound to that exact file.
`preview_save_summaries.py` produces a labelled static atlas reconstruction.

`suspend_format.py` validates all 296 text records, 57 scenes and 379 command
references and prepares English reuse candidates. After the four full-meaning
drafts and independent reviews, `review_suspend_messages.py` applies spelling
and writes `suspend_reviewed.json`. Both default to dry runs. These drafts are
not part of the ISO yet; no suspend renderer or pagination patch is approved.

For narration, `review_narration.py` applies the full meaning review and two
reviewed compact variants, then spelling and thirteen-line layout. Run it
without `--write`, inspect its samples, then save with `--write`.
`compile_narration.py` has the same dry-run/write flow and rebuilds the ten
length-delimited records and their native size/offset tables. It changes no
music, picture, timing or formatting commands. `test_narration_format.py`
checks expanded and malformed records without writes. `preview_narration.py`
has dry-run/write modes for reconstructed layouts, not emulator captures.

Assemble and verify:

```powershell
python -B tools/build_nonstory.py
python -B tools/build_nonstory.py --write --patch
python -B tools/audit_nonstory_build.py --version 0.2.13
python -B tools/audit_nonstory_build.py --version 0.2.13 --write
```

This pipeline changes font/menu runtime, archive locations and text tables.
The older graphics-only constraints below apply only to build 0.1.0. Decoded
COMPDATA/NISVDATA/STAGE-overlay sizes and bytes outside explicit write ranges
are protected. STAGE chunks 1–67 remain native; only chart chunk 0 changes.
The patch is reconstructed against the clean BIN. Emulator checks are pending.

## Archived graphics-only build 0.1.0

The new build tools use the local `shared/` library snapshot. They do not import
code from a moving SRW-Z checkout. The audit tool below retains its original
external reader defaults for comparison research.

Tested environment: Python 3.12.14, NumPy 2.3.5, Pillow 12.3.0. Use Python 3.11+
with `requirements.txt` for these dependency versions. This machine's bundled
interpreter is:

```text
python
```

Run from the project root. In the commands below, `python` means that interpreter
or another environment with the listed packages, not the older system Python.
The source must be the verified clean MODE1/2048 image at
`work/source/special-disc.bin`; see `docs/BUILD_0.1.0.md` for its hash.

### Inspect and author menu assets

```powershell
python -B tools/export_menu_assets.py
# Inspect the planned three atlases, then save previews:
python -B tools/export_menu_assets.py --write

python -B tools/author_front_end.py
# Inspect every label and its measured bounds, then freeze indexed pixels:
python -B tools/author_front_end.py --write
```

English text lives in `work/translation/en/front_end.json`. Authoring reads the
local Arial Narrow Bold font specified there, and records its SHA-256. The font
file is not copied. It preserves native palettes and pixels outside each label
rectangle. The three `.npy` files and `manifest.json` in `work/ui/english/` are
the frozen build inputs; the PNGs are inspection previews.

Only the three known 512x512 menu atlases are supported by this export workflow.
Smaller heading textures require separate layout validation. Do not treat the
TIM2 reader as a universal texture decoder.

### Assemble and verify

```powershell
python -B tools/build_front_end.py
# Inspect scope, compressed sizes and headroom, then build:
python -B tools/build_front_end.py --write --patch
```

The dry run includes compression and strict readback. A write validates the
entire source hash, copies the clean source, patches only the three native VT1
slots, then verifies every other byte and the final decoded textures. No
executable table edits, archive relocation, font hooks, or dialogue writes are
used. Build assembly from frozen pixels does not depend on the local font.

`--patch` currently uses `E:/Projects/SRW Z/xdelta3.exe`; it creates an xdelta,
decodes it against the clean source, and requires the restored ISO's hash to
match. Its temporary round-trip image is removed only after verification.
Without `--patch`, that external utility is not required.

Outputs are under `work/output/`. Existing versioned ISOs are never overwritten.
The current writer's version is fixed at 0.1.0. Increment the version and update
the changelog for later changed builds. Preserve original outputs and receipts.

To apply the existing patch separately, choose a new destination file:

```powershell
& 'E:/Projects/SRW Z/xdelta3.exe' -d -s 'work/source/special-disc.bin' 'work/output/SRW Z Special Disc English v0.1.0.xdelta' 'work/output/SRW Z Special Disc English v0.1.0-restored.iso'
```

The expected restored SHA-256 is in `docs/BUILD_0.1.0.md`. The patch source is
the extracted BIN, not the CHD and not an Original/Best/main-game image.

### Isolated emulator

```powershell
python -B tools/prepare_emulator.py
# Inspect the copy plan, then prepare the isolated instance once:
python -B tools/prepare_emulator.py --write
```

This copies the existing local PCSX2 1.7.4005 runtime and BIOS into
`work/emulator/`, without user memory cards or save states. It disables memory
cards and texture replacements and assigns keyboard controls. It refuses to
overwrite an existing destination. It neither boots a game nor proves runtime
compatibility. See the build notes for the pending emulator checks.

## Deployment and squad UI

`inspect_deployment_ui.py` inventories the late COMPDATA menu table and chapter
13's typed roster names. `prepare_deployment_ui.py` writes full drafts for
independent meaning review. `deployment_ui.py` applies that review, then the
glossary, freezes four sprite layouts and sets one ID-specific heading override.
Each defaults to dry run; inspect its samples before adding `--write`.

`build_nonstory.py` appends reviewed names to persistent English memory and
changes only exact pointer sites and four sprite rectangles. The final-disc
auditor calls `audit_deployment_ui.py` to prove dialogue/gameplay preservation,
English pointer readback and pixel boundaries. `test_deployment_ui.py` exercises
the protected-data and overflow rejection paths. See `docs/BUILD_0.2.18.md`.

## Tactical counters, terrain and movement footer

`prepare_tactical_ui.py` binds 13 small executable fields to their native and
v0.2.19 bytes, records seven coordinate edits, and copies the four user screenshots.
Run it dry before `--write`. Its draft receives independent meaning/encoding
review. `tactical_ui.py` then makes guarded in-place changes after the generic
system-text compiler; it never changes the persistent text pool.

`test_tactical_ui.py` exercises all 1,101 movement cases, exact two-byte cell
contracts, old-template regression, selector routing and rejection guards.
`preview_tactical_ui.py` defaults to dry run; `--write` saves the static diagnostic
preview. `audit_tactical_ui.py` is called by the finished-disc auditor and compares
the entire executable against v0.2.19 outside the 20 approved spans. See
`docs/TACTICAL_UI.md` for the native layout contracts.

## Terrain rating rows

`terrain_rows.py --prepare` inventories all 11 native rating-label rows and
binds the imported SRW Z glyph art and spacing technique. Inspect the dry run
before `--prepare --write`; the four label meanings then receive independent
review. The build applies the component after tactical UI, preserving each
16-byte slot and all code, rating values and coordinates.

`test_terrain_rows.py` contains the focused regression checks.
`preview_terrain_rows.py` defaults to dry run; `--write` saves the diagnostic
preview using exact donor glyph pixels. `audit_terrain_rows.py` verifies the
finished disc and compares every other executable byte with v0.2.20. See
`docs/TERRAIN_ROWS.md` and `docs/BUILD_0.2.21.md`.

## Challenge confirmation

`mission_prompt.py --prepare` inventories the one shared Challenge question,
its menu pointer and both native selector loads. Run without `--write` first;
then `--prepare --write` saves the bindings, draft and supplied screenshot.
After independent meaning review, the default invocation compiles the text
and its measured horizontal position in memory. The main builder installs it.

`test_mission_prompt.py` checks centering, selector readback and protected bytes.
`audit_mission_prompt.py` independently validates the finished field and position
against 0.2.21, then provides strictly verified prior comparison bytes to older
whole-file audits. It never writes an executable or bypasses unrelated changes.

## Original read-only audit

`inspect_special_disc.py` inspects the user's source disc without patching it.
Default invocation is a dry run; `--write` writes only the JSON metadata report.
It does not dump the Japanese script or copy translation corpora.

```powershell
python -B tools/inspect_special_disc.py
python -B tools/inspect_special_disc.py --write
```

Defaults are deliberately local and explicit:

- Source: `work/source/special-disc.bin`, a 2048-byte-per-sector image.
- Native inventory: `work/analysis/upstream-disc-inventory.json`.
- Existing readers: `E:/Projects/SRW-Z/tools`, including `best_adapter/disc.py`
  and `best_adapter/subtitles.py`.
- English caption export: `E:/Projects/SRW-Z/analysis/srvc_en_by_hash.json`.
- Caption freshness sources: `E:/Projects/SRW Z/_work/analysis/srvc_work.json`
  and `srvc_en.json`.
- Report: `work/analysis/special-disc-audit.json`.

All paths can be overridden; use `--help`. Python 3.8 was sufficient for this
audit. The upstream Chinese build tools have additional dependencies and are
not installed or executed here. Imported reader hashes are recorded in the report.

The audit verifies the exact known Special Disc image before using its native
table offsets. It then checks every member, strictly decodes all STAGE chunks
and the font/COMPDATA stream, and measures normalized source-text matches to the
existing English caption export. It regenerates caption mappings in memory to
measure export drift; it does not save changes to those source files.

Caption matches mean reuse candidates, not approved translations or proven
runtime layout. Normalization follows the original export's quote/padding
rules. Only a temporary in-memory SRVC header is adapted for the existing
reader; the source header remains `0x4F01` on disk.

The report is not a production build manifest. This tool does not verify text
relocation, all event pointers, rendering, gameplay, saves, or translation quality.

## Setup and Bazaar artwork (0.2.23)

`inspect_setup_art.py` previews native and donor graphics without editing game
data. `setup_art.py --prepare` inventories 26 bounded word tiles and previews
the planned patch; `--prepare --write` freezes bindings/drafts and atlas PNGs.
`bazaar_slogan.py --prepare` inventories the three fixed Bazaar banner fields;
`--prepare --write` saves their source bindings and English draft. Meaning
reviews must match those drafts before either component builds.

`build_nonstory.py` includes both components. `audit_setup_art.py` independently
reads the installed indexed pixels, banner geometry, instruction words and
three slogan fields before older audits see their verified prior comparison
view. The final build guard separately permits only these reviewed banner
fields in addition to the existing typed stage UI pointers. Story dialogue
and all other gameplay bytes remain protected.
