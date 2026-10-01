# Special Disc suspend messages

296 unique text records occur in 57 complete Special Theatre scenes, with
379 typed text-pointer operands. Source executable SHA-256:
`9c345c4a19e7abd791b00af707fe1f44086da6b1b21b8a4344a5872b307c5101`.
`tools/suspend_format.py` validates the inventory and exports coordinates,
hashes, scene membership and English reuse candidates without Japanese prose.

The text range is file `0x3B8BE0..0x3BE6F0`; the last string ends at
`0x3BE6E2`, followed by padding. Binary data starts at `0x3BE6F0`.
Scenes occupy `0x38CA90..0x39AD10`, followed by 57 pairs of scene address
and index and a zero terminator. Every command is 32 bytes. Opcode 6 has its
text pointer at +16. The numeric match at `0x353AAC` is part of an unrelated
monotonic table, not a pointer; it must never be relocated.

289 records exactly match native SRW Z STAGE chunk 0. The seven Special Disc
variants are 281, 283, 286, 288, 291, 293, 295. English candidates are found through
the corresponding typed command operands in the donor, not by assuming that
English and Japanese strings retain the same offset. Each donor command must
match all seven non-pointer words. Candidate provenance includes both decoded
chunk hashes and every matched command. Reuse still requires meaning review.

The upstream reference is
[migrate_slps_text.py](https://github.com/dyzz/srwz-zh/blob/f6673b1edf697df3501fba3889e930815fd1b001/tools/special_disc/writeback/migrate_slps_text.py).
Its suspend path likewise matches main-game system messages. It writes into
native slots; this project will instead relocate complete English text.

Four author slices cover 0–79, 80–159, 160–239, 240–295. They examine all
intersecting full scenes, repeated occurrences and neighboring boundaries.
Independent reviewers use separate hash-bound files. Source speaker/body
delimiters and corner quotes are retained; body wrapping awaits measured layout.
Translation drafts are not yet
installed in the ISO. Full meaning comes before display layout.

## Runtime investigation

The selector at VA `0x35FB40` obtains scene pointers from table `0x49A390`.
It launches an outer 16-byte command wrapper. That wrapper's opcode 17 calls
`0x204720`, entering the actual 32-byte script engine. Its opcode 6 must not
be confused with the outer engine's unrelated opcode 6.

The script manager stores the current command at object+12; `0x1E0220`
advances 32 bytes, and `0x1E0270` returns the command. Controller `0x1EBB70`
accesses that manager. Text-window setText maps to `0x2112D0`, with wrapper
`0x210830`. The setter may copy through `0x2056E0` or strcpy `0x1A5238`
into object+12. A related allocation is 464 bytes, but available text capacity
and intervening member ownership are not yet proved. Do not infer a safe
452-byte buffer from allocation size alone.

Pending before installation: prove the text parser/encoding path, window
width and row count, buffer ownership, and any continuation behavior needed
for long messages. No guessed pagination opcodes or global story hooks have
been installed. PCSX2 acceptance remains pending by user choice.

Independent source review is complete for all four slices. The consolidated
`work/translation/en/suspend_reviewed.json` binds all nine source/draft/review
inputs and the spelling glossaries. All 296 English meanings pass, with
interpretive uncertainty notes retained. The post-review spelling pass makes
no further changes. This does not approve the drafts' line wrapping for display.

The bounded follow-up audit is `work/analysis/suspend-buffer-audit.json`.
The outer wrapper stores a pointer at +8 to a separate 464-byte message
allocation; its setter dereferences that pointer. The text starts at allocation
+12, leaving a physical ceiling of 452 bytes including NUL. This is not yet a
proved declared text capacity. All 138 private English glyph pairs survive the
native classifier/substitution copy path in the bounded instruction model
(276 pair cases and three ASCII/control positions). Downstream parsing and
display remain separate, unresolved contracts. The longest current draft has
168 characters including the speaker, newline and quotes; byte capacity alone
would not establish that its full meaning fits the visible panel.

The follow-up `work/analysis/suspend-display-path-audit.json` binds28 native
instruction/data ranges. Constructor0x20E0E0 installs display vtable0x4C5EE0;
the display dispatch reaches0x20DD20 and then0x226090. ELF GP0x4D2870 makes
the native mode byte0x4CA9EC equal1, selecting the0x441xxx renderer path.
The legacy0x225F10 route is therefore not the native default. Later runtime
writes to that flag remain unproved.

The active parser skips lines longer than256 bytes and iterates at most16
source rows under the default style. This is not proof that16 rows fit the
visible panel. Empty lines advance the source index without a visible row.
Speaker detection requires the actual newline and a native opening quote.
Drawing reaches0x441C10,0x441D20 and0x22A200, while styled segments retain
byte-count-based placement with a21-unit advance. Next: establish English
glyph selection and proportional spacing on this active path. No suspend
translation or renderer hook is installed by these read-only findings.

`work/analysis/suspend-english-draw-audit.json` resolves the downstream font
question. The active draw reaches 0x13AD30 through 0x22A200, including already
ported hooks at 0x13B608 and 0x13B61C. All 419 bounded integer-width cases pass:
private glyphs advance proportionally, native space uses 13 units, and the
default quote brackets use 21. First-bank private glyphs use table width+1;
the second bank uses width+2, with the documented 0x8585 special case.

None of the 296 native messages or reviewed English drafts contains active
inline-style markers, so their lines avoid the separate fixed positioning
between styled segments. Current menu encoding preserves LF and native quote
wrappers for all 296 drafts; its maximum is 174 bytes including NUL and 167
bytes per unwrapped line, below the active 256-byte line guard. Native messages
use two to four total rows, including the speaker. These facts support reuse of
the existing font port, but do not approve logical storage or visible layout.
Those are the next gates before relocation and installation. No legacy donor
text hook or suspend translation has been installed.

`work/analysis/suspend-substitution-audit.json` closes the dictionary-expansion
question for the current drafts. The native setter first copies the source,
then checks fourteen two-byte keys, all beginning with `$`. Their replacement
values can change at runtime, but no encoded English draft contains even one
dollar byte. None of the 296 native records contains a recognized key either.
The initial and final English copy requirements are therefore identical under
the native setup dictionary: at most 174 bytes including NUL, at message 85.
This does not exclude arbitrary later corruption of the dictionary.

The reproducible check is `python -B tools/audit_suspend_substitution.py`.
Its source, review and opcode guards reject changed inputs; `--write` saves a
new report only after dry-run inspection. The saved audit is SHA-256
`c371192c5f775c566d159d22ad60c333c04e537ff89be40e934884d70787e4af`.
This result establishes a copy-size requirement, not logical storage ownership
or visible layout. Those remain necessary before installation.


## Targeted installation in v0.3.5

The user supplied a screenshot of Rand's scene-56 introduction. The complete eight-message Rand/Mel scene (IDs 288–295) is now installed in a local candidate; see [BUILD_0.3.5.md](BUILD_0.3.5.md). This supersedes the earlier “none installed” status only for those eight messages. Their original text slots and typed pointers remain intact. The v0.3.1 setText converter is already active, and all eight new messages were executed through its instruction model. They use at most three body lines at a conservative 400-unit width and at most 220 converted bytes including NUL. No pagination, new commands or buffer expansion was introduced. The remaining suspend conversations are unchanged and emulator visual acceptance remains pending.


## Complete installation in v0.3.6

All 296 unique texts in all 57 native scenes are installed in the local v0.3.6 candidate, superseding the historical partial/native installation status above. See [BUILD_0.3.6.md](BUILD_0.3.6.md). The reviewed corpus plus 43 source-checked compact fits uses 21,323 of the original 23,312 text-region bytes. All 379 typed references are updated; non-pointer commands and the numeric collision remain untouched. Every message was exercised through the installed converter and meets the three-body-line/400-unit layout bound and active parser limits. No extra message pages or allocations were introduced. In-game visual acceptance remains pending.
