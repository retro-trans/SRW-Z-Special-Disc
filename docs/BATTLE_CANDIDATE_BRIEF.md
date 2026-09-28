# Remaining battle-caption translation

Scope: all indexed battle captions remaining outside the v0.2.10 reviewed
release. Story dialogue is excluded. Process consecutive native identity ranges
of 80 rows, including any already approved rows inside a range. Existing
reviewed lines are retained unless a source-proven meaning defect is separately
reported; they do not count as new translations.

Read AGENTS.md and BASE_RULES.md. Read native Japanese directly in memory with
`battle_format.unique_sources()` and `battle_format.native()`. Do not save a
Japanese script. `work/translation/en/battle_reuse.json` supplies English
candidates and native occurrence bindings; candidates are reference material,
not approved answers. Read the entire allocated range, its boundaries, every
native occurrence and the full sequence containing each occurrence. Inspect
neighboring sequences when a subject, target or continuation is unclear.

Each author writes `work/translation/en/battle_candidate_NNNNN_NNNNN.json`:

```json
{
  "schema_version": 1,
  "source_bin_sha256": "...",
  "source_seg_sha256": "...",
  "source_manifest_sha256": "SHA256 of battle_reuse.json",
  "base_release_sha256": "SHA256 of battle_release_0.2.10.json",
  "reviewed_ids": [0, 1],
  "rows_in_slice": 80,
  "rows_examined": 82,
  "occurrences_examined": 0,
  "context": {"method": "Describe full-sequence and boundary reading", "unclear_ids": []},
  "entries": [
    {"id": 0, "source_sha256": "...", "text": "...", "retained_from_base": false}
  ],
  "uncertainties": [],
  "glossary_followups": []
}
```

Use all80 integer native IDs, in order, rather than the shortened example.
Report actual examined counts; do not equate script enumeration with reading.
Use literal `\\n` for existing native row breaks; preserve their count while
drafting. Draft full meaning before layout. Keep uncertainty rather than guessing
a speaker, gender, addressee or omitted subject. Report unresolved rows with
`text: null` and an explanatory uncertainty; the compiler will retain native text.
For retained rows, use the exact `text` value in the base release.

Use the settled glossaries in `work/glossary/`: `english.json`,
`srw-z-terms.json`, `battle-terms.json`, `battle-next-terms.json`,
`battle-spelling.json`, `suspend-terms.json`, `attract-demo-terms.json` and
`battle-candidate-terms.json`.
Do not reopen settled spellings. Ask root to research missing identities or
terms. Do not add a gender or biography without evidence. Meaning comes first;
root runs the source-scoped spelling pass afterward.

Do not change **Asakim Dowen**, **Raster Edge**, **Mach Band Shaker / Mach
Band**, or **Domepolis** after the script's source-bound name pass. Their
research is in `battle-candidate-terms.json` and
`battle-candidate-next-terms.json`. Historical author/reviewer files retain
their original spellings as evidence; the current release applies corrections
after meaning review.

An independent agent reviews each completed author file against native source,
with the same complete range and occurrence/sequence obligations. Write
`battle_candidate_review_NNNNN_NNNNN.json` with the four source hashes above,
`author_file_sha256`, exact `reviewed_ids`, examined counts, `corrections`,
`unresolved_ids`, and `uncertainties`. Each correction contains `id`,
`source_sha256`, exact `before`, corrected `text`, and a reason grounded in
meaning. An empty corrections list must follow actual review. Do not silently
rewrite the author's file. Fix incorrect meaning, not merely different style.

Scripts must be dry-run and their sample changes inspected before writes.
These files are meaning work; layout, relocation, final-disc verification and
emulator acceptance remain separate gates. No candidate file alone approves
an ISO change.
