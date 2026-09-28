# Squad menu follow-up candidate 0.2.24

This release addresses the Join report and SELECT NAMING screenshots. The
shared indexed button images now read **OK** and **Cancel**. Native highlight
palettes and sprite geometry are preserved.

Fourteen text fields are updated. Join headers are shortened to `[Join] Tag`
and `[Join] Unit`; the report reads `Sq NN - Confirm joining.` or
`Sq NN - Cancel joining.` The squad number remains supplied by the game.
The trailing space after Sq separates its letters from the colored number.
Confirm describes the highlighted action, rather than claiming it has already
completed.

## Composed help and layout

The naming help had an English red label over a Japanese sentence containing
a fixed gap for a shorter native label. The complete English composition is:

> Select a squad and rename it using
> a method above. Select a naming method.

The red phrase is `Select a squad`; twelve ASCII spaces reserve 156 units in
the black first line for its 142-unit width. Related formation help uses:

> Auto-form squads using this plan.
> Select a formation plan.

Fourteen spaces reserve 182 units for the 168-unit red phrase `Auto-form squads`.
Both overlays therefore have a 14-unit gap. Existing colors, selectors and
two-line positions are retained. These are font-based layout checks, not
emulator screenshots.

The clipped Keyword and Random descriptions are shortened to
`Name squads from members' keywords.` and
`Auto-pick a naming method for each squad.` They measure 362 and 423 units,
within the 430-unit limit for this panel. The other naming descriptions retain
their existing wording.

## Bindings and preservation

Five previously deferred composed-help fields are now translated at decoded
COMPDATA offsets `0x97150`, `0x97180`, `0x971b0`, `0x971e0` and `0x97210`.
Three existing pool fields and two fixed Join headers are updated in place,
as are four executable text fields. No instructions, pointers, allocations
or game logic change. The writer requires the exact 0.2.23 payloads first.

Only two 48-by-24 cells in KVMDATA sheet 4 change: `[160,32,208,56]` and
`[160,56,208,80]`. The texture header, palette and every other indexed pixel
remain identical. The independent audit restores only the 14 approved text
spans and these two cells, then compares the complete payloads to 0.2.23.
Every other archive, including STAGE and all story dialogue, stays identical.

All 16 entries passed independent meaning review. Component dry runs, atlas
inspection, the independent finished-disc audit, exact patch reconstruction
and recorded-input verification pass. Emulator testing remains pending by
user choice.

## Output verification

- ISO: `work/output/SRW Z Special Disc English v0.2.24.iso`, 3,791,781,888 bytes.
  SHA-256: `d7d88c7135a00e572a3d344740c77ab0d2ce39f0dae242f0e1180e2d48ff22b3`.
- Patch: `work/output/SRW Z Special Disc English v0.2.24.xdelta`, 5,064,472 bytes.
  SHA-256: `c4620a45da7c94ad6ef93ca0cc7a020a5c4d9bbd0b30f68a13c076807108a1fb`.
  Applying it to the clean source reproduces the exact ISO.
- All 3,728,966,076 bytes outside the 65 planned write ranges match the clean
  disc. Relative to 0.2.23, only COMPDATA, KVMDATA and the executable change.
  The independent audit verifies the 14 text fields, two tiles and all
  protected bytes, then runs every earlier component audit.
- Executable SHA-256:
  `363ba07027c595649efde63c69d4d0860a67d60757a74eb51e85f0ecbd3ae2df`.
  Its size, English pool, heap boundary and executable instructions are unchanged.
- All 313 recorded inputs match: 131 Python files, 153 translation files,
  19 glossary files and ten binding inventories. The 317-entry input ZIP is
  11,052,423 bytes; every entry was read back exactly. SHA-256:
  `13ca970964ab2b7097a33a03b13d802f87f4cca878989145ca834b08344787d4`.

The first audit completed its binary assertions but could not serialize its
report because a result variable was shadowed by an older squad byte buffer.
Renaming that variable fixes report output without changing any assertion,
ISO or patch. The receipt records both auditor hashes and the original
receipt hash in `post_build_audit_report_fix`; the original receipt is retained
in `work/analysis/build-0.2.24-original-receipt.json`. All final audits were rerun
successfully, and the input snapshot includes the corrected auditor.
