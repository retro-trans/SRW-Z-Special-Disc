# English episode-title candidate 0.2.17

Translates the complete episode-entry title-card category shown in the user's
screenshot: **Episode 1 — Fierce Battle! A Warrior's Rest**. All 21 selector
slots have English titles: 20 new images and one preserved native English
image. The shared episode heading uses **Ep.** with unchanged native numbers.

All 21 titles across 24 active stage bindings passed independent meaning
review against their native source and the project glossary. The title images
use full wording, centered within the original geometry. Selector 17's native
duplicate picture is corrected to Prologue according to its typed stage data.
See [format, source references and workflow](EPISODE_TITLES.md).

The change is limited to 21 compressed texture spans in VT1: 20 title images
and the shared number-word atlas. The original English card, ten digits,
palettes, frames, animation records and runtime offset tables are protected.
All previous translations, location cards and Story Mode panel fixes remain.
Story dialogue and pending battle/suspend drafts are unchanged.

Four targeted tests pass, including native pixel packing/orientation,
invalid/oversized text rejection, digit and animation protection, and exact
tail-compression reconstruction. The component and full build dry runs pass.
All changed images fit their original allocations; minimum headroom is 61
bytes. Full-disc verification results are recorded below.

Two reviewers inspected all 21 static titles and the shared-header preview;
full wording and punctuation are visible without clipping. These are extracted
assets, not emulator screenshots. In-game number spacing, title animation,
branch routing and visual acceptance remain pending by user choice.

## Verified output

- ISO: `work/output/SRW Z Special Disc English v0.2.17.iso`, 3,791,781,888 bytes.
- ISO SHA-256:
  `f7f58c6bfcf80800a83c1ec8efc1ec1336e6029eb96f220764e9a31822fe70c6`.
- Patch: `work/output/SRW Z Special Disc English v0.2.17.xdelta`, 4,801,254 bytes.
- Patch SHA-256:
  `483ae2532a61b871f1c2808a5c26fc4272816c396c66a083d9358cd0bb6d9551`.
- Applying the patch to the clean extracted BIN reconstructs the exact ISO.
  All 3,733,692,732 bytes outside the 64 planned writes remain native. ISO
  directory and runtime mappings agree; story chunks 1–67 remain unchanged.
- Independent final-disc readback verifies all 21 title slots, the ordinal
  header, ten unchanged digits, palettes, geometry, animations and offset table.
  The six protected records, including the native English card, are identical.
- Earlier coverage passes again: 4,995 Library fields, 313 reference names,
  395 chart fields, 65 recaps, ten narrations, 1,917 battle captions at 4,870
  occurrences, 20 demo titles/61 names, six aligned introductions and 13 globe
  location cards. All whole-member payload hashes match v0.2.16.
- The previous-release comparison confirms all 205,314,416 VT1 bytes outside
  the 21 new spans are identical. All 254 receipt-listed inputs match: 100
  Python files, 133 translation files, 19 glossary files and two image-binding
  inventories.
- The 258-entry input snapshot is 10,864,640 bytes, SHA-256
  `40b3bbb986a4f026f0174405d95ac5ae72ae6cc232e65f11b7ee21e6dac61086`.
  Every ZIP entry was read back exactly. It preserves the receipt-listed inputs
  and final audits; it does not redistribute the clean disc or font dependency.
