"""Install reviewed English story text into DATA/STAGE.BIN chunks 1-67.

Component for a STAGE archive that earlier components may already have
changed (mission-condition pointers moved to the English pool, roster names,
Bazaar slogans). For each story chunk it:

1. decodes the staged chunk and the native chunk;
2. binds every text string by its native offset and the absolute pointer
   words (base 0x8045F0) that reach it, dropping sites that sit inside a
   string span or in the header length words (0x0c/0x28/0x2c);
3. keeps strings another component already changed, drops strings whose
   every pointer now leaves the chunk (freed), and keeps labels native;
4. lays out dialogue (story_layout), captions (centred like the native
   ～place～ cards), the chunk-66 inline scene, choices and the silent row;
5. packs the deduplicated strings into the native text region only (text
   placed past the Japanese record end does not render), repoints every
   genuine pointer word, zero-fills the rest of the region;
6. proves: decoded length unchanged, every byte outside the text region and
   the repointed words identical to the staged chunk, every pointer reads
   back its intended text; then recompresses into the chunk's own slot.

A chunk that does not fit (bytes or slot) stays exactly as staged and is
reported; nothing is truncated.

Compression and archive repacking happen in build_story.py (chunks may grow
past their native compressed slots; HB.BIN's table is rewritten there).

  python -B tools/compile_story.py --stage <STAGE.BIN>     dry run report
"""
import argparse
import json
import re
import struct
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sp_disc import ROOT, SOURCE, Disc, decode, require, sha, banlz
from story_layout import load, layout_row, px, EN, CACHE

BASE = 0x8045F0
HEADER_WORDS = {0x0c, 0x28, 0x2c}
CAPTION_CENTER = 282          # native captions centre on half-width column 23.5
TM = re.compile('＜ｔｍ＞.*?＜／ｔｍ＞')


def cstr(data, off):
    return bytes(data[off:data.index(b'\x00', off)])


def span_end(data, off):
    k = data.index(b'\x00', off)
    while k < len(data) and data[k] == 0:
        k += 1
    return k


def restore_tags(en, jp):
    tags = TM.findall(jp)
    require(en.count('{tm}') == len(tags), 'tm tag count')
    for t in tags:
        en = en.replace('{tm}', t, 1)
    return en


def caption(en):
    body = '～'+en+'～'
    pad = max(0, round((CAPTION_CENTER-px(body)/2)/13))
    return '　\n'+' '*pad+body


def targets():
    """Map (chunk, native offset) -> dict(kind, text or None=keep native)."""
    source, speakers, final = load()
    out = {}
    for r in source:
        out[(r['chunk'], r['offset'])] = dict(kind='dialogue', id=r['id'],
                                              text=restore_tags(layout_row(r, speakers, final[r['id']])[0], r['jp']))
    extra = json.loads((CACHE/'extra.json').read_text(encoding='utf-8'))['rows']
    tr, fits = {}, {}
    for f in (EN/'story_extra_reviewed').glob('*.json'):
        for r in json.loads(f.read_text(encoding='utf-8'))['rows']:
            tr[r['id']] = r
    for f in (EN/'story_compact').glob('c*.json'):
        for r in json.loads(f.read_text(encoding='utf-8')).get('rows', []):
            if r.get('id', '').startswith('x_') and r.get('fit') and tr.get(r['id'], {}).get('en') == r.get('was'):
                fits[r['id']] = r['fit']
    from story_layout import fit_reviews
    for rid, c in fit_reviews().items():
        if fits.get(rid) == c.get('was_fit') and c.get('fit'):
            fits[rid] = c['fit']
    link_terms = {}
    for e in extra:
        if e['kind'] == 'label' and 66 in {o['chunk'] for o in e['occurrences']}:
            link_terms[tr[e['id']]['en']] = e['jp']
    for e in extra:
        en = fits.get(e['id'], tr[e['id']]['en'])
        if e['kind'] == 'label':
            # keyword-bank entries of the chunk-66 scene are translated with their links;
            # other labels (backgrounds, rooms, groups) stay native pending usage evidence
            text = en if (66 in {o['chunk'] for o in e['occurrences']} and en in link_terms) else None
        elif e['kind'] == 'caption':
            text = caption(en)
        elif e['kind'] == 'condition':
            text = None                     # owned by mission_conditions.py (English pool)
        elif e['kind'] == 'inline':
            speaker = tr[e['id']].get('speaker') or ''
            body = re.sub(r'\{\{([^}]*)\}\}', '《\\1》', en)
            text = speaker+'「'+body+'」'
        elif e['kind'] == 'choice':
            parts = en.split('\n')
            text = '「'+parts[0]+'」'+''.join('\n　「'+p+'」' for p in parts[1:])
        else:                               # silent dialogue row with a native speaker line
            text = e['jp'].split('\n')[0]+'\n「'+en+'」'
        for o in e['occurrences']:
            out[(o['chunk'], o['offset'])] = dict(kind=e['kind'], id=e['id'], text=text)
    return out


def compile_chunk(chunk, native, staged, plan):
    size = len(native)
    require(len(staged) == size, 'decoded size drift %d' % chunk)
    words = {}
    for at in range(0, size-3, 4):
        v = struct.unpack_from('<I', native, at)[0]-BASE
        if 0 <= v < size:
            words.setdefault(v, []).append(at)
    strings = sorted(off for (c, off) in plan if c == chunk)
    starts = set(strings)
    spans = {}
    for off in strings:
        # a string owns its NUL; trailing zeros only when they run exactly into
        # the next bound string (padding at a region's end may be a field)
        end, full = native.index(bytes(1), off)+1, span_end(native, off)
        spans[off] = (off, full if full in starts else end)
    regions = []                              # contiguous runs of native string spans
    for s0, e0 in sorted(spans.values()):
        if regions and regions[-1][1] == s0:
            regions[-1][1] = e0
        else:
            regions.append([s0, e0])
    inside = lambda at: any(s <= at < e for s, e in spans.values())
    new_text, sites, freed, kept = {}, {}, 0, 0
    for off in strings:
        p = plan[(chunk, off)]
        genuine = [at for at in words.get(off, []) if at not in HEADER_WORDS and not inside(at)]
        require(genuine, 'no pointer to %s' % p['id'])
        internal = [at for at in genuine if struct.unpack_from('<I', staged, at)[0] == BASE+off]
        if not internal:
            freed += 1
            continue                          # every reference now points elsewhere (English pool)
        if cstr(staged, off) != cstr(native, off) or p['text'] is None:
            text = cstr(staged, off)          # changed by another component, or kept native
            kept += p['text'] is None
        else:
            text = p['text'].encode('cp932')
        new_text[off] = text
        sites[off] = internal
    fill = [s0 for s0, _ in regions]          # next free byte in each region
    order, placed = {}, {}
    for off in strings:                       # script order, identical strings share one copy
        if off not in new_text:
            continue
        t = new_text[off]
        if t not in placed:
            for i, (s0, e0) in enumerate(regions):
                if fill[i]+len(t)+1 <= e0:
                    placed[t] = fill[i]
                    fill[i] += len(t)+1
                    break
            else:
                need = sum(len(x)+1 for x in set(new_text.values()))
                return None, dict(chunk=chunk, status='over', need=need,
                                  capacity=sum(e0-s0 for s0, e0 in regions), unplaced=placed.__len__())
        order[off] = placed[t]
    need = sum(f-s0 for f, (s0, _) in zip(fill, regions))
    cap = sum(e0-s0 for s0, e0 in regions)
    out = bytearray(staged)
    touched = set()
    for s0, e0 in regions:
        out[s0:e0] = bytes(e0-s0)
        touched.update(range(s0, e0))
    for t, at in placed.items():
        out[at:at+len(t)] = t
    for off, ats in sites.items():
        for at in ats:
            struct.pack_into('<I', out, at, BASE+order[off])
            touched.update(range(at, at+4))
    for i in range(size):                     # proof: nothing else changed
        if i not in touched and out[i] != staged[i]:
            raise ValueError('chunk %d byte 0x%x changed outside text/pointers' % (chunk, i))
    for off, ats in sites.items():
        for at in ats:
            require(cstr(out, struct.unpack_from('<I', out, at)[0]-BASE) == new_text[off], 'readback %d/0x%x' % (chunk, off))
    return bytes(out), dict(chunk=chunk, status='ok', need=need, capacity=cap, spare=cap-need, regions=len(regions),
                            strings=len(new_text), unique=len(placed), freed=freed, kept_native=kept)


def compile_stage(stage):
    disc = Disc(SOURCE)
    native_archive = disc.read('DATA/STAGE.BIN')
    offs = struct.unpack_from('<69I', disc.read('HEDBDY/HB.BIN'), 0x5170)
    require(len(stage) == len(native_archive), 'STAGE archive length changed')
    plan = targets()
    decoded, reports = {}, []
    for chunk in sorted({c for c, _ in plan}):
        lo, hi = offs[chunk], offs[chunk+1]
        native = decode(native_archive[lo:hi])[0]
        staged = decode(stage[lo:hi])[0]
        new, rep = compile_chunk(chunk, native, staged, plan)
        if new is not None:
            rep['decoded_sha256'] = sha(new)
            decoded[chunk] = new
        reports.append(rep)
        print(json.dumps(rep), flush=True)
    return decoded, reports


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage', required=True, help='staged DATA/STAGE.BIN to build on')
    args = ap.parse_args()
    stage = Path(args.stage).read_bytes()
    decoded, reports = compile_stage(stage)
    print('chunks that fit %d / %d' % (len(decoded), len(reports)))
    for r in reports:
        if r['status'] != 'ok':
            print('  over: chunk %d need %d capacity %d' % (r['chunk'], r['need'], r['capacity']))


if __name__ == '__main__':
    main()
