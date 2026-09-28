"""Bind all mission-condition tables by their native MIPS global assignments.

The stage initializer assigns victory/defeat/extra pointer tables to globals
0x61e1b0, 0x61e1b8 and 0x61e1c0. Do not classify dialogue by punctuation.
"""
import argparse,json,struct
from collections import Counter
from sp_disc import ROOT,Disc,SOURCE,sha,require,decode
from extract_story import BASE,HB_TABLE,CHUNKS

TARGET=ROOT/'work/ui/mission-conditions/native-inventory.json'
KINDS={0xe1b0:'victory',0xe1b8:'defeat',0xe1c0:'extra'}

def u32(data,p):return struct.unpack_from('<I',data,p)[0]
def signed(v):return v if v<32768 else v-65536

def tables(data):
    found={};code_end=min(0x80+u32(data,0x1c),len(data))
    for p in range(0x80,code_end-3,4):
        w=u32(data,p)
        if w>>26!=43 or w>>21&31!=1 or w>>16&31!=2 or w&65535 not in KINDS:continue
        recent=[(q,u32(data,q)) for q in range(max(0x80,p-32),p,4)]
        require(any(v==0x3c010062 for _,v in recent[-4:]),'Condition destination LUI')
        low=next(((q,v) for q,v in reversed(recent) if v>>26==9 and v>>21&31==2 and v>>16&31==2),None)
        require(low is not None,'Condition source ADDIU')
        high=next(((q,v) for q,v in reversed(recent) if q<low[0] and v>>26==15 and v>>16&31==2),None)
        require(high is not None,'Condition source LUI')
        off=((high[1]&65535)<<16)+signed(low[1]&65535)-BASE
        require(p+4<=off<len(data) and off%4==0,'Condition table is not aligned data')
        key=w&65535;require(key not in found,'Duplicate condition global assignment')
        found[key]=dict(kind=KINDS[key],offset=off,store_offset=p,high_offset=high[0],low_offset=low[0],
                        code_sha256=sha(data[high[0]:p+4]))
    require(not found or set(found)==set(KINDS),'Partial condition initializer')
    result=[]
    for key,t in sorted(found.items()):
        start=t['offset'];limit=min([r['offset'] for r in found.values() if r['offset']>start]+[len(data)])
        entries=[]
        for p in range(start,min(limit,start+64),4):
            value=u32(data,p)
            if value==0:break
            off=value-BASE;require(t['store_offset']+4<=off<len(data),'Condition text pointer is not data')
            end=data.index(0,off);raw=data[off:end];source=raw.decode('cp932')
            require(raw and source.encode('cp932')==raw,'Condition text decoding')
            entries.append(dict(pointer_site=p,offset=off,source=source,source_sha256=sha(raw)))
        require(1<=len(entries)<=3,'Condition table length')
        result.append(dict(t,entries=entries))
    return result

def inventory():
    disc=Disc(SOURCE);archive=disc.read('DATA/STAGE.BIN');hb=disc.read('HEDBDY/HB.BIN')
    offsets=struct.unpack_from('<69I',hb,HB_TABLE);chunks=[];unique={};absent=[]
    for i,(lo,hi) in enumerate(zip(offsets,offsets[1:])):
        if i==0:continue
        raw=decode(archive[lo:hi])[0];groups=tables(raw)
        if not groups:absent.append(i);continue
        for group in groups:
            for row in group['entries']:
                key=row['source_sha256'];entry=unique.setdefault(key,dict(id='m_'+key[:12],source=row['source'],
                      source_sha256=key,occurrences=[]))
                entry['occurrences'].append(dict(chunk=i,kind=group['kind'],offset=row['offset'],pointer_site=row['pointer_site']))
        chunks.append(dict(chunk=i,start=lo,end=hi,decoded_bytes=len(raw),source_sha256=sha(raw),tables=groups))
    return dict(schema_version=1,archive_sha256=sha(archive),hb_table_sha256=sha(hb[HB_TABLE:HB_TABLE+276]),
                globals={v:hex(0x610000+k) for k,v in KINDS.items()},chunks=chunks,
                chunks_without_tables=absent,entries=list(unique.values()))

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();d=inventory()
    print(json.dumps(dict(chunks=len(d['chunks']),unique=len(d['entries']),
         occurrences=sum(len(r['occurrences']) for r in d['entries']),
         kinds=dict(Counter(o['kind'] for r in d['entries'] for o in r['occurrences'])),
         samples=d['entries'][:3],last=d['entries'][-1]),ensure_ascii=True,indent=2))
    if not a.write:print('DRY RUN: no files written');return
    TARGET.parent.mkdir(parents=True,exist_ok=True);TARGET.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

if __name__=='__main__':main()
