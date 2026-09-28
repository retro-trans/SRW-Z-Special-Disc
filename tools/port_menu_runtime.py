"""Guarded Special Disc port of the donor's menu glyph runtime, no story hook."""
import argparse
import json
import struct
from sp_disc import ROOT, require, sha
from inspect_english_runtime import (A_BASE,B_BASE,CAVE,CAVE_FILE,DELTA,FONT_LO,FONT_HI,u32,s16)

SP_END=0x81C600
NEW_CAVE=SP_END+0x370
NEW_HEAP=SP_END+0x3000
NEW_FILE=0x3CB770
BREAK_OFFSET=0x34F0B4

def build(native):
    report=json.loads((ROOT/'work/analysis/english-runtime-map.json').read_text())
    donor=(ROOT/'work/cache/english-runtime/english.elf').read_bytes()
    require(sha(native)==report['source_sha256'],'SP runtime native preimage drift')
    require(sha(donor)==report['donor_sha256'],'English runtime donor drift')
    count=report['cave'][4];end=CAVE+count
    require(NEW_CAVE+count<=NEW_HEAP,'Runtime overlaps reserved heap')
    require(not report['gp_instructions'],'Unmapped GP-relative runtime code')
    globals_={int(k,16):int(v,16)for k,v in report['global_addresses'].items()}
    def address(va):
        if CAVE<=va<end:return va+NEW_CAVE-CAVE
        if FONT_LO<=va<FONT_HI:return va+DELTA
        if va in globals_:return globals_[va]
        raise ValueError('Unmapped runtime address '+hex(va))
    def offset(pc):return NEW_FILE+pc-CAVE if CAVE<=pc<end else pc+DELTA-B_BASE
    def word(pc):return u32(donor,CAVE_FILE+pc-CAVE if CAVE<=pc<end else pc-A_BASE)
    out=bytearray(native)
    if len(out)<NEW_FILE+count:out.extend(bytes(NEW_FILE+count-len(out)))
    out[NEW_FILE:NEW_FILE+count]=donor[CAVE_FILE:CAVE_FILE+count]
    changed={};highs={}
    def put(pc,w):
        p=offset(pc);struct.pack_into('<I',out,p,w&0xffffffff);changed[p]=w&0xffffffff
    for hook in report['hooks']:
        require(u32(native,hook['target']-B_BASE)==hook['sp'],'Font hook preimage drift')
    code=set(report['code'])|{h['pc']for h in report['hooks']}
    for pc in sorted(code):
        w=word(pc);op=w>>26;new=w
        if op in (2,3):new=(w&0xfc000000)|(address((w&0x3ffffff)<<2)>>2)
        elif op in (1,4,5,6,7,20,21,22,23):
            dest=pc+4+s16(w)*4;distance=(address(dest)-address(pc)-4)//4
            require(-32768<=distance<32768,'Runtime branch overflow');new=(w&0xffff0000)|(distance&65535)
        put(pc,new)
    relocations=[]
    for pair in report['address_pairs']:
        pc,hp,value=pair['pc'],pair['high_pc'],pair['value'];w=word(pc);mapped=address(value)
        upper=mapped>>16 if w>>26==13 else (mapped+0x8000)>>16
        high=(word(hp)&0xffff0000)|(upper&65535)
        require(hp not in highs or highs[hp]==high,'Conflicting shared high-half relocation')
        highs[hp]=high;put(hp,high);put(pc,(w&0xffff0000)|(mapped&65535))
        relocations.append(dict(pc=hex(pc),old=hex(value),new=hex(mapped)))
    po=u32(native,28);es,n=struct.unpack_from('<HH',native,42)
    headers=[struct.unpack_from('<8I',native,po+i*es)for i in range(n)]
    require(max(r[2]+r[5]for r in headers)==SP_END,'SP memory ceiling changed')
    require(po+(n+1)*es<=0x980 and NEW_FILE%128==NEW_CAVE%128,'ELF segment/header alignment')
    marker=po+(n-1)*es;out[marker+es:marker+2*es]=native[marker:marker+es]
    struct.pack_into('<8I',out,marker,1,NEW_FILE,NEW_CAVE,NEW_CAVE,count,count,7,128)
    struct.pack_into('<H',out,44,n+1)
    struct.pack_into('<I',out,marker+es+4,NEW_FILE+count)
    struct.pack_into('<I',out,32,0);struct.pack_into('<HH',out,48,0,0)
    require(u32(native,0x1001d0-B_BASE)==0x3c040082 and u32(native,0x1001d8-B_BASE)==0x2484c600,'InitHeap preimage')
    require(u32(native,BREAK_OFFSET)==SP_END,'libkernel break preimage')
    struct.pack_into('<I',out,0x1001d0-B_BASE,0x3c040000|((NEW_HEAP+0x8000)>>16))
    struct.pack_into('<I',out,0x1001d8-B_BASE,0x24840000|(NEW_HEAP&65535))
    struct.pack_into('<I',out,BREAK_OFFSET,NEW_HEAP)
    # Read every relocated word back, and ensure direct control transfers stay
    # inside mapped executable code. Story setText and layout hooks are excluded.
    for p,w in changed.items():require(u32(out,p)==w,'Runtime word readback')
    for pc in report['external']:require(FONT_LO<=pc<FONT_HI,'Runtime escapes verified native font routines')
    return bytes(out),dict(font_hook_words=len(report['hooks']),runtime_code_words=len(report['code']),
                          cave=hex(NEW_CAVE),cave_bytes=count,heap_base=hex(NEW_HEAP),
                          original_heap_base=hex(SP_END),heap_page_offset_preserved=True,
                          relocations=relocations,story_settext_hook=False,sha256=sha(out))

def main():
    from sp_disc import source_records
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    output,report=build(source_records()[1]);print(json.dumps(report,indent=2))
    if a.write:
        dest=ROOT/'work/cache/nonstory';dest.mkdir(parents=True,exist_ok=True)
        (dest/'runtime.elf').write_bytes(output)
        (ROOT/'work/analysis/menu-runtime-port.json').write_text(json.dumps(report,indent=2)+'\n')
    else:print('DRY RUN: no files written')

if __name__=='__main__':main()
