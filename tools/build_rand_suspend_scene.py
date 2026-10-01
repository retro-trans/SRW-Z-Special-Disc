"""Build v0.3.5 Rand/Mel suspend conversation; dry run unless --write."""
import argparse,hashlib,json,shutil,subprocess
from sp_disc import ROOT,SOURCE,SOURCE_SHA,Disc,require,file_sha
from rand_suspend_scene import build,SLOTS
from sp_disc import EXE as MEMBER

BASE_SHA='b259761e1e179f8885903048f49e4f39085e6560d693a4d626f0e46660d585c3'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write',action='store_true');p.add_argument('--patch',action='store_true');a=p.parse_args()
    base=ROOT/'work/output/SRW Z Special Disc English v0.3.4.iso'
    target=ROOT/'work/output/SRW Z Special Disc English v0.3.5.iso'
    disc=Disc(base);old=disc.read(MEMBER)
    require(old==Disc(base,True).read(MEMBER),'ISO/runtime archive mismatch')
    result,report=build(old)
    # One contiguous span holds precisely the eight original text slots.
    start=SLOTS[0][0];end=SLOTS[-1][0]+SLOTS[-1][1]
    offset=disc.entries[MEMBER]['lba']*2048+start
    data=result[start:end]
    print(json.dumps(dict(version='0.3.5',dialogue_rows=len(report['entries']),max_converted_bytes=max(r['converted_bytes'] for r in report['entries'])),indent=2),flush=True)
    if not a.write:print('DRY RUN: no game files written');return
    require(not target.exists() and not target.with_suffix('.xdelta').exists(),'Candidate already exists')
    require(file_sha(base)==BASE_SHA,'Wrong v0.3.4 input ISO')
    if a.patch:require(file_sha(SOURCE)==SOURCE_SHA,'Wrong clean source ISO')
    shutil.copyfile(base,target)
    with target.open('r+b') as f:f.seek(offset);f.write(data)
    require(Disc(target).read(MEMBER)==Disc(target,True).read(MEMBER)==result,'Archive readback failed')
    h=hashlib.sha256();at=0
    with base.open('rb') as src,target.open('rb') as dst:
        while True:
            before=src.read(8<<20)
            if not before:require(not dst.read(1),'ISO size changed');break
            after=dst.read(len(before));expected=bytearray(before)
            lo=max(at,offset);hi=min(at+len(before),offset+len(data))
            if lo<hi:expected[lo-at:hi-at]=data[lo-offset:hi-offset]
            require(after==expected,'Unplanned ISO change at '+hex(at));h.update(after);at+=len(before)
    receipt=dict(version='0.3.5',base=base.name,base_sha256=BASE_SHA,iso=target.name,
        iso_sha256=h.hexdigest(),iso_bytes=target.stat().st_size,rand_suspend_scene=report,
        all_other_bytes_identical=True,emulator='pending')
    if a.patch:
        patch=target.with_suffix('.xdelta');check=ROOT/'work/output/verify-rand-suspend-0.3.5.iso'
        require(not check.exists(),'Verification output exists')
        xdelta=ROOT.parent/'SRW Z/xdelta3.exe'
        print('Creating and reconstructing clean-disc patch...',flush=True)
        subprocess.run([str(xdelta),'-e','-9','-A','-s',str(SOURCE),str(target),str(patch)],check=True)
        subprocess.run([str(xdelta),'-d','-s',str(SOURCE),str(patch),str(check)],check=True)
        require(file_sha(check)==receipt['iso_sha256'],'Patch reconstruction mismatch');check.unlink()
        receipt['xdelta']=dict(name=patch.name,bytes=patch.stat().st_size,sha256=file_sha(patch),roundtrip_verified=True)
    target.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k!='rand_suspend_scene'},indent=2),flush=True)

if __name__=='__main__':main()
