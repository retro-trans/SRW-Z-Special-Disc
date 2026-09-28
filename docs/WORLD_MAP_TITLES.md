# Pre-dialogue globe location cards

The user's green-globe screenshot reads **Western Gallia Continent**. It is
MAPMODEL member 138, not a MAPNAME string or story dialogue field.

The format was located using the upstream
[Special Disc bindings](https://github.com/dyzz/srwz-zh/blob/main/config/assets/special-disc/world-map-title-bindings.json),
[writer](https://github.com/dyzz/srwz-zh/blob/main/tools/special_disc/writeback/world_map_titles.py), and
[Special Disc investigation](https://github.com/dyzz/srwz-zh/blob/main/docs/special-disc/FONT_AND_WORLD_MAP_TITLES_20260920.md).
The ten shared Japanese pixel hashes match our clean disc exactly. English
wording and pixels are independently authored; no Chinese pixels are imported.

## Native ownership

- `MAP/MAPMODEL.BIN`: 39,561,952 bytes, SHA-256
  `a104ef2ef8daaf122ffdcb6fd5b143940d5ab11515a4d5c25598636a5f0bca79`.
- Executable file offset `0x3542F0`: 202 offsets for 201 compressed members.
  Table SHA-256 `c86d90b9153d4f62a1f860e33275f0d5ecb66d4cb64c4b5b0585c1990287f86a`.
- All 120 world-map slots (81–200) are inventoried: 107 native 6,736-byte
  dummy payloads and 13 actual location cards. Their IDs are 102, 111, 118,
  119, 138, 139, 140, 160, 163, 193, 195, 196 and 197.
- Each caption owns exactly 8,192 bytes: a 512×32 image with two 4-bit indices
  per byte, low nibble first, and bottom-up rows. This is neither TIM2 nor a
  swizzled texture. Its transfer descriptor declares the full 512×32 region.
- Caption offset is `0x4B0` for 102, `0x10D060` for 193, and `0x115160` for
  the other eleven. The following palette, descriptor and English subtitle
  are protected. Member 102 has the inherited WORLD MAP subtitle; the other
  twelve have the Special Disc footer shown in the user's screenshot.
- Complete source bindings are in `work/ui/location-cards/world-map-bindings.json`.

The builder replaces the entire caption image, so clearing old Japanese
strokes is part of the owned operation. Every decoded byte outside those 13
spans remains native. All other 188 compressed members are byte-identical.
The archive, executable offset table, allocation sizes, map geometry and
STAGE dialogue chunks are unchanged.

## English and layout

All 13 source images were visually transcribed and independently reviewed.
The review changes general military references from Army to Forces; it does
not add military wording to the separate Federation Headquarters caption.
A subsequent scoped name pass changes Dome Polis to locked Domepolis.
Gallia, Ameria, Bellforest and Tresor Institute follow existing glossaries.
Katez and McConnell remain project spellings without an official-localization
claim. Newark is corroborated by an English Special Disc playthrough; see
`work/glossary/world-map-terms.json` for sources and limitations.

Full wording is used for every caption, including the southern portion of
South Ameria. Arial Narrow is centered within the declared image, with at
least eight horizontal and two vertical pixels of margin. Font sizes range
from 18 to 28; the two longest military-base captions use smaller type. The
font SHA, reviewed text, pixel SHA and measured ink bounds are frozen.

`world-map-titles-english-0.2.16.png` is a native/English texture comparison,
not an emulator screenshot. Runtime legibility and timing remain pending by
user choice. No PCSX2 session was run for this change.

## Checks

`test_world_map_titles.py` checks corner orientation, nibble order, all palette
indices and rejection of malformed or overflowing captions. Both native and
new compressed data pass strict decoding and exact pixel roundtrips. The
writer proves non-caption preservation and original-allocation fit.
`audit_world_map_titles.py` independently reads the final ISO, compares all
201 members, remeasures the 13 frozen pixel images, and protects all other
decoded data. The normal full-disc and xdelta reconstruction checks also run.
