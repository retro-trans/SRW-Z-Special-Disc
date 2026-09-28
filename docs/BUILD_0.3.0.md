# English test candidate 0.3.0 — story dialogue

First build with English story text. Base: `SRW Z Special Disc English v0.2.24.iso` (all its non-story
translations retained byte for byte). Built by `tools/build_story.py`; see
[STORY_BUILD.md](STORY_BUILD.md) for the method and memory rules.

## Coverage

- All 45 story STAGE chunks installed: 7,511 dialogue rows (7,509 plus the
  two silent `$n` rows), 71 scene captions, the chunk-66 demo/Kanada tribute
  scene with its keyword entries and both choice lists.
- Every row was translated, independently meaning-reviewed, passed through
  the glossary/rank name pass (SRW Z rank rulings), wrapped to at most three
  lines of 480 font units and packed inside its chunk's native text region.
- 796 rows use a shorter `fit` (needed for the 3-line box or the chunk byte
  budget); every fit was independently checked against the Japanese
  (86 corrections plus one added fit). Fits get the same name rules.
- Kept native on purpose: 334 label strings (room/background/group names that
  may be lookup keys) and the `???` condition identity. Mission conditions
  remain the English-pool versions from the base build (126 native condition
  strings are now unreferenced and reused as text space).

## Layout

Speaker line, then 「 body 」 (（ ）for thoughts), no continuation indent,
main-game format. Captions keep the native first line and are centred on the
native caption centre. Runtime value tags are restored verbatim.

## Verification (static)

- Each chunk: decoded length unchanged; every byte outside the text region and
  the repointed pointer words equals the base chunk; every pointer reads back
  its text. Chunk budgets: minimum spare 1 byte, total spare 10,292 bytes.
- STAGE.BIN rebuilt: 548,272 bytes (was 527,552), relocated to
  empty reserved space at LBA 1,793,717; ISO directory and VMAP
  entry updated. HB.BIN chunk table rewritten (no executable copy exists).
  All 68 chunks decode; untouched chunks keep their exact base bytes.
- Every ISO byte outside the planned writes equals the base ISO. STAGE and HB
  read back identically through the ISO directory and the runtime VMAP.
- ISO SHA-256 `ca444e5c078a6f3cb23a96c5b6d676de1df068cfa4219ecbc06e71cbea4186ec`.
- xdelta vs the clean Special Disc BIN: 4,644,212 bytes, SHA-256
  `2f419c79154ebe24d26b59f640cb0d5fd319f859647860091535e059d4f919ac`; exact reconstruction verified.

## Not yet verified in game

The dialogue renderer's handling of ASCII in story boxes, the 480-unit line
width in both box types, caption centring and STAGE relocation have only
static evidence. Please check: a scene box, a map (over-unit) box, a scene
caption, a long 3-line row, a thought row, and the chunk-66 demo if reachable.
