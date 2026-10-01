# v0.3.6 — Complete post-save scenes and next battle-caption batch

Local candidate based on v0.3.5, following the request to find and translate other battle lines like Shinn/Sting's and post-save conversations like Rand/Mel's.

| Category | Newly installed | Total installed |
| --- | --- | --- |
| Post-save / Special Theatre | 288 unique messages | 296 messages, 57 complete scenes, 379 typed references |
| Indexed battle captions | 236 unique captions at 694 occurrences | 2,155 unique captions at 5,566 occurrences |

All known post-save messages in the native 57-scene inventory are now English. Battle translation is still partial: 23,367 of 25,522 indexed identities remain native, including the deliberately suppressed production placeholder. This build does not claim to translate every battle line or unbound tail string.

## Post-save installation

`tools/complete_suspend.py` revalidates the complete independent source review, retaining every reviewed text and decision. Only the spelling glossary's dependency hash differs from the older saved review; fresh recomputation proves the actual reviewed content unchanged, and the report records both dependency sets.

Forty-three long messages use shorter wording in `work/translation/en/suspend_full_fits.json`. Each is bound to its original reviewed text and source hash and was checked against its Japanese source during this change. All eight Rand/Mel messages keep their exact v0.3.5 wording and line breaks. Other messages use balanced wrapping with a maximum of three body lines and a conservative 400-unit width.

The 296 strings occupy 21,323 of 23,312 bytes in the original executable region `0x3B8BE0..0x3BE6F0`. Only the 379 typed opcode-6 text pointers are repointed. All other command words remain identical; the false address match in the unrelated numeric table at `0x353AAC` is preserved. No executable instructions, heap boundary, timing, portraits, pagination or save data change.

All 296 strings were run through the installed setText converter instruction model. The maximum converted size is 226 bytes including NUL, below the audited 452-byte physical space after the message header. All lines meet the 256-byte parser guard, with no dictionary-expansion keys. The 452-byte figure is an allocation boundary, not a recovered source-level array declaration. Visual acceptance is still pending.

## Battle installation

`tools/next_battle_batch.py` validates the pending independent author/reviewer sets for IDs 960–1199, applies their reviewed corrections and compact variants, and skips four identities already translated in the frozen baseline. This yields 236 new identities. All lines fit the two-row, 460-unit battle area and the existing 96-byte caption buffers.

The source identity, all occurrences, current Japanese preimages and voice metadata are checked. New strings are appended to the affected banks; only their selected index words change. Existing translated strings and opaque tails are preserved. The rebuilt SRVC archive and segment table are moved into verified empty reserved disc space with both ISO and VMAP entries updated.

A separate comparison traversed all 59,262 indexed records and found exactly 694 changed text occurrences and zero voice-metadata changes. Shinn and Sting's v0.3.4 fixes are retained.

## Reproduction and output

```text
python -B tools/build_dialogue_batch.py
python -B tools/build_dialogue_batch.py --write --patch
```

The default is a full dry run. The writer requires the verified v0.3.5 image and refuses existing output. It checks final executable/archive readback through both disc paths, then compares every ISO byte against the exact planned writes. The clean-disc xdelta must reconstruct the same ISO hash.

English inventory: `work/translation/en/dialogue_batch_0.3.6.json`. Layout records and audit: `work/ui/dialogue-batch-0.3.6/`. Source Japanese scripts are not exported or committed. The public v0.3.0 release remains unchanged.

For runtime testing, cold boot v0.3.6 and view several post-save scenes, especially long conversations and repeated variants. Check all body text stays in three lines and speaker names remain separate. Test the additional battle captions for wrapping and voice pairing. Emulator testing remains pending by user choice.

## Verified hashes

- ISO: `work/output/SRW Z Special Disc English v0.3.6.iso` (3791781888 bytes).
- ISO SHA-256: `83b462d6c5b08baf24a48a42f48cdd2e894814a1e2774bbb9149e59952c13f46`.
- Patch: `work/output/SRW Z Special Disc English v0.3.6.xdelta` (7999669 bytes).
- Patch SHA-256: `959229d491d2ddc88a553a11f11689cca6501211f2888c848a4f4ab8634ff340`.
- Whole-disc planned-write comparison and exact clean-disc patch reconstruction passed.
