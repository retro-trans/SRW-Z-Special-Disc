# Battle-caption batch 480-719

This is unreleased work after v0.2.12. Follow AGENTS.md, BASE_RULES.md and
BATTLE_CANDIDATE_BRIEF.md, with these explicit batch overrides.

- Baseline: `work/translation/en/battle_release_0.2.12.json`, SHA-256
  `e20ad0dd4d0a3f5b3f167b10336f3bbe2927ddc782150732edc7aef7c7a8efde`.
- Slices: 480-559, 560-639 and 640-719, each exactly 80 native identity IDs.
- Supplement: `work/glossary/battle-candidate-00480-00719-terms.json`.
- Preserve all approved baseline text exactly in author files. Report any
  source-proven defect as a separately bound amendment proposal.
- Baseline includes two null deferrals, 323 and 444. Preserve them and their
  distinct meaning/runtime dispositions. Do not count them as English or
  require every baseline entry to have a translation.
- Read every assigned native occurrence and complete containing sequence,
  boundary IDs and neighboring sequences needed to resolve referents.
  Report actual identities, records and sequences read; do not use enumeration
  counts as evidence of reading.
- Keep native Japanese in memory. Author and review artifacts contain English,
  identity hashes and coordinates rather than extensive native scripts.
- Draft full meaning before layout. Independent meaning review precedes the
  source-scoped name pass and font/relocation checks.

Use author names `battle_candidate_00480_00559.json`,
`battle_candidate_00560_00639.json`, `battle_candidate_00640_00719.json` and
matching `battle_candidate_review_*` files. Independent reviewers bind the
completed author hash and all source/baseline hashes; authors remain immutable
after review begins. Capture every uncertainty, including a retained line
that appears inconsistent with the native source. Do not silently fix style.

Captain for late-DESTINY Mu is restricted to native Mu + one-colonel-equivalent
rank, or rank-only continuation with verified sequence context. It is not a
global rank mapping. METEOR is equipment: a request to deploy it is not firing
it. Overfreeze is the researched one-word spelling; a future script must also
check the older Library/menu fields, without modifying historical artifacts.
Caption 600 remains deferred until Gain's birth-name spelling is substantiated.

The v0.2.12 receipt and final audits were completed before these new draft
files were written. No new draft is installed in that ISO. Story dialogue is
excluded from this active build and emulator acceptance remains pending by
user choice.

## Completed review checkpoint

All three independent reviews are saved. They found no further meaning
corrections to the new full drafts. Twenty-four baseline entries stay exact.
Caption 600 remains null. The separate 604 compact supplement preserves all
facts at widths 438/397. Its notes supersede the main review's overly narrow
Latin-only tilde finding: ASCII 7E maps to native CP932 8160; no 576 text
change is required.

| Slice | Assigned occurrences | Reviewer identities read | Reviewer records read | Complete sequences read |
| --- | ---: | ---: | ---: | ---: |
| 480-559 | 88 | 129 | 142 | 130 |
| 560-639 | 296 | 544 | 1,129 | 913 |
| 640-719 | 112 | 145 | 190 | 155 |

These are actual reported reading counts, including boundaries and neighbors;
the ranges overlap in context and should not be summed as a unique total.
Some legacy `rows_examined` fields count identities and others physical
records; use the explicit context counts above for comparisons.

`tools/review_battle_batch_00480_00719.py` consolidates the source-bound
reviews and compact supplement onto the immutable baseline without changing
that baseline. Its default is a dry run; `--write` saves only
`work/translation/en/battle_candidates_00480_00719_reviewed.json`.
The saved result has 215 new English identities / 427 occurrences and only
600 deferred. SHA-256:
`4b0b1a3be867f0a42b272b27c2e131c89b9b750e94d0ce0c4eec702c31868ed3`.

Fresh consolidation equals the saved result. All 215 laid-out captions pass
encoding roundtrip; the largest converted string is 89 bytes including NUL,
inside the existing 96-byte buffer. Seven focused spelling checks protect
unrelated text and inflected forms. These are candidate checks, not an ISO
build or emulator acceptance.

Independent validator review found and fixed a truthiness gap: compact
approval now requires the boolean `true`, rejecting the string `"false"`.
Fifteen distinct malformed/stale scenarios are verified rejected across 19
test executions, including the recheck after that fix. The actual result
still equals the saved candidate exactly. Evidence is recorded in
`work/analysis/battle-candidate-00480-00719-preflight.json`.

Released in v0.2.13: native-bound spelling follows independent Library meaning
review, and all candidates merge while retaining baseline deferrals 323/444.
The separately versioned ISO passes final-disc readback and exact patch
reconstruction. Installed coverage is 1,678 identities / 4,323 occurrences.
The next consecutive author range begins at 720; its drafts are not included
in v0.2.13. See `BUILD_0.2.13.md` for the release and remaining work.
