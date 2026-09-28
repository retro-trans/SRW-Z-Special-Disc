"""Verify the native SRVC loading/display contracts; export metadata only."""
import argparse
import collections
import json
import struct
from sp_disc import ROOT,Disc,SOURCE,EXE,sha,require
from battle_format import native,normalize,unique_sources

BASE=0xff680
RANGES={
    'bank_initializer':(0x2fe610,0x2fe690,'571116e558189f5b2b6ee6eed382427f817be88b5e7fac64f098547e83ff4b50'),
    'newline_converter':(0x2f1760,0x2f1800,'d6b313ba337af3da631cd45506a0a529ba6af8e32d796b4868c0f29848a2e704'),
    'caption_draw':(0x2f20b0,0x2f2190,'1de39e12f70581d98af8e0d622e00499f19f678baf1f64411c92a959fdc540bf'),
    'caption_initializer':(0x2f2190,0x2f21e0,'08e8d3941004ac6eb5fbad16be3b33edf91cb4344ca962d8fe2623da54928057'),
    'font_dispatch':(0x2fd890,0x2fd8b0,'b7bc1bdc76869e719f4962affa1ef676585dd513323b33921753ea5e059386fd'),
    'bank_load':(0x305580,0x3056e0,'5fce53b7d2b9da0d8bfbf3b4919e4f5974a9b3a87d403dec1bce32a7d000ca3b'),
    'async_read_setup':(0x13a1f0,0x13a390,'6390812fb585719fe9d64704d79a4bc846759e4fccaf1e550e5d5b0925acf26b'),
    'allocate_and_offset':(0x139edc,0x139f30,'3521f6deaa61b2e37174c1f645c66b990747bdca89f9755ee32da31cb760d294'),
    'sector_allocation':(0x139b80,0x139bd0,'bc5f6a82b2a8a0938d730cd0af13cd9c8c4dd6b4213af777ae4daa6915a1d4b2')
}
WORDS={
    0x2f1988:0x26a402b8,0x2f198c:0x0c0bc5d8,0x2f1990:0x0200282d,
    0x2f1ba8:0x266402b8,0x2f1bac:0x0c0bc5d8,
    0x2f2120:0x260502b8,0x2f21b8:0x262402b8,0x2f21c4:0x24060060,
    0x2f1e5c:0x8ee20014,0x2f1e68:0x000318c0,0x2f1e70:0xaea20000,
    0x2f1904:0x8e430004,0x2f1940:0x8c840018,0x2f194c:0x00838021,
    0x3056a4:0x8c450000,0x3056a8:0x8c420004,0x3056ac:0x0c04e87c,0x3056b0:0x00453023,
    0x305744:0x8e420004,0x305748:0xae420014,0x305778:0x0c0bf984,
    0x2e97d8:0x0c0c363c,0x2e97dc:0x24845870,
    0x2e97f8:0x0c0c363c,0x2e97fc:0x24845870,
    0x30e120:0x24021150,0x30e12c:0x0c0c0ef4,0x30e130:0x24443a80,0x30e138:0x2a020002,
    0x303c90:0x26440420,0x303c98:0x0c0bc864
}


def inspect():
    exe=Disc(SOURCE).read(EXE)
    # Use the already pinned clean executable identity, never the patched build.
    lock=json.loads((ROOT/'work/analysis/english-runtime-map.json').read_text(encoding='utf-8'))['source_sha256']
    require(sha(exe)==lock,'Battle runtime clean executable identity')
    for name,(lo,hi,digest)in RANGES.items():require(sha(exe[lo-BASE:hi-BASE])==digest,'Runtime function drift: '+name)
    for va,value in WORDS.items():require(struct.unpack_from('<I',exe,va-BASE)[0]==value,'Runtime word drift: '+hex(va))
    _,_,_,chunks,parsed=native();stats=collections.Counter();per_block=[];tail_unbound=[]
    sources={r['source_sha256']for r in unique_sources()}
    for i,(raw,p)in enumerate(zip(chunks,parsed)):
        count=struct.unpack_from('<H',raw,6)[0];seq_count=struct.unpack_from('<H',raw,4)[0]
        seq=8+raw[1]*4;coverage=collections.Counter()
        for j in range(seq_count):
            at=seq+8*j;first=struct.unpack_from('<H',raw,at+4)[0];n=raw[at+6]
            require(first+n<=count,'SRVC sequence references outside indexed records')
            coverage.update(range(first,first+n))
        stats['sequence_rows']+=seq_count;stats['selected_record_references']+=sum(coverage.values())
        stats['unreferenced_indexed_records']+=len(set(range(count))-set(coverage))
        stats['multiply_referenced_indexed_records']+=sum(n>1 for n in coverage.values())
        stats['blocks']+=1;stats['indexed_records']+=count
        per_block.append(dict(block=i,index=p['index'],pool=p['pool'],indexed_end=p['end'],
            block_bytes=len(raw),indexed_records=count,sequences=seq_count))
        # Trailing material includes stale-looking Japanese text. Do not assume
        # it is unused, and never reinterpret it as indexed caption records.
        start=p['end']or 8;at=start
        for value in raw[start:].split(b'\0'):
            if value.startswith(b'\x81\x75')and value.endswith(b'\x81\x76'):
                try:normalized=normalize(value)
                except UnicodeDecodeError:normalized=''
                if normalized and all(ord(c)>=32 for c in normalized):
                    digest=sha(normalized.encode('cp932'));stats['quoted_tail_fields']+=1
                    if digest not in sources:tail_unbound.append(dict(block=i,offset=at,source_sha256=digest))
            at+=len(value)+1
    stats['distinct_unbound_tail_texts']=len({r['source_sha256']for r in tail_unbound})
    require(stats['blocks']==352 and stats['indexed_records']==stats['selected_record_references']==59262,'Runtime indexed inventory')
    return dict(schema_version=1,status='Static contract verified; buffer hook and emulator acceptance pending',
        source_exe_sha256=sha(exe),stats=dict(stats),blocks=per_block,
        functions={name:dict(start=lo,end=hi,sha256=digest)for name,(lo,hi,digest)in RANGES.items()},
        guarded_words={hex(va):hex(w)for va,w in WORDS.items()},
        layout='index = 8 + byte[1]*4 + u16[4]*8 + byte[2]*8 + byte[3]*4; pool = index + u16[6]*8',
        loading='SEG[i+1]-SEG[i] passed to 0x13a1f0; 0x139edc allocates aligned sector span via 0x139b80, including leading sector offset',
        indexed_selection='Sequence +4 u16 first record, +6 u8 count; 0x2f1e58 selects 8-byte descriptors; +4 u32 is relative to bank text pool',
        display=dict(converter=0x2f1760,temporary_buffer_offset=0x2b8,temporary_buffer_bytes=96,
            fill_calls=[0x2f198c,0x2f1bac],reader=0x2f2120,initializer=0x2f21b8,
            font_path=[0x2f20b0,0x2fd9a0,0x2fd890,0x13ad30],
            observed_manager_addresses=[0x685870+0x3a80+0x420+i*0x1150 for i in range(2)],
            manager_evidence='Two parent objects initialized at base 0x685870 + 0x3a80 + i*0x1150; caption member +0x420'),
        unresolved_tail_text_bindings=tail_unbound,
        cautions=['Relocation component preserves native tails; their complete runtime reachability still needs auditing.',
            'No 96-byte buffer enlargement is installed by this inspector.',
            'Static font call path is not emulator layout/timing acceptance.'])


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    r=inspect();print(json.dumps(dict(stats=r['stats'],display=r['display'],loading=r['loading']),indent=2))
    if a.write:(ROOT/'work/analysis/battle-runtime-contract.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no files written')


if __name__=='__main__':main()
