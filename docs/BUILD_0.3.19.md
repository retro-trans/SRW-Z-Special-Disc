# Build 0.3.19

Local test candidate based on v0.3.18. Translates the bottom-left Battle Viewer help shown in the Exit and BGM Setup screenshots, plus the remaining entries in the same options/BGM table.

| Item | English help |
| --- | --- |
| Start | Start the Battle Viewer. |
| Save | Save settings to a memory card (PS2). |
| Load | Load settings from a memory card (PS2). |
| BGM Setup | Set automatic battle BGM updates. |
| Vibration | Controller-button token followed by “Toggle controller vibration.” |
| Exit | Exit the Battle Viewer. |
| Right leader's theme | Use the right leader's default theme. |
| Left leader's theme | Use the left leader's default theme. |
| Manual | Choose BGM manually. |

The three BGM choice labels are translated as well, for 12 fields total. The blank options-table entry stays blank.

## Implementation and checks

The strings occupy decoded COMPDATA offsets `0x98500..0x98710`, referenced by the options/BGM pointer tables at `0x6A354..0x6A388`. All pointers, allocations, control tokens, unrelated text, gameplay data, and executable bytes remain unchanged. Recompressed COMPDATA is relocated through the existing reserved-space planner, updating both the ISO directory and runtime VMAP.

The guarded builder checks the v0.3.18 image hash, packed/decoded COMPDATA hashes, each field preimage and pointer, encoded capacities, text readback, and exact preservation outside the 12 fields. Each message fits one line within a conservative 470-unit budget using the installed English glyph advances; the longest measures 463. The vibration button token is preserved byte-for-byte.

Build: `python -B tools/build_battle_viewer_help.py --write --patch` (dry run without flags).

Translations: `work/translation/en/public/battle_viewer_help.json`.
Local layout and native-font preview: `work/ui/battle-viewer-help/`.
The normal COMPDATA translation pass also reads these overrides for future rebuilds.

Whole-image comparison and clean-disc xdelta reconstruction passed.

- ISO SHA-256: `b90c78a891b20a2361a8ea42df84d26adb422dcbb44452674f3165d9ff860d59`.
- ISO size: 3,791,781,888 bytes.
- Clean-disc patch: 17,096,491 bytes; SHA-256 `5bbd2d1c771e1d8a33b7a1c7129e1233150ee75ae057161ed73ec24d21f5ef5b`.
- COMPDATA placement: LBA 1,811,239, 184,628 bytes; ISO and runtime reads agree.
- Every other disc byte matches v0.3.18.

## In-game verification pending

Cold boot v0.3.19 without loading an old emulator save state. Open Battle Viewer, move through the options menu and its BGM Setup submenu, and check the bottom help bar.
