"""Build v0.3.2 bonus-result fixes; dry run unless --write."""
import argparse, hashlib, json, shutil, struct, subprocess
from sp_disc import ROOT, SOURCE, SOURCE_SHA, EXE, Disc, require, file_sha
from bonus_results import build, MEMBER
from build_story import reserved_cursor

BASE_SHA='c1ae1dc250ac687188d8ed6380751686bb47010fbaf60f44028c7ce9ece5d174'


def plan(disc,members):
    cursor,limit=reserved_cursor(disc,{})
    writes=[]; placements={}
    for name,payload in members.items():
        sectors=(len(payload)+2047)//2048
        require(cursor+sectors<=limit,'Reserved disc area exhausted')
        data=payload+bytes(sectors*2048-len(payload)); offset=cursor*2048
        with disc.path.open('rb') as f:
            f.seek(offset); require(f.read(len(data))==bytes(len(data)),'Relocation area not empty')
        writes.append((offset,data))
        e=disc.entries[name]; record=e['directory_record']
        writes.append((record+2,struct.pack('<I',cursor)+struct.pack('>I',cursor)))
        writes.append((record+10,struct.pack('<I',len(payload))+struct.pack('>I',len(payload))))
        if name in disc.runtime:
            vm=disc.entries['VMAP.DAT']['lba']*2048+disc.runtime[name]['vmap_offset']+40
            writes.append((vm,struct.pack('<II',cursor,sectors)))
        else:
            require(name==EXE,'Missing runtime mapping for data member')
        placements[name]=dict(lba=cursor,size=len(payload),sectors=sectors)
        cursor+=sectors
    writes.sort()
    require(all(a+len(b)<=c for (a,b),(c,d) in zip(writes,writes[1:])),'Overlapping writes')
    return writes,placements


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write',action='store_true');p.add_argument('--patch',action='store_true')
    args=p.parse_args()
    base=ROOT/'work/output/SRW Z Special Disc English v0.3.1.iso'
    target=ROOT/'work/output/SRW Z Special Disc English v0.3.2.iso'
    disc=Disc(base); runtime=Disc(base,True)
    require(all(disc.read(n)==runtime.read(n) for n in (EXE,MEMBER)),'ISO/runtime inputs disagree')
    exe,comp,report=build(disc.read(EXE),disc.read(MEMBER))
    members={EXE:exe,MEMBER:comp};writes,placements=plan(disc,members)
    print(json.dumps(dict(version='0.3.2',translated_fields=len(report['fields']),
        placements=placements,heap_unchanged=report['heap_base'],segment_end=report['segment_end']),indent=2),flush=True)
    if not args.write:
        print('DRY RUN: no game files written');return
    require(not target.exists() and not target.with_suffix('.xdelta').exists(),'Candidate already exists')
    require(file_sha(base)==BASE_SHA,'Wrong v0.3.1 input image')
    if args.patch:require(file_sha(SOURCE)==SOURCE_SHA,'Wrong clean source image')
    shutil.copyfile(base,target)
    with target.open('r+b') as f:
        for at,data in writes:f.seek(at);f.write(data)
    patched=Disc(target);running=Disc(target,True)
    for name,data in members.items():
        require(patched.read(name)==running.read(name)==data,'Member readback '+name)
    # Verify the entire image against exactly the planned writes, including
    # spans crossing chunk boundaries. Old extents and unrelated assets remain.
    h=hashlib.sha256();at=0
    with base.open('rb') as a,target.open('rb') as b:
        while True:
            old=a.read(8<<20)
            if not old:require(not b.read(1),'Output size changed');break
            new=b.read(len(old));expected=bytearray(old)
            for off,data in writes:
                lo=max(at,off);hi=min(at+len(old),off+len(data))
                if lo<hi:expected[lo-at:hi-at]=data[lo-off:hi-off]
            require(new==expected,'Unexpected disc change at '+hex(at))
            h.update(new);at+=len(old)
    result=dict(version='0.3.2',base=base.name,base_sha256=BASE_SHA,iso=target.name,
        iso_sha256=h.hexdigest(),iso_bytes=target.stat().st_size,placements=placements,
        bonus_results=report,all_other_bytes_identical=True,emulator='pending')
    if args.patch:
        patch=target.with_suffix('.xdelta');check=ROOT/'work/output/verify-bonus-results-0.3.2.iso'
        require(not check.exists(),'Verification output exists')
        xdelta=ROOT.parent/'SRW Z/xdelta3.exe'
        print('Creating and reconstructing clean-disc patch...',flush=True)
        subprocess.run([str(xdelta),'-e','-9','-A','-s',str(SOURCE),str(target),str(patch)],check=True)
        subprocess.run([str(xdelta),'-d','-s',str(SOURCE),str(patch),str(check)],check=True)
        require(file_sha(check)==result['iso_sha256'],'Patch reconstruction mismatch')
        check.unlink()
        result['xdelta']=dict(name=patch.name,bytes=patch.stat().st_size,sha256=file_sha(patch),roundtrip_verified=True)
    target.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='bonus_results'},indent=2),flush=True)

if __name__=='__main__':main()
