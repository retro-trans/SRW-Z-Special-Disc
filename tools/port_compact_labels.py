"""Port fixed-width spirit abbreviations and keep Japanese story glyphs native."""
import argparse
import json
import struct
from library_text import *
from reuse_system_text import AREAS
from inspect_english_runtime import A_BASE,B_BASE,CAVE,CAVE_FILE
from port_menu_runtime import NEW_FILE
from reuse_compdata import POOL_BASE

TABLE=0x355540
SPIRITS='熱魂閃不鉄集必加迅覚手狙直幸努乱分'
PAIRS=['Va','So','Al','En','Wa','Fo','St','Ac','Sw','Aw','Me','Sn','Pi','Lu','Ga','Di','An']
TERRAIN={'空':('AIR',0x85dc),'陸':('GND',0x85dd),'海':('SEA',0x85de),'宇':('SPC',0x85df),'水':('WTR',0x85e0)}

def build(exe,pool):
    native=(ROOT/'work/cache/english-runtime/special.elf').read_bytes()
    original=(ROOT/'work/cache/english-runtime/original.elf').read_bytes()
    out=bytearray(exe);pool=bytearray(pool);changes=[]
    def cstr(data,p):return data[p:data.index(0,p)]
    def put(p,value,label):
        require(out[p:p+len(value)]==native[p:p+len(value)],'Compact-label overlap '+label)
        out[p:p+len(value)]=value;changes.append(dict(offset=p,bytes=len(value),label=label,payload_hex=value.hex()))
    mapping={c:struct.pack('>H',0x85ca+i)for i,c in enumerate(SPIRITS)}
    for p in (0x3bf590,0x3bf5c0,0x3bf5f0,0x3bf620,0x3bf650,0x3bf680):
        raw=cstr(native,p);value=b''.join(mapping.get(c,c.encode('cp932')) for c in raw.decode('cp932'))
        require(len(value)==len(raw),'Spirit strip cell count');put(p,value,'spirit strip')
    require(native[0x39b468:0x39b46b]==b'\x81\x40\0' and native[0x3bf6a8:0x3bf6ac]==b'\x81\x40%s','Spirit mask preimage')
    put(0x39b468,b'\x85\xdb','blank spirit cell');put(0x3bf6a8,b'\x85\xdb','blank spirit format cell')
    seen=set();spirit_records=[]
    for i in range(37):
        an,ak,ad,flags=struct.unpack_from('<4I',original,0x3fa290-A_BASE+i*16)
        bn,bk,bd,other=struct.unpack_from('<4I',native,TABLE+i*16)
        require(flags==other and cstr(original,an-A_BASE)==cstr(native,bn-B_BASE),'Spirit table correspondence')
        raw=cstr(native,bk-B_BASE)
        char=raw.decode('cp932')
        if char in mapping and bk not in seen:
            put(bk-B_BASE,mapping[char],'spirit '+PAIRS[SPIRITS.index(char)]);seen.add(bk)
        name=cstr(native,bn-B_BASE).decode('cp932')
        if name in ('魂','愛','絆'):
            en={'魂':'Soul','愛':'Love','絆':'Bond'}[name]
            va=POOL_BASE+len(pool);pool.extend(en.encode()+b'\0');pool.extend(bytes((-len(pool))%4))
            struct.pack_into('<I',out,TABLE+i*16,va)
            spirit_records.append(dict(index=i,name=en,address=va))
    # Donor micro terrain art originally intercepted ordinary Japanese kanji.
    # Move it to private codes, then point only UI labels at those codes.
    for i,(ch,(label,code)) in enumerate(TERRAIN.items()):
        at=NEW_FILE+0x78be80-CAVE+i*8
        require(struct.unpack_from('<H',out,at)[0]==int.from_bytes(ch.encode('cp932'),'big'),'Terrain glyph preimage')
        struct.pack_into('<H',out,at,code)
        needle=ch.encode('cp932')+b'\0'
        for lo,hi in AREAS:
            p=lo
            while True:
                p=native.find(needle,p,hi)
                if p<0:break
                if p%4==0 and native[p-1]==0 and out[p:p+2]==native[p:p+2]:put(p,struct.pack('>H',code),'terrain '+label)
                p+=len(needle)
    return bytes(out),bytes(pool),dict(changes=changes,spirit_records=spirit_records,
        spirit_pairs=dict(zip(SPIRITS,PAIRS)),terrain_codes={k:hex(v[1])for k,v in TERRAIN.items()},
        japanese_story_glyphs_preserved=True,pool_bytes=len(pool),runtime='pending')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    root=ROOT/'work/cache/nonstory';exe,pool,r=build((root/'system.elf').read_bytes(),(root/'system-pool.bin').read_bytes())
    print(json.dumps(r,ensure_ascii=True,indent=2))
    if a.write:
        (root/'compact.elf').write_bytes(exe);(root/'compact-pool.bin').write_bytes(pool)
        (ROOT/'work/analysis/compact-labels.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no files written')

if __name__=='__main__':main()
