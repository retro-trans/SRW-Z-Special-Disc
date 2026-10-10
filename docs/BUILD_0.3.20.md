# Build 0.3.20

Local test candidate based on v0.3.19. Translates the six remaining Japanese labels visible in the user's Battle Viewer screenshots.

| Label | English |
| --- | --- |
| Attack icon | ATK |
| Counterattack icon | CNT |
| Battle-start button | Start Battle |
| HIT: barrier | B |
| HIT: barrier penetration | P |
| HIT: defend | D |

Single-letter HIT abbreviations fit the original narrow indicator cells. ATK and CNT use matching font sizes. The native selected/disabled coloring remains controlled by the game.

## Native bindings

The three artwork labels are in the linear 256×256, 4-bit word sheet at `KURODATA/KVMDATA.BIN + 0x41200`. The sampling rectangles come from KVPDATA sprite definitions:

| Label | Rectangle (left, top, right, bottom) | Matching sprite records |
| --- | --- | --- |
| Start Battle | 88, 16, 176, 40 | 0x3C80, 0x3CA2, 0x3E90, 0x3EB2 |
| ATK | 112, 64, 144, 96 | 0x293D6, 0x29450, 0x29472 |
| CNT | 144, 64, 176, 96 | 0x292D0, 0x29356 |

Only pixels inside these rectangles change. Their shared frame/state definitions and palettes remain identical. The HIT labels occupy three eight-byte executable string fields at file offsets `0x3C3EA0`, `0x3C3EA8`, and `0x3C3EB0`. No instructions or string pointers change.

## Build and verification

Build: `python -B tools/build_battle_viewer_labels.py --write --patch` (dry run without flags).

The builder pins the base image, atlas, executable, sprite definitions, font, and each original label. It checks native sampling bounds, glyph margins, pixel and text readback, untouched texture pixels, unchanged palette/header bytes, and unchanged executable data outside the three string fields. ISO and runtime-VMAP reads must agree; the entire output is compared against the exact planned writes. The clean-disc xdelta is reconstructed and its output hash checked.

Translations/bindings: `work/translation/en/public/battle_viewer_labels.json`.
Local screenshots, decoded atlas, layout and static preview: `work/ui/battle-viewer-labels/`.

## Verified output

- ISO: `SRW Z Special Disc English v0.3.20.iso`, 3,791,781,888 bytes.
- ISO SHA-256: `414c0228a9bf23caeeb697aacda6cf69a9bfc95d2fb88dc6ab0a2b31309053f6`.
- Patch: `SRW Z Special Disc English v0.3.20.xdelta`, 17,096,103 bytes.
- Patch SHA-256: `61d5741c682ea7f38107e81f969989390fd602a32f28678c40af744c2f556817`.
- Full-disc comparison passed: all bytes outside the planned writes are identical to v0.3.19. Applying the patch to the clean disc reproduced the output ISO exactly.

## In-game verification pending

Cold boot v0.3.20 without an older emulator save state. Open Battle Viewer and check both attack/counter sides, their selected/disabled appearances, the three HIT indicators, and Start Battle. The v0.3.19 help translations are retained.
