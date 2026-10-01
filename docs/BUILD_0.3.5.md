# v0.3.5 — Rand and Mel console-care scene

Local candidate based on v0.3.4. The screenshot is message 288 of Special Theatre/suspend scene 56. The complete eight-message exchange is stored directly in the executable, outside the main STAGE story scripts. All eight messages and both speaker names are translated.

Rand's introduction now reads:

> We're Beater Services, the familiar roving repair crew! Known for honest service and our staff's smiles.

The existing independently reviewed meanings in `work/translation/en/suspend_reviewed.json` (IDs 288–295) were reused and shortened where needed. The company name follows the project's current “Beater Services” wording. The conversation retains the company pitch, the “love” answer, Mel's uncertain Gunleon fault report, Rand's full-force 45-degree chop joke and Mel's explicit rejection of it.

## Bounded installation

`tools/rand_suspend_scene.py` edits only the eight native text slots in `SLPS_259.20`, file offsets `0x3BE460..0x3BE6F0`. No pointers or command words change. Each source matches its reviewed hash and its typed scene-56 command. The entire base executable is hash-locked.

The installed v0.3.1 converter handles ASCII before the native parser, retaining the actual newlines and corner quotes. Each message is executed through the converter's integer instruction model, with output checked against the reference conversion. The longest converted message is 220 bytes including NUL, below the audited 452-byte physical space from the message's text offset to the allocation end. This is a physical allocation bound, not a recovered source-level array declaration. All converted lines stay below the parser's 256-byte line guard; no message contains dictionary-expansion keys.

Each message uses a speaker row and at most three body rows. Balanced wrapping is restricted to 400 units using the conservative story width model; the longest chosen line is 394. This is more conservative than the ordinary 480-unit story limit and the screenshot's native long lines. Actual in-game rendering still needs verification.

## Reproduction

```text
python -B tools/build_rand_suspend_scene.py
python -B tools/rand_suspend_scene.py --prepare
python -B tools/build_rand_suspend_scene.py --write --patch
```

The first invocation is a dry run. Preparation records the English fits, source hashes, pointer locations, widths and screenshot privately under `work/translation/en/rand_suspend_scene.json` and `work/ui/rand-suspend-scene`. The original review file is unchanged. No original Japanese conversation is exported or added to Git.

The builder writes the unchanged-size text span in place, reads the executable through both disc access paths and compares every ISO byte against the permitted write. The xdelta is reconstructed against the clean disc and must match the output hash. The other 288 suspend messages remain as in v0.3.4; this candidate does not claim full suspend-dialogue coverage.

Cold boot v0.3.5 and view all eight messages, checking Rand/Mel speaker names, the three-line introduction, punctuation and the final correction. Emulator testing remains pending by user choice. Public v0.3.0 release assets are unchanged.

## Verified output

- ISO: `work/output/SRW Z Special Disc English v0.3.5.iso` (3791781888 bytes).
- ISO SHA-256: `05e06eea01e9c7930e850a6abcc21333cb6ed662e4ce51d7e176604b8fe17fac`.
- Patch: `work/output/SRW Z Special Disc English v0.3.5.xdelta` (7307483 bytes).
- Patch SHA-256: `a9108efd29c305859538a7b0310913aaa5bec1a75fe995181f51ae15e1cb23b4`.
- Whole-disc comparison and exact patch reconstruction from the clean source passed. All bytes outside the eight text slots are identical to v0.3.4.
