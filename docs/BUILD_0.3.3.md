# v0.3.3 — Character setup labels

Local candidate based on v0.3.2, addressing the Setsuko character setup screenshot. These labels occupy shared tiles used by the character setup screens.

| Meaning | Compact artwork |
| --- | --- |
| Rename | RENAME |
| Name | NAME |
| Nickname | ALIAS |
| Birthday | BORN |
| Blood Type | BLOOD |
| Confirm | OK |

The labels reuse the main SRW Z English v0.9.85 artwork. All six source rectangles match the native main-game tiles byte for byte at the pixel level; all palette banks and TIM2 headers also match. Only the six rectangles on page 5 of `KURODATA/KVMDATA.BIN` are copied. This changes 4,708 indexed pixels while preserving the surrounding translated Bazaar labels, portraits, texture dimensions and palette. No executable or text-data edits are required.

## Reproduction and checks

```text
python -B tools/build_character_setup.py
python -B tools/character_setup.py --prepare
python -B tools/build_character_setup.py --write --patch
```

The first invocation performs a dry run. Preparation writes the English inventory, screenshot record and atlas preview to private work folders. The builder rejects a changed v0.3.2 input hash or existing outputs. It checks every source tile, header, palette and indexed pixel roundtrip, then verifies that pixels outside the six rectangles are unchanged. The resulting atlas was inspected visually.

The ISO builder writes only the unchanged-size texture pixel plane. It reads the archive through both ISO and runtime mappings and checks the entire disc against the one permitted write span. The optional xdelta is encoded without local paths and reconstructed against the clean disc for an exact hash comparison.

Local metadata and previews: `work/ui/character-setup/`. English inventory: `work/translation/en/character_setup.json`. These work files remain ignored by Git. Continue future incremental builds from v0.3.3 to retain the artwork fix.

## Emulator validation pending

Cold boot this ISO and check the six labels on Setsuko's and Rand's setup screens. Verify that highlighted and idle labels fit their buttons. The user left emulator testing pending, so an in-game visual pass is not claimed. Public v0.3.0 release assets are unchanged.

## Verified output

- ISO: `work/output/SRW Z Special Disc English v0.3.3.iso` (3791781888 bytes).
- ISO SHA-256: `42c66969a1f02c43662eede6fad1dd67c28820ef794ab29aa594d71e7b124ac0`.
- Patch: `work/output/SRW Z Special Disc English v0.3.3.xdelta` (6343805 bytes).
- Patch SHA-256: `7c54fc8bc87a36ef4be7483c73d7a749ba5f395ab5f63a572dc77782eded5544`.
- Full reconstruction from the clean disc matched the ISO hash. Every byte outside the planned texture plane matches v0.3.2; every pixel outside the six label rectangles is unchanged.
