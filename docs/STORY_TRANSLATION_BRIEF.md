# Story dialogue translation brief (Special Disc)

Read this whole file before translating. Also read `BASE_RULES.md` at the
project root; its dialogue rules apply and win over anything here.

Do not spawn sub-agents or forks; do the work yourself.

## Inputs

- Your slices: `work/cache/story/slices/cNN_SSS.json` — `{name, chunk, rows:[{id, jp}]}`.
  `jp` is the native row: line 1 is the **speaker**, lines 2–4 the body,
  wrapped in 「…」 (speech) or （…） (thought). Rows are in script order.
  A chunk is one scenario; the next/previous slice of the same chunk is
  `cNN_SSS±1`. Read neighbours whenever a referent or addressee is unclear.
- Glossary: `work/cache/story/glossary.tsv` (source, English, notes). Search
  it (Grep) for every proper noun, unit, weapon, organization and place.
  Glossary spelling is mandatory. If a name is missing, transliterate it
  sensibly, list it under `new_terms` in your output, and flag it.
- Scene/location captions and other strings are not your job.

## Output

For each slice write `work/translation/en/story/cNN_SSS.json` (UTF-8):

```json
{
  "slice": "c01_000",
  "rows_in_slice": 80,
  "rows_examined": 80,
  "rows": [
    {"id": "c01_04110", "en": "All units have finished launching."},
    {"id": "c01_04140", "en": "...", "note": "optional: uncertainty"}
  ],
  "unresolved": [{"id": "...", "why": "..."}],
  "new_terms": [{"source_romaji": "...", "english": "...", "why": "..."}],
  "uncertain_calls": ["c01_05xxx: addressee inferred from reply two rows later"]
}
```

- `en` is the **body only**: no speaker name, no 「」/（）/quotes, no manual
  line breaks. The build adds the speech/thought wrapper from the source and
  wraps the text to the box. Do not include Japanese in the output file.
- One entry per row, same order, every id. A row you truly cannot verify goes
  in `unresolved` (and is omitted from `rows`) — do not guess.
- Keep placeholders exactly: `$n` (pilot short name), `$f`, `$F` (full name),
  `$l`, `$c` (player's squad name). They expand at runtime.
- Runtime value tags such as `＜ｔｍ＞撃墜数＜／ｔｍ＞` (fullwidth, with a Japanese
  key inside) are replaced by a number in game. Write `{tm}` in their place,
  once per tag; the build restores the native tag verbatim. Never translate
  or drop the key. Allow ~6 characters for the value.
- ASCII only: `...` for …, `--` for ―/—, straight quotes `'` `"`. `~` is
  allowed for a drawn-out tone. No `…`, curly quotes, or accented letters.
- Fullwidth Latin in the source (e.g. ｔｈｅ　ＥＮＤ) is a proper name: use the
  glossary spelling (`the END`).

## How to translate

- Natural spoken English that keeps each character's register: soldiers
  sound like soldiers, kids like kids, nobles like nobles. American spelling.
- Full meaning, nothing added, nothing dropped: keep も (too), だけ (only),
  まだ (still/not yet), conditionals, names and ranks used as address.
- Write the line in full. Do **not** shorten because you fear it won't fit;
  the box is about 3 lines × ~42 characters (≈120 characters). If your full
  line is clearly longer than ~130 characters, still write it in full and add
  `"compact": "..."` with a shorter version that keeps the whole meaning
  (compress/abbreviate — never drop the end of the sentence).
- Japanese omits subjects. When the scene does not settle who, keep the
  ambiguity (imperative, passive, "someone") rather than inventing I/we/he.
- Never infer gender from a name. Use he/she only when the character is
  established (glossary note, the series, or the dialogue itself); otherwise
  use they/them or the name. Record the call in `uncertain_calls`.
- Read rows either side before deciding who a line addresses; the reply two
  rows later usually settles it.
- Honorifics: drop -san/-kun/-sama unless meaningful; translate ranks
  (大佐 Colonel, 艦長 Captain, 隊長 Commander/Captain by context, 少佐 Major).
  Keep established nicknames from the source series.
- Series catchphrases and attack names: use the glossary; if absent, use the
  series' established English (official dub/subs) and list it in `new_terms`.
- Existing translations you know are references for how a shape was solved;
  translate your own line.

## Report

When finished reply with one short block per slice: rows in slice, rows
examined, rows translated, unresolved count, and the calls you were unsure of
(tie-breaks, inferred referents, gender calls, missing glossary terms). An
honest uncertainty is worth more than a clean report.
