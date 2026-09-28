# Pre-title battle demo

The user identified the supplied Mazinger Z screenshot as a pre-title demo
on v0.2.9. The matching title pixels and Koji field occur in `BTL/OP.BIN`.
This is an engine-rendered battle demo, not burned-in movie subtitles.
No PSS movies are modified. An FFmpeg tool was downloaded into the ignored
cache during format identification, but it is not a build dependency.

Native OP SHA-256:
`e2c7f59a6ae5723da16adb090f9d8cd8f12201d3a39da95cdcef838ed4b77489`.
`BTL/OP.SEG` contains seven offsets:
`0, 48, 266224, 266272, 532096, 532144, 798496`.
They alternate three directory blocks and three payload blocks. The banks
contain 7, 6 and 7 scenes. Each payload begins with a count and twelve reserved
bytes, followed by a 512 by 512 indexed TIM2 atlas. Titles occupy 40-pixel rows.

Each scene starts with sixteen bytes, then two unit records and one or two
sixteen-byte event records. Unit+20 holds the crew count. Crew records begin
at unit+32 with stride 32: pilot ID, two reserved words, then a twenty-byte
display-name field. A unit occupies `144 + 32 * crew_count` bytes. The entire
directory, both unit boundaries and event boundaries are verified for all
twenty scenes before writing. In particular, name+20 can be the next pilot ID;
it must never be treated as spare string capacity.

The compiler binds each of the 61 names to the same native pilot/display ID
in the already released COMPDATA report. Family and given-name slots are
excluded. The twenty title translations use established Library PRDC wording.
Independent meaning review covers every mapped title and name. Titles are
authored with a local Times New Roman Bold Italic font and quantized into
each original palette; the font file itself is not copied or distributed.
The longest title fits its cell at size 30; the remaining titles use size 34.

Screenshot binding: bank 0, scene 1, title rectangle `[0,40,512,40]`, Koji name
at `0x4064c`, pilot 2. The exact caption text is SRVC block 301 record 6,
normalized source 22375. Two other versions of the same call are source 17440
and 20018. All three received independent contextual meaning review before
the spelling pass. The selected attack term is supported by
[Mazinger Wiki](https://mazinger.fandom.com/wiki/Mazinger_Z_(Robot)/TV);
it is a project rendering, not a claim of one unique official localization.

`tools/attract_demo.py` prepares the English manifest and writes only name
cells and title pixels. The archive size, segment table, texture headers,
palettes, unused pixels, gameplay values, pilot IDs, commands and voice
selection remain native. `tools/audit_attract_demo.py` independently parses
the finished disc, compares each name to the regular English display name,
verifies title pixels against the inspected atlas hashes and restores only
permitted ranges before demanding exact equality with the native archive.

Static previews are in `work/ui/english/attract-demo-0.png` through `-2.png`;
coordinates, pixel bounds and hashes are in `work/ui/attract-demo-layout.json`.
They are extracted/compiled texture previews, not emulator screenshots.
Emulator display and timing acceptance remain pending by user choice.
Other battle dialogue in these demonstrations is not declared translated.
