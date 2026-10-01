# Build 0.3.12

Local test candidate based on v0.3.11. The reported Hyakki Soldier line reads: "Damn you, Getter Robo... Die!"

The source-bound entry is 24439, identified by its digest in `work/translation/en/hyakki_caption.json`. All six occurrences in banks 332–334 are updated. The installed caption uses one row, a conservative measured width of 334 against the 460-unit limit, and 35 encoded bytes including its terminator against the 96-byte minimum buffer.

The shared caption writer now accepts explicitly supplied entries and input archive hashes while retaining its original defaults. It validates the native caption identities, preserves voice metadata and all existing text outside the selected records, and keeps opaque archive tails unchanged. The new wrapper requires exactly one translated caption at six occurrences.

Build with `python tools/build_hyakki_caption.py --write --patch` using the project Python environment. This requires the verified v0.3.11 image and clean source disc. It writes a versioned ISO and xdelta under `work/output`, verifies every disc byte against planned writes, and reconstructs the image from the clean-source patch. The adjacent attack banner was already translated in v0.3.9 and is preserved.

Emulator testing is pending. Cold boot the new ISO; loading an old emulator state can restore old caption data.
