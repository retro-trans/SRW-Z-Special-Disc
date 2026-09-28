# Special Disc battle captions

Version 0.2.10 adds three independently reviewed Great Wheel Rocket Punch
shouts, including the source 22375 caption in the user's pre-title screenshot.
Coverage is now 1,003 identities at 2,315 occurrences; the previous 1,000 entries
are unchanged. The demo has separate speaker names and title textures; see
[pre-title demo research](ATTRACT_DEMO_RESEARCH.md). The format and 0.2.8
baseline described below remain applicable.

Version 0.2.8 contains 1,000 independently reviewed captions at 2,312 indexed
occurrences: all 123 captions without a safe main-game candidate and
all 877 active/donor disagreements. The remaining 24,522-identity candidate
inventory is not approved build input. Story dialogue remains excluded;
emulator acceptance is pending by user choice.

## Sources and reuse

Clean `BTL/SRVC.BIN` SHA-256:
`acf7b4b00fbd104b3320ae44f2e7548f4d31ad1f434231df35e39920928cd7e1`.
SEG SHA-256:
`46d9f8bd07c95f0b029801854857e0ab7650e74ab492da25605cbdbed4e6ac71`.
There are 352 blocks, 59,262 indexed records and 25,522 normalized identities.
Native text is read in memory; manifests contain English, hashes and record
coordinates rather than an exported Japanese script.

The format agrees with the pinned Chinese project's
[SRVC reader](https://github.com/dyzz/srwz-zh/blob/f6673b1edf697df3501fba3889e930815fd1b001/tools/srwz/srvc.py)
and [Special Disc migration tool](https://github.com/dyzz/srwz-zh/blob/f6673b1edf697df3501fba3889e930815fd1b001/tools/special_disc/writeback/migrate_srvc.py).
The local main-game indexed reader is useful for comparison. Historical
heuristic readers can mistake sequence data for an index. No Chinese font,
unlock patch or fixed-capacity writer is imported.

Donor reads follow its relocated VMAP extents. Matching Japanese identities
produce candidates, not automatic approval: 24,522 match the built donor,
877 have active/donor disagreements and 123 need new translations. The
inventory records 3,672 active candidates with differing literal line-break
counts. These categories must not be conflated with completion.

## Native format and relocation

The bank initializer at `0x2FE610` computes the index as
`8 + byte[1]*4 + u16[4]*8 + byte[2]*8 + byte[3]*4`.
Each eight-byte record contains voice metadata and an unsigned text offset
relative to the following pool. Sequence fields at +4/+6 select first record
and count. All 50,332 sequences partition the 59,262 indexed records exactly
once. An independent contiguous-pool search agrees with the native formula.

The loader passes SEG[i+1]-SEG[i] to its asynchronous reader, whose allocation
covers the sector-aligned extent and leading sector offset. Growing blocks
does not rely on original capacities. The ISO writer updates directory extents
and runtime VMAP entries as well as SEG.

English is appended after each complete original block. Only selected index
offset words change. Headers, groups, sequences, conditions, voice IDs, original
string bytes and opaque tails remain intact. The tails include 180 distinct
quoted identities outside the indexed inventory. Their complete reachability
is unresolved; they are preserved and are not counted as translated.

## Display and layout

`0x2F1760` converts literal backslash-n to LF without a length check. The native
temporary buffer is 96 bytes at manager+0x2B8. Two managers at `0x689710` and
`0x68A860` are established by the parent initialization loop. Caption drawing
reaches the same `0x13AD30` font interpreter already ported for menus.

The caption setup at `0x303340` starts at x=160 with width=480 on a 640-unit
canvas. A conservative 460-unit limit includes quote marks. Native captions
have at most two rows. Default height is eleven units and the caption object
adds a one-unit row gap. Full/split-view origins and guarded setup instructions
are recorded in `work/ui/battle-caption-layout-0.2.8.json`.

All 1,000 reviewed captions fit, including four independently approved compact forms.
Their largest converted requirement, including NUL, is 91 bytes; the complete
native corpus peaks at 86. Version 0.2.8 therefore keeps all original
caption display instructions and its 96-byte buffer. No ending is dropped.

Optional `battle_buffer.py` adapters pass instruction-execution tests for both
known managers, unknown-pointer fallback, delay slots and large capacities.
They map fill, draw and clear calls to storage sized from actual encoded text.
They activate only when a later approved release needs more than 96 bytes and
are not installed in 0.2.8. Seven reconstructed previews use the actual Latin
atlas; they establish static fit, not in-game clipping, timing or playback.
The tilde uses a substitute preview glyph. The game maps ASCII 7E to native
CP932 8160; this mapping is guarded. The 24-unit layout allowance is conservative
against the 13-unit ASCII advance and preserves the vocal inflection.

## Editorial status

New slices 0-79 and 80-122 and all eleven reuse slices from 0 through 876 received separate
meaning reviews. Reviewers inspected every occurrence, neighbors and boundaries.
Fixes include support direction, missing firepower, the world's fate, lost
Newtype status, and a successful hit incorrectly turned into a revenge promise.
Follow-ups approved the compact 10,000-hit taunt and White Mustache recognition.
Later reviews restore named relatives, explicit futility, machine operators,
counterattack announcements and the Double Reversal attack variant. The dust
proverb's compact form retains uncertainty about its unfinished ending.

Name normalization follows meaning edits and is gated by native terms. A
corpus-wide inventory of reported variants is in `battle-spelling-audit.json`.
It includes historical drafts and donor alternatives and is not a defect count.
Version 0.2.7 applies the verified spelling rules to 148 Library fields,
52 menu/name fields and two Q&A pages. Identity includes the native article
owner for prose and the full pilot name for reordered name fields. Regression
checks protect ordinary saber weapons, unrelated people and paragraph breaks.
Version 0.2.8 adds corrections in 45 Library fields, 15 menu fields and seven
chart summaries. The chart compiler applies source-scoped terms after meaning
review while retaining the hash-bound review drafts. The release input is
`battle_release_0.2.8.json`; `battle_release_0.2.7.json` and `battle_release.json`
retain earlier inputs. The remaining 56,950 indexed occurrences stay native.

Remaining work includes other indexed candidates, COMPDATA battle text, tail
reachability, speaker-name layout, runtime acceptance and the scope ledger's
other surfaces. No emulator was launched for this pass.
