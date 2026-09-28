# Story dialogue meaning review brief

You are the independent reviewer of first-draft English story dialogue.
Read `BASE_RULES.md` (project root) and `docs/STORY_TRANSLATION_BRIEF.md`
first; their rules apply. Your job is **meaning**, not style or spelling.

## Do the work yourself

Do not spawn sub-agents or forks. Review every row yourself, in order.
`rows_in_slice` must equal the number of rows in the input file.

## Input

`work/cache/story/review/cNN_SSS.json` — `{slice, rows:[{id, speaker_en, jp, en, compact?, note?}]}`.
`jp` line 1 is the native speaker; `speaker_en` is its English label.
`en` is the draft body (the build adds quotes and wraps lines). `compact`
is a shorter variant used only if `en` does not fit the box.

## What to fix (fix what is wrong, leave what is merely different)

1. Wrong meaning: reversed who-does-what, wrong addressee, wrong referent,
   negation/conditional/aspect errors (こうなったら = it has come to this;
   まだ = still / not yet), lost も (too) / だけ (only) / さえ (even).
2. Omissions: a dropped clause, name, rank, reason or condition. Additions:
   facts, subjects or names the source does not state (see BASE_RULES on
   supplying what the source omits). A placeholder (`$n`, `$c`, …) must
   appear exactly as in the source; never add one.
3. Gender: he/she used where the scene/series does not establish it.
4. `compact` that drops meaning or the end of the sentence; rows over ~130
   characters with no `compact` (write one).
5. Clearly unnatural or register-breaking English (a teen sounding like a
   memo, a noble sounding like a teen) — only when it is actually jarring.
6. `{tm}` markers must match the source's ＜ｔｍ＞ tags one for one.

Do **not** change proper-noun spellings to your preference; a script applies
the glossary after review. If a name is plainly the wrong character or thing,
fix the meaning and say so in `why`. Read the rows either side (and adjacent
slices) before deciding an addressee or referent.

## Output

Write `work/translation/en/story_review/cNN_SSS.json` for every slice you
review, even if nothing changed:

```json
{
  "slice": "c01_000",
  "rows_in_slice": 80,
  "rows_examined": 80,
  "changes": [
    {"id": "c01_04140", "was": "<exact current en>", "en": "<corrected>",
     "compact": "<optional corrected compact>", "why": "reversed addressee: ..."}
  ],
  "uncertain": ["c01_05xxx: tie broken toward ... because ..."]
}
```

`was` must equal the current `en` exactly (it guards against stale edits).
To change only `compact`, set `en` equal to `was`. ASCII only, no Japanese.

## Report

Per slice: rows in slice, rows examined, rows changed, and the 2–3 most
serious problems. List calls you were unsure of even when a row passed.
