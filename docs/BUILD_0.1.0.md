# English front-end build 0.1.0

Built 2026-09-25. This is a limited graphics test candidate. The current scope
excludes story dialogue; battle dialogue also remains untouched in this build.

## Delivered scope

| Native VT1 chunk | Atlas | Labels |
| --- | --- | --- |
| 16 | Title menu | EXTRA STAGE, SPECIAL THEATER, LIBRARY, BATTLE VIEWER |
| 30 | Extra Stage menu | STORY MODE, LOAD, CHALLENGE, CONTINUE |
| 53 | Battle Viewer menu | NORMAL, TRI, SIMPLE, SINGLE |

Each 512x512 atlas holds four 256x200 button groups. Each group contains five
256x40 state tiles. Labels are centered within the existing frames, using
Arial Narrow Bold at 25 pixels, rasterized at 4x and reduced with antialiasing.
Only local rectangle `(29, 4)..(237, 34)` in each tile may change. Original
palette bytes, TIM2 headers, padding, and pixels outside the label rectangles
are protected. The five native states intentionally include pale transition
frames; these are not five different labels.

The longest measured label is SPECIAL THEATER at 191.5 pixels; all labels fit
the 208x30 permitted rectangle. Measurements are texture-space bounds, not
in-game screen coordinates. See `work/ui/english/manifest.json` for each label.

## Artifacts and identities

All output paths below are under `work/output/`:

- `SRW Z Special Disc English v0.1.0.iso`: 3,791,781,888 bytes.
- `SRW Z Special Disc English v0.1.0.xdelta`: 204,843 bytes.
- `SRW Z Special Disc English v0.1.0.json`: source and output identities,
  texture capacity, hashes, tool snapshot, and validation results.

| Artifact | SHA-256 |
| --- | --- |
| Clean MODE1/2048 source | `c3bd8c1af4e411e5ab2ae2d4be877170b6ab1ea9b51fa62bc0b91a51ba1a2952` |
| English ISO | `f7665547079e7c6427a589a0b8b6b960a9fd5e02c970965cc546f2eb301eaac6` |
| xdelta patch | `024a233aadc48e8c9f361ab785ec8972898f775aa47e70d88bc54419c6451ba0` |

The patch applies to `work/source/special-disc.bin`, not directly to the CHD.
Source extraction and identity were checked in the initial assessment.

## Completed validation

- Asset authoring dry run: all label measurements inspected before writing.
- Native and English atlas previews visually checked for readable text and
  intact frames. These PNGs are texture previews, not emulator screenshots.
- Each replacement is read back through both regular and strict decompressors.
- All three replacements fit their original slots, without moving archive data.
- Whole-image comparison verifies **3,791,501,264 protected bytes** unchanged.
  All differences are within the three menu texture slots; 277,854 bytes differ.
- Every ISO member retains its original path, size, and LBA.
- The executable, font, STAGE story data, and SRVC battle dialogue are unchanged.
- Decoding the xdelta against the clean source reproduces the exact output hash.

| Atlas | Native slot | New compressed bytes | Remaining bytes |
| --- | ---: | ---: | ---: |
| Title menu | 119,344 | 98,980 | 20,364 |
| Extra Stage menu | 106,496 | 82,648 | 23,848 |
| Battle Viewer menu | 54,784 | 44,696 | 10,088 |

The build receipt captures tools as they existed at assembly time. Afterwards,
`export_menu_assets.py` was restricted to the three verified atlases and its
unused heading previews removed. That exporter is not a build dependency;
the ISO, frozen English pixels, and build code were unchanged.

## Runtime validation: pending

An isolated PCSX2 1.7.4005 instance was prepared in `work/emulator/` and opened.
Windows activation failed, captures were black, and attempting the System menu
returned `GetCursorPos failed: Access is denied. (0x80070005)`. No ISO was booted
through that instance. No runtime screenshot or gameplay acceptance is claimed.
The user explicitly chose to leave emulator testing pending.

Once desktop access is available:

1. Open the ISO through the isolated emulator's System menu.
2. Inspect all four title-menu buttons and their selection transitions.
3. Inspect Extra Stage's four buttons without starting Story Mode.
4. Inspect Battle Viewer's four buttons and return to the title menu.
5. Capture F8 screenshots under `work/ui/runtime/`, recording the ISO hash.
6. Check navigation, clipping, stale pixels, and readability at native scale.

The isolated settings disable both memory-card slots and texture replacement.
Keyboard mapping: arrows for direction, X for Circle/confirm, Z for Cross/back,
Enter for Start, and F8 for a screenshot. Existing user memory cards were not
copied. Save/load and main-game Data Link behavior have not been tested.

## Next non-story work

1. Complete runtime acceptance of these three menus and adjust artwork if needed.
2. Decode the smaller heading textures correctly before translating them; the
   512x512 atlas mapping is not yet proven for those textures.
3. Port the English font/width runtime with SP-specific address and capacity
   checks, enabling system prompts and other text-rendered UI.
4. Reconcile the documented glossary conflicts before importing names, abilities,
   and interface terminology. Preserve provenance and SP record identities.
5. Add further menus and library/UI text in small verified builds. Story dialogue
   remains excluded unless the user changes that instruction.
