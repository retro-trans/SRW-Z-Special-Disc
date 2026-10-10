# Build 0.3.18

Local test candidate based on v0.3.17. Translates the title artwork and Special Theater menu reported in the two screenshots.

## Artwork

- Reuse the accepted SRW Z English logo from its v0.9.82/v0.9.83 title bank, SHA-256 `fed49ccb59cffe2ddbf0f7de6cbaede647a03aa51fe372941b429f0c4e2ba6b5`.
- Update both title consumers in VT1 records 7 and 29: the English wordmark and matching glow. Keep the original Z texture, animation sprites, palettes, and texture headers. Special Disc has several extra palette colors; differing donor indices map to exact native RGBA matches instead of replacing its palette.
- Translate the separate Special Disc subtitle in VT1 record 28. Preserve its parallelogram border, orange tail, flame textures, and palette variants.
- Translate the Special Theater header and all five banners in AIDDATA's third compressed record, at `0xC5F0..0x63B50`. Labels: **Quit Messages**, **Movie Gallery**, **Design Gallery**, **Battle Theater**, **Wallpapers**. The latter is an additional menu asset beyond the four shown in the screenshot.
- Preserve native illustrations outside the text regions, underlines, banner edges, and all menu geometry. Reconstruct only the old glyph backing and render English through the original palette.

The title's 512×256 8-bit textures, subtitle's 512×256 4-bit textures, and Theater's 1024×128 banner textures use their native GS upload layouts. Theater's 512×64 heading also requires unswizzling; the superficially similar VT1 mode headings use a different layout.

## Build and verification

`python -B tools/build_title_theater.py --write --patch`

Without flags, the builder authors local previews and validates resources without writing a game image. Requires the local SRW Z reference bank and native compressor. The original game resources remain local and are not included in source control.

- Pin v0.3.17's full-image hash and each of the four decoded resource preimages.
- Verify texture index roundtrips, strict BanLZ decoding, slot capacities, protected texels, all palettes and headers.
- Patch only the four original compressed slots, with no relocation or executable changes.
- Verify both ISO-directory and runtime-VMAP member reads and compare the entire candidate against exactly the planned writes.
- Create a clean-disc xdelta and verify the reconstructed image hash.

Public short-label translations: `work/translation/en/public/title_theater.json`.
Local coordinates, raw resources, native-palette previews and verification reports: `work/ui/title-theater/`.

## Verified output

- ISO: `SRW Z Special Disc English v0.3.18.iso` (3,791,781,888 bytes).
- ISO SHA-256: `113301a3597717c00add5911289885ab9d60671314ff827af0bc7b5344487ae1`.
- Clean-disc xdelta: 17,096,133 bytes; SHA-256 `ee11527940290f27465c7a1642e00cadc67442c0280621d400f66ba08e067278`.
- Clean-disc reconstruction matched the ISO exactly. The final authoring report matches all four installed resource hashes.
- Native-slot spare bytes: 16410, 1595, 9203, 29821, for title intro, subtitle, title menu, and Theater respectively.

## In-game check still needed

Cold boot v0.3.18 without an older save state. Check the animated opening and main title, then enter Special Theater and move through its menu options. Preview images show decoded native textures; they do not establish emulator playback correctness. The static title preview omits the animated flame fill of the Z.
