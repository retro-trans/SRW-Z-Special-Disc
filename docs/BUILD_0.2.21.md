# English terrain-row candidate 0.2.21

All 11 Air/Ground/Sea/Space rating rows now use the same compact character-cell
technique as `../SRW Z`: exact donor AIR/GND/SEA/SPC images separated by native
full-width blank cells. This repairs the ordinary-text overlap shown in the
pilot, mech and weapon screenshots. See TERRAIN_ROWS.md for the source tools,
complete row inventory and encoding contract.

The four meanings received independent review. Six focused regression tests
pass, including exact row coverage, spacer behavior, donor art and rejection of
unrelated edits. The earlier tactical audit also passes with this component
applied, including its 13 fields, seven coordinates and 1,101 movement cases.

The component changes eleven 16-byte text slots. It adds no runtime code, image
data, pointers or pool allocation. Rating values, draw positions, previous UI
fixes, movement-only labels and story dialogue remain unchanged. The static
preview uses exact donor glyph pixels; rank lettering and scale are illustrative.

Emulator testing remains pending by user choice. A fresh boot of this ISO is
required for a useful runtime check of the newly loaded text fields.

## Output verification

- ISO: `work/output/SRW Z Special Disc English v0.2.21.iso`, 3,791,781,888 bytes.
- ISO SHA-256:
  `a7b92c6d3c9d3dee5cc8a6151744cf843a16c22118e6a3c695acf498d2406c91`.
- Patch: `work/output/SRW Z Special Disc English v0.2.21.xdelta`, 5,052,912 bytes.
- Patch SHA-256:
  `fe33b67ae98d9d18f3946d28bb56fe54973f5c2f39e93b4f9f75144b9e9caf47`.
- Applying the patch to the clean source reconstructs the exact ISO. All
  3,728,966,076 bytes outside the 65 planned write ranges match the clean disc.
- The independent finished-disc audit passes all earlier translation checks,
  all 11 terrain rows, exact donor artwork, empty full-width spacer glyphs,
  the previous 13 tactical fields, seven coordinates and 1,101 movement cases.
- Restoring only the eleven approved 16-byte slots reproduces the v0.2.20
  executable exactly. Every other translated archive and all VT1 textures
  match v0.2.20.
- The executable stays 4,112,380 bytes. SHA-256:
  `8f6e6054753290561caad398692ce13ae8a835e462ffdbd8ccdb67e232c6f4b3`.
- The English pool remains 122,876 bytes, ending at `0x83d1fc` below heap
  `0x83d600`. No pool bytes or allocation changed.
- All 292 receipt-listed inputs match: 122 Python files, 145 translation files,
  19 glossary files and six binding inventories. The 296-entry input snapshot
  is 11,012,079 bytes and every entry was read back exactly.
  Snapshot SHA-256:
  `82015227897991ec5c646257ede5ec7d251205414ff3e0c83e39be65c2ed68ca`.
