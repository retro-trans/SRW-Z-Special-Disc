# Episode-entry title cards

The screenshot reads “Episode 1 — Fierce Battle! A Warrior's Rest.” These
captions are textures, separate from the already-translated Scenario Chart.
Version 0.2.17 covers all 21 selector slots (24 active COMPDATA stage records).
Twenty title images are translated; the native English “at the risk of pride”
image is retained byte-for-byte. The shared ordinal prefix becomes “Ep.” and
the Japanese suffix becomes transparent; every number tile is unchanged.

## Ownership and layout

The [upstream Special Disc investigation](https://github.com/dyzz/srwz-zh/blob/main/docs/special-disc/STAGE_ENTRY_TITLES_20260920.md)
identified DATA/VT1.BIN group 9 and the nested offset table at ELF file offset
0x3763E0. This was verified against the local native disc. The group contains
27 records; indices 6–26 map to selectors 1–21. COMPDATA records begin at
0x68630, stride 48, with the selector at +28. Three branch pairs share titles.

Each title is a 512×64 linear low-nibble-first 4bpp TIM2, starting at wrapper
offset 0x20. Its pixel range is 0x60–0x4060. The native palette and wrapper are
preserved. The display compensates double-width source columns; English type
is rendered in square-pixel space then column-doubled. Full titles use 18–24
point Times New Roman Bold, centered within the 256-wide logical canvas. Ink
stays in y=4..27. Wandering and Meaning use four and eight antialias shades,
respectively, to fit native compressed allocations without altering wording.

The episode-number atlas is the second TIM2 in shared record 4. Its 416×24
image at decoded offset 197376 contains ten 32-pixel number tiles followed by
two 48-pixel ordinal-word tiles. Only x=320..415 changes. Complete native LZ
groups preceding the changed tail are retained; the suffix is independently
compressed and strictly decoded. All other bytes, palettes and animations are
protected. The original glyph positions are retained; runtime heading spacing
and animation remain to be checked in PCSX2.

Selector 17's native bitmap duplicates selector 16, but its typed stage data
and chart identify Prologue. The English image follows that binding. This is
a statically verified correction, not a claim that the branch was played.

## Review and validation

`work/translation/en/episode_titles_review.json` records independent meaning
review of every title and glossary checks for Teral, Adette, Black History and
Executor. `episode_titles.json` pins that review, source inventory, font hash,
final pixel hashes and layouts. No story dialogue is extracted or translated.

`test_episode_titles.py` checks nibble order, orientation, invalid/oversized
inputs, digit protection, tail-compression reconstruction and complete frozen
coverage. `audit_episode_titles.py` independently reads the final disc and
checks pixels, source bindings, ink bounds, palettes, tables, number tiles and
the six unchanged records. The full build separately verifies all bytes outside
its explicit write spans and reconstructs the ISO from its xdelta patch.

Preview images are extracted/reconstructed assets, not emulator screenshots:
`work/ui/episode-titles/english-0.2.17.png` and `header-0.2.17.png`.
Emulator testing remains pending by user choice.

Reproduce with the configured Python runtime (dry run before each write):

```powershell
python -B tools/inspect_episode_titles.py
python -B tools/inspect_episode_titles.py --write
python -B tools/episode_titles.py --prepare
python -B tools/episode_titles.py --prepare --write
python -B tools/test_episode_titles.py
python -B tools/build_nonstory.py
python -B tools/build_nonstory.py --write --patch
python -B tools/audit_nonstory_build.py --version 0.2.17
python -B tools/audit_nonstory_build.py --version 0.2.17 --write
python -B tools/verify_build_inputs.py --version 0.2.17 --previous 0.2.16
python -B tools/verify_build_inputs.py --version 0.2.17 --previous 0.2.16 --write
python -B tools/snapshot_build_inputs.py --version 0.2.17
python -B tools/snapshot_build_inputs.py --version 0.2.17 --write
```
