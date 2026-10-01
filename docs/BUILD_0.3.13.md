# Build 0.3.13

Local test candidate based on v0.3.12, addressing the reported combat forecast screen.

- Attack and counter icons: ATK / CNT.
- Support defense badge: SD plus the unchanged numeric rank.
- Getter Robo squad names: two strings, referenced at four script sites, in stage chunks 18 and 40.
- Hyakki Empire: already English in the fixed stage headings, including the 21 occurrences in challenge chunk 40.

The atlas is KURODATA/KVMDATA.BIN, TIM2 page 0x20900. Only four explicitly bound rectangles change. Their original pixels match the native game. Text is rendered with the established palette-index renderer; the original palette, framing and sprite coordinates are preserved. The local SRW-Z reference still has Japanese in these icon cells, so these bounded English sprites are newly rendered.

The Getter Robo string replacements fit within the original 13-byte strings, including terminators. All four pointer words are bound back to the native strings; they remain unchanged. Every unrelated byte in both decoded stage chunks is restored and compared, all 68 stage chunks are verified, and the HB file only changes within its stage offset table.

Build with `python tools/build_combat_forecast.py --write --patch` using the project Python environment. The output ISO and xdelta are under `work/output`. Full-image verification compares against the previous disc plus only planned writes, and clean-source patch reconstruction must reproduce the exact output hash. The preview is `work/ui/combat-forecast/preview-0.3.13.png`; it is an atlas preview, not emulator evidence.

In-game testing is pending. Cold boot the new ISO. Existing saves may retain old squad names; restart the affected mission or rename the squad where supported. No save files are modified.
