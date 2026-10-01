# Build 0.3.10 — Grendizer Experience-panel name

The screenshot reads `グレンダイザー` (Grendizer). The regular COMPDATA unit name already translates to Grendizer. Six separate scripted squad presets still carried the Japanese name. This build translates those six fields in stage chunks 18, 19, 20 and 21.

## Scope and guards

- Preset offsets: 18/0x6509; 19/0x3DE9 and 0x40A9; 20/0x45A9 and 0x4835; 21/0x6C45.
- Each name follows the index in a 52-byte record; its area is 33 bytes, followed by six 16-bit member IDs and record flags.
- Only the original 14-byte name and terminating NUL are replaced. The English value fits without relocation or changes to pointers and record sizes.
- Each complete preset is compared with the native disc. Both record boundaries and zero padding are checked. All native stage chunks are searched to confirm the six-item inventory.
- All 68 stage chunks are checked after rebuilding. Every decoded byte outside the six name writes is preserved; unchanged compressed chunks remain identical. Only the stage offset table changes in HB.BIN.
- The builder verifies ISO and runtime reads, every planned disc write and clean-source xdelta reconstruction. The build receipt records final hashes and results.

Build with `tools/build_experience_name.py --write --patch`. Base: v0.3.9, SHA-256 `7aa8820bc12bf555586d4bac91dd94ec7c2dd7f3601ed475bb91d4659b5ea446`.

UI bindings and screenshot: `work/ui/experience-name/`. Translation inventory: `work/translation/en/experience_name.json`.

## Verification limit

Emulator testing and confirmation of the reported Experience panel remain pending. Cold boot the new ISO. A squad name already stored in a save may retain its previous value; renaming that squad to Grendizer or starting the affected episode again should avoid relying on an old saved name. This patch does not edit user save data.
