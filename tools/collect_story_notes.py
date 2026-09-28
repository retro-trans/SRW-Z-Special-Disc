"""Collect translator-reported new terms, uncertain calls and notes for review.

Read-only over work/translation/en/story/*.json. Groups new terms by English
spelling so disagreements between batches become visible.

  python -B tools/collect_story_notes.py            print summary
  python -B tools/collect_story_notes.py --write    save work/analysis/story-notes.json
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sp_disc import ROOT

STORY = ROOT/'work/translation/en/story'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    terms, calls, notes, unresolved = defaultdict(list), [], [], []
    for path in sorted(STORY.glob('c*.json')):
        data = json.loads(path.read_text(encoding='utf-8'))
        name = path.stem
        for t in data.get('new_terms', []):
            if isinstance(t, dict):
                key = (t.get('english') or '').strip()
                terms[key].append(dict(slice=name, **{k: v for k, v in t.items() if k != 'english'}))
            else:
                terms[str(t)].append(dict(slice=name))
        calls += [dict(slice=name, call=c) for c in data.get('uncertain_calls', [])]
        notes += [dict(slice=name, id=r['id'], note=r['note']) for r in data.get('rows', []) if r.get('note')]
        unresolved += [dict(slice=name, **u) for u in data.get('unresolved', [])]
    print('new terms %d distinct; uncertain calls %d; row notes %d; unresolved %d'
          % (len(terms), len(calls), len(notes), len(unresolved)))
    for k in sorted(terms, key=str.lower)[:400]:
        print('  %-40s %s' % (k[:40], ','.join(sorted({x['slice'][:3] for x in terms[k]}))))
    if args.write:
        out = dict(new_terms=terms, uncertain_calls=calls, row_notes=notes, unresolved=unresolved)
        (ROOT/'work/analysis/story-notes.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
