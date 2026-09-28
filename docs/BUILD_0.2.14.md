# English translation candidate 0.2.14

Adds 239 independently authored and reviewed battle captions at 547 native
occurrences. Installed coverage is 1,917 identities / 4,870 occurrences;
23,605 indexed identities / 54,392 occurrences remain native. The full
non-story translation goal remains incomplete.

Three complete 80-ID slices cover 720-959 and 550 assigned occurrences.
Caption 807 is retained exactly; all 1,681 v0.2.13 release entries remain exact,
including deferred 323, 444 and 600. Meaning review precedes spelling and layout.
Three compact versions, 754/768/948, have separate independent meaning approval;
no new caption is deferred. The new captions require at most 80 bytes including
NUL; the complete release maximum remains 91 in the existing 96-byte buffers.
Static previews using the actual Latin atlas have been inspected.

Source, author, review and compact-approval hashes are pinned. All 56 independent
preflight cases pass after fixing the review-file integrity and malformed-layout
guards. The independent release preflight also verifies all earlier entries,
all source occurrences and exact provenance of the three compact changes.
See `BATTLE_CANDIDATE_BATCH_00720_00959.md` and both preflight reports.
The release SHA-256 is
`6c0ac25deb878cdd3340c47e65170929450d85eba4d61c052de70c2f25c708ad`.

Only the SRVC caption and segment payloads change from v0.2.13; the executable,
Library, menus, narration and pre-title demo payload hashes are unchanged.
All 20 demo titles, 61 demo names and the pictured Rocket Punch shout remain
included. Story chunks 1-67, suspend messages and the native save archive remain
protected. All 3,773,343,084 bytes outside the 42 planned writes remain native.
The English pool remains 115,476 bytes at 0x81F200; its end, 0x83B514, stays below
the unchanged heap boundary, 0x83B600.

Exact patch reconstruction and independent final-disc readback pass. The audit
reads all 1,917 captions at 4,870 occurrences, 4,995 Library fields with 34,957
lines, 729 relocated texts, 313 reference names, 395 chart fields, 65 recaps,
ten narrations and all demo names/titles. Voice metadata and original caption
bank bytes are preserved except for the selected text-offset words.

Outputs use `work/output/SRW Z Special Disc English v0.2.14.*`.
ISO: 3,791,781,888 bytes, SHA-256
`52c6c5de1cb46357490a4651fb36a3d7561fe17b59ec3747952e376a48da3ac2`.
Patch: 4,491,757 bytes, SHA-256
`f87ab6ca472354939fbf5f85bb5d447d8a8f2469678b292cfb25eb4471359203`.

All 219 receipt-listed inputs match: 84 tools, 119 translation files and
16 glossaries. The input snapshot preserves these inputs, the receipt, both
final audits and a dependency note in 223 entries; every member reads back
exactly. Snapshot: 10,599,960 bytes, SHA-256
`8af858799275d27f4b85626be0e9352a511ba242647d9f787b97cf4a46e8f1fa`.
It excludes the clean game image, donor assets, fonts and runtime dependencies,
so it is not a standalone build kit. Subsequent drafts remain separate.

Emulator testing remains pending by user choice; static checks do not establish
playback, timing or in-game visual acceptance.
