"""Build 0.1.0 front-end graphics from a clean SP image and locked assets.

Default is dry-run including compression/readback. --write creates a new ISO.
No executable, font, story, battle dialogue, save behavior, or layout is patched.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import numpy as np
from sp_disc import (ROOT,SOURCE,SOURCE_SHA,VT1,Disc,file_sha,source_records,decode,
                     tim2,replace_indices,sha,require,banlz)

VERSION='0.1.0'
ASSETS=ROOT/'work/ui/english'
OUT=ROOT/'work/output'/('SRW Z Special Disc English v%s.iso'%VERSION)


def components():
    manifest=json.loads((ASSETS/'manifest.json').read_text(encoding='utf-8'))
    require(file_sha(ROOT/'work/translation/en/front_end.json')==manifest['translation_sha256'],'Translation changed; re-author assets')
    require([a['chunk'] for a in manifest['atlases']]==[16,30,53],'Unexpected build scope')
    disc,exe,archive,offsets=source_records()
    changes=[]
    for a in manifest['atlases']:
        i=a['chunk'];lo,hi=offsets[i:i+2];raw,_=decode(archive[lo:hi])
        require(sha(raw)==a['source_sha256'],'Texture source lock mismatch')
        idx=np.load(ASSETS/(a['id']+'.npy'),allow_pickle=False)
        require(sha(idx.tobytes())==a['indices_sha256'],'Frozen pixels changed')
        info=tim2(raw);allowed=np.zeros(info['indices'].shape,bool)
        x0,y0,x1,y1=manifest['label_rect']
        require((x0,y0,x1,y1)==(29,4,237,34),'Unexpected label rectangle')
        for x,y in ((0,0),(0,1),(1,0),(1,1)):
            for state in range(5):allowed[y*200+state*40+y0:y*200+state*40+y1,x*256+x0:x*256+x1]=True
        require(np.array_equal(info['indices'][~allowed],idx[~allowed]),'Protected texture pixels changed')
        new=replace_indices(raw,idx)
        _,flags,_=banlz.parse_header(archive[lo:hi])
        print('Compressing',a['id'],flush=True)
        packed=banlz.compress_record(new,flags=flags)
        require(len(packed)<=hi-lo,'%s exceeds native slot by %d bytes'%(a['id'],len(packed)-(hi-lo)))
        check,used=decode(packed)
        require(check==new and used==len(packed),'Compressed texture verification failed')
        payload=packed+bytes(hi-lo-len(packed))
        changes.append(dict(chunk=i,id=a['id'],start=lo,end=hi,payload=payload,
                            source_sha256=sha(archive[lo:hi]),decoded_sha256=sha(new),
                            compressed_sha256=sha(payload),compressed_bytes=len(packed),
                            headroom=hi-lo-len(packed),labels=a['labels']))
    return disc,manifest,changes


def verify(image,changes):
    target=Disc(image);native=Disc(SOURCE)
    require(target.entries==native.entries and target.size==native.size,'ISO layout changed')
    start=native.entries[VT1]['lba']*2048
    spans=sorted((start+c['start'],start+c['end']) for c in changes)
    changed_bytes=0;protected_bytes=0
    with SOURCE.open('rb') as before,Path(image).open('rb') as after:
        pos=0
        while True:
            a=before.read(8<<20);b=after.read(len(a))
            if not a:break
            require(len(a)==len(b),'Output truncated')
            regions=[(max(lo,pos)-pos,min(hi,pos+len(a))-pos) for lo,hi in spans if lo<pos+len(a) and hi>pos]
            cursor=0
            for lo,hi in regions:
                require(a[cursor:lo]==b[cursor:lo],'Protected ISO bytes changed')
                protected_bytes+=lo-cursor
                changed_bytes+=sum(x!=y for x,y in zip(a[lo:hi],b[lo:hi]));cursor=hi
            require(a[cursor:]==b[cursor:],'Protected ISO bytes changed')
            protected_bytes+=len(a)-cursor;pos+=len(a)
        require(not after.read(1),'Output grew')
    vt1=target.read(VT1)
    for c in changes:
        raw=vt1[c['start']:c['end']]
        require(sha(raw)==c['compressed_sha256'],'Final image texture hash mismatch')
        decoded,used=decode(raw)
        require(sha(decoded)==c['decoded_sha256'],'Final image decoded pixels mismatch')
    return dict(changed_bytes=changed_bytes,protected_bytes=protected_bytes,
                all_bytes_outside_three_vt1_slots_identical=True,
                executable_unchanged=True,font_unchanged=True,story_dialogue_unchanged=True,
                battle_dialogue_unchanged=True,iso_layout_unchanged=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true')
    ap.add_argument('--patch',action='store_true',help='Also create and roundtrip-check an xdelta patch')
    args=ap.parse_args();disc,assets,changes=components()
    rows=[{k:v for k,v in c.items() if k!='payload'} for c in changes]
    print(json.dumps(dict(version=VERSION,output=str(OUT),textures=rows),indent=2),flush=True)
    if not args.write:
        print('DRY RUN passed. No ISO written.');return
    require(not OUT.exists(),'Versioned output already exists')
    require(file_sha(SOURCE)==SOURCE_SHA,'Source ISO identity drift')
    OUT.parent.mkdir(parents=True,exist_ok=True)
    temporary=OUT.with_suffix('.iso.partial');require(not temporary.exists(),'Partial output already exists')
    shutil.copyfile(SOURCE,temporary)
    with temporary.open('r+b') as f:
        for c in changes:
            f.seek(disc.entries[VT1]['lba']*2048+c['start']);f.write(c['payload'])
    checks=verify(temporary,changes)
    result=dict(version=VERSION,scope='12 front-end labels, five states each; story dialogue excluded',
                source_sha256=SOURCE_SHA,output=str(OUT),output_bytes=temporary.stat().st_size,
                output_sha256=file_sha(temporary),textures=rows,validation=checks,runtime='pending',
                asset_manifest_sha256=file_sha(ASSETS/'manifest.json'),
                source_files={str(p.relative_to(ROOT)):file_sha(p) for p in sorted((ROOT/'tools').rglob('*.py'))})
    temporary.rename(OUT)
    receipt=OUT.with_suffix('.json');receipt.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    if args.patch:
        patch=OUT.with_suffix('.xdelta');restored=ROOT/'work/cache/patch-roundtrip.iso'
        require(not patch.exists() and not restored.exists(),'Patch or roundtrip path already exists')
        restored.parent.mkdir(parents=True,exist_ok=True)
        exe=Path('E:/Projects/SRW Z/xdelta3.exe')
        require(exe.is_file(),'Existing xdelta tool missing')
        subprocess.run([str(exe),'-e','-9','-S','none','-s',str(SOURCE),str(OUT),str(patch)],check=True)
        subprocess.run([str(exe),'-d','-s',str(SOURCE),str(patch),str(restored)],check=True)
        require(file_sha(restored)==result['output_sha256'],'Patch roundtrip mismatch')
        result['patch']=dict(path=str(patch),bytes=patch.stat().st_size,sha256=file_sha(patch),roundtrip_verified=True)
        # Delete only the exact scratch file this run created inside this project.
        require(restored.resolve().is_relative_to(ROOT.resolve()),'Scratch path outside workspace')
        restored.unlink()
        receipt.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Build verified:',OUT,flush=True)


if __name__=='__main__':main()
