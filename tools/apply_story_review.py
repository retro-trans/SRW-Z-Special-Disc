"""Merge independent meaning-review changes into reviewed story slices.

Drafts in work/translation/en/story/ stay immutable. For each slice with a
review file in work/translation/en/story_review/, writes
work/translation/en/story_reviewed/<slice>.json with the corrected rows and
the SHA-256 of both inputs. A change is rejected (and the run fails) when its
`was` differs from the draft `en`, its id is unknown, or the result breaks
the placeholder/{tm}/ASCII contract. Name/glossary spelling runs AFTER this.

  python -B tools/apply_story_review.py            dry run: counts + samples
  python -B tools/apply_story_review.py --write
"""
import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sp_disc import ROOT, require

EN = ROOT/'work/translation/en'
CACHE = ROOT/'work/cache/story'
CODES = re.compile(r'\$[nfFlc]')
TM = '＜ｔｍ＞'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def valid(text, jp):
    return (all(0x20 <= ord(c) <= 0x7e for c in text) and text.strip()
            and Counter(CODES.findall(text)) == Counter(CODES.findall(jp))
            and text.count('{tm}') == jp.count(TM))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    source = {r['id']: r['jp'].split('\n', 1)[1] for r in
              json.loads((CACHE/'source.json').read_text(encoding='utf-8'))['rows']}
    results, samples, missing = {}, [], []
    for s in json.loads((CACHE/'slices.json').read_text(encoding='utf-8')):
        draft_path, review_path = EN/'story'/(s['name']+'.json'), EN/'story_review'/(s['name']+'.json')
        if not review_path.exists():
            missing.append(s['name'])
            continue
        draft, review = (json.loads(p.read_text(encoding='utf-8')) for p in (draft_path, review_path))
        require(review.get('rows_examined') == review.get('rows_in_slice') == len(draft['rows']),
                'Incomplete review '+s['name'])
        rows = {r['id']: dict(r) for r in draft['rows']}
        seen = set()
        for c in review.get('changes', []):
            rid = c.get('id')
            require(rid in rows and rid not in seen, 'Unknown/duplicate change %s in %s' % (rid, s['name']))
            seen.add(rid)
            require(c.get('was') == rows[rid]['en'], 'Stale change %s: was does not match draft' % rid)
            row = rows[rid]
            row['en'] = c['en']
            if 'compact' in c:
                row['compact'] = c['compact']
            row['review'] = c.get('why', '')
            for k in ('en', 'compact'):
                if row.get(k) is not None:
                    require(valid(row[k], source[rid]), 'Invalid %s after review %s: %r' % (k, rid, row[k]))
            if len(samples) < 12:
                samples.append((rid, c['was'], c['en'], c.get('why', '')))
        results[s['name']] = dict(slice=s['name'], draft_sha256=sha(draft_path), review_sha256=sha(review_path),
                                  changed=len(seen), rows=[rows[r['id']] for r in draft['rows']])
    print('reviewed slices %d, pending %d, changed rows %d'
          % (len(results), len(missing), sum(v['changed'] for v in results.values())))
    for rid, was, en, why in samples:
        print('-', rid, '|', was[:70], '\n  ->', en[:70], '\n  why:', why[:100])
    if args.write:
        out = EN/'story_reviewed'
        out.mkdir(exist_ok=True)
        for name, data in results.items():
            (out/(name+'.json')).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
        print('wrote', len(results), 'slices to', out)


if __name__ == '__main__':
    main()
