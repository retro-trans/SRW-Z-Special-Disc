"""Export the story text that extract_story.py's dialogue pass did not cover.

Read-only. Covers every pointer-referenced text string in STAGE chunks 1-67
that is not already a row of work/cache/story/source.json:
  dialogue   speaker line + 「…」/（…） rows the Japanese-script filter missed
  inline     speaker「…」 written on one line (chunk 66 demo scene)
  choice     「…選択」 choice lists
  caption    ～place～ scene captions
  condition  win/lose/mission condition and description text
  label      short names (places, units, groups, brackets)
Binary false positives (lone CJK + 0x80, private-use prefixes, half-width
kana fragments) are excluded and counted. Translation is keyed by unique
text (source_sha256); every occurrence (chunk, offset, pointer sites) is kept
for the build. Japanese stays in the ignored cache.

  python -B tools/extract_story_extra.py            dry run
  python -B tools/extract_story_extra.py --write
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sp_disc import ROOT, sha
from extract_story import chunks, pointer_map, CACHE

TEXTISH = re.compile('[　-ヿ一-鿿！-～]')
JUNK = re.compile('[\x00-\x09\x0b-\x1f\x7f-\x9f-｡-ﾟ]')


def strings(data, refs):
    for off in sorted(refs):
        if off and data[off-1] != 0:
            continue
        raw = data[off:data.find(b'\0', off)]
        if len(raw) < 2:
            continue
        try:
            text = raw.decode('cp932')
            if text.encode('cp932') != raw:
                continue
        except UnicodeError:
            continue
        if TEXTISH.search(text):
            yield off, raw, text


def kind(text):
    lines = text.split('\n')
    if JUNK.search(text) or not text.strip() or text.startswith('＃'):
        return 'junk'
    if len(lines) >= 2 and lines[1][:1] in '「（':
        return 'dialogue'
    if text.startswith('「') and '選択」' in lines[0]:
        return 'choice'
    if re.match('^[^「\n]{1,12}「', text):
        return 'inline'
    if re.search('～.*～', text):
        return 'caption'
    if '\n' in text or text.endswith('。') or len(text) > 20:
        return 'condition'
    return 'label'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    done = {(r['chunk'], r['offset']) for r in
            json.loads((CACHE/'source.json').read_text(encoding='utf-8'))['rows']}
    unique, junk = {}, Counter()
    for chunk, data in chunks():
        if chunk == 0:
            continue
        refs = pointer_map(data)
        for off, raw, text in strings(data, refs):
            if (chunk, off) in done:
                continue
            k = kind(text)
            if k == 'junk':
                junk[text] += 1
                continue
            key = sha(raw)
            entry = unique.setdefault(key, dict(id='x_'+key[:10], kind=k, source_sha256=key, jp=text, occurrences=[]))
            entry['occurrences'].append(dict(chunk=chunk, offset=off, pointer_sites=refs[off]))
    rows = sorted(unique.values(), key=lambda e: (e['kind'], e['occurrences'][0]['chunk'], e['occurrences'][0]['offset']))
    counts = Counter(e['kind'] for e in rows)
    print('unique texts %d (%s); occurrences %d; junk excluded %d unique'
          % (len(rows), dict(counts), sum(len(e['occurrences']) for e in rows), len(junk)))
    print('junk:', [j[:12] for j in list(junk)[:30]])
    if args.write:
        (CACHE/'extra.json').write_text(json.dumps(dict(rows=rows, junk=sorted(junk)), ensure_ascii=False, indent=1), encoding='utf-8')
        print('wrote', CACHE/'extra.json')


if __name__ == '__main__':
    main()
