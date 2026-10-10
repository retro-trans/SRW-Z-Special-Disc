"""v0.3.17 component: Back Log ASCII conversion + Fedayeen weapon names.

* Executable: backlog_runtime.apply (six guarded instruction words).
* COMPDATA: the two Gabthley weapon-name fields (native フェダーイン・ライフル and
  its 連射 variant) change Fedain -> Fedayeen in place. Each field keeps its
  native capacity (24 and 32 bytes) with zero fill; every other decoded byte
  must equal the base COMPDATA. Bound to the native source hash recorded in
  work/translation/en/compdata.json.
"""
import json
from sp_disc import ROOT, SOURCE, EXE, Disc, decode, banlz, require, sha
from backlog_runtime import apply as apply_backlog

COMP = 'DATA/COMPDATA.BN'
FIELDS = {'text/7e280': 'Fedayeen Rifle', 'text/7e2a0': 'Fedayeen Rifle (Rapid)'}


def build(disc):
    exe = disc.read(EXE)
    new_exe, backlog = apply_backlog(exe)
    raw = disc.read(COMP)
    plain, _ = decode(raw)
    native, _ = decode(Disc(SOURCE).read(COMP))
    rows = {r['id']: r for r in json.loads((ROOT/'work/translation/en/compdata.json').read_text(encoding='utf-8'))}
    out, entries = bytearray(plain), []
    for ident, text in FIELDS.items():
        r = rows[ident]
        at, cap = r['offset'], r['capacity']
        require(r['text'] == text, 'Translation file not updated for '+ident)
        src = native[at:at+cap]
        require(sha(src) == r['source_sha256'] or sha(src.split(b'\0')[0]) == r['source_sha256'], 'Native source drift '+ident)
        old = plain[at:at+cap]
        require(old.split(b'\0')[0] in (text.replace('Fedayeen', 'Fedain').encode(), text.encode()),
                'Unexpected base text '+ident)
        enc = text.encode('ascii')
        require(len(enc)+1 <= cap, 'Capacity '+ident)
        out[at:at+cap] = enc+bytes(cap-len(enc))
        entries.append(dict(id=ident, offset=at, capacity=cap, before=old.split(b'\0')[0].decode(), after=text))
    changed = [i for i in range(len(plain)) if out[i] != plain[i]]
    spans = [(r['offset'], r['offset']+r['capacity']) for r in entries]
    require(all(any(a <= i < b for a, b in spans) for i in changed), 'COMPDATA change outside the two fields')
    flags = banlz.parse_header(raw)[1]
    packed = banlz.compress_record(bytes(out), flags=flags)
    require(decode(packed)[0] == bytes(out), 'COMPDATA compression readback')
    members = {EXE: new_exe, COMP: packed}
    report = dict(backlog=backlog, fedayeen=entries, compdata_decoded_sha256=sha(bytes(out)),
                  compdata_bytes=[len(raw), len(packed)])
    return members, report
