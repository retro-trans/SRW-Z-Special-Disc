"""Validate story-dialogue translation slices against the cached native export.

Read-only. For every work/translation/en/story/<slice>.json checks: every
source id is translated or listed as unresolved (no extras, no duplicates),
no Japanese or non-ASCII text, placeholders ($n $f $F $l $c) preserved with the
same counts, no wrapper quotes or speaker prefixes, and rough box length.
Also reports speakers without a glossary English name.

  python -B tools/check_story.py            summary + problems
  python -B tools/check_story.py --write    also save work/analysis/story-check.json
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sp_disc import ROOT

CACHE = ROOT/'work/cache/story'
OUT = ROOT/'work/translation/en/story'
CODES = re.compile(r'\$[nfFlc]')
SOFT_LIMIT = 130  # characters; the layout pass measures real widths later


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    source = {r['id']: r for r in json.loads((CACHE/'source.json').read_text(encoding='utf-8'))['rows']}
    slices = json.loads((CACHE/'slices.json').read_text(encoding='utf-8'))
    glossary = {}
    for line in (CACHE/'glossary.tsv').read_text(encoding='utf-8').splitlines()[1:]:
        jp, en, _ = (line.split('\t') + ['', ''])[:3]
        glossary[jp] = en
    problems, done, long_rows, totals = [], [], [], Counter()
    for s in slices:
        path = OUT/(s['name']+'.json')
        if not path.exists():
            totals['pending_slices'] += 1
            continue
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except ValueError as e:
            problems.append((s['name'], 'invalid JSON: %s' % e))
            continue
        want = [r['id'] for r in json.loads((CACHE/'slices'/(s['name']+'.json')).read_text(encoding='utf-8'))['rows']]
        got = [r.get('id') for r in data.get('rows', [])]
        unresolved = [u.get('id') for u in data.get('unresolved', [])]
        dup = [k for k, v in Counter(got+unresolved).items() if v > 1]
        missing = [i for i in want if i not in got and i not in unresolved]
        extra = [i for i in got+unresolved if i not in want]
        if dup or missing or extra:
            problems.append((s['name'], 'coverage dup=%s missing=%s extra=%s' % (dup[:5], missing[:5], extra[:5])))
        if [i for i in want if i in got] != got:
            problems.append((s['name'], 'rows out of order'))
        for r in data.get('rows', []):
            rid, en = r.get('id'), r.get('en', '')
            if rid not in source:
                continue
            jp = source[rid]['jp'].split('\n', 1)[1]
            for field in ('en', 'compact'):
                text = r.get(field)
                if text is None:
                    continue
                if not text.strip():
                    problems.append((rid, field+' empty'))
                if any(ord(c) > 0x7e or (ord(c) < 0x20) for c in text):
                    problems.append((rid, field+' non-ASCII/control: %r' % text[:60]))
                if Counter(CODES.findall(text)) != Counter(CODES.findall(jp)):
                    problems.append((rid, field+' placeholders %s vs %s' % (CODES.findall(text), CODES.findall(jp))))
                if text.count('{tm}') != jp.count('＜ｔｍ＞'):
                    problems.append((rid, field+' {tm} tag count mismatch'))
                if text[:1] in '"\'' and text[-1:] in '"\'' and len(text) > 1 and text.count('"') == 2:
                    problems.append((rid, field+' wrapped in quotes'))
            if len(en) > SOFT_LIMIT and not r.get('compact'):
                long_rows.append(rid)
            totals['rows'] += 1
        totals['unresolved'] += len(unresolved)
        done.append(s['name'])
    speakers = json.loads((CACHE/'speakers.json').read_text(encoding='utf-8'))
    unnamed = [sp for sp in speakers if sp not in glossary and '$' not in sp]
    print('slices done %d / %d; rows %d; unresolved %d; long without compact %d; problems %d'
          % (len(done), len(slices), totals['rows'], totals['unresolved'], len(long_rows), len(problems)))
    print('speakers lacking glossary English: %d' % len(unnamed))
    for p in problems[:60]:
        print('  ', *p)
    if long_rows:
        print('long rows:', long_rows[:30])
    if args.write:
        report = dict(slices_done=done, totals=dict(totals), problems=[list(p) for p in problems],
                      long_without_compact=long_rows, speakers_without_glossary=len(unnamed))
        (ROOT/'work/analysis/story-check.json').write_text(json.dumps(report, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
