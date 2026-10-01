# Build 0.3.14

Local test candidate based on v0.3.13. The canonical faction name is **Hyakki Empire**, replacing **Hundred Demon Empire**. Hyakki Hundred remains the name of a distinct subgroup.

The installed correction covers 23 occurrences: 16 dialogue strings in stage chunks 2, 3, 18 and 40; five executable strings used by UI, chart text and save recaps; and one row each in the introduction and Challenge briefing banks. Matches spanning a line break are included. Existing line breaks remain, each line becomes no wider, and the replacements fit within the original allocations. String pointers and executable instructions remain unchanged.

The glossary now normalizes the alternate faction name. Twenty-two active/public English files were updated, including story final and compact inputs, briefing and override inputs, and public exports. Future story layout applies the same faction correction. Historical draft/review/layout receipts are retained as records of earlier builds; the new source-bound terminology inventory is the authoritative incremental correction.

`tools/build_hyakki_terminology.py --write --patch` creates the versioned test ISO and xdelta under `work/output`. It validates the exact base image and all text preimages, unchanged decoded stage bytes outside the selected strings, all 68 stage chunks, unchanged VT1 bytes outside the two compressed slots, every disc write, ISO/runtime reads, and clean-source patch reconstruction.

The additional archive audit checks the encyclopedia text fields, battle captions, COMPDATA and auxiliary text archives for the alternate faction name. No additional matches were found. English Hyakki Hundred entries remain intact.

In-game testing is pending. Cold boot the new ISO to avoid restoring old text from an emulator state.
