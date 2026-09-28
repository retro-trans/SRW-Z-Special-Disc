# English translation candidate 0.2.9

Adds five save/load summaries (IDs 2, 13, 17, 44, 53), bringing coverage to 65 of 66
records. All five preserve the complete native meaning after independent
review and fit three rows within 520 font units. ID 27 remains native; its full
English draft needs four rows. The other 60 approved recap objects are unchanged.
The native HSFC archive and save-record layout remain unchanged; English text
is stored in the existing relocated pool and selected by the guarded getter.

The follow-up input is `work/translation/en/save_summaries_release_0.2.9.json`.
It binds the immutable earlier reviewed file, full drafts, both earlier reviews,
follow-up proposals and independent review by SHA-256. Duplicate proposal IDs,
stale input hashes, incorrect correction preimages, edits to unapproved records
and false archive hashes are rejected. Independent fault checks confirm these
gates and exact preservation of 60 earlier recaps and deferred 27.

The name pass corrects PT/76/CHFN and PT/76/DSC2 to Takeshi Tsukikage,
supported by [Ashi Productions' cast](https://ashipro.jp/theatrical/w001a.html).
The source-scoped rule runs after editorial review; historical donor files
remain intact. All 1,000 battle-caption entries and their 2,312 occurrences are
unchanged from 0.2.8, with a new versioned release input binding the glossary.
Licensed [Good Smile wording](https://special.goodsmile.info/gravion/en/)
corroborates the existing Ergo spelling; no caption wording changes are needed.

All 296 suspend texts have full English drafts and independent native-source
meaning reviews across all 57 scenes and 379 occurrences. The reviewed output
is `work/translation/en/suspend_reviewed.json`. It is not installed in this
build; encoding, buffer ownership and display layout remain under investigation.
See [suspend format research](SUSPEND_RESEARCH.md).

Full component dry run and name regression checks pass. The pool remains
115,476 bytes, ending at 0x83B514 before heap 0x83B600. The reconstructed
save-summary preview is labelled as a static reconstruction, with non-atlas
punctuation disclosed separately. PCSX2 acceptance remains pending by user
choice. The non-story translation is still incomplete.

Verified artifacts:

- ISO: 3,791,781,888 bytes; SHA-256
  `0670690184da4fcf67ad080e6a4f56029ceb51ff58bc825683087a6e1a4e6a1f`.
- xdelta: 4,358,034 bytes; SHA-256
  `6d867dc9bb6a48b18ce1072a2f6fb16c0a5c3becc3d6c6ba62853b8e5469c380`.
  Reconstruction from the clean Special Disc BIN matches the ISO exactly.
- All 3,774,186,636 bytes outside 41 planned writes match the clean image.
  Disc directory and runtime mappings agree. Story chunks 1–67, original
  suspend text and native HSFC save data are unchanged.
- A separate finished-ISO check confirms all 57 suspend command sequences,
  379 text operands, the scene table and the unrelated numeric collision
  remain native. See `build-0.2.9-suspend-preservation.json`.
- The receipt matches all 63 tools, 77 translation files and eight glossary
  files captured at build time. The 0.2.8 artifacts remain available.

Outputs: `work/output/SRW Z Special Disc English v0.2.9.*`.

Independent finished-ISO readback passes: 4,995 Library fields and 34,956
description lines, 729 relocated targets, 313 reference names, 395 chart fields,
65 recaps, ten narration records and all 2,312 translated battle-caption
occurrences. All 56,950 unreviewed indexed caption occurrences and voice
metadata retain native data. The English segment remains below the heap.
Report: `work/analysis/build-0.2.9-independent-audit.json`.

Reviewed input SHA-256 values:

- Save recap release: `d134fbbba9bd5c250b358dd4956090ff5c39ff982e0571460b68af6c113eb6af`.
- Battle release: `831194a6332b56994cb129fb23044ccc1b4b1bcf15eabadce47df50288f45c2f`.
- Suspend meanings, not installed: `05edb8c96ec18f9e37317b0220f0eee2d81ca58916ae1ded3dcfbf8507e43818`.
