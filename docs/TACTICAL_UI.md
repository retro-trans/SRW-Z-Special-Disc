# Tactical UI repair and translation

The four reference screenshots are preserved under `work/ui/tactical/`.
The current pass covers Tactical Situation counters, formation selection,
System settings help, and the allied-unit list footer. It does not alter story
dialogue. Emulator testing remains pending by the user's choice.

## New text fields

Thirteen entries received independent meaning and encoding review:

- Five standalone 隊 suffixes become **Sq** (Squad/Squads). Three belong to squad
  naming, one to deployment counts, and one to tactical force counts.
- The compact **Will** label replaces Morale in the shared footer stat field.
- Four movement-format fields use English square brackets and dash placeholders.
- Three terrain cells become **A**, **G**, **S** (Air, Ground, Sea/Water), using
  two-byte private Latin glyphs. AirOnly, GndOnly and AirSea retain their wording.

`native-inventory.json` binds exact file offsets, capacities, source bytes and
previous-release bytes. The five deferred COMPDATA squad-naming fragments from
0.2.18 are a separate category and remain deferred.

## Movement formatting defect

Native function `0x392b00` copies its template, writes four numeric bytes at
offsets 2–5, truncates at byte 8, appends a terrain string and adds a closing
bracket. The preceding ASCII replacement shortened the prefix, so numeric
insertion damaged the slash and subsequent text. The terrain helper `0x392bb0`
also writes two-byte cells at offsets 0, 2 and 4; its earlier three-ASCII-dash
placeholder could terminate before later cells.

The corrected populated template starts with bytes
`81 6d 81 40 81 40 81 5e`: a two-byte opening bracket, two fullwidth spaces for
the number, and a two-byte slash. The terrain placeholder is again six bytes.
Native number generation, buffer writes, movement rules and terrain tests are
unchanged. The special terrain strings fit the eight-byte scratch buffer,
including NUL. The longest composed string needs 18 bytes including NUL, fitting
the smallest observed caller field (`0x3a` through `0x4b`, before the pointer at
`0x4c` in the structure used by `0x3809e4`).

The diagnostic model uses the native digit table, native fullwidth spaces,
exact replacement bytes and the guarded native insertion sequence. It checks
0–99 movement points against all eight terrain masks and all three special
terrain types, plus the no-unit template: **1,101 cases**. This is a byte/layout
model, not execution in an emulator.

## Layout

Seven ADDIU immediate coordinates change, without changing their instructions'
registers or operation. Move starts at x24 and its value at x76; the widest
movement string is GndOnly at 198 conservative units, ending at x274. Pilot
starts at x280; the name remains at x338. Will uses 34 units at x536, before
the three-digit value region beginning at x574. Level/name numeric values remain
unchanged.

Forces moves to x96. Allied numbers retain right edge x204 and their Sq suffix.
The slash moves to x227. Enemy numbers and their suffix move to x288. The model
checks three-digit values and the left panel's x320 boundary.

The preview uses the installed Latin atlas and conservative advances. Native
wide punctuation/digits use an approximate Windows font. It is explicitly
labelled as a reconstruction, and makes no runtime acceptance claim.

## Existing text shown in the screenshots

The relevant formation, help and heading translations were already in 0.2.18
and 0.2.19. The new audit checks the actual native selector bases:

| Display | Native routine / COMPDATA array | English entries |
| --- | --- | --- |
| Formation list | `0x363d20` / `0x6a170` | 3 |
| Formation diagram label | `0x363f24` / `0x6a180` | 3 |
| Settings help | `0x3c0e9c` / `0x6a0e0` | 22, plus 14 empty option slots |
| Unit/squad list headings | `0x34dd6c` / `0x6a1d0` | 15 |
| Group Formation hint | `0x365b78` / `0x6a198` | 1 |

The pictured music option resolves through slot 4 to **Play unit music during
battle animations.** All 44 nonempty targets resolve to reviewed English in
the loaded executable pool. Source Japanese strings remain in COMPDATA because
the earlier translation deliberately redirected the pointers. No second active
Japanese display path was identified. The screenshot build was not confirmed.
A fresh boot of the new ISO is the appropriate runtime test; an older save state
may retain previously loaded code and text.

## Preservation and verification

The component changes 13 bounded text fields and seven coordinate words, with
preimage checks. The independent final-disc audit restores those 20 spans and
requires the complete executable to equal v0.2.19. Every other translated archive
member is compared with the previous build, and the parent audit retains all
story, graphics, pointer, patch-reconstruction and input-integrity checks.
