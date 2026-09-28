# Reused SRW-Z format libraries

Copied without changes from the local `E:/Projects/SRW-Z` working tree on
2026-09-25. That working tree contains uncommitted work, so file hashes, rather
than its HEAD alone, identify this snapshot. Its MIT license is retained in
`LICENSE`; that license does not cover the underlying game assets.

| Local module | Donor path relative to SRW-Z | SHA-256 |
| --- | --- | --- |
| `banlz.py` | `tools/banlz.py` | `dc0886353bc32b7d87bce9e8f308028e09e7a03b2ba019323112dcd1306dbb87` |
| `banlz_strict.py` | `tools/banlz_strict.py` | `a600b6b1d7ab323d1fff6d1459dc5c34ccb0aef70afa6cb1ab52459d16420619` |
| `disc.py` | `tools/best_adapter/disc.py` | `fab937a911b1177d325e0c18989d9dd550ec684adbc4266ad03faaecf45e7656` |

The SP workflow imports the compression/verification functions and ISO reader.
It does not invoke these donor modules' standalone main-game utilities.
SP-specific paths, offsets, identities, and writers live one directory above.

Special Disc format research was checked against
[dyzz/srwz-zh at f6673b1](https://github.com/dyzz/srwz-zh/tree/f6673b1edf697df3501fba3889e930815fd1b001/tools/special_disc).
No Chinese translation corpus, feature modification, or upstream full-text
pipeline is incorporated in 0.1.0. See `docs/REUSE_ASSESSMENT.md` for sources.
