# Build 0.3.11 — Search panel alignment

The screenshot shows two layout failures: the long Search heading intersects the fixed OK legend, and Repair Module's five-line description runs below the help box.

## Changes

- Search Item, Search Filter and Search Use replace the three long decorated headings. Their conservative measured widths are 122, 135 and 111 units, below the 150-unit budget. The screenshot places the button legend near x=200, with the heading beginning near x=12.
- The help text begins near x=86 on the game's 640-wide canvas. Three lines at the existing 24-unit spacing stay inside the footer. A conservative width limit of 510 ends at x=596, before the panel's right border.
- Inspect the native description pointer table at COMPDATA offsets 0x54A60–0x54B80, accepting only native description targets 0x81F20–0x837D0. Deduplicate references: 57 unique descriptions checked, 26 changed. Leave descriptions that already fit unchanged.
- Reflow English wording except five compacted entries: Shield, Supply, Repair, the nearby-enemy Oversense debuff, and the longest Over Skill effect list. Keep targeting, thresholds, resource recovery, all effects and squad-member applicability. Use existing UI abbreviations Agi/Sight in the longest entry.

## Installation and checks

`tools/prepare_search_layout.py` records current strings, exact preimages, allocations, pointer bindings and widths in `work/translation/en/search_layout.json`.

`tools/search_layout.py` checks v0.3.10 member hashes and exact field bytes, edits only existing text slots in COMPDATA and the existing executable text pool, and checks every description after installation. No pointers, executable instructions, allocations or gameplay parameters change. The compressed COMPDATA is read back with the strict decoder.

`tools/build_search_layout.py --write --patch` builds the ISO, relocates the two members into unused reserved space, verifies ISO and runtime reads, compares the whole disc against its planned writes, and reconstructs the clean-disc xdelta for a hash comparison. Base ISO SHA-256: `07f4dd245a3cf8e4b1ef533ef8583574b064bc8a228c3a7d0e58ee6e3a5f4e43`. Final hashes and verification results are recorded in the output JSON receipt.

The screenshot and static font reconstruction are in `work/ui/search-layout/`. The preview uses the shipped English glyph atlas, conservative advances and approximate native punctuation; it is not an emulator capture. The prompt and the Repair, Supply and longest effect descriptions fit visibly in this reconstruction.

In-game acceptance remains pending. Cold boot v0.3.11 rather than restoring an older emulator state.
