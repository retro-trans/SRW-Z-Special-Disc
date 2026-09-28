# Terrain rating rows: reuse of SRW Z's micro-glyphs

The user reported overlapping Air/Ground/Sea/Space labels on the pilot, mech
and weapon panels, and asked for the technique used in `../SRW Z`.

The primary local references are the donor's `_work/tools/patch_micro_glyphs.py`
and `_work/tools/fix_terrain_spacing.py`. The first draws each abbreviation as
a miniature image inside one 24×24 stored character cell. The second replaces
ordinary fullwidth word spaces with private blank cells so the overlaid rank
letters retain the native character pitch. Runtime styles can scale these cells;
24×24 is their stored image size, not a universal on-screen advance.

Special Disc already imports this renderer and the exact donor artwork through
`port_menu_runtime.py` and `port_compact_labels.py`. Its terrain dispatch uses
private codes, preserving ordinary Japanese characters for story text:

| Meaning | Visible image | Private code |
| --- | --- | --- |
| Air | AIR | `85dc` |
| Ground | GND | `85dd` |
| Sea | SEA | `85de` |
| Space | SPC | `85df` |
| Full-width blank | no visible ink | `85db` |

The bug was the row input. All 11 native copies of the seven-cell rating row
had been translated to the ordinary string `Air Gnd Sea Spc`, so the words
used variable-width Latin rendering instead of the imported compact images.
Single-character terrain labels were already handled by the earlier port;
its scan did not match these combined rows.

## Binding and repair

`terrain_rows.py --prepare` verifies the complete native row inventory, the
v0.2.20 preimages, cached donor ELF, imported art, glyph dispatch and renderer.
It defaults to dry run. Four meanings received independent review. The writer
retains each original 16-byte slot and replaces its input with:

`85dc 85db 85dd 85db 85de 85db 85df 0000`

These are four full-width image cells and three full-width blank cells, followed
by the original-size terminator/padding. Rating values, drawing coordinates,
runtime instructions, artwork, memory allocation and all other data are
unchanged. The separate movement-only A/G/S labels from 0.2.20 are unchanged.

The exact field offsets are `3b0460`, `3b2d48`, `3b2eb8`, `3b3038`, `3b3198`,
`3b32f8`, `3b3c10`, `3b4258`, `3b5068`, `3c0a58`, and `3c0dc8` in the executable.
The frozen inventory, original screenshots and preview are under
`work/ui/terrain-rows/`.

## Verification

Six regression tests check complete coverage, exact readback, old ASCII failure,
rejection of ordinary spaces, missing rows, changed donor art and unrelated edits.
The finished-disc audit expands the installed two-bit glyph images and confirms
the four images match the donor artwork. Visible ink stays within x2–20 and
y13–20; the spacer has no ink. Every code remains outside the private half-width
Latin range, so all seven characters follow the native full-width advance path.

The independent auditor restores the eleven slots and compares the complete
executable to v0.2.20. The prior tactical audit accepts only these separately
validated later fields as exceptions to its older whole-executable comparison;
its own 13 fields, seven coordinates and movement-model checks still use the
actual final executable. All other archives and VT1 artwork must equal 0.2.20.

The preview uses exact miniature-image pixels with illustrative rank letters
and a nominal 21-unit advance from the donor's documented example. It is not
an emulator capture. PCSX2 verification remains pending by user choice.
