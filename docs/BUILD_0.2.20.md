# English tactical UI candidate 0.2.20

This release translates five squad suffixes and three terrain markers, fixes
the movement formatter's byte layout, and uses the compact Will stat label.
Seven position adjustments separate the tactical count and unit-list footer.
All 13 text/template fields received independent meaning and encoding review.
The reference screenshots and a reconstructed layout are under `work/ui/tactical/`.

The 44 related formation, settings-help and list-heading texts were already
English in 0.2.18 and 0.2.19. Their five native selector paths are now traced
and checked against the loaded English pool. The pictured music option reads
“Play unit music during battle animations.” Screenshot build identity was not
confirmed. Start this ISO with a fresh boot for runtime testing.

Seven focused regression tests pass. They include all 1,101 valid movement and
terrain combinations, the original shortened-template failure, two-byte terrain
cells, protected executable bytes and the 44 selector outputs. Conservative
movement width is at most 198 units; the value ends at x274 before Pilot x280.
The native numeric styles use 14-unit digit images with 11-unit advance, so
three digits span 36 units and two span 25. Both remain clear of the labels at
the revised coordinates. The preview's nominal 12-unit numeric placement is a
diagnostic approximation, with sufficient margin for the native spans.

The patch preserves story dialogue, scenario data, all previous English pool
bytes, graphics and earlier translations. Separate pending battle/suspend
drafts remain uninstalled. See TACTICAL_UI.md for the fixed-byte contracts.

Emulator testing remains pending by user choice. Static previews and binary
checks do not establish runtime acceptance.

## Output verification

- ISO: `work/output/SRW Z Special Disc English v0.2.20.iso`, 3,791,781,888 bytes.
- ISO SHA-256:
  `d0f899afebedf7f825d6bea548232cdafba1ca0235d767b6bab42841dd1f7766`.
- Patch: `work/output/SRW Z Special Disc English v0.2.20.xdelta`, 5,052,908 bytes.
- Patch SHA-256:
  `eade3f618ca543768a35778e344b506ee1803ef18cc9a0272cf974f266c5fa2e`.
- Applying the patch to the clean source reconstructs the exact ISO. All
  3,728,966,076 bytes outside the 65 planned write ranges match the clean disc.
- The independent finished-disc audit passes all earlier translation checks,
  all 13 tactical fields, seven coordinate words, 1,101 movement cases and
  44 existing English selector targets. Fourteen unused help slots remain empty.
- Only the executable payload hash differs from 0.2.19. Restoring the 20
  approved spans reproduces that previous executable exactly. Every other
  translated member and the complete VT1 texture archive match 0.2.19.
- The executable stays 4,112,380 bytes. SHA-256:
  `9dcbc7a8442ccf120adbbef08f5a1947957e9ce0c62dcad8e44211c3f213a6c2`.
- The English pool remains 122,876 bytes, ending at `0x83d1fc` below heap
  `0x83d600`. Every earlier pool byte is unchanged.
- STAGE remains 527,552 bytes with SHA-256
  `8d0c0d0b012c01a8f9a4f053abc7a55173447e633501bb1d98bba60b88f7ad9e`.
- All 285 receipt-listed inputs match: 118 Python files, 143 translation files,
  19 glossary files and five binding inventories. The 289-entry input snapshot
  is 11,000,816 bytes and every entry was read back exactly.
  Snapshot SHA-256:
  `28a146ef0f4f7e07778679f4c42f7887863c4aa458e409167c1927932926d929`.
