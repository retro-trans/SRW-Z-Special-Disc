"""Story dialogue layout and per-chunk byte budget (shared by compiler and checks).

Wraps reviewed English (work/translation/en/story_final/) to the dialogue box
using the installed English font advances, adds the speaker line and native
「」/（） wrapper, and measures each chunk's need against the byte span its
native Japanese strings occupied. Strings must stay inside the original
record (main-game finding: text past the Japanese record end renders blank
or crashes), so the span of the native strings is the whole budget.

Layout contract (main SRW Z English format): speaker line, then up to three
body lines, the first opened by 「 and the last closed by 」, no indentation
on continuation lines. Line limit LIMIT units; the full-width quote marks
count 24 units. Width model: installed 69-glyph table (+2 spacing), space 13,
anything else 24 (native full-width).

  python -B tools/story_layout.py            report
  python -B tools/story_layout.py --write    also save work/analysis/story-layout.json
"""
import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sp_disc import ROOT
from library_text import CHARS
from inspect_english_runtime import CAVE, CAVE_FILE

LIMIT = 480
MAX_LINES = 3
EN = ROOT/'work/translation/en'
CACHE = ROOT/'work/cache/story'
_W = (ROOT/'work/cache/english-runtime/english.elf').read_bytes()[CAVE_FILE+0x78b960-CAVE:CAVE_FILE+0x78b960-CAVE+69]


def px(s):
    return sum(_W[CHARS.index(ord(c))]+2 if ord(c) in CHARS else 13 if c == ' ' else 24 for c in s)


def wrap(text, opener, closer):
    """Greedy word wrap; returns lines including the wrapper marks."""
    words, lines, line = text.split(), [], ''
    for w in words:
        cand = (line+' '+w).strip()
        head = opener if not lines else ''
        if line and px(head+cand+closer) > LIMIT:
            lines.append(line)
            line = w
        else:
            line = cand
    lines.append(line)
    lines[0] = opener+lines[0]
    lines[-1] = lines[-1]+closer
    return lines


def load():
    source = json.loads((CACHE/'source.json').read_text(encoding='utf-8'))['rows']
    speakers = json.loads((EN/'story_speakers.json').read_text(encoding='utf-8'))['speakers']
    final = {}
    for f in (EN/'story_final').glob('c*.json'):
        for r in json.loads(f.read_text(encoding='utf-8'))['rows']:
            final[r['id']] = dict(r)
    # Reviewed fit variants from the compaction pass (only when `was` still matches)
    for f in (EN/'story_compact').glob('c*.json'):
        for r in json.loads(f.read_text(encoding='utf-8')).get('rows', []):
            row = final.get(r.get('id'))
            if row and r.get('was') == row['en'] and r.get('fit'):
                row['fit'] = r['fit']
    # fits added by a fit reviewer (for rows that had none), bound the same way
    for f in (EN/'story_compact_review').glob('c*.json'):
        for r in json.loads(f.read_text(encoding='utf-8')).get('new_fits', []):
            row = final.get(r.get('id'))
            if row and r.get('was') == row['en'] and r.get('fit') and 'fit' not in row:
                row['fit'] = r['fit']
    apply_fit_reviews(final)
    # fits are written after the name pass: run the same spelling/rank rules on them
    from story_names import apply_rules, RULES
    rules = json.loads(RULES.read_text(encoding='utf-8'))['rules']
    jp = {r['id']: r['jp'] for r in source}
    for rid, row in final.items():
        if row.get('fit'):
            row['fit'] = apply_rules(row['fit'], jp[rid], rid, rules)
    import re
    for row in final.values():
        for key in ('en', 'fit'):
            if row.get(key):
                row[key] = re.sub(r'(?<![A-Za-z])Hundred\s+Demon\s+Empire(?![A-Za-z])',
                                  'Hyakki Empire', row[key])
    return source, speakers, final


def fit_reviews():
    """Independent fit-review corrections, keyed by id; applied only over the exact fit they reviewed."""
    out = {}
    for f in (EN/'story_compact_review').glob('c*.json'):
        for c in json.loads(f.read_text(encoding='utf-8')).get('changes', []):
            out[c['id']] = c
    return out


def apply_fit_reviews(rows):
    for rid, c in fit_reviews().items():
        row = rows.get(rid)
        if row is not None and row.get('fit') == c.get('was_fit') and c.get('fit'):
            row['fit'] = c['fit']


def layout_row(row, speakers, tr):
    """Return (string, lines, variant) for one dialogue row; variant is en/compact/overflow."""
    speaker, body = row['jp'].split('\n', 1)
    opener, closer = ('（', '）') if body[0] == '（' else ('「', '」')
    text, variant = tr['en'], 'overflow'
    # a reviewed `fit` is written for the chunk byte budget as well as the
    # 3-line limit, so it wins whenever it exists and fits
    for name in ('fit', 'en', 'compact'):
        candidate = tr.get(name)
        # {tm} expands to a runtime number: reserve three full-width cells
        if candidate and len(wrap(candidate.replace('{tm}', '　'*3), opener, closer)) <= MAX_LINES:
            text, variant = candidate, name
            break
    lines = wrap(text, opener, closer)
    return speakers[speaker]+'\n'+'\n'.join(lines), lines, variant


def report():
    source, speakers, final = load()
    chunks, overflow = {}, []
    for row in source:
        s, lines, variant = layout_row(row, speakers, final[row['id']])
        c = chunks.setdefault(row['chunk'], dict(capacity=0, strings=set(), rows=0))
        c['capacity'] += row['slot']
        c['strings'].add(s)
        c['rows'] += 1
        if variant == 'overflow':
            overflow.append(dict(id=row['id'], lines=len(lines), widths=[px(l) for l in lines]))
    out = {}
    for k, c in sorted(chunks.items()):
        need = sum(len(s.encode('cp932'))+1 for s in c['strings'])
        out[k] = dict(rows=c['rows'], dialogue_capacity=c['capacity'], dialogue_need=need)
    return out, overflow


def _span(data, off):
    k = data.index(bytes(1), off)
    while k < len(data) and data[k] == 0:
        k += 1
    return k-off


def budget(prefer_fit=True):
    """Per-chunk bytes: capacity = every native text string span; need = new strings (deduplicated)."""
    source, speakers, final = load()
    if not prefer_fit:
        for r in final.values():
            r.pop('fit', None)
    extra = json.loads((CACHE/'extra.json').read_text(encoding='utf-8'))['rows']
    tr = {}
    for f in (EN/'story_extra_reviewed').glob('*.json'):
        for r in json.loads(f.read_text(encoding='utf-8'))['rows']:
            tr[r['id']] = r
    inv = json.loads((ROOT/'work/ui/mission-conditions/native-inventory.json').read_text(encoding='utf-8'))
    pooled = {(o['chunk'], o['pointer_site']) for e in inv['entries'] if e['source'] != '？？？' for o in e['occurrences']}
    fits = {}
    for f in (EN/'story_compact').glob('c*.json'):
        for r in json.loads(f.read_text(encoding='utf-8')).get('rows', []):
            if r.get('id', '').startswith('x_') and r.get('fit') and tr.get(r['id'], {}).get('en') == r.get('was'):
                fits[r['id']] = r['fit']
    for rid, c in fit_reviews().items():
        if fits.get(rid) == c.get('was_fit') and c.get('fit'):
            fits[rid] = c['fit']
    cap, strs, data = {}, {}, {}
    for r in source:
        c = r['chunk']
        cap[c] = cap.get(c, 0)+r['slot']
        strs.setdefault(c, set()).add(layout_row(r, speakers, final[r['id']])[0])
    for e in extra:
        for o in e['occurrences']:
            c = o['chunk']
            d = data.setdefault(c, (CACHE/'chunks'/('%02d.bin' % c)).read_bytes())
            cap[c] = cap.get(c, 0)+_span(d, o['offset'])
            if all((c, p) in pooled for p in o['pointer_sites']):
                continue
            if e['kind'] == 'label':
                strs.setdefault(c, set()).add(e['jp'])
            elif e['kind'] == 'caption':
                strs.setdefault(c, set()).add(chr(0x3000)+chr(10)+' '*20+'\uff5e'+tr[e['id']]['en']+'\uff5e')
            else:
                strs.setdefault(c, set()).add(fits.get(e['id'], tr[e['id']]['en'])+'  ')
    return {c: dict(capacity=cap[c], need=sum(len(s.encode('cp932'))+1 for s in strs.get(c, ()))) for c in cap}


def compiler_budget(chunk):
    """Exact budget from compile_story on the newest verified build's STAGE (None if unavailable)."""
    try:
        import struct
        import compile_story
        from build_story import latest_base
        from sp_disc import Disc, SOURCE, decode
        base = Disc(latest_base(), True)
        stage, hb = base.read('DATA/STAGE.BIN'), base.read('HEDBDY/HB.BIN')
        offs = struct.unpack_from('<69I', hb, 0x5170)
        noffs = struct.unpack_from('<69I', Disc(SOURCE).read('HEDBDY/HB.BIN'), 0x5170)
        native = decode(Disc(SOURCE).read('DATA/STAGE.BIN')[noffs[chunk]:noffs[chunk+1]])[0]
        staged = decode(stage[offs[chunk]:offs[chunk+1]])[0]
        _, rep = compile_story.compile_chunk(chunk, native, staged, compile_story.targets())
        return dict(need=rep['need'], capacity=rep['capacity'])
    except Exception as e:                    # fall back to the estimate
        print('(compiler budget unavailable: %s; showing estimate)' % e)
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--measure', help='wrap one body text and print its lines and widths')
    ap.add_argument('--thought', action='store_true', help='with --measure: （） wrapper')
    ap.add_argument('--chunk', type=int, help='print one chunk byte budget and its rows still over 3 lines')
    args = ap.parse_args()
    if args.measure:
        o, c = ('（', '）') if args.thought else ('「', '」')
        lines = wrap(args.measure, o, c)
        for l in lines:
            print('%4d  %s' % (px(l), l))
        print('lines: %d (max %d, limit %d units each)' % (len(lines), MAX_LINES, LIMIT))
        return
    if args.chunk is not None:
        b = compiler_budget(args.chunk) or budget()[args.chunk]
        print('chunk %d: need %d, capacity %d, %s %d bytes' % (args.chunk, b['need'], b['capacity'],
              'OVER by' if b['need'] > b['capacity'] else 'spare', abs(b['need']-b['capacity'])))
        _, overflow = report()
        print('rows still over 3 lines:', [o['id'] for o in overflow if o['id'].startswith('c%02d_' % args.chunk)])
        return
    chunks, overflow = report()
    over = {k: v for k, v in chunks.items() if v['dialogue_need'] > v['dialogue_capacity']}
    print('rows needing a 4th line even with compact: %d' % len(overflow))
    print('chunks whose dialogue alone exceeds its dialogue span: %d' % len(over))
    for k, v in over.items():
        print('  chunk %d need %d cap %d (+%d)' % (k, v['dialogue_need'], v['dialogue_capacity'], v['dialogue_need']-v['dialogue_capacity']))
    if args.write:
        (ROOT/'work/analysis/story-layout.json').write_text(json.dumps(dict(limit=LIMIT, max_lines=MAX_LINES, chunks=chunks, overflow=overflow), indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
