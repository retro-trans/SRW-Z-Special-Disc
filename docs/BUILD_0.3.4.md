# v0.3.4 — Reported SEED Destiny battle captions

Local candidate based on v0.3.3. Addresses the Sting and Shinn screenshots from the pre-title battle demo. Their pilot names and series title were already translated; the remaining dialogue comes from the shared `BTL/SRVC.BIN` archive.

| Speaker | Caption | Source ID | Bank / record |
| --- | --- | --- | --- |
| Sting | Hyaa-ha-ha-ha! / This is awesome! | 10946 | 137 / 47 |
| Shinn | You're not even that good! | 10385 | 131 / 100 |

The slash indicates Sting's line break. His caption preserves the excited laugh and enthusiasm; Shinn's preserves the taunt about the opponent's lack of skill. Each source has one indexed occurrence, shared between playback contexts. This is a targeted fix, not a claim that all remaining battle dialogue is translated.

## Implementation

`tools/demo_battle_captions.py` binds both source IDs to their native normalized hashes and occurrences, then verifies that their live v0.3.3 entries are still Japanese. English strings are appended after the existing banks and only the selected offset words are changed. Existing translated strings, voice metadata and opaque tails remain intact. The archive grows by 80 bytes; its segment table is regenerated with unchanged record ordering.

Shinn's quoted line is 309 layout units wide. Sting's lines are 168 and 185 units wide, below the 460-unit limit. The strings use 28 and 34 encoded bytes respectively, within even the original 96-byte caption buffer. No executable, heap, voice selection, title artwork or pilot-name changes are needed.

The builder relocates both archive members into verified empty reserved space and updates their ISO and VMAP records. It checks both read paths and every ISO byte against the planned writes. The patch is reconstructed against the clean source disc for an exact hash comparison.

## Reproduction and verification

```text
python -B tools/build_demo_battle_captions.py
python -B tools/demo_battle_captions.py --prepare
python -B tools/build_demo_battle_captions.py --write --patch
```

The first invocation is a dry run; the writer refuses existing outputs. A separate audit compared all 59,262 indexed records in the old and rebuilt archives and found exactly the two expected text changes, with all voice metadata preserved. Evidence, measured layout and the audit are saved privately under `work/ui/demo-battle-captions`. The English-only inventory is `work/translation/en/demo_battle_captions.json`.

Cold boot v0.3.4 to check both captions during the SEED Destiny demo and confirm Sting's two-line layout. Emulator testing remains pending by user choice. Prior fixes are retained and the public v0.3.0 release is unchanged.

## Verified output

- ISO: `work/output/SRW Z Special Disc English v0.3.4.iso` (3791781888 bytes).
- ISO SHA-256: `b259761e1e179f8885903048f49e4f39085e6560d693a4d626f0e46660d585c3`.
- Patch: `work/output/SRW Z Special Disc English v0.3.4.xdelta` (7307534 bytes).
- Patch SHA-256: `3e6024f871ff7a65ae0aae066e3e2c1503e69afa562708c12bb0ecf1ca73ab44`.
- Whole-disc comparison passed; exact reconstruction from the clean source disc passed.
