# SRW Z Special Disc reuse assessment

Checked 2026-09-25. Recommendation: reuse the English project's translation
assets and format libraries, with a separate Special Disc profile and writers.
Do not apply an Original or Best patch directly to Special Disc.

**Implementation update:** the user subsequently requested work without story
dialogue. [Build 0.1.0](BUILD_0.1.0.md) implements three front-end menu atlases.
The original proposed story sequence below is historical and is not the active
plan. Binary/patch validation passed; runtime validation remains pending.

## 1. Workspace and source identity

The workspace initially contained `AGENTS.md`, `BASE_RULES.md`, and the supplied
CHD. It had no `.git`, tools, translations, or builds. No Git repository was
initialized during this assessment.

The CHD was extracted with the existing SRW Z `chdman.exe` into
`work/source/special-disc.bin` and its CUE. This is an unmodified MODE1/2048
source image, not a translated output. The CHD was not changed.

| Check | Measured result |
| --- | --- |
| Disc executable | `SLPS_259.20` |
| Disc version | `SYSTEM.CNF`: `VER = 1.01` |
| Image bytes | 3,791,781,888 |
| Image SHA-256 | `c3bd8c1af4e411e5ab2ae2d4be877170b6ab1ea9b51fa62bc0b91a51ba1a2952` |
| Upstream inventory match | All 65 members match path, LBA, size, and SHA-256 |
| Shared paths with Original | 57; 13 complete files have identical hashes |
| Shared paths with Best | 57; 14 complete files have identical hashes |
| STAGE | 68 chunks; all pass the local strict decoder |
| COMPDATA | 652,800 decoded bytes |
| Original font | 1,290,240 decoded bytes; exact match to upstream's main-game font hash |

The whole-file comparison uses the pinned upstream Original/Best inventories;
it is not a comparison of translated English images. Identical whole files
include movies, audio, and engine resources, so that count is not translation
coverage. Many useful shared assets live inside otherwise different archives.

Evidence: [source audit](../work/analysis/special-disc-audit.json),
[upstream inventory](../work/analysis/upstream-disc-inventory.json).

## 2. Which local SRW Z work to use

| Location | Finding and intended use |
| --- | --- |
| `E:/Projects/SRW Z/repo` | Early proof of concept: 59 top-level tools, obsolete renderer blocker and byte-budget assumptions. Useful history, not the current implementation baseline. |
| `E:/Projects/SRW-Z` | Current distributable source tree: codecs, ISO readers, source exports, verifiers, font/runtime work, and Best adapter. HEAD was `ebd036dfff5746c1e8918bfe322805f75d4bfb44`; there are substantial uncommitted changes. |
| `E:/Projects/SRW Z/_work` | Active local tools, analysis, native extraction, translation work, and release repair scripts. Some required inputs are only here. |
| `E:/Projects/SRW Z/CURRENT_BUILD.json` | Latest local release record is 0.9.85, dated September 22. It reports verified patch round trips and pending runtime confirmation. Use its exact Original output as a candidate donor, then verify its hash and relevant content before importing. |

The build record points at `E:/Projects/SRW Z/SRW Z English Original v0.9.85.iso`
with SHA-256 `8299318b990baa3f811f3e8375b8d12315b71af350a72e01c29088584faa5f73`.
That hash is from the existing manifest; this assessment did not re-hash the
English release ISO. The record also warns that the translation master contains
older control structures that were excluded from the cumulative release build.
Use the release's verified text together with native Special Disc structures.

Concrete reuse candidates:

- `banlz.py` and `banlz_strict.py`: verified here on the SP font, COMPDATA, and
  all STAGE chunks. Codec compatibility is established; SP writers still need
  separate tables and reference validation.
- `best_adapter/disc.py`: working ISO9660 reader and VMAP-aware reader for
  translated donor images. Reused by this audit.
- `best_adapter/subtitles.py`: useful indexed subtitle parsing and metadata
  preservation. The SP header differs; the audit adapts a read buffer only.
- `best_adapter/elfmap.py`: reusable instruction-matching approach. Its existing
  Original/Best address spans are not an SP address map.
- `analysis/glossary*.json`, `name_sweep.py`, and English name dictionaries:
  starting terminology, subject to the discrepancies below.
- Font rasterization, texture manipulation, measured-width logic, and English
  glyph assets: reusable methods/assets after SP renderer and slot adaptation.
- Pointer, control-code, strict-compression, changed-range, and final-image
  readback checks: reuse their checks, replacing Original/Best hardcoded addresses.

Do not directly execute older `extract_script.py`, `pool.py`, `rewrap_dialogue.py`,
`stage_store.py`, or runtime patchers on this disc. Examples of embedded main-game
constants include STAGE LBA `1651029`, COMPDATA base `0x6D6800`, and renderer hook
`0x20C9B0`. SP has different values. Several historic tools write in place.

## 3. English text reuse and source quality

The actual SP SRVC archive contains 352 blocks, 59,262 indexed records, and
25,526 distinct raw text strings. Under the English export's established
normalization, that becomes 25,522 unique lines:

| Measurement | Result |
| --- | ---: |
| Lines with an existing English hash key | 25,399 / 25,522 (99.52%) |
| Indexed records covered by those keys | 59,012 / 59,262 |
| Unmatched normalized lines | 123 |
| Records using unmatched lines | 250 |

This verifies a large pool of reuse candidates, not final English readiness.
The matcher removes Japanese quote wrappers and fullwidth padding around the
literal backslash-n marker, exactly as `srvc_work.inner` does. That normalization
merges four raw variants. Upstream Chinese reports use different binding and
normalization rules, so their 269 unmatched occurrences must not be substituted
for this audit's 250. Context, timing, special codes, and English rendering need
separate checks. Store strong full source hashes in the eventual SP binding
manifest; the legacy export uses truncated SHA-1 keys.

Source problems found without changing either SRW Z project:

- Both caption exports contain 25,810 keys and are byte-identical, but regenerating
  from the active local worklist and `srvc_en.json` changes **67 values**. Of
  those, **65 occur in SP**. The key set is unchanged. Regenerate and verify the
  English mapping against the pinned donor build before import.
- The local glossary has **1,094** terms; the canonical source has **1,078**.
  There are 16 local-only terms and two conflicting values: `Genganam` versus
  `Ghingnham`, and `Zieg` versus `Zeek`. These remain unresolved; this assessment
  did not choose names or merge glossaries.
- Provenance has only 1,004 entries, of which 562 are `legacy-unverified`.
  The glossary is useful groundwork, but it does not yet satisfy the requested
  character research and source requirements for every entry.
- `english_script.json` differs substantially: **89,128 rows** in the active
  local analysis folder versus **167,720** in the canonical tree. These counts
  are not coverage percentages. They show why a filename alone cannot establish
  the correct translation snapshot.
- The local technical notes document stale dialogue exports and erroneous
  same-offset pairing after relocation. Bind by verified native ownership,
  source text, speaker, and context; ambiguous matches should remain unresolved.

Evidence: [local inventory](../work/analysis/local-reuse-inventory.json) and
the caption section of [the source audit](../work/analysis/special-disc-audit.json).

## 4. What dyzz/srwz-zh teaches us about Special Disc

Inspected commit **`f6673b1edf697df3501fba3889e930815fd1b001`**. The tree has 92
files under `tools/special_disc/` and 24 SP-specific test files. References are
pinned in [upstream-sources.json](upstream-sources.json).

The project already has a separate SP export, migration, writeback, graphics,
and verification toolset. Its documentation describes 8,629 draft entries
written into a candidate image, plus later repairs. This is useful technical
evidence, not a claim of complete translation or full runtime acceptance.
The active output path is `build/iso/special-disc/sp-current.iso`; older docs
preserve historical preview paths.

The active build still depends on local main-game components, font proposals,
and hash-locked preview/text-canary deltas. `build_full_text.py` does not make
the repository a source-ISO-only reproducible SP pipeline. Our English project
should use the discovered format contracts and develop its own reproducible
input chain. The Chinese encoder, font allocation, and layout limits cannot be
substituted for the English renderer.

| Area | SP contract / required work |
| --- | --- |
| STAGE | 68 chunks; base `0x8045F0`; HB table at `0x5170..0x5284`; function table starts at executable offset `0x358980`. SP adds opcode `0x63`. Use its native event parser and protect non-text fields. |
| COMPDATA | Base `0x764F80`; decoded size 652,800. Weapon records grow from 36 to 40 bytes and pilot records from 176 to 178. Rebind names/text by native record identity. |
| SRVC | Block magic `0x4F01`, compared with main-game `0x4F00`. Preserve SP index metadata, trigger records, opaque tails, and alignment. |
| Font / VT1 | Font is chunk 3 instead of main-game chunk 2. SP executable table is at `0x353790`; native font slot is 599,344 bytes. SP inserts a large audio block before the font. |
| Executable strings | Offset-only transfer is unsafe. Upstream found seven supposed text locations were actually jump-table words; its `exe_data_guard.py` records them. |
| NISVDATA / Q&A | Counts and layouts differ; original main-game Q&A offsets and page records cannot be copied wholesale. |
| Graphics | Identify by archive/chunk/picture and verify pixels/palette before reuse. Shared title/menu art often moves, while SP menus and chapter labels need new English art. |
| Fixed-grid text | VT1 chunks 40 and 50 hold SP group introductions and challenge briefings. They need dedicated layout handling. |
| ISO layout | Upstream preserves member sizes/LBAs and repacks within archives. If English needs extra space, separately prove relocation, VMAP/directory updates, and runtime load limits. |

The source image, native font identity, chunk count, and decoded COMPDATA size
were independently confirmed here. Record strides, opcode semantics, patch
sites, and runtime address contracts above are upstream research to verify
again as each writer is implemented.

Upstream made its larger Chinese font fit by moving the preceding audio block
back 29,760 bytes and updating two VT1 table entries. This is a tested layout
strategy to study, not an amount to hardcode for English: measure our final
font first. The English ASCII/variable-width hooks need SP addresses and a
verified memory reservation, even though the original font pixels match.

For story text, relocate strings into verified owned space and update their
actual references. Do not squeeze initial translations into old byte slots.
Relocation still needs valid decoded-memory limits and compressed capacity;
blindly appending beyond the loaded overlay is not safe.

Primary references:

- [SP plan and format research](https://github.com/dyzz/srwz-zh/blob/f6673b1edf697df3501fba3889e930815fd1b001/docs/special-disc/PLAN.md)
- [SP tools and current workflow](https://github.com/dyzz/srwz-zh/blob/f6673b1edf697df3501fba3889e930815fd1b001/tools/special_disc/README.md)
- [Text binding and writeback design](https://github.com/dyzz/srwz-zh/blob/f6673b1edf697df3501fba3889e930815fd1b001/docs/special-disc/TEXT_WRITEBACK_PLAN.md)
- [Candidate coverage and verification limits](https://github.com/dyzz/srwz-zh/blob/f6673b1edf697df3501fba3889e930815fd1b001/docs/special-disc/FULL_TEXT_CANDIDATE.md)
- [Font installation](https://github.com/dyzz/srwz-zh/blob/f6673b1edf697df3501fba3889e930815fd1b001/tools/special_disc/writeback/install_font.py)
- [Executable data guard](https://github.com/dyzz/srwz-zh/blob/f6673b1edf697df3501fba3889e930815fd1b001/tools/special_disc/writeback/exe_data_guard.py)

## 5. Original proposed implementation order (superseded)

This proposal preceded the instruction to exclude story dialogue. Use the
non-story backlog in [the build notes](BUILD_0.1.0.md) for current work.

1. Freeze native SP and English donor identities. Reconcile the two glossary
   conflicts, preserve provenance, and refresh English exports against the
   selected release. Keep only glossary/UI source terms and target text in
   shareable files; derive Japanese story text locally when needed.
2. Add an SP profile with ISO members, runtime bases, archive tables, record
   strides, original bytes at patch sites, and source locks. Share format
   libraries with SRW Z; keep SP-specific patch locations separate.
3. Port the English font/ASCII/width runtime and one menu label. Check the
   final font size, memory reservation, and a fresh emulator boot.
4. Implement native event-owned relocation and a no-change round trip. Then
   translate the first story stage (`stg_001`, chunk 001) and first challenge
   (`stg_200`, chunk 039), including their visible intro/briefing surfaces.
5. Produce **0.1.0** under `work/output/` with a changelog, source/output hashes,
   readback evidence, and measured in-game screenshots under `work/ui/`.
6. Import shared captions, names, abilities, suspend messages, library material,
   and matched graphics. Preserve SP metadata and require explicit resolution
   when one source string has several English answers.
7. Expand to SP-only story, 18 challenge missions, narration, Battle Viewer,
   Special Theater, Q&A differences, and new menus. Verify each mode and saving,
   loading, suspend/resume, and main-game Data Link. Track new/old save behavior.

Do not automatically bring across upstream feature changes such as default
unlocks, chart visibility, reward changes, or skip behavior as part of a text
port. They require a separate project decision.

## 6. What was and was not tested during the initial assessment

Completed: CHD extraction, full source SHA-256, all member hashes/positions,
font identity, strict decoding of all 68 STAGE chunks and COMPDATA, indexed
caption parsing, English match counts, and source-export freshness comparison.

Not done: building or booting an English SP image, porting executable hooks,
relocation round trips, measuring screen capacity, or gameplay/save testing.
There is no playable build from this assessment and no runtime success claim.
