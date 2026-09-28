"""Read-only research for porting the verified donor's font/menu runtime."""
import argparse
import json
import struct
from pathlib import Path
from sp_disc import ROOT, source_records, Disc, sha, require

DONOR=Path('E:/Projects/SRW Z/SRW Z English Original v0.9.85.iso')
ORIGINAL=Path('E:/Projects/SRW Z/_work/extracted/SLPS_258.87')
A_BASE=0xFE580
B_BASE=0xFF680
CAVE=0x78A070
CAVE_FILE=0x34D770
DELTA=0xAA0
FONT_LO,FONT_HI=0x139B00,0x13B7D0

def u32(d,o):return struct.unpack_from('<I',d,o)[0]
def s16(w):return (w&0xffff)-0x10000 if w&0x8000 else w&0xffff

def normal(w):
    op=w>>26
    if op in (2,3):return w&0xfc000000
    if op in (1,4,5,6,7,20,21,22,23,9,13,15,25):return w&0xffff0000
    if ((w>>21)&31) in (1,28) and op in (24,32,33,35,36,37,39,40,41,43,49,55,57,63):return w&0xffff0000
    return w

def writes_reg(w,r):
    op,rs,rt,rd=w>>26,(w>>21)&31,(w>>16)&31,(w>>11)&31
    if op in (0,28):return rd==r and w&63 not in (8,12,13,16,17,18,19,24,25,26,27)
    if op in (1,2,4,5,6,7,20,21,22,23,40,41,42,43,44,45,46,47,57,61,63):return False
    return r==31 if op==3 else rt==r

def hi_pair(read,pc,w,lo):
    r=(w>>21)&31
    if not r:return None
    for p in range(pc-4,max(pc-132,lo-4),-4):
        x=read(p)
        if x>>26==15 and (x>>16)&31==r:return p,x
        if x>>26==0 and x&63 in (0x21,0x2d) and (x>>11)&31==r and r in ((x>>21)&31,(x>>16)&31):continue
        if writes_reg(x,r) or x>>26 in (2,3) or x>>26==0 and x&63 in (8,9):return None
    return None

def research():
    disc,b,_,_=source_records();a=ORIGINAL.read_bytes();c=Disc(DONOR,runtime=True).read('SLPS_258.87')
    require(sha(a)=='6c4c81c4e5aa3db1f52d70b8183ce11c01fc6b265ae4d53fa4d6a657c5019b50','Native donor executable changed')
    po=u32(c,28);es,n=struct.unpack_from('<HH',c,42)
    segment=next(struct.unpack_from('<8I',c,po+i*es) for i in range(n) if u32(c,po+i*es+8)==CAVE)
    end=CAVE+segment[4]
    def ac(pc):return u32(a,pc-A_BASE)
    def bc(pc):return u32(b,pc+DELTA-B_BASE)
    def cc(pc):return u32(c,CAVE_FILE+pc-CAVE if pc>=CAVE else pc-A_BASE)
    conflicts=[hex(pc) for pc in range(FONT_LO,FONT_HI,4) if normal(ac(pc))!=normal(bc(pc))]
    require(not conflicts,'Native font routines diverged: '+str(conflicts[:12]))
    hooks=[pc for pc in range(FONT_LO,FONT_HI,4) if ac(pc)!=cc(pc)]
    pending=[(cc(pc)&0x3ffffff)<<2 for pc in hooks if cc(pc)>>26 in (2,3)]
    seen=set();external=set()
    while pending:
        pc=pending.pop()
        if pc in seen:continue
        if not CAVE<=pc<end:external.add(pc);continue
        seen.add(pc);w=cc(pc);op=w>>26
        if op in (2,3):
            pending.append((w&0x3ffffff)<<2);seen.add(pc+4)
            if op==3:pending.append(pc+8)
        elif op in (1,4,5,6,7,20,21,22,23):pending.extend([pc+8,pc+4+s16(w)*4]);seen.add(pc+4)
        elif op==0 and w&63 in (8,9):
            seen.add(pc+4)
            if w&63==9:pending.append(pc+8)
        else:pending.append(pc+4)
    addresses={};pairs=[]
    for pc in range(FONT_LO,FONT_HI,4):
        w=ac(pc);op=w>>26
        if op not in (9,13,25,32,33,35,36,37,39,40,41,43,49,55,57,63):continue
        hi=hi_pair(ac,pc,w,FONT_LO)
        if not hi:continue
        hp,hw=hi;value=((hw&65535)<<16)+((w&65535)if op==13 else s16(w))
        other=((bc(hp)&65535)<<16)+((bc(pc)&65535)if op==13 else s16(bc(pc)))
        if 0x100000<=value<0x2000000:
            require(value not in addresses or addresses[value]==other,'Conflicting global relocation')
            addresses[value]=other
    for pc in sorted(seen):
        w=cc(pc);op=w>>26
        if op not in (9,13,25,32,33,35,36,37,39,40,41,43,49,55,57,63):continue
        hi=hi_pair(cc,pc,w,CAVE)
        if not hi:continue
        hp,hw=hi;value=((hw&65535)<<16)+((w&65535)if op==13 else s16(w))
        if 0x100000<=value<0x2000000:pairs.append(dict(pc=pc,high_pc=hp,value=value,target=addresses.get(value)))
    report=dict(source_sha256=sha(b),original_sha256=sha(a),donor_sha256=sha(c),
                native_font_delta=DELTA,cave=list(segment),hooks=[dict(pc=pc,target=pc+DELTA,native=ac(pc),sp=bc(pc),english=cc(pc))for pc in hooks],
                code=sorted(seen),external=sorted(external),global_addresses={hex(k):hex(v)for k,v in addresses.items()},address_pairs=pairs,
                gp_instructions=[hex(pc)for pc in seen if (cc(pc)>>21)&31==28])
    return report,a,b,c

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    report,a,b,c=research()
    print(json.dumps({k:v for k,v in report.items() if k not in ('code','global_addresses')},indent=2))
    if args.write:
        out=ROOT/'work/analysis/english-runtime-map.json';out.write_text(json.dumps(report,indent=2)+'\n')
        cache=ROOT/'work/cache/english-runtime';cache.mkdir(parents=True,exist_ok=True)
        for name,data in [('original.elf',a),('special.elf',b),('english.elf',c)]: (cache/name).write_bytes(data)
    else:print('DRY RUN: no files written')

if __name__=='__main__':main()
