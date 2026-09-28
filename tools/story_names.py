"""Apply glossary spellings to reviewed story dialogue (runs after meaning review).

Reads work/translation/en/story_reviewed/, applies english.json reviewed
spelling corrections and the source-scoped rules in
work/glossary/story-name-rules.json (a rule fires only when the native row
contains its `requires` text), then writes work/translation/en/story_final/.
Reviewed files stay immutable. Every change is listed in the dry run.

  python -B tools/story_names.py            dry run: every change
  python -B tools/story_names.py --write
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sp_disc import ROOT, require
from glossary_terms import canonicalize

EN = ROOT/'work/translation/en'
RULES = ROOT/'work/glossary/story-name-rules.json'


def apply_rules(text, jp, row_id=None, rules=None):
    """Reviewed spelling corrections plus source-scoped rules for one text."""
    rules = rules if rules is not None else json.loads(RULES.read_text(encoding='utf-8'))['rules']
    text = canonicalize(text)
    for r in rules:
        need = r['requires'] if isinstance(r['requires'], list) else [r['requires']]
        if 'ids' in r and row_id not in r['ids']:
            continue
        if all(n in jp for n in need):
            text = re.sub(r['pattern'], r['english'], text)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    source = {r['id']: r['jp'] for r in json.loads((ROOT/'work/cache/story/source.json').read_text(encoding='utf-8'))['rows']}
    rules = json.loads(RULES.read_text(encoding='utf-8'))['rules']
    out, changes = {}, []
    for path in sorted((EN/'story_reviewed').glob('c*.json')):
        data = json.loads(path.read_text(encoding='utf-8'))
        for row in data['rows']:
            jp = source[row['id']]
            for field in ('en', 'compact'):
                old = row.get(field)
                if old is None:
                    continue
                new = canonicalize(old)
                for r in rules:
                    need = r['requires'] if isinstance(r['requires'], list) else [r['requires']]
                    if 'ids' in r and row['id'] not in r['ids']:
                        continue
                    if all(n in jp for n in need):
                        new = re.sub(r['pattern'], r['english'], new)
                if new != old:
                    require(all(0x20 <= ord(c) <= 0x7e for c in new), 'Non-ASCII after names '+row['id'])
                    changes.append((row['id'], field, old, new))
                    row[field] = new
        data['names_rules'] = RULES.name
        out[path.name] = data
    print('rows changed by name pass: %d' % len(changes))
    for rid, field, old, new in changes:
        print('-', rid, field, '|', old[:90], '\n   ->', new[:90])
    if args.write:
        (EN/'story_final').mkdir(exist_ok=True)
        for name, data in out.items():
            (EN/'story_final'/name).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
        print('wrote', len(out), 'slices to', EN/'story_final')


if __name__ == '__main__':
    main()
