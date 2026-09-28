# Story fit (compaction) brief

The reviewed English must now fit the game: each dialogue box shows at most
**3 lines**, and each STAGE chunk's English must fit in the **bytes its
Japanese occupied** (strings past the original record end do not render).
Your job: write shorter `fit` versions for chosen rows until your chunks fit.
Read `BASE_RULES.md` first. Do not spawn sub-agents; do the work yourself.

## Rules (BASE_RULES)

- Keep the **full meaning**: every clause, name, rank, reason, condition,
  negation, も/だけ/まだ nuance, and the end of the sentence. Compress wording,
  never content. Abbreviations are fine (Capt., Lt., Gen., HQ, info, etc.).
- Keep the speaker's voice and register. Keep placeholders (`$n`, `$c`…),
  `{tm}` markers and `{{Term}}` links exactly.
- Do not change glossary spellings. ASCII only. No Japanese in output.
- If a row cannot be shortened without losing meaning, leave it and list it
  under `could_not_fit` with the reason.

## Tools

- `python -B tools/story_layout.py --measure "text"` prints how the body
  wraps (add `--thought` for （） rows). It must be 3 lines or fewer.
- `python -B tools/story_layout.py --chunk N` prints the chunk's byte
  budget (need vs capacity) and its rows still over 3 lines, **including
  your saved fit file**. Re-run after writing; you are done with a chunk
  when it reports spare bytes (aim for 1-2% spare) and no rows over 3 lines.

## Input

`work/cache/story/fit/cNN.json` has every row of chunk NN in script order:
`id`, `jp`, current `en` (reviewed, names applied), `compact`, `bytes` (the
installed string), `lines_now` and `variant_used` (`overflow` = over 3 lines). Rows over 3 lines must get a `fit`. For the byte
deficit, prefer the longest rows and rows whose English is wordier than the
Japanese; each fit should save real bytes.

Chunk 66 (developer demo / Kanada tribute scene) strings are in
`work/cache/story/extra_A.json` + `work/translation/en/story_extra_reviewed/A.json`
(ids `x_...`); fit those the same way (the long keyword descriptions and the
magazine passage may be condensed but must keep every point).

## Output

`work/translation/en/story_compact/cNN.json`, one file per chunk:

```json
{"chunk": 11, "rows": [
  {"id": "c11_06070", "was": "<exact current en>", "fit": "<shorter full-meaning text>", "why": "4 lines -> 3"}
 ],
 "could_not_fit": [], "uncertain": []}
```

`was` must equal the row's current `en` exactly (from the fit input, or for
chunk-66 `x_` rows, the reviewed extra file); otherwise it is ignored.

## Report

Per chunk: deficit before/after, rows over 3 lines before/after, number of
fits, and any row where meaning was hard to keep.

## Fit review (independent)

Reviewers compare each `fit` with the Japanese (`jp` in `work/cache/story/fit/cNN.json`,
or `extra_A.json` for chunk-66 `x_` rows) and with the full `was`. Flag and fix only
real losses: a dropped clause, name, rank, condition, negation, も/だけ/まだ, a
changed referent or addressee, a broken placeholder/`{tm}`/`{{Term}}`, or English
that no longer reads naturally. Any fix must still fit (`--measure`) and must not
be longer in bytes than the `fit` it replaces unless the chunk has spare
(`--chunk N`). Write `work/translation/en/story_compact_review/cNN.json`:
`{"chunk": N, "fits_examined": K, "changes": [{"id", "was_fit", "fit", "why"}], "uncertain": []}`
(`was_fit` = the exact current fit). Do not edit the compact files.
