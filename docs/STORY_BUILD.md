# Story dialogue build

Story text is installed by a separate step on top of a finished non-story
build, so the non-story pipeline (`build_nonstory.py`, which guards every
story byte) is not modified.

```powershell
python -B tools/story_layout.py                          # 3-line fit + per-chunk byte budget
python -B tools/compile_story.py --stage <STAGE.BIN>     # dry run per chunk
python -B tools/build_story.py --version 0.3.x           # dry run on newest verified ISO
python -B tools/build_story.py --version 0.3.x --write --patch
```

After a new non-story build (e.g. 0.2.25), rerun `build_story.py` with
`--base` pointing at it; the story step reads that ISO's STAGE/HB and keeps
every change it contains.

## Inputs and order

1. `work/translation/en/story_final/` — reviewed dialogue after the name pass
   (`story_names.py`, SRW Z rank rulings included).
2. `work/translation/en/story_compact/` — `fit` variants used only when a row
   would need a 4th line or its chunk would not fit; bound by `was`.
3. `work/translation/en/story_extra_reviewed/` — captions, chunk-66 scene,
   choices, the silent row. Labels stay native (possible lookup keys) except
   the chunk-66 keyword entries whose links are translated with them. Mission
   conditions are owned by `mission_conditions.py` (English pool).

## Format

Speaker line (English, from `story_speakers.json`), then up to three body
lines; the first opens with 「 (（ for thoughts), the last closes with 」.
No indentation on continuation lines (main SRW Z English format). Line limit
480 font units using the installed Latin advances; 「」 count 24. Runtime
value tags `{tm}` are restored to the native ＜ｔｍ＞…＜／ｔｍ＞ text.
Captions keep the native `　` first line and are centred on 282 units with
ASCII spaces between ～ marks.

## Memory rules (from the SRW Z main-game tests)

- Strings stay inside the native Japanese text region of their chunk; text
  past the original record end draws an empty box or crashes.
- Trailing zero padding counts as free only when it runs into the next bound
  string (in chunk 66 a pointer word sits in such padding).
- Genuine pointer words: aligned absolute words (base 0x8045F0) outside every
  string span and not the header length words 0x0c/0x28/0x2c. Every repointed
  word must read back its intended text; every other decoded byte must equal
  the staged chunk.
- Decoded chunk lengths never change. Compressed chunks may grow: the archive
  is re-laid and HB.BIN's table (0x5170, 69 words; no executable copy) is
  rewritten. A grown STAGE.BIN moves into empty reserved DMY space with its
  ISO extent and VMAP entry updated.

A chunk whose text still does not fit stays exactly as the base build had it
(Japanese) and is listed in the receipt; nothing is truncated.
