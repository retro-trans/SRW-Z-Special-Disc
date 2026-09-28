# Super Robot Wars Z Special Disc — English Translation

An unofficial English translation patch for **Super Robot Taisen Z Special Disc** on PlayStation 2. This is the Japanese **SLPS-25920** Special Disc, a separate game from [Super Robot Wars Z](https://github.com/retro-trans/SRW-Z).

**Latest: v0.3.0 — story test build.** Includes the existing menu and Library translation plus all 45 story chunks. Translation and binary checks have been performed; in-game rendering and a complete playthrough are still pending. This project uses AI-assisted translation and review and needs further human editing and playtesting.

[Download the release](https://github.com/retro-trans/SRW-Z-Special-Disc/releases/latest) · [Changelog](CHANGELOG.md) · [Report an issue](https://github.com/retro-trans/SRW-Z-Special-Disc/issues) · [Community Discord](https://discord.gg/MssepShjmB)

## Play / apply the patch

### Retro Trans

Use the [Retro Trans patching app](https://github.com/retro-trans/retro-trans-tools/releases/latest). Its automatic catalog selects a patch from the exact input image hash and checks the output. Public catalog discovery requires this repository and its release to be public; a private release cannot be downloaded by the public app.

1. Open Retro Trans, refresh its catalog, and choose your clean Japanese Special Disc image (ISO, or a supported CHD).
2. Select **Super Robot Taisen Z Special Disc**, English **0.3.0** / **Latest**, when recognized.
3. Choose a new output filename and apply. Use the verified output ISO in your emulator or your own compatible hardware setup.

This release contains the canonical `BUILD-MANIFEST.json`, `VALIDATION.json`, `SHA256SUMS.txt`, and `SRWZ-SP-English-v0.3.0.xdelta` expected by Retro Trans. SHA-1 aliases support DVD CHD recognition; the extracted image is still verified by SHA-256 before patching.

### Manual patching

Download `SRWZ-SP-English-v0.3.0.xdelta` from the release. Apply it with [Delta Patcher](https://github.com/marco-calautti/DeltaPatcher) or xdelta3 to your **clean, extracted Special Disc image**, not to a CHD container or an earlier translated image. Keep your original image.

```sh
xdelta3 -d -s "Special Disc (Japan).iso" "SRWZ-SP-English-v0.3.0.xdelta" "SRW Z Special Disc English v0.3.0.iso"
```

Check `chdman info -i "Special Disc (Japan).chd"` before manual extraction. For a DVD CHD use `chdman extractdvd -i "Special Disc (Japan).chd" -o "Special Disc (Japan).iso"`. For a single data-track CHD use `chdman extractcd -i "Special Disc (Japan).chd" -o "Special Disc (Japan).cue" -ob "Special Disc (Japan).bin"`, then patch the BIN only if it matches the source hash below.

The local test CHD stores this DVD image as a **single MODE1/2048 CD track**; Retro Trans supports that container and extracts it before identification. A logical ISO with a `.bin` filename is valid when its bytes match. Raw 2352-byte CD sectors are not the required format.

| Image | Required identity |
| --- | --- |
| Edition | Japan, SLPS-25920 / executable SLPS_259.20 |
| Source format | 2048-byte-sector DVD image, 3,791,781,888 bytes |
| Source SHA-256 | `c3bd8c1af4e411e5ab2ae2d4be877170b6ab1ea9b51fa62bc0b91a51ba1a2952` |
| v0.3.0 output bytes | 3,791,781,888 |
| v0.3.0 output SHA-256 | `ca444e5c078a6f3cb23a96c5b6d676de1df068cfa4219ecbc06e71cbea4186ec` |

Patches for the main SRW Z game, other editions, modified images, and previous English Special Disc builds are not interchangeable with this full patch. No game image, BIOS, or original script dump is distributed here.

## Translation coverage

| Area | Included in v0.3.0 |
| --- | --- |
| Story | All 45 story chunks: 7,511 dialogue rows, 71 scene captions, and the chunk-66 demo scene |
| Library | 330 robots, 413 characters and 52 glossary entries; 4,995 translated fields |
| Menu and names | 5,521 menu/name fields and 2,362 executable UI fields |
| Strategy Q&A | 102 pages and 264 chapter/keyword fields |
| Scenario Chart | 131 titles and summaries, 128 episode labels and five control hints |
| Mission conditions | 60 distinct victory, defeat and Challenge texts at 114 occurrences across 39 modules |
| Graphics | Front-end and Library buttons, 13 globe locations, 21 episode titles, intermission/Bazaar artwork and squad confirmation tiles |
| Battle captions | 1,917 reviewed texts at 4,870 occurrences; other captions remain untranslated |
| Other text | Data Link, episode introductions, Challenge briefings, ten narration/journal entries, and 65 of 66 save summaries |

Compact AIR/GND/SEA/SPC artwork uses the main SRW Z technique to preserve rating-letter placement. Squad naming help, Join reports, formation descriptions and shared Challenge confirmation include the latest layout fixes.

## Known limitations and testing

- **This is a test build.** Emulator testing remains pending. Story box width, three-line rows, thought boxes, caption centering and the relocated stage archive need runtime checks.
- Remaining work includes other battle captions, suspend-message integration, one save summary, remaining artwork and broader editorial review of inherited Library text.
- 334 internal story labels that may serve as lookup keys and hidden `???` condition identities remain native deliberately.
- Binary reconstruction verifies bytes, not playability. Please report the build, mode/episode, steps and a screenshot for translation, clipping or crash issues.

See [v0.3.0 build evidence](docs/BUILD_0.3.0.md), [story implementation](docs/STORY_BUILD.md), [non-story base](docs/BUILD_0.2.24.md) and the [scope ledger](docs/TRANSLATION_SCOPE.md). Older build notes describe their own versions; the v0.3.0 story scope supersedes earlier non-story-only plans.

## Source and contributions

The repository contains translation tools, research, and [English-only review exports](work/translation/en/public). Original dialogue, encyclopedia and battle-caption source corpora, extracted archives, local caches, screenshots and disc images are excluded. Public exports retain stable IDs and selected source hashes without original text.

This is **not a turnkey rebuild kit**: historical builders require privately generated extraction inventories, reviewed inputs and donor assets from a matching local main-game workspace. Read [tools/README.md](tools/README.md) and [publication instructions](docs/PUBLISHING.md) before using them. Release patches are the supported way to play.

Translation corrections and reproducible bug reports are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). Please do not attach game images or original script dumps to issues or pull requests.

## Credits

- [retro-trans/SRW-Z](https://github.com/retro-trans/SRW-Z): English terminology, font/runtime work, reusable menu artwork and format libraries.
- [dyzz/srwz-zh](https://github.com/dyzz/srwz-zh): Special Disc archive and text-format research.
- [retro-trans/retro-trans-tools](https://github.com/retro-trans/retro-trans-tools): patch packaging, validation and automatic patch selection.

See [third-party notices](THIRD_PARTY_NOTICES.md). This is a fan project, unaffiliated with the game's publishers or rights holders. Game content remains the property of its respective owners.
