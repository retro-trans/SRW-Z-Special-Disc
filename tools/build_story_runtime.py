"""Build the v0.3.1 story-renderer candidate; dry run unless --write.

Preserves every v0.3.0 byte except the 13 guarded executable words. --patch
also produces a clean-disc xdelta and verifies exact reconstruction.
"""
import argparse
import hashlib
import json
import shutil
import struct
import subprocess
from sp_disc import ROOT, SOURCE, SOURCE_SHA, EXE, Disc, require, file_sha
from story_runtime import apply

BASE_SHA = 'ca444e5c078a6f3cb23a96c5b6d676de1df068cfa4219ecbc06e71cbea4186ec'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write',action='store_true'); p.add_argument('--patch',action='store_true')
    args=p.parse_args()
    base=ROOT/'work/output/SRW Z Special Disc English v0.3.0.iso'
    target=ROOT/'work/output/SRW Z Special Disc English v0.3.1.iso'
    disc=Disc(base); runtime=Disc(base,True)
    exe=disc.read(EXE); require(runtime.read(EXE)==exe,'ISO/runtime executable disagree')
    patched,report=apply(exe)
    writes=[(disc.entries[EXE]['lba']*2048+r['offset'],struct.pack('<I',r['after'])) for r in report['patches']]
    require(len(writes)==13,'Unexpected patch count')
    print(json.dumps(dict(version='0.3.1',base=base.name,target=target.name,
                         changed_instruction_words=len(writes),dialogue_changes=0,
                         executable_sha256=report['sha256']),indent=2),flush=True)
    if not args.write:
        print('DRY RUN: no game files written'); return
    require(not target.exists() and not target.with_suffix('.xdelta').exists(),'Candidate output already exists')
    require(file_sha(base)==BASE_SHA,'Wrong v0.3.0 input image')
    if args.patch: require(file_sha(SOURCE)==SOURCE_SHA,'Wrong clean source image')
    print('Copying base and applying guarded instruction words...',flush=True)
    shutil.copyfile(base,target)
    with target.open('r+b') as f:
        for at,data in writes: f.seek(at); f.write(data)
    require(Disc(target).read(EXE)==patched==Disc(target,True).read(EXE),'Executable readback mismatch')
    digest=hashlib.sha256(); at=0
    with base.open('rb') as a,target.open('rb') as b:
        while True:
            old=a.read(8<<20); new=b.read(len(old))
            if not old: require(not b.read(1),'Output length changed'); break
            expected=bytearray(old)
            for off,data in writes:
                if at<=off<at+len(old): expected[off-at:off-at+len(data)]=data
            require(new==expected,'Unexpected disc change at '+hex(at))
            digest.update(new); at+=len(old)
    result=dict(version='0.3.1',base=base.name,base_sha256=BASE_SHA,iso=target.name,
                iso_sha256=digest.hexdigest(),iso_bytes=target.stat().st_size,
                story_runtime=report,all_other_bytes_identical=True,emulator='pending')
    if args.patch:
        patch=target.with_suffix('.xdelta'); check=ROOT/'work/output/verify-story-runtime-0.3.1.iso'
        require(not check.exists(),'Verification output already exists')
        xdelta=ROOT.parent/'SRW Z/xdelta3.exe'
        subprocess.run([str(xdelta),'-e','-9','-A','-s',str(SOURCE),str(target),str(patch)],check=True)
        subprocess.run([str(xdelta),'-d','-s',str(SOURCE),str(patch),str(check)],check=True)
        require(file_sha(check)==result['iso_sha256'],'Patch reconstruction mismatch')
        check.unlink()
        result['xdelta']=dict(name=patch.name,bytes=patch.stat().st_size,sha256=file_sha(patch),roundtrip_verified=True)
    target.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__': main()
