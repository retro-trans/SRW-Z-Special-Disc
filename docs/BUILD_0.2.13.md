# English translation candidate 0.2.13

Adds 215 independently authored and reviewed battle captions at 427 native
occurrences. Installed coverage is 1,678 identities / 4,323 occurrences.
23,844 indexed identities / 54,939 occurrences remain native. The full
non-story translation goal remains incomplete.

Three complete 80-ID slices cover 480-719 and all 496 occurrences. Twenty-four
existing translations are retained exactly. Caption 600 remains native while
Gain's birth-name spelling is unresolved. Earlier deferred captions 323 and
444 also remain native; the latter is a hidden production placeholder, not
translated content. Both native suppression branches are rechecked.

Meaning review precedes terminology and layout. Caption 604 uses a separately
reviewed compact rendering preserving Article 9, the Citizens' Charter and
the Exodus Law alias. The new captions require at most 89 bytes including the
terminator; the complete release maximum remains 91 in the existing 96-byte
buffers. Static previews using the actual Latin atlas were inspected. The
tilde preview uses a substitute glyph; the game maps it to native CP932 8160.

The release preserves every v0.2.12 caption. The merge pins the previous release,
reviewed candidates and all author/reviewer/source bindings. Fresh candidates
must match the saved review exactly apart from the current spelling-file hash.
The 15 previously checked malformed-input cases remain documented in
`BATTLE_CANDIDATE_BATCH_00480_00719.md`.

A separate native-source Library review corrects three meanings: Martina cuts
off Jinba's arms, and the two Jinba descriptions target the people of Yapan's
Ceiling. Six reviewed affected-state forms become Overfrozen. Source-bound
spelling rules standardize Overfreeze, METEOR equipment and Hughes Gauli.
All 4,995 Library fields were compared against frozen v0.2.12 inputs: exactly
16 fields change, preserving all other words. Two menu fields adopt Overfreeze;
the song titled Meteor remains unchanged. Narration text and layout are exact
matches to v0.2.12; only the spelling dependency hash is refreshed.

The pre-title demo retains all 20 series titles, 61 speaker names and Koji's
pictured Great Wheel Rocket Punch shout. Its reviewed manifest remains frozen
and its compiled archive matches v0.2.12. Story chunks 1-67, suspend messages
and the native save archive are protected by the build checks.

Outputs use `work/output/SRW Z Special Disc English v0.2.13.*`.
Exact patch reconstruction and independent final-disc readback pass. The audit
reads all 1,678 translated caption identities at 4,323 occurrences, 4,995 Library
fields with 34,957 lines, 729 relocated texts, 313 reference names, 395 chart
fields, 65 recaps, ten narrations and all 61 demo names / 20 demo titles.
All 3,773,353,324 bytes outside the 42 planned writes remain native.
The demo and narration archives are byte-identical to v0.2.12. The English pool
remains 115,476 bytes and ends below the unchanged heap boundary.

ISO: 3,791,781,888 bytes, SHA-256
`ba99a71895bdcf57ef396b8bf70c16c6d09b800fae94225ea2ae43a29a71a9c4`.

Patch: 4,486,385 bytes, SHA-256
`dc73751f6a3f632500cb3c16013be15a34a0ac36d1b15059af4ab08a3fe7e0fc`.

The frozen caption release SHA-256 is
`3af2752da15dca8e77e41e32da02323d14c09ab205b379f0a81f092836bfea8a`.
Detailed evidence is in `work/analysis/build-0.2.13-independent-audit.json`
and the build receipt.

All receipt-listed inputs match: 82 Python tools, 109 translation files and
15 glossary files. The verified `v0.2.13.inputs.zip` preserves those 206 inputs,
the receipt, both audits and a dependency note (210 entries). Every member was
read back exactly. It is 10,036,282 bytes, SHA-256
`1c7cc6e6a003343ba33a7eb0b7671df7e47ac2d83ccaa1e32f987f69751f18d7`.
This snapshot excludes the clean game image, donor assets, fonts and runtime;
it is not a standalone build kit. Later drafts remain separate from this release.

Emulator testing remains pending by user choice; static checks do not establish
playback, timing or in-game visual acceptance.
