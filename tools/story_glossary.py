"""Merge project glossaries into one lookup table for story-dialogue agents.

Order of authority (later wins): inherited SRW Z terms, battle/narration/
suspend supplements, english.json reviewed terms and provisional names.
English values pass through the reviewed spelling corrections. Output is a
Git-ignored cache TSV (it contains Japanese source terms): source, English,
notes (gender/position/status where researched).

  python -B tools/story_glossary.py            dry run
  python -B tools/story_glossary.py --write
"""
import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sp_disc import ROOT
from glossary_terms import canonicalize

G = ROOT/'work/glossary'
OUT = ROOT/'work/cache/story/glossary.tsv'


def load(name):
    return json.loads((G/name).read_text(encoding='utf-8'))


def note(entry):
    parts = []
    for k in ('gender', 'position', 'nickname', 'personality', 'kind', 'type'):
        v = entry.get(k)
        if v:
            parts.append('%s: %s' % (k, v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)))
    return '; '.join(parts)


def build():
    table = {}
    for jp, en in load('srw-z-terms.json')['terms'].items():
        table[jp] = [en, '']
    for name in ('battle-terms.json', 'narration-terms.json', 'battle-next-terms.json',
                 'battle-followup-terms.json', 'suspend-terms.json', 'story-terms.json'):
        for e in load(name).get('entries', []):
            for jp in (e['source'] if isinstance(e['source'], list) else [e['source']]):
                table[jp] = [e['english'], note(e)]
    for r in load('battle-spelling.json')['rules']:
        for jp in (r['native'] if isinstance(r['native'], list) else [r['native']]):
            table[jp] = [r['english'], table.get(jp, ['', ''])[1]]
    data = load('english.json')
    for e in data['terms']:
        table[e['source']] = [e['english'], note(e)]
    for jp, en in data['provisional_names']['names'].items():
        table[jp] = [en, 'provisional romanization']
    return {jp: [canonicalize(en if isinstance(en, str) else ' / '.join(en)), n] for jp, (en, n) in table.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    table = build()
    print('terms', len(table))
    for jp in list(table)[:5]:
        print(jp, table[jp])
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        lines = ['source\tenglish\tnotes'] + ['%s\t%s\t%s' % (jp, en, n.replace('\t', ' ').replace('\n', ' '))
                                              for jp, (en, n) in sorted(table.items(), key=lambda x: -len(x[0]))]
        OUT.write_text('\n'.join(lines)+'\n', encoding='utf-8')
        print('wrote', OUT)


if __name__ == '__main__':
    main()
