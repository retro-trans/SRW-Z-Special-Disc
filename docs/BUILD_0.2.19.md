# English mission-condition candidate 0.2.19

The reported conditions now read **Defeat all enemies** and **An allied
battleship is shot down**. This release covers all 60 distinct mission-condition
texts at 114 pointer sites across 39 modules, including all 18 Challenges and
the developer test module. All 38 hidden “???” pointers stay native.

Both the complete translations and 14 compact/layout variants received
independent meaning review before glossary spelling. Every group fits within
the native four-row limit; every line is at most 460 font units. Deadlines,
funds earned, damage/kill thresholds, reinforcements and deployment restrictions
are retained. See MISSION_CONDITIONS.md for category ownership and layout proof.

All six focused tests pass. Static previews cover every module. Translation
changes only typed display pointers; dialogue, event logic, mission rules and
source strings remain intact. The separate battle/suspend drafts are not
installed. All earlier translations remain included.

Emulator testing remains pending by user choice. Static layouts and binary
verification do not replace in-game acceptance.

## Output verification

- ISO: `work/output/SRW Z Special Disc English v0.2.19.iso`, 3,791,781,888 bytes.
- ISO SHA-256:
  `d4696bdaf0f4cdf16b13b382427bd24f63780d2208f8ccff42b5a0dfbbff0dbe`.
- Patch: `work/output/SRW Z Special Disc English v0.2.19.xdelta`, 5,052,893 bytes.
- Patch SHA-256:
  `83c01bad1979b8181aa5b34aaeefbcd9a884692f04413a01a06e73555b3f6f51`.
- Applying the patch reconstructs the exact ISO. The 3,728,966,076 bytes outside
  the 65 planned writes match the clean disc; ISO and runtime mappings agree.
- Independent finished-disc readback passes for all 60 texts and 114 pointers,
  all 38 native hidden placeholders, and all 117 table layouts. All earlier
  Library, menus, chart, recap, narration, battle, demo, panel and title audits
  pass as well.
- Only the 114 new condition pointers and 27 earlier roster-name pointers differ
  in decoded story modules. Every other story/gameplay byte matches the native
  source. The other 28 modules remain compressed-byte identical.
- All 39 updated modules fit their original slots; minimum headroom is 81 bytes.
  STAGE remains 527,552 bytes with its original table offsets and decoded sizes.
- The English pool grows by 3,352 bytes to 122,876. Its 119,524-byte prior prefix
  matches v0.2.18 exactly. The segment ends at `0x83d1fc`, below heap `0x83d600`.
- All 205,402,816 bytes of VT1 match v0.2.18 exactly (SHA-256
  `e3934c40ad268d6bd7f599c41a0428099d94f8663503bbd3b77fa8d93ae56d86`).
- The reference screenshot, 39 reconstructed previews, four contact sheets and
  measured layouts are under `work/ui/mission-conditions/`. Previews use exact
  Latin glyphs and advances, with approximate frames and native punctuation.
- Release comparison confirms that only STAGE and the executable have changed
  payload hashes since v0.2.18. No new archive members were added.
- All 277 receipt-listed inputs match: 113 Python files, 141 translation files,
  19 glossary files and four binding inventories. The 281-entry input snapshot
  is 10,984,536 bytes and every entry was read back exactly.
  Snapshot SHA-256:
  `0bce72e98d7219652b178f8b4989259aa001ab7ebb40690e48ac8d4653bcf9e7`.
