"""Pair native story rows with draft English for independent meaning review.

Writes Git-ignored work/cache/story/review/<slice>.json:
{slice, rows:[{id, speaker_en, jp, en, compact?, note?}]}. Read-only on
translations. Reviewers write only changed rows to
work/translation/en/story_review/<slice>.json (see STORY_REVIEW_BRIEF.md).

  python -B tools/prepare_story_review.py            dry run
  python -B tools/prepare_story_review.py --write
"""
import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sp_disc import ROOT, require

CACHE = ROOT/'work/cache/story'
EN = ROOT/'work/translation/en'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    speakers = json.loads((EN/'story_speakers.json').read_text(encoding='utf-8'))['speakers']
    out = {}
    for s in json.loads((CACHE/'slices.json').read_text(encoding='utf-8')):
        src = json.loads((CACHE/'slices'/(s['name']+'.json')).read_text(encoding='utf-8'))['rows']
        tr = {r['id']: r for r in json.loads((EN/'story'/(s['name']+'.json')).read_text(encoding='utf-8'))['rows']}
        rows = []
        for r in src:
            require(r['id'] in tr, 'Missing draft '+r['id'])
            t = tr[r['id']]
            row = dict(id=r['id'], speaker_en=speakers[r['jp'].split('\n')[0]], jp=r['jp'], en=t['en'])
            for k in ('compact', 'note'):
                if t.get(k):
                    row[k] = t[k]
            rows.append(row)
        out[s['name']] = dict(slice=s['name'], rows=rows)
    print('review slices', len(out), 'rows', sum(len(v['rows']) for v in out.values()))
    if args.write:
        (CACHE/'review').mkdir(exist_ok=True)
        for k, v in out.items():
            (CACHE/'review'/(k+'.json')).write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding='utf-8')
        print('wrote', CACHE/'review')


if __name__ == '__main__':
    main()
