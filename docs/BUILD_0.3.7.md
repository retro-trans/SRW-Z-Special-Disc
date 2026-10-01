# v0.3.7 menu reader correction

Local test candidate based on v0.3.6. Public release unchanged.

## Problem and correction

The reported Beater Services Work Log / Funds panel displays stale gold glyphs beneath its heading. Native menu preprocessor `0x363510` copies ordinary text two bytes at a time. For an odd-length ASCII label such as `Funds`, it copies the null terminator as the second byte and advances beyond it. A newline in the reused segment tail flushes the label and starts drawing stale bytes on another line. The earlier append-column tests did not exercise this reader.

The hook at `0x3638B0` sends the ordinary-text path to a 44-byte helper at `0x83D2E0`. ASCII consumes one byte; the native signed/high-bit two-byte path is retained. The native parser still handles button, spacing, style and newline tokens. This shared reader correction also protects other panels using odd-length English labels. It does not alter the story dialogue converter or any translated text.

The existing totals helper changes its relative X from 80 to 32 (absolute x400 to x352). Native font preset 0x33 uses 16-unit cells: Funds pads to 12 cells, giving a right edge of x544; BS/PP pad to 10 cells, giving x512. This leaves room inside the panel. Heading and row-marker columns remain unchanged.

## Validation

- Seven tests in `tools/test_menu_reader_fix.py` execute the actual installed scanner and native button/spacing handlers. Font submissions and standard library helpers are intercepted; this is not GPU/emulator validation.
- Reproduce the old reader's extra line with stale bytes after `Funds`, then verify the fixed reader never reads beyond its terminator.
- Check all bonus labels, ASCII lengths 1–65, Japanese/private glyph pairs, newline boundaries, button and spacing tokens, unchanged executable bytes outside the six guarded word changes, and the unchanged heap boundary.
- Extend the existing English segment by 48 bytes including alignment. New executable size 4,112,652 bytes; segment end `0x83D30C`, below heap `0x83D600`.
- Relocate the executable to reserved sector 1,799,524; verify the complete ISO against the exact write plan. Reconstruct the clean-disc patch and compare the entire output hash.

In-game visual testing remains pending by user choice. Cold boot v0.3.7; older save states can restore the old executable.

## Outputs

- `work/output/SRW Z Special Disc English v0.3.7.iso` — 3,791,781,888 bytes.
- ISO SHA-256: `1235ec81df67d9b877f15b317e8dc46ead17e165fe362ba662e0025554e301cc`.
- `work/output/SRW Z Special Disc English v0.3.7.xdelta` — 9,587,633 bytes.
- Patch SHA-256: `c217439b8fed87297b56141773d9a31bc117bf43f35de97a073f8cc0c67546d8`.
- Build receipt beside the outputs; screenshot and private layout record in `work/ui/menu-reader-0.3.7`.

Reproduce with `python -B tools/build_menu_reader_fix.py --write --patch` after moving existing outputs aside. Without `--write`, it only validates the inputs and placement.
