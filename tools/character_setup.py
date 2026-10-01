"""Reuse the six matching SRW Z character setup label tiles."""
import argparse,json,shutil
import numpy as np
from sp_disc import ROOT,SOURCE,Disc,sha,require
from library_text import ORIGINAL,DONOR
from setup_art import pixels
from episode_titles import pack,unpack
from inspect_archive_graphics import picture

MEMBER='KURODATA/KVMDATA.BIN'
PAGE=0x28B40
BASE_SHA='25adbb92e6503effd2b9c8b29042593c9a63829eec75c355c314131d2a9aaf00'
FOLDER=ROOT/'work/ui/character-setup'
TILES=(
 ('name',(216,112,256,136),'NAME','Name'),
 ('nickname',(216,136,256,160),'ALIAS','Nickname'),
 ('confirm',(216,160,256,184),'OK','Confirm'),
 ('birthday',(200,184,256,208),'BORN','Birthday'),
 ('blood_type',(200,208,256,232),'BLOOD','Blood Type'),
 ('rename',(184,232,256,256),'RENAME','Rename'),
)


def build(current):
    require(sha(current)==BASE_SHA,'Character setup baseline changed')
    native=Disc(SOURCE).read(MEMBER)
    original=(ORIGINAL/'KURODATA_KVMDATA.BIN').read_bytes()
    donor=Disc(DONOR,True).read(MEMBER)
    # Texture dimensions, encoding and all CLUT banks must match exactly.
    for data in (current,original,donor):
        require(data[PAGE:PAGE+64]==native[PAGE:PAGE+64],'Character sheet header mismatch')
        require(data[PAGE+32832:PAGE+33344]==native[PAGE+32832:PAGE+33344],'Character sheet palette mismatch')
    old=pixels(current,5);out=old.copy();allowed=np.zeros(old.shape,bool);rows=[]
    for key,box,label,meaning in TILES:
        x,y,r,b=box;a=pixels(native,5)[y:b,x:r];z=pixels(original,5)[y:b,x:r]
        value=pixels(donor,5)[y:b,x:r]
        require(np.array_equal(a,z) and np.array_equal(a,old[y:b,x:r]),'Native tile identity '+key)
        require(not np.array_equal(a,value),'Donor tile is untranslated '+key)
        out[y:b,x:r]=value;allowed[y:b,x:r]=True
        rows.append(dict(id=key,box=box,text=label,meaning=meaning,
                         native_pixel_sha256=sha(a.tobytes()),english_pixel_sha256=sha(value.tobytes())))
    require(np.array_equal(old[~allowed],out[~allowed]),'Pixels outside labels changed')
    payload=pack(out);require(np.array_equal(unpack(payload,256,256),out),'Indexed texture roundtrip')
    result=bytearray(current);result[PAGE+64:PAGE+32832]=payload
    require(result[:PAGE+64]==current[:PAGE+64] and result[PAGE+32832:]==current[PAGE+32832:],
            'Header, palette or unrelated archive data changed')
    return bytes(result),dict(member=MEMBER,page=5,page_offset=PAGE,entries=rows,
        source_sha256=sha(current),donor_sha256=sha(donor),result_sha256=sha(result),
        modified_pixels=int(np.count_nonzero(old!=out)),geometry_and_palettes_unchanged=True,
        scope='Shared character setup labels, including male and female protagonists',emulator='pending')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepare',action='store_true')
    p.add_argument('--screenshot',type=type(ROOT),help='Optional local before screenshot')
    a=p.parse_args();disc=Disc(ROOT/'work/output/SRW Z Special Disc English v0.3.2.iso')
    result,report=build(disc.read(MEMBER));print(json.dumps(report,indent=2))
    if not a.prepare:print('DRY RUN: no game files written');return
    FOLDER.mkdir(parents=True,exist_ok=True)
    (FOLDER/'build-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    picture(result[PAGE:PAGE+33344]).resize((768,768)).save(FOLDER/'english-page5.png')
    (ROOT/'work/translation/en/character_setup.json').write_text(json.dumps(dict(version='0.3.3',entries=report['entries']),indent=2)+'\n',encoding='utf-8')
    if a.screenshot and not (FOLDER/'user-before.png').exists():
        shutil.copyfile(a.screenshot,FOLDER/'user-before.png')

if __name__=='__main__':main()
