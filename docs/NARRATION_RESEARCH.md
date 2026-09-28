# Special Disc narration format and English integration

Read-only inspection of the Special Disc source found:

- `DATA/MTZSPROS.BIN`: 6,592 compressed bytes, ten records with `vpro` tags.
- Whole-member SHA-256:
  `1aa53992cbaea30e95a2c66e771e95e10076ff8645a9e9b7c1f841dc5e32c59f`.
- Decoded record lengths: 800, 928, 800, 768, 848, 880, 880, 864, 848, 848.
- Every record has a 32-byte wrapper followed by a 28-byte `vpro` header.
  Its three children are `pict`, `text` and `bgm_`. All ten native records
  parse and serialize to identical bytes with `narration_format.py`.

The main-game donor does not have the same member name. Its
`DATA/MTV_PROS.BIN` is 9,056 bytes with fourteen `vpro` records, while
`DATA/MTV_PROP.BIN` is 2,232,448 bytes with twenty-three `TIM2` records.
These are potential format references, not established text matches. Do not
assume a common record index or copy their tables into Special Disc.

Build 0.2.4 leaves narration native. Build 0.2.5 translates all ten records:
episode openings/conclusions and two signed journals, separate from story
dialogue in STAGE chunks 1–67.

## Container and allocation contracts

The wrapper's two length fields both equal decoded length minus 32. The
`vpro` header holds record ID, duration, three child counts and total child
bytes at file offset 56. Each child has a four-byte tag and little-endian
payload length. Zero padding aligns the complete decoded record to 16 bytes.

The `text` payload consists of 30 bytes of formatting/active-time commands,
`rawt`, a four-byte text length, the length-delimited text (without a NUL),
then two 22-byte `modi` commands and one 12-byte `clip` command. The compiler
rebuilds only the raw text and containing lengths/alignment. Picture, music,
IDs, timing, formatting, modifiers and clipping remain byte-identical.

The executable contains ten decoded sizes at file `0x387850` (VA `0x486ED0`)
and eleven compressed offsets, including the end, at file `0x387880`
(VA `0x486F00`). Narration is resource kind 3; its native range guards accept
records 1–10. Shared pointer arrays at VA `0x486F30` and `0x486F40` point to
the size and offset tables, respectively.

Native loader `0x2E7EA0` calculates the compressed span from adjacent offsets.
At `0x2E8048` and `0x2E8138`, the loader reads the selected decoded size and
reallocates its buffer when needed (`0x100B70`). The `rawt` parser at
`0x2BF950` stores text pointer and length. Copier `0x2C4360` allocates length
plus one, copies that exact length and appends a NUL. Thus expanded records
use native allocation; the old Japanese byte counts are not English budgets.
The ISO assembler relocates the larger member and updates ISO and VMAP maps.

## Renderer and layout

Parser `0x2BF860` copies the four formatting bytes to object offsets
`0x40..0x43`. `0x2C20A0` transfers them to the drawing state. Drawing paths
call font setup `0x13A7F0` at `0x2C4E14`/`0x2C53A0`, then wrapper `0x22A200`,
which calls the ported native printer `0x13AD30`. They use the existing menu
font port and do not require a story setText hook.

All ten source entries have 13 lines; font parameters are `[25,12,25,14]`,
origin is `(-285,-92)`, and clip bounds are `(-320,-112,640,224)`.
The four parameters provide glyph dimensions and pen pitches. The fourth
is also used in native vertical clipping at `0x2C4B48..0x2C4BF0`.
The English wrapper conservatively limits horizontal advance to 550 units.
It uses the donor's wider bold advance directly, without scaling by 25/24.
At that width the right edge is at most x=265, inside the x=320 clip edge.
Thirteen rows at pitch 14 retain the native vertical sequence.

Balanced word wrapping preserves all words and exactly 12 newline bytes.
Journal dates and signatures occupy dedicated rows; the complete final book
attribution occupies two rows. All ten full drafts received source meaning
review. Two compact variants, IDs 6 and 9, received additional independent
meaning checking before insertion. Name normalization runs after these edits.
Provisional calendar/war/book names and their sources are recorded in
`work/glossary/narration-terms.json`; none is claimed as an official translation.

Ten reconstructed previews and `work/ui/narration-layout.json` record text
positions, bounds and timing. These previews use the donor Latin glyph atlas,
with fallback symbols in Arial. They do not simulate animation and are not
emulator captures. Runtime acceptance remains pending by user choice.

## Verification

`test_narration_format.py` checks all ten native identities, 70 expanded
compression/restoration cases across alignment boundaries, and 70 corrupt
length/truncation cases. The compiler checks native source hashes, review
hashes, glossary hashes, all table preimages, strict decompression and final
English text readback. The finished-ISO audit independently walks the nested
container lengths and compares all nontext commands with the clean image.
