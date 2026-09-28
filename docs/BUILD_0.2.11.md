# English translation candidate 0.2.11

Adds 229 independently authored and reviewed battle captions at 1,114 native
occurrences. The release covers 1,232 text identities at 3,429 occurrences.
There are still 24,290 indexed identities / 55,833 occurrences in Japanese.
This is progress toward the full non-story translation, not a completion claim.

Three consecutive 80-identity ranges (0-239) were checked against all 1,168
native occurrences and their complete sequences. Eleven previously released
identities were retained in the author files. A separate reviewed amendment
changes caption 169 from "ZAFT scum" to "ZAFT weaklings", restoring the original
taunt about weak enemies. Other meaning fixes in the new translations include
support handoff direction, bailout wording, a prized-asset idiom and a stolen
machine previously described as a person. Unknown targets stay unnamed.

The candidate consolidator binds native sources, the earlier release, both
author and independent reviewer files, and the terminology glossary. Meaning
review precedes source-scoped spelling and wrapping. New King Gainer and Big O
terms are documented with references in `battle-candidate-terms.json`.
Every new caption retains its full wording within the two-row layout.

The name pass retains the existing menu/Library spellings **Mach Band Shaker**
and **Domepolis**. One existing chart synopsis also changes "Dome Polis Katez"
to "Domepolis Katez" in `main-synopsis/31` and rewraps the same prose. All ten
lines fit (maximum 556/560 font units). Its English pool size and
addresses remain unchanged; the executable difference is confined to that
stored text. No new battle-display hook is needed: the longest converted
caption remains 91 bytes including its terminator, within the native 96 bytes.

Static caption previews were inspected. Independent code review rejected 13
in-memory fault cases covering stale sources/reviews, omitted identities,
unauthorized baseline changes and malformed caption-169 amendments.

All pre-title demo fixes from v0.2.10 remain included, including the pictured
Mazinger Z title, Koji name and Great Wheel Rocket Punch shout. Story dialogue
and separate suspend drafts are not installed by this release.

Emulator acceptance remains pending by user choice. Static previews and binary
readback checks do not establish playback or timing acceptance.

Outputs: `work/output/SRW Z Special Disc English v0.2.11.*`.
Final validation passed:

- ISO: 3,791,781,888 bytes, SHA-256
  `a301f6bd3e9337cc109243fe50b9fc1ffc91a726b237840b421b8a6644a9e5ea`.
- xdelta: 4,477,387 bytes, SHA-256
  `33162252ef916053975a56b21653c75a797797a7bd16591ca260e79e8d136db6`.
  Reconstruction from the clean Special Disc BIN matches the ISO exactly.
- All 3,773,371,756 bytes outside 42 planned writes match the clean image.
  Story chunks 1-67, suspend text, save data and voice metadata are unchanged.
- Independent finished-disc readback passes for all 3,429 translated caption
  occurrences, 20 demo titles and 61 demo names, plus the existing Library,
  reference, chart, save-summary and narration coverage.
- All 74 Python tools, 90 top-level translation files and 13 glossary files
  recorded in the receipt match their build-time hashes.
- Compared with v0.2.10, only the SRVC caption members and executable payload
  differ. The executable's 446 changed bytes lie entirely in the one reflowed
  chart text at file offsets 0x3d7510-0x3d76d5. Code and pointers are unchanged.

Reports: `work/analysis/build-0.2.11-independent-audit.json` and
`work/analysis/build-0.2.11-input-verification.json`.
