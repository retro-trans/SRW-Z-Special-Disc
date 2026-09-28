# English translation candidate 0.2.12

Adds 231 independently authored and reviewed battle captions at 467 native
occurrences. The release installs 1,463 identities at 3,896 occurrences.
24,059 indexed identities / 55,366 occurrences remain native, including 382
copies of a hidden production placeholder. This is progress toward the full
non-story translation; the goal is not complete.

Three complete 80-identity slices cover IDs 240-479 and all 865 occurrences.
Independent reviewers read their full containing sequences and neighboring
context: 285 native records for 240-319, 162 for 320-399, and 1,333 for
400-479. Counts overlap between slices and are not a unique combined total.
Seven earlier translations are retained exactly in the new author files.
Caption 323 stays native because a coined term remains unresolved. Caption
444 stays native because executable branches suppress its text in both known
fill paths. It is not counted as English; previous-caption clearing and timing
remain untested. The build and final audit recheck those instructions.

The v0.2.11 caption baseline is pinned by SHA-256. New author/reviewer hashes,
source hashes, all IDs, occurrence bindings, and unhandled baseline proposals
are validated before merging. Four earlier captions receive only the explicit
source-bound Asakim Dowen correction. A separate independent supplement changes
caption 270 punctuation to supported glyphs without changing its meaning.

The same name pass corrects four Library fields, three menu fields, nine
system labels and narration record 5. Seven Library fields use the settled
Domepolis spelling. All other words are preserved and layouts are recomputed.
Unversioned system metadata also refreshes two stale Z Gundam labels to Zeta
Gundam, already present in v0.2.11; these are not new in-game changes.
See `work/analysis/build-0.2.12-name-pass.json`.

The pre-title demo's 20 series titles, 61 speaker names and pictured Great
Wheel Rocket Punch shout remain included. Its original reviewed manifest and
review remain immutable. Unrelated Library edits may change that dependency's
whole-file hash only when every freshly derived demo field still equals the
reviewed content. Current and reviewed dependency hashes are recorded.

Static caption previews use the actual Latin atlas. They were inspected for
clipping and row fit. Five source-scoped spelling regression tests pass;
independent fault checks reject stale authors, corrections, source hashes,
missing IDs, retained-text edits and unhandled baseline amendments.

Story dialogue and suspend messages are unchanged. Emulator acceptance remains
pending by user choice. Static layout and binary checks do not establish
playback, timing or in-game visual acceptance.

Outputs: `work/output/SRW Z Special Disc English v0.2.12.*`.
The finished ISO and 4,482,107-byte xdelta pass exact patch reconstruction.
Independent ISO readback passes for all installed captions, 4,995 Library
fields, 729 relocated texts, 313 reference names, 395 chart fields, 65 recaps,
ten narration entries and all 61 names / 20 titles in the pre-title demo.
All 3,773,363,564 bytes outside the planned writes remain native. Every recorded
input hash matches: 76 tool files, 99 translation files and 14 glossary files.
The demo archive is byte-identical to v0.2.11. Eight other payloads changed.

ISO SHA-256:
`bd1e907eb766f005181f192cb1ae8a2507c49ee639ade42dd7b572fbaf359556`

Patch SHA-256:
`ba518126ed96d73b3759573794e414b636f75cdb8381df3b8525c549c60783cb`

Results are saved in `work/analysis/build-0.2.12-independent-audit.json` and
`work/analysis/build-0.2.12-input-verification.json`, alongside the output
receipt. These checks do not replace the pending emulator acceptance.

`work/output/SRW Z Special Disc English v0.2.12.inputs.zip` preserves all
189 receipt-listed Python, translation and glossary files, the receipt and
both final audits. Every ZIP member was read back exactly. The archive is
9,536,238 bytes, SHA-256
`5b437aee8ba9cc72b5e82d4518c1b952f77152d8623695b0af5ac6d572230c73`.
It is an input snapshot, not a standalone build kit; the clean game image,
donor assets, font and dependency runtime remain external.
