"""Export Special Disc story dialogue (STAGE chunks 1-67) for translation.

Read-only against the clean source image. Japanese source rows go to the
Git-ignored cache (work/cache/story/); only English targets belong in
work/translation/en/story/. Every row is bound to its chunk, native offset,
source SHA-256 and the absolute pointer words (base 0x8045F0) that reach it.

Dialogue row shape: line 1 speaker, then body lines opened by 「 (speech) or
（ (thought). Other referenced Japanese strings are exported as `other` for a
later non-story/story audit; they are not sliced for dialogue agents.

Usage:
  python -B tools/extract_story.py            dry run: counts and samples
  python -B tools/extract_story.py --write    write cache export and slices
"""
import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from sp_disc import ROOT, SOURCE, Disc, decode, require, sha

BASE = 0x8045F0
HB_TABLE = 0x5170
CHUNKS = 68
SLICE = 80
CACHE = ROOT/'work/cache/story'
JP = re.compile('[぀-ヿ一-鿿！-～]')
OPEN = ('「', '（')  # 「 （


def chunks():
    disc = Disc(SOURCE)
    raw = disc.read('DATA/STAGE.BIN')
    offs = struct.unpack_from('<%dI' % (CHUNKS+1), disc.read('HEDBDY/HB.BIN'), HB_TABLE)
    require(offs[0] == 0 and list(offs) == sorted(offs) and offs[-1] <= len(raw), 'STAGE chunk table')
    for i in range(CHUNKS):
        yield i, decode(raw[offs[i]:offs[i+1]])[0]


def pointer_map(data):
    refs = {}
    for at in range(0, len(data)-3, 4):
        v = struct.unpack_from('<I', data, at)[0]-BASE
        if 0 <= v < len(data):
            refs.setdefault(v, []).append(at)
    return refs


def strings(data, refs):
    for off in sorted(refs):
        if off and data[off-1] != 0:
            continue
        end = data.find(b'\0', off)
        raw = data[off:end]
        if len(raw) < 2:
            continue
        try:
            text = raw.decode('cp932')
            if text.encode('cp932') != raw:
                continue
        except UnicodeError:
            continue
        if not JP.search(text):
            continue
        slot = end
        while slot < len(data) and data[slot] == 0:
            slot += 1
        yield off, raw, text, slot-off


def classify(text):
    lines = text.split('\n')
    if len(lines) >= 2 and lines[1][:1] in OPEN:
        return 'dialogue'
    return 'other'


def export():
    rows, other = [], []
    for chunk, data in chunks():
        if chunk == 0:
            continue  # Scenario Chart overlay, translated separately
        refs = pointer_map(data)
        for off, raw, text, slot in strings(data, refs):
            row = dict(id='c%02d_%05x' % (chunk, off), chunk=chunk, offset=off, slot=slot,
                       pointer_sites=refs[off], source_sha256=sha(raw), jp=text)
            (rows if classify(text) == 'dialogue' else other).append(row)
    return rows, other


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    rows, other = export()
    speakers = sorted({r['jp'].split('\n')[0] for r in rows})
    codes = sorted({m for r in rows for m in re.findall(r'\$[A-Za-z]|《[^》]*》', r['jp'])})
    by_chunk = {}
    for r in rows:
        by_chunk.setdefault(r['chunk'], []).append(r)
    slices = []
    for chunk, items in sorted(by_chunk.items()):
        for n in range(0, len(items), SLICE):
            part = items[n:n+SLICE]
            slices.append(dict(name='c%02d_%03d' % (chunk, n//SLICE), chunk=chunk,
                               rows=[dict(id=r['id'], jp=r['jp']) for r in part]))
    multi = sum(1 for r in rows if len(r['pointer_sites']) != 1)
    print('dialogue rows %d, other strings %d, speakers %d, slices %d, rows with !=1 pointer %d'
          % (len(rows), len(other), len(speakers), len(slices), multi))
    print('chunks:', {k: len(v) for k, v in sorted(by_chunk.items())})
    print('codes:', codes[:40])
    if not args.write:
        for r in rows[:3]+other[:5]:
            print(json.dumps({k: r[k] for k in ('id', 'slot', 'pointer_sites', 'jp')}, ensure_ascii=False))
        return
    (CACHE/'slices').mkdir(parents=True, exist_ok=True)
    dump = lambda p, o: p.write_text(json.dumps(o, ensure_ascii=False, indent=1), encoding='utf-8')
    dump(CACHE/'source.json', dict(base=hex(BASE), rows=rows))
    dump(CACHE/'other.json', dict(base=hex(BASE), rows=other))
    dump(CACHE/'speakers.json', speakers)
    for s in slices:
        dump(CACHE/'slices'/(s['name']+'.json'), s)
    dump(CACHE/'slices.json', [dict(name=s['name'], chunk=s['chunk'], rows=len(s['rows'])) for s in slices])
    print('wrote', CACHE)


if __name__ == '__main__':
    main()
