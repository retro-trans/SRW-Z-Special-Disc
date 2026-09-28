"""Strict Special Disc vpro narration containers, without Japanese prose exports."""
import struct
from sp_disc import ROOT, Disc, SOURCE, EXE, decode, sha, require

MEMBER='DATA/MTZSPROS.BIN'
SOURCE_SHA='1aa53992cbaea30e95a2c66e771e95e10076ff8645a9e9b7c1f841dc5e32c59f'
SIZE_TABLE=0x387850
OFFSET_TABLE=0x387880
COUNT=10


def parse(raw):
    require(len(raw)>=60 and len(raw)%16==0,'Narration record alignment')
    require(struct.unpack_from('<8I',raw)==(1,32,0,len(raw)-32,len(raw)-32,0,0,0),'Narration wrapper')
    require(raw[32:36]==b'vpro','Narration container tag')
    require(struct.unpack_from('<3I',raw,44)==(1,1,1),'Narration child counts')
    end=60+struct.unpack_from('<I',raw,56)[0]
    require(end<=len(raw) and len(raw)-end<16 and not any(raw[end:]),'Narration container tail')
    children=[];at=60
    while at<end:
        require(at+8<=end,'Narration child header bounds')
        n=struct.unpack_from('<I',raw,at+4)[0];stop=at+8+n
        require(stop<=end,'Narration child bounds');children.append((at,raw[at:stop]));at=stop
    require(at==end and [b[:4]for _,b in children]==[b'pict',b'text',b'bgm_'],'Narration child inventory')
    text_at,chunk=children[1];body=chunk[8:]
    require(len(body)>=94 and body[2:6]==b'actv' and body[30:34]==b'rawt','Narration text commands')
    size=struct.unpack_from('<I',body,34)[0];value=body[38:38+size];suffix=body[38+size:]
    require(len(suffix)==56 and suffix[:4]==b'modi' and suffix[22:26]==b'modi'
        and suffix[44:48]==b'clip','Narration modifiers/clip')
    require(b'\0'not in value,'Unexpected NUL in length-delimited narration')
    return dict(children=children,prefix=body[:30],suffix=suffix,text=value,
        text_offset=text_at+46,rawt_offset=text_at+38,record_id=struct.unpack_from('<I',raw,36)[0],
        duration_ms=struct.unpack_from('<I',raw,40)[0],header=raw[32:60])


def replace_text(raw,value):
    before=parse(raw);require(b'\0'not in value,'NUL in narration replacement')
    body=before['prefix']+b'rawt'+struct.pack('<I',len(value))+value+before['suffix']
    changed=b'text'+struct.pack('<I',len(body))+body
    children=before['children'][0][1]+changed+before['children'][2][1]
    header=bytearray(before['header']);struct.pack_into('<I',header,24,len(children))
    payload=bytes(header)+children;payload+=bytes((-len(payload))%16)
    result=struct.pack('<8I',1,32,0,len(payload),len(payload),0,0,0)+payload
    after=parse(result)
    require(after['text']==value,'Narration text roundtrip')
    require(after['prefix']==before['prefix'] and after['suffix']==before['suffix']
        and after['children'][0][1]==before['children'][0][1]
        and after['children'][2][1]==before['children'][2][1]
        and after['header'][:24]==before['header'][:24],'Narration nontext commands changed')
    return result


def native_records():
    disc=Disc(SOURCE);exe=disc.read(EXE);archive=disc.read(MEMBER)
    require(sha(archive)==SOURCE_SHA,'Narration source identity')
    offsets=list(struct.unpack_from('<11I',exe,OFFSET_TABLE));sizes=list(struct.unpack_from('<10I',exe,SIZE_TABLE))
    require(offsets[0]==0 and offsets[-1]==len(archive) and offsets==sorted(set(offsets)), 'Narration offset table')
    records=[]
    for i,(lo,hi,size)in enumerate(zip(offsets,offsets[1:],sizes)):
        raw,consumed=decode(archive[lo:hi]);require(len(raw)==size and not any(archive[lo+consumed:hi]),'Narration archive record')
        info=parse(raw);require(info['record_id']==i+1 and info['text'].count(b'\n')==12,'Narration source record contract')
        require(replace_text(raw,info['text'])==raw,'Narration native parse/serialize identity')
        records.append((lo,raw,info))
    return exe,archive,offsets,sizes,records


if __name__=='__main__':
    import json
    _,_,offsets,sizes,records=native_records()
    print(json.dumps(dict(records=len(records),offsets=offsets,decoded_sizes=sizes,
        fields=[dict(id=i,text_bytes=len(p['text']),lines=p['text'].count(b'\n')+1,
        duration_ms=p['duration_ms'],source_text_sha256=sha(p['text']))for i,(_,_,p)in enumerate(records)]),indent=2))
    print('DRY RUN: native roundtrip checked; no files written')
