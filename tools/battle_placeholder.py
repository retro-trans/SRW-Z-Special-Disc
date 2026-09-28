"""Recheck the evidence for preserving the hidden native production caption."""
import json
import struct
from sp_disc import ROOT, Disc, SOURCE, EXE, sha, require
from battle_format import unique_sources, BIN_SHA, SEG_SHA

AUDIT=ROOT/'work/analysis/battle-placeholder-444-audit.json'
AUDIT_SHA='3ee57767ce928e88808a9ee93f833db7e39247e940d538dbf850ef2806bc0c08'


def verify(exe=None):
    raw=AUDIT.read_bytes();require(sha(raw)==AUDIT_SHA,'Placeholder audit changed')
    report=json.loads(raw);clean=Disc(SOURCE).read(EXE)
    require(sha(clean)==report['source_exe_sha256'] and report['source_bin_sha256']==BIN_SHA
            and report['source_seg_sha256']==SEG_SHA,'Placeholder native sources changed')
    source=unique_sources()[444]
    require(source['source_sha256']==report['source_identity_sha256']
            and len(source['occurrences'])==382, 'Placeholder native identity')
    observed=[(r['block'],r['record'],r['metadata'],r['raw_sha256']) for r in source['occurrences']]
    expected=[(r['block'],r['record'],int(r['metadata'],16),r['raw_sha256']) for r in report['occurrences']]
    require(observed==expected and all(r[2]&65535==0 for r in observed),'Placeholder zero-halfword predicate')
    target=clean if exe is None else exe
    for address,word in report['guarded_instructions'].items():
        require(struct.unpack_from('<I',target,int(address,16)-0xff680)[0]==int(word,16),
                'Placeholder suppression instruction changed '+address)
    return dict(id=444,status='Statically suppressed in the verified native caption pipeline',
        native_occurrences=382,action='Retain original bytes and metadata; do not install production-note text',
        audit_file=str(AUDIT.relative_to(ROOT)),audit_sha256=AUDIT_SHA,
        limitation='Does not prove prior-caption clearing, timing, or absence of every computed indirect path; emulator pending')
