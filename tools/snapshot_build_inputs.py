"""Preserve receipt-listed text/tool inputs, without bundling a game image."""
import argparse
import json
import re
import zipfile

from sp_disc import ROOT, sha, require


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', required=True)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    require(re.fullmatch(r'0\.\d+\.\d+', args.version) is not None, 'Expected version 0.x.y')
    receipt = ROOT / f'work/output/SRW Z Special Disc English v{args.version}.json'
    doc = json.loads(receipt.read_text(encoding='utf-8'))
    require(doc['version'] == args.version, 'Receipt version mismatch')
    sources = {}
    counts = {}
    for group in ('source_files', 'translation_files', 'glossary_files', 'artifact_files'):
        counts[group] = len(doc.get(group,{}))
        for relative, expected in doc.get(group,{}).items():
            path = (ROOT / relative).resolve()
            name = path.relative_to(ROOT.resolve()).as_posix()
            raw = path.read_bytes()
            require(sha(raw) == expected, 'Changed receipt input: ' + name)
            require(name not in sources, 'Duplicate receipt input: ' + name)
            sources[name] = raw
    sources[receipt.relative_to(ROOT).as_posix()] = receipt.read_bytes()
    for suffix in ('independent-audit', 'input-verification'):
        path = ROOT / f'work/analysis/build-{args.version}-{suffix}.json'
        sources[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    sources['SNAPSHOT-NOTE.txt'] = (
        'Receipt-listed translation, glossary and Python files frozen at build time.\n'
        'Includes the receipt and final audits. This is not a standalone build kit: '
        'the clean disc, donor assets, font, dependency runtime and other external '
        'inputs are not bundled. No ISO or original game archives are included.\n').encode('utf-8')
    out = ROOT / f'work/output/SRW Z Special Disc English v{args.version}.inputs.zip'
    require(not out.exists(), 'Refusing to overwrite an existing snapshot')
    print(json.dumps(dict(version=args.version, input_counts=counts, archive_entries=len(sources),
                          uncompressed_bytes=sum(map(len, sources.values())),
                          largest=sorted(((len(v), k) for k, v in sources.items()), reverse=True)[:5]), indent=2))
    if not args.write:
        print('DRY RUN: no files written')
        return
    with zipfile.ZipFile(out, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, raw in sources.items():
            archive.writestr(name, raw)
    with zipfile.ZipFile(out) as archive:
        require(set(archive.namelist()) == set(sources), 'Snapshot inventory mismatch')
        require(all(archive.read(name) == raw for name, raw in sources.items()), 'Snapshot readback mismatch')
    print(json.dumps(dict(snapshot=str(out), bytes=out.stat().st_size,
                          sha256=sha(out.read_bytes()), every_entry_read_back=True), indent=2))


if __name__ == '__main__':
    main()
