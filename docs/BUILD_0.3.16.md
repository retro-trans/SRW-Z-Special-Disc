# Build 0.3.16

Local test candidate based on v0.3.15. The shared title-card ordinal changes from Ep. to Stage, with the capital height and baseline matching the native number shown in the report.

## Layout

VT1 group 9, record 4 contains a 416 by 24 pixel atlas: ten digit tiles followed by two ordinal-word tiles. The new Stage label uses both word tiles, leaving every digit pixel unchanged. Times New Roman Bold at 24 pixels supplies a 16-pixel capital height. The capital sits at rows 4–19 with baseline 20; the descender fits the four remaining rows. The word is fitted horizontally to 46 logical pixels within a 48-pixel region. Eight antialias shades fit the original compressed allocation.

Seven guarded instruction edits in the native number compositor widen the prefix copy, move the digits and remove the obsolete suffix copies. Single-digit labels start at logical x=8, followed by the digit at x=56. Two-digit labels start at x=0, with digits at x=48 and x=64. The 160 by 24 pixel, 4bpp output allocation, 80-byte row stride, 24-row loop and original texture dimensions remain unchanged. Horizontal texels remain doubled to compensate for the native display aspect.

All numbers from 0 through 99 are checked for buffer bounds and exact native digit preservation. The shared renderer covers all stage-entry cards; mission titles and other UI uses of episode terminology are outside this change.

## Build and validation

Run `python tools/build_stage_label.py --write --patch` on the pinned v0.3.15 image. The builder checks expected instructions and the existing Ep. artwork, changes only the shared texture slot and seven words, verifies decompression, reads back the modified ISO/runtime members, compares every disc byte with the planned writes, then reconstructs the ISO from the clean-source xdelta.

The English label inventory is `work/translation/en/stage_label.json`. Layout evidence and native addresses are in `work/ui/stage-label/verification.json`; `preview-0.3.16.png` shows reconstructed Stage 1, 9, 10 and 24 beside the previous layout.

## Verification limit

The preview uses the actual installed texture pixels and native composition dimensions, but is not an emulator capture. In-game title-card appearance and animation remain pending. Cold boot the v0.3.16 ISO and enter a stage; do not restore an old emulator state.
