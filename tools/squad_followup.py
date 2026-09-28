"""Bounded squad confirmation artwork and composed naming/formation help."""
import argparse,json,struct,shutil
import numpy as np
from sp_disc import ROOT,Disc,SOURCE,EXE,sha,file_sha,require,decode,banlz
from menu_encoding import menu_encode
from library_text import text,CHARS
from reuse_compdata import BBASE
from align_story_panels import actual_width
from deployment_ui import render,FONT
from episode_titles import unpack,pack

PREVIOUS=ROOT/'work/output/SRW Z Special Disc English v0.2.23.iso'
COMP='DATA/COMPDATA.BN';ART='KURODATA/KVMDATA.BIN';PAGE=0x20900
FOLDER=ROOT/'work/ui/squad-followup'
BINDINGS=FOLDER/'native-inventory.json'
DRAFT=ROOT/'work/translation/en/squad_followup_draft.json'
REVIEW=ROOT/'work/translation/en/squad_followup_review.json'
# Fixed decoded fields, and existing relocated fields selected by native UI pointers.
FIELDS=[
 ('comp',0x97150,48,'              using this plan.',0x6a0b0),
 ('comp',0x97180,48,'Select a formation plan.',0x6a0b4),
 ('comp',0x971b0,48,'Auto-form squads',0x6a0b8),
 ('comp',0x971e0,48,'            and rename it using',0x6a0c0),
 ('comp',0x97210,56,'a method above. Select a naming method.',0x6a0c4),
 ('pool',0x97248,0,'Select a squad',0x6a0c8),
 ('pool',0x97000,0,"Name squads from members' keywords.",0x6a078),
 ('pool',0x97080,0,'Auto-pick a naming method for each squad.',0x6a084),
 ('comp',0x96600,24,'[Join] Tag',None),
 ('comp',0x96620,24,'[Join] Unit',None),
 ('exe',0x3c1ca0,8,'Sq ',None),
 ('exe',0x3c1ca8,8,' - ',None),
 ('exe',0x3c1cb0,28,'Cancel joining.',None),
 ('exe',0x3c1cd0,28,' - Confirm joining.',None),
]
TILES=[([160,32,208,56],'確定','OK'),([160,56,208,80],'取消','Cancel')]

def measure(value):
    return sum(actual_width(c) if c==' ' or ord(c) in CHARS else 24 for c in value)

def loaded(exe,address):
    po=struct.unpack_from('<I',exe,28)[0];es,n=struct.unpack_from('<HH',exe,42)
    matches=[]
    for i in range(n):
        s=struct.unpack_from('<8I',exe,po+i*es)
        if s[0]==1 and s[2]<=address<s[2]+s[4]:matches.append(s[1]+address-s[2])
    require(len(matches)==1,'Squad UI address is not in exactly one segment')
    return matches[0]

def inventory():
    prior=Disc(PREVIOUS);native=Disc(SOURCE);e=prior.read(EXE);co=decode(prior.read(COMP))[0]
    ne=native.read(EXE);nc=decode(native.read(COMP))[0];entries=[]
    for kind,source_at,cap,value,pointer in FIELDS:
        at=source_at;data=co if kind=='comp'else e;source=ne if kind=='exe'else nc
        if pointer is not None:
            require(struct.unpack_from('<I',nc,pointer)[0]==BBASE+source_at,'Native squad selector')
            address=struct.unpack_from('<I',co,pointer)[0]
            if kind=='pool':
                at=loaded(e,address);old=data[at:].split(b'\0')[0];cap=(len(old)+4)//4*4
            else:require(address==BBASE+source_at,'Fixed squad selector changed')
        encoded=menu_encode(value);require(len(encoded)<cap,'Squad field exceeds allocation')
        row=dict(id=f'{kind}/{source_at:x}',kind=kind,source_offset=source_at,offset=at,capacity=cap,
                 source=source[source_at:].split(b'\0')[0].decode('cp932'),text=value,
                 before_hex=data[at:at+cap].hex(),after_hex=(encoded+bytes(cap-len(encoded))).hex(),
                 width=measure(value),pointer=pointer)
        if kind=='pool':row['address']=address
        entries.append(row)
    kvm=prior.read(ART);native_kvm=native.read(ART)
    require(kvm[PAGE:PAGE+64]==native_kvm[PAGE:PAGE+64] and kvm[PAGE:PAGE+8]==b'TIM2\x04\0\x01\0','Squad atlas identity')
    p=unpack(kvm[PAGE+64:PAGE+32832],256,256)
    for i,(box,source,value)in enumerate(TILES):
        x,y,r,b=box;tile,layout=render(value,box)
        entries.append(dict(id=f'art/{i}',kind='art',source=source,text=value,box=box,
                            before_sha256=sha(p[y:b,x:r].tobytes()),after_sha256=sha(tile.tobytes()),layout=layout))
    return dict(baseline='0.2.23',entries=entries,font_sha256=file_sha(FONT),
        prior_sha256={name:sha(prior.read(name))for name in (EXE,COMP,ART)},
        help_line_limit=430,description_limit=430,header_limit=140,
        callers={'naming': [0x3ffed4,0x3ffee0,0x3ffeec], 'formation':[0x3ffdec,0x3ffdf8,0x3ffe04],
                 'report':[0x3ef734,0x3ef764,0x3ef77c,0x3ef7f4,0x3ef824]},
        notes='Black help lines and red overlay lines share their origin. ASCII spaces advance 13 units; keep the red phrase inside the leading blank region.')

def prepare():
    inv=json.loads(BINDINGS.read_text(encoding='utf8'));draft=json.loads(DRAFT.read_text(encoding='utf8'))
    review=json.loads(REVIEW.read_text(encoding='utf8'))
    require(inv==inventory(),'Squad bindings changed')
    require(draft['bindings_sha256']==file_sha(BINDINGS) and review['draft_sha256']==file_sha(DRAFT),'Squad review drift')
    require(review['entries_examined']==review['entries_in_slice']==len(inv['entries']) and review['verdict']=='pass','Incomplete squad review')
    require(review['entries']==draft['entries']==[dict(id=r['id'],source=r['source'],text=r['text'])for r in inv['entries']],'Squad wording not approved')
    return inv

def compile_component(exe,comp,kvm,inv):
    require({n:sha(v)for n,v in [(EXE,exe),(COMP,comp),(ART,kvm)]}==inv['prior_sha256'],'Squad component must follow 0.2.23 exactly')
    e=bytearray(exe);co=bytearray(decode(comp)[0]);a=bytearray(kvm)
    p=unpack(kvm[PAGE+64:PAGE+32832],256,256);mask=np.zeros((256,256),bool)
    fields=[];tiles=[]
    for r in inv['entries']:
        if r['kind']=='art':
            x,y,z,b=r['box'];tile,layout=render(r['text'],r['box'])
            require(sha(tile.tobytes())==r['after_sha256'],'Frozen squad tile changed')
            p[y:b,x:z]=tile;mask[y:b,x:z]=True;tiles.append(r);continue
        owner=co if r['kind']=='comp'else e;at=r['offset'];cap=r['capacity']
        require(owner[at:at+cap].hex()==r['before_hex'],'Squad field preimage')
        owner[at:at+cap]=bytes.fromhex(r['after_hex']);fields.append(r)
    a[PAGE+64:PAGE+32832]=pack(p)
    indexed=unpack(kvm[PAGE+64:PAGE+32832],256,256)
    require(np.array_equal(indexed[~mask],p[~mask]),'Other squad atlas pixels changed')
    rows={r['id']:r for r in fields}
    for row,overlay,pad in [('comp/97150','comp/971b0',14),('comp/971e0','pool/97248',12)]:
        require(rows[row]['text'].startswith(' '*pad) and rows[overlay]['width']+8<=13*pad,'Squad help color overlay overlap')
    for r in fields:
        if r['source_offset']in (0x97150,0x97180,0x971e0,0x97210,0x97000,0x97080):require(r['width']<=430,'Squad help/description overflow')
        if r['source_offset']in (0x96600,0x96620):require(r['width']<=140,'Squad control heading overflow')
    packed=banlz.compress_record(bytes(co),flags=banlz.parse_header(comp)[1]);require(decode(packed)[0]==co,'Squad overlay compression')
    return bytes(e),packed,bytes(a),dict(fields=fields,tiles=tiles,text_fields=len(fields),image_tiles=len(tiles),
        prior_sha256=inv['prior_sha256'],after_sha256={EXE:sha(e),COMP:sha(packed),ART:sha(a)},
        overlay_gaps=[14*13-rows['comp/971b0']['width'],12*13-rows['pool/97248']['width']],
        runtime='pending by user choice')

def build(exe,comp,kvm):
    e,c,a,report=compile_component(exe,comp,kvm,prepare())
    return e,c,a,dict(report,bindings_sha256=file_sha(BINDINGS),draft_sha256=file_sha(DRAFT),review_sha256=file_sha(REVIEW))

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--prepare',action='store_true');ap.add_argument('--write',action='store_true');args=ap.parse_args()
    require(not args.write or args.prepare,'Only preparation writes metadata')
    if args.prepare:
        inv=inventory();print(json.dumps(inv,ensure_ascii=True,indent=2))
        if not args.write:print('DRY RUN: no files written');return
        FOLDER.mkdir(parents=True,exist_ok=True);BINDINGS.write_text(json.dumps(inv,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        DRAFT.write_text(json.dumps(dict(bindings_sha256=file_sha(BINDINGS),entries=[dict(id=r['id'],source=r['source'],text=r['text'])for r in inv['entries']]),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        from PIL import Image,ImageDraw
        p=unpack(Disc(PREVIOUS).read(ART)[PAGE+64:PAGE+32832],256,256)
        for box,_,value in TILES:
            x,y,r,b=box;p[y:b,x:r]=render(value,box)[0]
        Image.fromarray(p*17).resize((768,768)).save(FOLDER/'english-sheet-4.png')
        for filename,label in [('codex-clipboard-6bdca9f4-1495-413b-a5f6-63174020548f.png','user-join.png'),('codex-clipboard-1de2d1e7-8a2b-46a6-a760-28cb72847002.png','user-naming.png')]:
            src=ROOT.__class__(__import__('tempfile').gettempdir())/filename;dst=FOLDER/label
            shutil.copyfile(src,dst);require(file_sha(src)==file_sha(dst),'Screenshot copy mismatch')
        return
    d=Disc(PREVIOUS);_,_,_,report=build(d.read(EXE),d.read(COMP),d.read(ART));print(json.dumps(report,indent=2));print('DRY RUN: no game files written')

if __name__=='__main__':main()
