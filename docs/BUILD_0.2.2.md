# English reference-screen candidate 0.2.2

This pass adds **598 reference fields**: 113 squad names, 200 map labels,
131 Scenario Chart titles, 128 episode labels, 21 full Special Disc chart summaries and
five control hints. Story dialogue is unchanged. Emulator testing remains
pending by user choice; this is a test candidate, not runtime acceptance.

## Source binding and preservation

- Squad names own 28 bytes at `0x22 + index * 286` in NISVDATA record 4.
  All membership, flags, headers and other decoded bytes are preserved.
- Map names own 200 fixed 256-byte slots. Only 74 have an exact native-text
  English donor match used in this build; SP-only fields are authored or
  translated with checked placeholder/variant patterns. A same-index donor
  would incorrectly overwrite the four SP maps at 75–78 and world-map variants.
- STAGE chunk 0 owns the chart. Its two node tables have 21 and 110 records,
  with 16-byte episode labels and 64-byte titles. Three route nodes have empty
  labels and retain them. Shared titles use exact pointed-to native strings.
- The 21 synopsis pointers at `0x74B4` are redirected to the English ELF pool.
  Old synopsis spans are cleared only after their data references are checked.
  Every other chart byte is checked against the source. The 98,192-byte decoded
  buffer and 44,016-byte compressed slot remain fixed; story chunks 1–67 stay
  byte-identical, as do their archive offsets.
- Summaries use at most eleven lines and 560 font units per line, including
  the wider bold advance. This is conservative against the upstream 29-cell
  panel estimate. Emulator screenshots are still required for final acceptance.

The finished-build receipt and independent audit in `work/analysis/` record
the ISO hash, xdelta reconstruction, field readbacks, protected bytes and
ELF segment/heap separation. Older versioned outputs are preserved.

Verified output:

- ISO: `work/output/SRW Z Special Disc English v0.2.2.iso`
- ISO SHA-256: `09e249007b256c6adff6af803cbb259d0312b9cafeb6af4e9536259dc2014cee`
- Patch: `work/output/SRW Z Special Disc English v0.2.2.xdelta`, 3,133,784 bytes
- Patch SHA-256: `e9f5123d8f7ba0fc084630f37b2fb70c422d0f45716ce79b354be8ac0760848e`
- Patch reconstruction matches the full ISO. All 3,777,753,664 bytes outside
  the 32 planned write ranges match the clean source.
- Independent readback passed for 4,995 Library fields, 313 reference names,
  285 chart fields and 555 relocated texts. All 34,964 Library description
  lines and all chart summaries pass their width checks.
- English segment `0x81C970..0x825478` stays above native memory and below the
  adjusted heap at `0x825600`.

## Editorial review

A meaning reviewer examined all 21 new summaries with adjacent entries for
context, all 113 squad names and the six authored map labels. Corrections
retain the Shadow Angels' repulsion, clarify Phantom Pain's new comrades,
remove an unsupported fatal outcome, identify Metropolis as a book, and
describe King Gainer's parallel-world counterpart without implying a split.

The title table and synopsis pointer list have different ordering; they must
never be paired by array index. The compiler keeps each in its native position.
Long summaries are relocated, not truncated to the Japanese byte capacity.

Reviewed terminology: [Earthgertz](https://en.wikipedia.org/wiki/Gravion),
[Meeya and Medaiyu](https://en.wikipedia.org/wiki/Overman_King_Gainer),
[Mischa](https://eurekaseven.fandom.com/wiki/Mischa),
[Vodara Shrine](https://eurekaseven.fandom.com/wiki/Vodarac), and
[lift boards](https://eurekaseven.fandom.com/wiki/Lifting).
The Meeya spelling follows the English reference over inherited Miiya/Miya;
biographical details of the historic namesake are not assumed from the present
day singer. “Fixers” remains a context-based rendering of the squad of Timp,
Hola and Geraba, referring to underworld operatives.

The Special Disc structures were corroborated against
[dyzz/srwz-zh](https://github.com/dyzz/srwz-zh/blob/f6673b1edf697df3501fba3889e930815fd1b001/tools/special_disc/writeback/write_frame_text.py).
No Chinese text, font or unlock patch is imported.

## Remaining scope

The 110 main-game summaries within the chart overlay remain native. Save/load
summaries, narration, battle captions, suspend messages, remaining
embedded text/artwork and stage UI still require work. Only story dialogue is
excluded. See [the complete scope ledger](TRANSLATION_SCOPE.md).
