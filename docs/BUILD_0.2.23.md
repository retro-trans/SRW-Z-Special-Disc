# English setup and Bazaar artwork candidate 0.2.23

This release applies the main game's indexed-image method to the reported
intermission and Bazaar menus. Fifteen English tiles come directly from the
local SRW Z v0.9.85 donor after verifying that their Japanese source pixels and
complete palettes match the Special Disc. Eleven additional tiles cover the
two intermission headings, large BAZAAR heading and eight scrolling fragments.

The 26 reviewed entries include Units, Pilots, Squads, Bazaar, Options, Data,
Next Map, Buy, Sell, Parts, Items, EP, Funds and SR Points. The scrolling
messages read `Cleared through EP N "Title"`, `Cleared through "Prologue"`,
`NEXT: Deploy N squads` and `MISSION N In progress`. Existing MISSION, NORMAL,
HARD and EX-HARD artwork remains, with consistent display geometry.

## Artwork and layout

Only indexed pixels in KVMDATA sheets 5, 6 and 10 change. Texture headers,
palettes, dimensions, unrelated pixels and the earlier sheet-7 squad patches
are preserved. Native palette animation continues to supply button colors.

The main-game donor's new scrolling text begins at y64, which would overwrite
the Special Disc's MISSION/NORMAL/status artwork. The new fragments instead
use verified empty space at y104–248. The Prologue tile is replaced in place.
The Special Disc's twelve 14-byte sprite records begin at ELF file offset
`0x3a0440`. Their colors remain unchanged; only UVs, advances, heights and
vertical offsets are adjusted. Eleven instructions in the banner's title and
digit drawing paths align the title, three digit styles and fragments. No
jump targets, gameplay conditions or new executable code are introduced.

The two INTERMISSION headings keep INTER and MISSION in separate native word
regions. MISSION begins in the source suffix area at x96 instead of falling
in the middle of a proportionally spaced English word. The composed SETUP
heading is an explicit in-game visual check; its final appearance has not
been confirmed in an emulator.

## Bazaar banner

The pictured slogan is a fixed 128-byte Bazaar banner in STAGE records 44,
49 and 50, at decoded offsets `0x1d44`, `0x2b24` and `0x1d84`. All three share
the same surrounding shop structure. They now read **Does willpower decide
the outcome?**, independently reviewed as ordinary willpower, not a named
Will/Morale mechanic. The complete inventory finds exactly these three copies.

The English text measures 343 units in the installed font. It fits the fixed
field and the 500-unit banner budget. Compression stays inside each original
record allocation. Restoring only the three banner fields reproduces every
other decoded byte from 0.2.22, including dialogue, shop configuration, mission
conditions and gameplay data.

## Validation

The combined component dry run and independent preflight pass. The audit
checks all 26 tile hashes, 12 banner records, 11 instruction words and three
slogan slots. It verifies all other executable/archive bytes against 0.2.22.
Older component audits receive the previous data only after these actual new
changes have been validated. Source bindings, reviewed English and native/
English previews are under `work/ui/setup-art` and `work/translation/en`.

The finished-disc audit, patch reconstruction and recorded-input verification
pass. Emulator testing remains pending by user choice. No story dialogue is
translated.

## Output verification

- ISO: `work/output/SRW Z Special Disc English v0.2.23.iso`, 3,791,781,888 bytes.
  SHA-256: `364823867ffab1a5b2a610b172a6621b165cf08cd2c17e3330e0904dd8d896b5`.
- Patch: `work/output/SRW Z Special Disc English v0.2.23.xdelta`, 5,063,804 bytes.
  SHA-256: `49b9e78704c7849f45e770800de5af494bba182da413a3dafb406a0b3ea9b5b5`.
  Applying the patch to the clean source reconstructs the exact ISO.
- All 3,728,966,076 bytes outside the 65 planned write ranges match the clean
  disc. Relative to 0.2.22, only STAGE, KVMDATA and the executable change.
  The independent audit restores the explicitly allowed fields and verifies
  every other byte against that release, including all story dialogue.
- The executable remains 4,112,380 bytes. SHA-256:
  `72ac82c1efd277b1ac9de84e9f898604bad7dbe491f04d58e72389f8e2b22172`.
  The English pool remains 122,876 bytes, ending at `0x83d1fc` below heap
  `0x83d600`.
- All 308 recorded inputs match: 129 Python files, 151 translation files,
  19 glossary files and nine binding inventories. The 312-entry input archive
  is 11,040,709 bytes; every entry was read back exactly. SHA-256:
  `230b9897e739b75cd8e4ae0887fc99347468b0a47122a891d12a1873d84264ce`.
