"""Bounded combat forecast icon sprites and Getter Robo squad labels."""
import json,struct
import numpy as np
from PIL import Image,ImageDraw
from sp_disc import ROOT,SOURCE,Disc,decode,require,sha,file_sha
from build_story import STAGE,HB,TABLE,repack
from episode_titles import unpack,pack
from deployment_ui import render,FONT
from menu_encoding import menu_encode
from library_text import text

ART='KURODATA/KVMDATA.BIN'
PAGE=0x20900
BASE=0x8045f0
FOLDER=ROOT/'work/ui/combat-forecast'
INVENTORY=ROOT/'work/translation/en/combat_forecast.json'


def build(disc):
    inv=json.loads(INVENTORY.read_text(encoding='utf-8'))
    require(file_sha(FONT)==inv['font_sha256'],'Icon font changed')
    native=Disc(SOURCE);raw=disc.read(ART);nr=native.read(ART)
    require(sha(raw)==inv['art_sha256'],'Forecast atlas input changed')
    require(raw[PAGE:PAGE+64]==nr[PAGE:PAGE+64] and struct.unpack_from('<HH',raw,PAGE+36)==(256,256),'Atlas frame changed')
    before=unpack(raw[PAGE+64:PAGE+32832],256,256);after=before.copy()
    npix=unpack(nr[PAGE+64:PAGE+32832],256,256);mask=np.zeros((256,256),bool);icons=[]
    for e in inv['icons']:
        x,y,r,b=e['box'];old=before[y:b,x:r]
        require(sha(old.tobytes())==e['before_sha256'] and np.array_equal(old,npix[y:b,x:r]),'Icon source changed')
        require(not mask[y:b,x:r].any(),'Overlapping icon edits')
        tile,layout=render(e['text'],e['box']);after[y:b,x:r]=tile;mask[y:b,x:r]=True
        icons.append(dict(e,layout=layout))
    require(np.array_equal(before[~mask],after[~mask]),'Unrelated atlas pixels changed')
    artwork=bytearray(raw);artwork[PAGE+64:PAGE+32832]=pack(after)
    restored=bytearray(artwork);restored[PAGE+64:PAGE+32832]=raw[PAGE+64:PAGE+32832]
    require(restored==raw and np.array_equal(unpack(artwork[PAGE+64:PAGE+32832],256,256),after),'Atlas readback')
    stage=disc.read(STAGE);hb=disc.read(HB);off=struct.unpack_from('<69I',hb,TABLE)
    ns=native.read(STAGE);no=struct.unpack_from('<69I',native.read(HB),TABLE)
    before_chunks={};changed={};fields=[]
    for e in inv['names']:
        c,at=e['chunk'],e['offset'];n=decode(ns[no[c]:no[c+1]])[0]
        if c not in changed:
            before_chunks[c]=decode(stage[off[c]:off[c+1]])[0];changed[c]=bytearray(before_chunks[c])
        old=e['source'].encode('cp932')+b'\0';replacement=menu_encode(e['text'])+b'\0'
        require(len(replacement)<=len(old) and text(replacement[:-1])==e['text'],'Squad name capacity')
        cur=before_chunks[c]
        require(cur[at:at+len(old)]==n[e['native_offset']:e['native_offset']+len(old)]==old,'Squad name preimage')
        pointers=[p for p in range(0,len(cur)-3,4) if struct.unpack_from('<I',cur,p)[0]==BASE+at]
        require(pointers==e['pointers'],'Squad name pointer bindings changed')
        require(all(struct.unpack_from('<I',n,p)[0]==BASE+e['native_offset'] for p in pointers),'Native squad name pointer')
        changed[c][at:at+len(old)]=replacement+bytes(len(old)-len(replacement));fields.append(e)
    for c,out in changed.items():
        restored=bytearray(out)
        for e in fields:
            if e['chunk']==c:
                at=e['offset'];size=len(e['source'].encode('cp932'))+1
                restored[at:at+size]=before_chunks[c][at:at+size]
        require(restored==before_chunks[c],'Changed stage data outside selected name strings')
    newstage,newhb,_=repack(stage,hb,{c:bytes(v) for c,v in changed.items()})
    newoff=struct.unpack_from('<69I',newhb,TABLE)
    for c in range(68):
        old=stage[off[c]:off[c+1]];new=newstage[newoff[c]:newoff[c+1]]
        require(decode(new)[0]==changed[c] if c in changed else old==new,'Stage chunk readback')
    restored=bytearray(newhb);restored[TABLE:TABLE+276]=hb[TABLE:TABLE+276]
    require(restored==hb,'HB change outside stage table')
    return {ART:bytes(artwork),STAGE:newstage,HB:newhb},dict(icons=icons,fields=fields,chunks=sorted(changed),
        protected_pixels_and_stage_bytes_verified=True,all_68_stage_chunks_verified=True,emulator='pending')
