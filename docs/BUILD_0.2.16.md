# English location-card candidate 0.2.16

Translates all 13 native globe location cards shown before dialogue, including
the user's **Western Gallia Continent** screenshot. This is the complete
non-dummy world-map title set in Special Disc. The location pictures are
separate from the 200 MAPNAME labels translated earlier.

All 13 meanings received independent review. Full geographic and organization
details are preserved, using centered type that fits each 512×32 texture.
The longest base names use smaller type. Existing glossary spellings are
applied after meaning review. See [format and research](WORLD_MAP_TITLES.md).

Only MAPMODEL changes relative to v0.2.15. Its offsets, size, palette, subtitle,
map data and all 188 unrelated compressed members are preserved. Earlier
translations and Story Mode alignment fixes remain included. Story dialogue
is unchanged; pending battle/suspend drafts remain separate.

Three targeted tests pass, covering exact pixel orientation/packing and
invalid-input/clipping guards. Component dry-run passes all 13 original
allocations with at least 16,568 bytes of compressed headroom. The output
MAPMODEL SHA-256 is
`3f92e77f079d03fc652c953b368f63b3dedb229db7b3336958f3479e03a6bd7c`.

The assembled ISO and patch pass exact reconstruction and independent final
readback. Emulator testing remains pending by user choice.

## Verified output

- ISO: `work/output/SRW Z Special Disc English v0.2.16.iso`, 3,791,781,888 bytes.
- ISO SHA-256:
  `0006cb813072dc4bcb58cee1ea94ab209ccc5d90d0cc2c278b65596bfa7b445f`.
- Patch: `work/output/SRW Z Special Disc English v0.2.16.xdelta`, 4,781,579 bytes.
- Patch SHA-256:
  `2e2a8ebe6e8dd81e2257965f826c2d3c21e067a99a2df6a6f1b80693b52ca297`.
- Reconstructing from the clean source produces the exact ISO hash. Both ISO
  directory and runtime mappings agree; all 3,733,781,132 bytes outside the
  43 planned writes remain native.
- A separate whole-disc comparison to v0.2.15 confirms all 3,752,219,936 bytes
  outside MAPMODEL are identical, including the previous alignment changes.
- Independent readback verifies all 13 caption pixel images, their centered
  bounds, original palettes, subtitles, offsets and map bytes. All 188 other
  compressed members are byte-identical.
- Earlier coverage passes again: 4,995 Library fields, 313 reference names,
  395 chart fields, 65 recaps, ten narrations, 1,917 battle captions at 4,870
  occurrences, all 20 demo titles/61 names, and all six aligned introductions.
- Source scripts, translation inputs, glossary inputs and native image bindings
  are recorded in the receipt and frozen with final audits in the input ZIP.
  All 247 receipt-listed inputs match. The 251-entry snapshot is 10,843,583
  bytes, SHA-256
  `a6a0af0489ea6f50ff295bbcaf5dfaf9c91a997272aa3e6f7e6108c998da301f`;
  every ZIP entry was read back exactly.

Two readers inspected all 13 static native/English image comparisons. Full
words remain visible without clipping; titles 139, 195 and 197 are smaller.
This is static layout evidence, not in-game legibility or timing acceptance.
