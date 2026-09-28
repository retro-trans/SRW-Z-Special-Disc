# Remaining story text brief

Covers story strings outside the 7,509 dialogue rows: scene captions,
mission conditions, labels, the chunk-66 demo scene and choice lists.
Read `BASE_RULES.md` and `docs/STORY_TRANSLATION_BRIEF.md` first; their
translation rules apply. Do not spawn sub-agents; do the work yourself.

## Input

`work/cache/story/extra_<SET>.json` — `{set, rows:[{id, kind, chunks, first_offset, jp}]}`.
Each row is one unique native text (it may appear in several places).
Glossary: `work/cache/story/glossary.tsv`; spelling rules already settled
are in `work/glossary/story-name-rules.json` (use their English).

## Output

`work/translation/en/story_extra/<SET>.json`:

```json
{"set": "A", "rows_in_set": 76, "rows_examined": 76,
 "rows": [{"id": "x_...", "en": "...", "note": "optional"}],
 "unresolved": [{"id": "...", "why": "..."}],
 "new_terms": [], "uncertain_calls": []}
```

ASCII only, no Japanese, placeholders (`$n` …) exactly as in the source.
Use `\n` in `en` only where the kind below says so.

## Per kind

- **caption** — `jp` is padding + `～Place～` (a scene location card).
  Write only the place, e.g. `Newark Base - Command Room`, no tildes, no
  padding (the build centers it). Ship/base/room names from the glossary.
- **condition** — victory/defeat/mission-rule text shown in the mission
  info window. Keep every condition, number and exception. Plain concise
  imperative/statement style, e.g. `Defeat all enemies.`,
  `An allied battleship is shot down.`, `Turn 6 begins.` Keep the source's
  line breaks as `\n` only where they separate separate rules/sentences.
  Numbers in ASCII with thousands separators (350,000).
- **label** — a short name: character, unit, place, room, group or bracket
  (`準々決勝第１組` = `Quarterfinal Group 1`). Glossary spelling. Room
  labels like `アーガマ　食堂` → `Argama - Mess Hall`. `黒ベタ` (black
  screen) and `真っ暗` are editor names for a black background: translate
  literally (`Black Screen`, `Pitch Dark`) and note it.
- **dialogue** — body only, as in the main brief.
- **inline** — `Speaker「…」` on one line (chunk 66 demo scene, a
  developer/tribute scene). Write `en` as the body only, like dialogue, and
  put the speaker's English name in `"speaker"`. Keep `\n` breaks out; the
  build wraps. `《term》` is an in-game keyword link: write it `{{English}}`,
  and the English must be exactly your translation of the matching label
  row in this set (`オルファン` → `Orphan`, `バルマー戦役` → `Balmar War`,
  `金田伊功` → `Yoshinori Kanada`).
- **choice** — first line is the chooser's prompt (`「アムロ選択」`), the
  rest are options. Write `en` as `Amuro's Choice\nOption 1\nOption 2`
  (no quotes).
- Long `condition` rows in chunk 66 are keyword-link descriptions (Balmar
  War, Orphan) or a quoted magazine passage about animator Yoshinori
  Kanada: translate fully and faithfully; keep the magazine attribution.

## Report

Rows in set, examined, translated, unresolved, and the calls you were
unsure of.
