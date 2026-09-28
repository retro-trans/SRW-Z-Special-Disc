"""Source-bound indexed SRVC captions; never treat opaque tails as text.

Layout corroborated against dyzz/srwz-zh f6673b1, tools/srwz/srvc.py,
and the local SRW-Z best_adapter/subtitles.py. No foreign writer is executed.
"""
import re
import struct
from sp_disc import Disc,SOURCE,ROOT,sha,require

BIN='BTL/SRVC.BIN'
SEG='BTL/SRVC.SEG'
BIN_SHA='acf7b4b00fbd104b3320ae44f2e7548f4d31ad1f434231df35e39920928cd7e1'
SEG_SHA='46d9f8bd07c95f0b029801854857e0ab7650e74ab492da25605cbdbed4e6ac71'


def blocks(data,seg):
    require(len(seg)%4==0,'SRVC segment table alignment')
    offsets=struct.unpack('<%dI'%(len(seg)//4),seg)
    require(offsets[0]==0 and offsets[-1]==len(data) and list(offsets)==sorted(set(offsets)),'SRVC segment bounds')
    require(all(x%16==0 for x in offsets),'SRVC block alignment')
    return offsets,[data[a:b]for a,b in zip(offsets,offsets[1:])]


def indexed(raw,index,count):
    pool=index+count*8;rows=[]
    require(index>=8 and index%4==0 and pool<len(raw),'SRVC index bounds')
    for n in range(count):
        metadata,offset=struct.unpack_from('<II',raw,index+n*8);at=pool+offset
        require(pool<=at<len(raw) and (at==pool or raw[at-1]==0),'SRVC text pointer boundary')
        end=raw.find(b'\0',at);require(end>=at,'SRVC text terminator')
        rows.append(dict(record=n,metadata=metadata,offset=offset,start=at,end=end+1,raw=raw[at:end]))
    return rows


def native_layout(raw,magic=0x4f01):
    require(len(raw)>=8 and struct.unpack_from('<H',raw)[0]==magic,'SRVC source magic')
    count=struct.unpack_from('<H',raw,6)[0]
    if not count:return dict(index=None,pool=None,end=None,rows=[])
    candidates=[]
    for at in range(8,len(raw)-count*8,4):
        if struct.unpack_from('<I',raw,at+4)[0]:continue
        try:
            rows=indexed(raw,at,count);cursor=at+8*count
            for row in rows:
                require(row['start']==cursor,'Non-consecutive native SRVC text')
                value=row['raw'].decode('cp932')
                require(value and all(ord(c)>=32 for c in value),'Nontext indexed SRVC bytes')
                cursor=row['end']
            candidates.append(dict(index=at,pool=at+8*count,end=cursor,rows=rows))
        except (ValueError,UnicodeDecodeError):continue
    require(len(candidates)==1,'SRVC source index candidates: '+str(len(candidates)))
    # Independently corroborated by SP's bank initializer at VA 0x2fe610.
    # Byte 1 is the group count; bytes 2/3 are separate condition counts.
    expected=8+raw[1]*4+struct.unpack_from('<H',raw,4)[0]*8+raw[2]*8+raw[3]*4
    require(candidates[0]['index']==expected,'SRVC index disagrees with native runtime layout')
    return candidates[0]


def normalize(raw):
    value=raw.decode('cp932')
    if value.startswith('\u300c'):value=value[1:]
    if value.endswith('\u300d'):value=value[:-1]
    return re.sub('\u3000'+r'*\\n'+'\u3000'+r'*',r'\\n',value).strip('\u3000')


def native():
    disc=Disc(SOURCE);data=disc.read(BIN);seg=disc.read(SEG)
    require(sha(data)==BIN_SHA and sha(seg)==SEG_SHA,'SP caption source identity')
    offsets,chunks=blocks(data,seg)
    require(len(chunks)==352,'SP caption chunk count')
    parsed=[native_layout(raw)for raw in chunks]
    require(sum(len(p['rows'])for p in parsed)==59262,'SP indexed caption count')
    return data,seg,offsets,chunks,parsed


def unique_sources():
    _,_,_,chunks,parsed=native();entries=[];lookup={}
    for block,p in enumerate(parsed):
        for row in p['rows']:
            value=normalize(row['raw']);digest=sha(value.encode('cp932'))
            if digest not in lookup:
                lookup[digest]=len(entries)
                entries.append(dict(id=len(entries),source_sha256=digest,text=value,occurrences=[]))
            entry=entries[lookup[digest]];require(entry['text']==value,'Caption source hash collision')
            entry['occurrences'].append(dict(block=block,record=row['record'],metadata=row['metadata'],raw_sha256=sha(row['raw'])))
    require(len(entries)==25522,'SP unique caption source count')
    return entries


if __name__=='__main__':
    import json
    data,seg,offsets,chunks,parsed=native()
    print(json.dumps(dict(blocks=len(chunks),indexed_records=sum(len(p['rows'])for p in parsed),
        indexed_pool_bytes=sum(p['end']-p['pool']for p in parsed if p['rows']),
        opaque_tail_bytes=sum(len(b)-(p['end']or 8)for b,p in zip(chunks,parsed)),
        unique_normalized_lines=len(unique_sources())),indent=2))
    print('READ ONLY: no Japanese dialogue exports or data writes')
