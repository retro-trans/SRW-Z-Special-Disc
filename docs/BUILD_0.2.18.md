# English deployment and squad candidate 0.2.18

Addresses both supplied screenshots:

- `＜出撃準備＞ 出撃の準備を行います。` becomes **<Deploy> Prepare for deployment.**
- The screen heading becomes **Squads**, leaving room for the NEXT counter.
- `リザーブへ` becomes **To Reserve**; the matching New Squad, To Squads and
  Deployed sprites are translated in the same sheet.
- `一回戦敗退組` becomes **Round 1 Losers**. All eight quarterfinal groups and
  three ships in the same tournament roster also receive reviewed English names.

The missed COMPDATA table contains 101 native entries. This pass installs 96;
five dynamic naming fragments remain native because their spacing and runtime
composition need confirmation. The draft, independent meaning review, approved
compact forms, source hashes and final geometry are stored under
`work/translation/en/deployment_ui*.json` and `work/ui/deployment/`.

All 113 entries passed meaning review before the glossary spelling pass.
Twenty compact equivalents retain the reviewed meaning. “Squads” is scoped
to one screen heading; the menu command remains “Squad Setup”. Sort/sub-info
“positions” is a literal translation whose precise saved-state behavior is
not yet confirmed. Full ship spellings follow the glossary.

## Data ownership and preservation

The menu strings live in the persistent English pool. Only their exact typed
COMPDATA pointer sites change; all prior translated menu data remains intact.
The twelve tournament names also use that pool. Chapter 13 changes only the
27 final pointer words in three 32-byte roster tables (12 squads, three ships,
12 deployed squads). Restoring those pointers produces the exact original
42,256 decoded bytes. Dialogue, membership, positions and event commands are
protected. The other 66 story chunks remain compressed-byte identical.

Four indexed sprite rectangles in KVMDATA sheet 7 change. Header, palette
banks, dimensions, other sprites and every other archive byte are protected.
The frozen pixel hashes are checked independently in the finished disc.
The preview is an extracted asset comparison, not an emulator screenshot.

Five tests pass: an allowed name-pointer edit, rejected squad-membership edit,
rejected unrelated chapter edit, rejected change to another story chunk,
and oversized button rejection. The component dry run and static visual review
confirm that all four English labels stay within their tiles.

Emulator validation remains pending by user choice. Check the NEXT gap,
hint alignment, button legibility, roster naming and save/reload behavior in
the tournament episode when testing resumes.

## Verified output

- ISO: `work/output/SRW Z Special Disc English v0.2.18.iso`, 3,791,781,888 bytes.
- ISO SHA-256:
  `e523bf977e8e4278aeec023cf7907e732ce269de23b45943eed7d283db7adb19`.
- Patch: `work/output/SRW Z Special Disc English v0.2.18.xdelta`, 4,815,171 bytes.
- Patch SHA-256:
  `e088733e7fd6b30447f537bf331107b345a5820451942fe406ddcb63a8a6cb92`.
- Applying the patch reconstructs the exact ISO. All 3,728,968,124 bytes
  outside the 65 planned writes remain native. ISO and runtime mappings agree.
- Independent final-disc readback passes for all 96 additional menu entries,
  12 roster names, 27 roster pointers, four word tiles and the Squads heading.
  It independently confirms all story dialogue and gameplay bytes unchanged.
- The longest new hint measures 553 units against the conservative 560 limit.
  The heading measures 66 units, down from 123. Chapter 13 retains 515 bytes
  of compressed-slot headroom and its original decoded length.
- All 205,402,816 bytes of VT1 match v0.2.17 exactly. Only COMPDATA, STAGE,
  KVMDATA and the executable have changed payload hashes. Earlier Library,
  chart, recap, narration, battle, demo, panel and title audits pass again.
- The original supplied screenshots are preserved as
  `work/ui/deployment/reported-deployment-hint.png` and
  `work/ui/deployment/reported-squad-screen.png`. The asset comparison is
  `work/ui/deployment/english-0.2.18.png`.
- All 263 receipt-listed inputs match: 105 Python files, 136 translation
  files, 19 glossaries and three binding inventories. The 267-entry input
  snapshot is 10,910,946 bytes; every entry was read back exactly.
  Snapshot SHA-256:
  `bb1e1fc46697e967061bdc04d44f5b479894619a07e919379de5eb783de7effd`.
