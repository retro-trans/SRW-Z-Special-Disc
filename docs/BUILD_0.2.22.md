# English Challenge confirmation candidate 0.2.22

The reported Japanese question now reads **Attempt this mission?** This one
shared prompt serves all 18 Challenge briefings. The wording received an
independent meaning review, and fits its existing 32-byte UI text slot.

The native COMPDATA string is at decoded offset `0x98270`, selected through
pointer slot `0x6a2c8`. Both the width measurement and drawing paths load that
same slot, at executable addresses `0x437020` and `0x437058`. The earlier menu
passes stopped before this table entry.

The installed English font gives the question a 210-unit width. Replace the
final x calculation at `0x437038` with `addiu v0, zero, -189`, placing its left
edge at x131 and center at x236, the native Yes/No anchor. The original
measurement call, draw call, style, vertical position, choices and delay slots
remain intact. No text pool, pointer, buffer or gameplay change is required.

Four focused regression checks pass. They verify the shared selector and
measured center, reject the old Japanese field, and reject changes to adjacent
menu data or executable bytes. The screenshot and source bindings are under
`work/ui/mission-prompt/`. Story dialogue stays unchanged.

The new independent audit compares the final decoded COMPDATA and entire ELF
against 0.2.21 after restoring only the approved text slot and position word.
It also compares every other translated archive and all VT1 textures. Only
after this succeeds do historical deployment, tactical and terrain audits get
a comparison view with these two changes reversed. This lets their older
whole-file baselines remain strict without exempting any unrelated edits.

Emulator testing remains pending by user choice. Start the new ISO with a
fresh boot when testing; a save state can retain the earlier loaded overlay.

## Output verification

- ISO: `work/output/SRW Z Special Disc English v0.2.22.iso`, 3,791,781,888 bytes.
- ISO SHA-256:
  `e20a6851df99ae8545dcfe33b77fb8022fce94e839f2d86bfdab3d3597df5ae9`.
- Patch: `work/output/SRW Z Special Disc English v0.2.22.xdelta`, 5,052,921 bytes.
- Patch SHA-256:
  `2de7050c8b7a17f843526af7b516e1907f47b0689c648f7a834577e93c347b6d`.
- The patch reconstructs the exact ISO from the clean source. All
  3,728,966,076 bytes outside the 65 planned write ranges match the clean disc.
- The independent finished-disc audit passes the prompt, native pointer,
  installed font width and x-position checks, plus all earlier component audits.
  Only the approved 32-byte decoded COMPDATA field and one executable word
  differ from 0.2.21. Every other translated archive and all VT1 textures match.
- COMPDATA is 184,689 compressed bytes (652,800 decoded). SHA-256:
  `e4abe3266e23dd6ee4b7d57d1d77ed83dfd575d0150c858be168ded350f8ecee`.
- The executable stays 4,112,380 bytes. SHA-256:
  `eb322c645a6af6a93d19e76ca40bec22601f52f1ed1484d9b371555cb9838e0d`.
- The English pool stays 122,876 bytes, ending at `0x83d1fc` below heap
  `0x83d600`; every earlier pool byte is unchanged.
- All 298 recorded inputs match: 125 Python files, 147 translation files,
  19 glossary files and seven binding inventories. The 302-entry input archive
  is 11,020,176 bytes; every entry was read back exactly. SHA-256:
  `ad9ff0ef6fccd7e1accd5b395f44a4313e444bdce21dcde1397871060dded6f8`.
