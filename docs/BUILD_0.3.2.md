# v0.3.2 — Story Mode bonus results

Local candidate based on v0.3.1. This addresses the Funds, BS, PP and Parts screenshots for Another Side Record; their shared fields also serve the other episode selections.

| Page | English fields |
| --- | --- |
| Funds | Funds; Starting Funds; Total Funds |
| BS | BS; Starting BS; Total BS |
| PP | PP; Starting PP; Total PP |
| Parts | Parts; Added the above parts to your starting parts. |

The category starts at native-screen x=432, after the longest episode heading. Reward totals start at x=400, independent of label length. Route status markers use x=448 in all result modes. The parts message is 462 pixels wide at x=92, within the x=576 content margin.

## Implementation and validation

`tools/bonus_results.py` edits eleven existing COMPDATA fields without moving pointers or changing the decoded length. It guards the v0.3.1 executable hash and each text slot against the original disc. Four heading calls and six total calls retain the native append operation and then set only the second segment's horizontal position. The existing bounded status helper now also handles result modes 1–4. The heap and all reward calculations remain unchanged.

The two small helpers extend the English executable segment by 224 bytes, leaving 804 bytes before the unchanged heap. The builder moves the executable and COMPDATA into empty reserved disc space, updates ISO metadata and the data member's VMAP record, and checks every other image byte against v0.3.1. The boot executable has no VMAP entry.

Run with the project's Python environment:

```text
python -B -m unittest discover -s tools -p test_bonus_results.py -v
python -B -m unittest discover -s tools -p test_story_runtime.py -v
python -B tools/build_bonus_results.py
python -B tools/build_bonus_results.py --write --patch
```

The first build invocation is a dry run. The write invocation refuses existing outputs. Four bonus-panel tests exercise the machine instructions, row/segment limits, register preservation, text/style preservation, all five status modes, field widths, pointer preservation and rejection of changed preimages. Six story-renderer tests retain coverage of all 7,509 ordinary dialogue rows and two silent occurrences.

Local screenshots and coordinates live in `work/ui/bonus-results`; the English field inventory lives in `work/translation/en/bonus_results.json`. These private work files are ignored by Git. Continue future story builds from this candidate to retain the bonus-panel component; the older non-story builder still targets its frozen v0.2.24 baseline.

## Runtime check pending

Cold boot the v0.3.2 ISO and use an in-game save rather than an old emulator save state. Check all four bonus-result pages, with and without imported clear data, for headings, totals, dashes and the parts message. Reward values should match the previous build. The user has left emulator testing pending; no in-game visual pass is claimed. Public v0.3.0 release assets are unchanged.

## Completed local output

- ISO: `work/output/SRW Z Special Disc English v0.3.2.iso` (3,791,781,888 bytes).
- ISO SHA-256: `a60c118abc7c9470ed4df7894f335e613b0c87a229b781a824c6784cb4ec2552`.
- Patch: `work/output/SRW Z Special Disc English v0.3.2.xdelta` (6,342,716 bytes).
- Patch SHA-256: `9f6aa4c4abc3a6d71129f49623813a22f4e4ed825ade97a0c2fc2c6b6d6ef6a5`.
- Full clean-disc patch reconstruction matched the ISO hash. Whole-image verification found only the planned file placements and metadata changes.
- Final executable passes the story-renderer component's idempotence check; the v0.3.1 fix is retained.
