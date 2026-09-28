"""Read back panel code, pooled helpers and all introduction rows from the ISO."""
import json
import struct
from sp_disc import ROOT, VT1, require, sha, source_records, decode
from library_text import text, encode
from save_summary_text import width
from glossary_terms import canonicalize
from align_story_panels import (BASE, MARGINS, STATUS_CALLS, CENTER_CALLS,
                               LEFT, STATUS_X, APPEND, MEASURE, QUESTIONS,
                               actual_width, status_code, center_code)


def audit(disc, exe, loaded, report):
    native=(ROOT/'work/cache/english-runtime/special.elf').read_bytes()
    require(report['source_executable_sha256']==sha(native),'Panel source binding')
    helpers={r['kind']:r for r in report['helpers']}
    strings=report['strings']
    require([r['text'] for r in strings]==['CLEAR!','---']+list(QUESTIONS),'Panel string inventory')
    for row in strings:
        expected=encode(row['text'])+b'\0';at=loaded(row['address'])
        require(exe[at:at+len(expected)]==expected==bytes.fromhex(row['bytes_hex']),'Panel pooled string')
    expected_code={'status':status_code(strings[0]['address'],strings[1]['address']),
                   'center':center_code([r['address']for r in strings[2:]])}
    for kind,payload in expected_code.items():
        row=helpers[kind];at=loaded(row['address'])
        require(exe[at:at+len(payload)]==payload==bytes.fromhex(row['payload_hex'])
                and sha(payload)==row['sha256'],'Panel helper code readback')
    expected={va:0x24060000|(LEFT&65535) for va in MARGINS}
    expected.update({va:0x0C000000|helpers['status']['address']>>2 for va in STATUS_CALLS})
    expected.update({va:0x0C000000|helpers['center']['address']>>2 for va in CENTER_CALLS})
    require({r['address']for r in report['patches']}==set(expected),'Panel patch inventory')
    for va,word in expected.items():
        at=va-BASE
        require(struct.unpack_from('<I',exe,at)[0]==word,'Panel patched instruction')
        require(exe[at+4:at+8]==native[at+4:at+8],'Panel delay slot changed')
    # Preserve the native caller modes, append routine and the shared global
    # text measurement function; the correction applies only at scoped calls.
    for lo,hi in ((0x37D8B0,0x37D9EC),(0x4378C0,0x437900)):
        require(exe[lo-BASE:hi-BASE]==native[lo-BASE:hi-BASE],'Panel behavior outside alignment changed')
    _,_,source_archive,offsets=source_records();archive=disc.read(VT1)
    lo,hi=offsets[40:42];raw=decode(archive[lo:hi])[0]
    require(len(raw)==3078,'Introduction grid size')
    rows=raw.splitlines(keepends=True)
    require(len(rows)==54 and all(len(r)==57 and r[-1:]==b'\n'for r in rows),'Introduction grid stride')
    target=json.loads((ROOT/'work/translation/en/briefings.json').read_text(encoding='utf-8'))['intro']
    previous=json.loads((ROOT/'work/analysis/build-0.2.14-briefings.json').read_text(encoding='utf-8'))
    prior_intros={p['id']:p for p in previous['pages']if p['id'].startswith('40/')}
    maximum=0
    for i,item in enumerate(target):
        page=[text(r[:56].split(b'\0',1)[0])for r in rows[i*9:(i+1)*9]]
        require(page[0]==item['title'] and page[-1]==item['question'],'Panel title/question changed')
        words=' '.join(page[1:8]).split()
        require(words==canonicalize(item['text']).split(),'Introduction words lost or changed')
        require(words==' '.join(prior_intros['40/'+str(i)]['lines'][1:8]).split(),
                'Introduction wording differs from previous release')
        require(all(width(line)<=500 for line in page),'Introduction exceeds corrected limit')
        maximum=max(maximum,*map(width,page))
    lo,hi=offsets[50:52]
    challenge=decode(archive[lo:hi])[0].splitlines()
    prior=[r for r in previous['pages']if r['id'].startswith('50/')]
    require([text(r.split(b'\0',1)[0])for r in challenge]==[line for p in prior for line in p['lines']],
            'Challenge panels changed during intro alignment')
    return dict(patched_instructions=len(expected),helpers_read_back=2,pooled_strings_read_back=5,
        intro_pages_read_back=6,full_intro_meanings_preserved=True,maximum_conservative_line_width=maximum,
        left_x=64,status_column_x=320+STATUS_X,question_center_x=316,
        questions=[dict(text=q,width=actual_width(q),x=316-actual_width(q)//2)for q in QUESTIONS],
        challenge_panels_unchanged=True,original_append_and_mode_logic_unchanged=True,
        runtime='pending by user choice')
