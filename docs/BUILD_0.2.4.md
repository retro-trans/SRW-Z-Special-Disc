# English save/load recap candidate 0.2.4

Adds 60 English save/load summaries to 0.2.3. Story dialogue remains unchanged.
Binary and patch verification passed. Emulator testing is pending by user choice.

## Meaning and layout

All 66 full drafts were reviewed against native HSFC chunk 0; all 66 compact
alternatives then received a separate review. Nine corrections restore details
lost or distorted during compaction, including Loran's group, the incoming
machine/person delivery, the food sabotage's target, machines going berserk,
the Destiny Plan's announced implementation, the caravan referent, and the
requirement to defeat bandits before the Federation does.

Sixty records pass both meaning and three-line layout gates. Six remain native:

| Recap ID | Detail that requires more space |
| --- | --- |
| 2 | Joining Bran, the nearby-town battle, helpers and subsequent delivery |
| 13 | Teral's deceased lover and the past recalled by Rie's rescue attempt |
| 17 | Food sabotage, fasting/hunger, victory and its toll |
| 27 | Black History, the Executor, Japan, Ghingnham and pursuit |
| 44 | Announced Destiny Plan implementation and the challenge objective |
| 53 | Defeating the bandits before the Federation and the funding target |

These records retain full English targets for further layout work. They are
not shortened by deleting facts. The three native text cells are preserved
verbatim inside widened records so the shared printer can still display them.
The review also documents that recap 46 does not specify the caravan's ship
count. No exact count or identity was invented.

The font's actual advance is used directly; it is not scaled by the native
16/24 font-size ratio. The conservative bound is 520 units per line and three
rows. No font size, screen coordinates, row count or gameplay data is changed.
See [the research](SAVE_SUMMARY_RESEARCH.md) and the UI profile in
`work/ui/save-summary-layout.json`.

## Storage and protection

- Native HSFC chunk 0: 13,312 bytes, 66 records and 52 unique record hashes.
- The original HSFC archive remains byte-identical, including other chunks.
- The ELF pool holds an empty record, 52 deduplicated records and 67 pointers.
- Each record has three 256-byte cells, replacing the old 66-byte byte budget.
- A 44-byte getter replacement preserves the low-16-bit index contract and
  maps invalid indices to the empty record. Only two printer strides also change.
- The getter tests execute MIPS instructions and delay slots for all 65,536
  index values at two table addresses, covering signed low-half address carry
  and preserved registers. Additional cases verify ignored high index bits.
- All existing story-chunk, non-text-data, archive and disc-range checks remain.

## Validation

The ISO and 3,161,438-byte xdelta are in `work/output/` as
`SRW Z Special Disc English v0.2.4`.

- ISO SHA-256: `37a9010a39cabe8c297c7825c9fcb11e8c89ee3109f3d0b071b9b5a069e81e7d`.
- Patch SHA-256: `98a6cc7b5eda077e42d8ffc858885e46609a75c0d337cbc75db926137918453c`.
- Patch reconstruction matches the full ISO. All 3,777,663,552 bytes outside
  the 32 planned write ranges match the clean source.
- Independent readback passed for 4,995 Library fields, 313 reference names,
  395 chart fields, 60 English recaps and all six native recap deferrals.
  The total is 725 relocated English text targets, with all configured line
  bounds checked. Native HSFC, battle/narration members and story chunks remain
  byte-identical.
- English segment `0x81C970..0x83B57C` is above native memory and below the
  adjusted heap at `0x83B600`. The text pool occupies 115,580 bytes.
- All receipt hashes match the 36 tool files, 24 translation files and two
  glossary files used in this build. Older outputs were not modified.

The build receipt and independent audit are in `work/output/` and
`work/analysis/`. Static checks do not establish runtime layout or gameplay
acceptance; those remain pending.

The broader translation goal remains active. See the
[scope ledger](TRANSLATION_SCOPE.md) for remaining recaps, narration, battle
captions, suspend messages, artwork and stage UI.
