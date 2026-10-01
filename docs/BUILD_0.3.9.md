# Build 0.3.9 — Battle formation and attack banners

## Changes

- Translate the screenshot's `トライ・フォーメーション` as **TRI Formation**, matching the SRW-Z battle artwork.
- Reuse all 12 source-matched SRW-Z formation/attack banner sprites: TRI Formation, Wide Formation, Center Formation, Single Attack, Squad Attack, All Attack, Counter, Support Attack, TRI Charge, Attack Again, Support Defend, Combo Attack.
- Reuse the three adjacent translated warning sprites: No Target, Can't Attack, (Range).
- Based on v0.3.8, preserving its Challenge briefing alignment, squad headings, menu reader fix and all earlier dialogue and UI work.

## Binding and safety

The asset is `BTL/TRICMN.BIN`, a multi-picture TIM2 beginning at member offset `0x36560`. The ordinary single-picture TIM2 scanner does not identify it. Picture 0 contains the 12 banners; picture 1 contains the three reused warning sprites. The 512×256 PSMT4 textures use a CT32 upload arrangement; the mapping is adapted from SRW-Z's `patch_battle_banners.py` in its local build sources.

Reference: `SRW Z English Original v0.9.85.iso`, with its native counterpart from the same project's extracted files. Each complete source rectangle must match Special Disc before reuse. The two games have other differences within the same texture and palette bank, so replacing the whole texture/member would be wrong. Only the 15 rectangles' mapped nibbles are copied. Their logical palettes 23 and 25 must match; all palette bytes are preserved, including Special Disc's other palettes.

- 15 complete native rectangles matched; 45,378 member bytes changed.
- Decode after writing must match donor pixels inside each selected rectangle and original Special Disc pixels everywhere else.
- All headers, palettes, sprite coordinates, animations, later pictures and segment offsets remain unchanged.
- English inventory and rectangle coordinates: `work/translation/en/battle_banners.json`.
- Source screenshot, decoded preview and build report: `work/ui/battle-banners/`.
- The preview uses one palette per picture; unrelated numeric sprites use different palettes in-game and can look unusual in the atlas preview.

The remaining warning reasons, status-change and defensive ability sprites are separate untranslated categories; this build covers the complete 12-banner set plus the three existing reference warning translations. It does not claim all battle graphics are translated.

## Build and verification

Run `tools/build_battle_banners.py --write --patch` using Python with NumPy and Pillow. Input v0.3.8 SHA-256: `24bffecb1635f49c1f60565129ca850a97aa242fe2e07f1c6fcecabc074cef51`.

The builder refuses existing output paths, checks source identities, verifies both ISO and runtime member reads, compares the entire output with the exact planned writes, then applies its xdelta to the clean source and verifies the reconstructed image hash. Final hashes and results are in the output JSON receipt.

Emulator acceptance remains pending. Cold boot v0.3.9 rather than loading a state saved with an older build.
