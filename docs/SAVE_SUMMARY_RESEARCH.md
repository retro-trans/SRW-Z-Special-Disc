# Save/load summary integration research

Research after build 0.2.3; first integration is in candidate 0.2.4.

Native HSFC chunk 0 has SHA-256
`695ccf4e07f6269baa95019d74caa8764a4f12d5a2231144f0f78a2e0c3a851e`.
It decodes to 13,312 bytes. Its compressed allocation is 5,072 bytes; strict
decoding consumes 5,058. Executable offset `0x3AE8A0` contains boundaries
`0, 5072, 452944, 876544, 876768`; decoded sizes at `+32` are
`13312, 1299456, 694608, 432`. Later chunks contain other assets.

The source contains 66 summary records from `0xE6`, each three 66-byte cells.
There are 52 unique complete-record hashes. An empty record precedes them at
`0x20`. The UI therefore uses record indices 1–66 for exported IDs 0–65;
index 0 is the empty fallback. Keep the debug filename `SvLd_Notice_List.txt`
literal in the five repeated developer placeholders.

Verified Special Disc runtime addresses (file offset = address - `0xFF680`):

- `0x43CB60..0x43CB88`: getter loads the decoded buffer from object offset
  `0x2C`, sign-extends the supplied 16-bit index, calculates index * 198, and
  returns buffer + index * 198 + `0x20`.
- `0x43CA20` chooses the entry from a save record's field at `+0xCE`, or index
  zero for an empty save; the returned text pointer goes into object `+0x30`.
- `0x43CB90`: display routine. It calls the font setup at `0x13A7F0` with
  alternating 16 and 8 dimensions, then displays three lines at x = -236 and
  y = 64, 74, 84. The two later text pointers use `+0x42` and `+0x84`.
- Those additions are at `0x43CC54` (`0x24640042`) and `0x43CC78`
  (`0x24640084`). These are text strides, not screen coordinates.
- The printer at `0x13D050` tail-jumps to `0x13AD30`, inside the font routine
  range already covered by the English runtime port. Verify private glyph
  behavior and widths in the compiler; emulator acceptance remains pending.

The getter's 44-byte native preimage is:

```text
2c00828c3c2c05003f2c05004019050021206500801804002318640040180300211043000800e00320004224
```

Proposed next-build approach: store complete English three-line records in
the loaded ELF pool with wider cells; replace the getter with a guarded
67-entry pointer lookup and update only the two display strides. Preserve
HSFC itself, its allocations, the save record format and all other UI data.
Do not use a smaller English summary merely to satisfy the old byte slots.
The measured font-width and three-row limits still apply; compact wording
only after the full meaning is reviewed. Establish the final line-width
profile before calling layout valid.

The inherited main-game HSFC patcher uses a different layout: 208 records,
50-byte cells and a different panel. Its text budget, encoding assertions and
old truncated English recap export are not Special Disc evidence.

The donor's actual VWF advance routine (`0x78BA60`, relocated with the rest
of the English runtime) adds the per-glyph width directly to the screen pen
at `0x78BAB0`. There is no multiplication by the native 16/24 font-size ratio.
Use the 69-byte table at donor `0x78B960`, plus two for conservative bold
spacing, and 13 for spaces. `save_summary_text.py` uses a 520-unit bound from
x = -236, leaving 36 units before the 640-wide canvas's right edge. Three
rows remain the native limit. These are static bounds; emulator acceptance
is pending, and the panel has not been measured from a new screenshot.

The complete drafts passed independent source review for all 66 records,
including all 18 challenge objectives. No full-draft meaning corrections
were requested. The source does not specify a ship count in recap 46; its
English plural is documented as an interpretation. Before compaction, 15
records fit three rows and 51 require four to six. A separate layout pass
must preserve the facts and explicitly flag any entries that still do not fit.

`compile_save_summaries.py` implements the guarded pointer table and two
stride changes. It requires reviewed layout metadata before use, validates
all native preimages and source hashes, and checks every mutation. Its getter
is tested by executing its MIPS instructions with delay slots for all 65,536
indices at two table addresses, including signed low-half address carry.
This compiler is first included in build 0.2.4. It adds 60 English recaps;
IDs 2, 13, 17, 27, 44 and 53 retain native strings after the final review.

The getter has two direct call sites, `0x43CA78` and `0x43CA8C`; both enter
at its first instruction. The replacement preserves the low-16-bit index
contract and maps invalid indices to the empty entry. The three-line record
uses 256-byte cells in the loaded English pool. When a recap fails the meaning
or layout gate, the compiler retains each original native cell verbatim inside
that wider record; returning its original 66-byte layout after changing the
printer strides would be invalid. Reports distinguish English entries from
these native deferrals and avoid dumping their Japanese prose.

Build 0.2.9 adds five of the six deferred records after another independent
meaning review. ID 13 uses a neutral military repulse rather than inventing
flight. Only ID 27 still needs four rows. The follow-up merger preserves the
old reviewed input and writes `save_summaries_release_0.2.9.json`; the compiler
requires exact fresh preparation and actual archive/review hashes. Independent
fault checks reject duplicate proposals and forged matching archive hashes.
All 60 prior approved records and the deferred record retain their prior objects.

`preview_save_summaries.py` reconstructs the five new layouts from the donor's
actual Latin atlas. Its widest row is 511 of 520 font units. Three punctuation
glyphs (two semicolons and one plus) use explicitly marked preview substitutes
at the same conservative advance. The preview is not an emulator screenshot.
