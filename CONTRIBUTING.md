# Contributing

Report the release version, mode or episode, steps to reproduce, and a screenshot when possible. Runtime testing and English wording corrections are particularly useful for v0.3.0.

English review exports live in `work/translation/en/public/`. Identify the file and row ID in proposed corrections. These files are publication exports; changes must also be reconciled into the private reviewed build inputs before the next patch is built.

Do not commit disc images, extracted game archives, original dialogue or reference corpora, encoded copies of those corpora, credentials, local receipts, or private paths. UI labels and small format examples are acceptable. Run `python -B tools/check_publication.py` after staging changes. Update CHANGELOG.md for each change and use a new 0.x.y version for each changed game build.

See docs/PUBLISHING.md for packaging. No in-game compatibility claim should be based only on static checks.
