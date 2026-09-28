"""Reviewed late menu table, tournament roster names and squad word sprites.

Only typed name pointers change in chapter 13; its complete dialogue and
gameplay bytes are otherwise restored and compared with the pristine chunk.
"""
import argparse,json,struct
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from sp_disc import ROOT,Disc,SOURCE,decode,banlz,sha,file_sha,require
from menu_encoding import menu_encode,TOKENS
from collections import Counter
from reuse_compdata import POOL_BASE,BBASE
from glossary_terms import canonicalize
from save_summary_text import width
from episode_titles import unpack,pack

BINDINGS=ROOT/'work/ui/deployment/native-inventory.json'
DRAFT=ROOT/'work/translation/en/deployment_ui_draft.json'
REVIEW=ROOT/'work/translation/en/deployment_ui_review.json'
TARGET=ROOT/'work/translation/en/deployment_ui.json'
FONT=Path('C:/Windows/Fonts/arialbd.ttf')
COMP='DATA/COMPDATA.BN';STAGE='DATA/STAGE.BIN';ART='KURODATA/KVMDATA.BIN'
STAGE_BASE=0x8045f0;LO=173296;HI=189648;SHEET=0x38fc0
STAGE_SHA='86d115d71dcfc4495ec77ada5acad22adbd88cfd6deb772253011852386c5c35'
ART_SHA='e6cca493d595c990c0da8dd2020f6dc99db5d3abb055adf615e4328349e88300'
BOXES={'graphic/new':[98,24,173,47], 'graphic/reserve':[174,24,256,47],
       'graphic/squads':[40,177,112,200], 'graphic/deployed':[136,160,158,215]}

def render(value,box,vertical=False):
    x,y,r,b=box;w,h=r-x,b-y
    if vertical:w,h=h,w
    for size in range(16,9,-1):
        font=ImageFont.truetype(str(FONT),size*4);bb=font.getbbox(value,stroke_width=4)
        tw,th=bb[2]-bb[0],bb[3]-bb[1]
        if tw<=(w-2)*4 and th<=(h-2)*4:break
    else:raise ValueError('Squad artwork overflow: '+value)
    fill=Image.new('L',(w*4,h*4));stroke=Image.new('L',fill.size)
    pos=((w*4-tw)//2-bb[0],(h*4-th)//2-bb[1])
    ImageDraw.Draw(fill).text(pos,value,font=font,fill=255)
    ImageDraw.Draw(stroke).text(pos,value,font=font,fill=255,stroke_width=4,stroke_fill=255)
    a=np.asarray(fill.resize((w,h),Image.Resampling.LANCZOS),dtype=np.uint16)
    s=np.asarray(stroke.resize((w,h),Image.Resampling.LANCZOS))
    pixels=np.where(s>=32,1,0).astype(np.uint8)
    pixels=np.where(a>=16,1+(a*14+127)//255,pixels).astype(np.uint8)
    if vertical:pixels=np.rot90(pixels).copy()
    yy,xx=np.nonzero(pixels)
    require(len(xx)>0 and xx.min()>0 and yy.min()>0 and xx.max()<r-x-1 and yy.max()<b-y-1,
            'Squad artwork touches tile edge')
    return pixels,dict(font_size=size,ink_bbox=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],
                       rotation=90 if vertical else 0,pixel_sha256=sha(pixels.tobytes()))

def prepare():
    inv=json.loads(BINDINGS.read_text(encoding='utf8'));draft=json.loads(DRAFT.read_text(encoding='utf8'))
    review=json.loads(REVIEW.read_text(encoding='utf8'))
    require(draft['bindings_sha256']==file_sha(BINDINGS) and review['draft_sha256']==file_sha(DRAFT),
            'Deployment review input drift')
    require(review['entries_examined']==review['entries_in_slice']==113,'Deployment incomplete review')
    require([r['id'] for r in review['entries']]==[r['id'] for r in draft['entries']],'Deployment review inventory')
    entries=[];layouts={}
    for src,checked in zip(draft['entries'],review['entries']):
        require(checked['verdict']=='pass','Unreviewed deployment UI')
        value=canonicalize(checked['text']);row=dict(src,text=value)
        require(Counter(TOKENS.findall(src['source']))==Counter(TOKENS.findall(value)),'Deployment controls changed')
        if row['id'].startswith('menu/'):
            row['line_widths']=[width(line) for line in value.splitlines()]
            require(max(row['line_widths'])<=560,'Deployment hint width overflow '+row['id'])
        if row['id'].startswith('stage/'):
            require(len(menu_encode(value))+1<=28 and width(value)<=190,'Squad name display overflow')
        if row['id'] in BOXES:
            _,layout=render(value,BOXES[row['id']],row['id']=='graphic/deployed');layouts[row['id']]=layout
        entries.append(row)
    return dict(schema_version=1,status='meaning-reviewed',entries=entries,deferred=draft['deferred'],
                bindings_sha256=file_sha(BINDINGS),review_sha256=file_sha(REVIEW),
                font_sha256=file_sha(FONT),boxes=BOXES,layouts=layouts,
                menu_line_limit=560,stage_name_limit=190)

def artwork(entries):
    raw=Disc(SOURCE).read(ART);require(sha(raw)==ART_SHA,'Squad source artwork drift')
    require(raw[SHEET:SHEET+8]==b'TIM2\x04\0\x01\0' and
            struct.unpack_from('<HH',raw,SHEET+36)==(256,256),'Squad word sheet layout')
    pixels=unpack(raw[SHEET+64:SHEET+32832],256,256);out=pixels.copy();rows=[]
    for row in entries:
        key=row['id']
        if key not in BOXES:continue
        box=BOXES[key];x,y,r,b=box;tile,layout=render(row['text'],box,key=='graphic/deployed')
        out[y:b,x:r]=tile;rows.append(dict(id=key,text=row['text'],box=box,**layout))
    return raw[:SHEET+64]+pack(out)+raw[SHEET+32832:],rows,pixels,out

def assert_story_preserved(stage,entries=None):
    native=Disc(SOURCE).read(STAGE)
    require(len(stage)==len(native) and stage[44016:LO]==native[44016:LO] and stage[HI:]==native[HI:],
            'Story chunk outside tournament roster changed')
    old=decode(native[LO:HI])[0];new,used=decode(stage[LO:HI]);require(sha(old)==STAGE_SHA,'Tournament source drift')
    require(len(new)==len(old) and not any(stage[LO+used:HI]),'Tournament chunk bounds/padding')
    protected=bytearray(new);inv=json.loads(BINDINGS.read_text(encoding='utf8'))
    sites=[p for r in inv['stage_names'] for p in r['pointer_sites']]
    expected=[base+i*32+28 for base,count in ((0x3fa0,12),(0x4140,3),(0x41c0,12)) for i in range(count)]
    require(sorted(sites)==sorted(expected),'Tournament typed roster pointer ownership')
    for p in sites:protected[p:p+4]=old[p:p+4]
    require(protected==old,'Tournament dialogue/gameplay bytes changed')
    if entries is not None:
        for row in entries:
            if row['id'].startswith('stage/'):
                for p in row['pointer_sites']:
                    require(struct.unpack_from('<I',new,p)[0]==row['relocated_address'],'Tournament name pointer mismatch')
    return dict(other_story_chunks_compressed_identical=66,tournament_name_pointers=27,
                tournament_all_other_decoded_bytes_identical=True,story_dialogue_unchanged=True)

def build(pool,comp,stage):
    cfg=json.loads(TARGET.read_text(encoding='utf8'));require(cfg==prepare(),'Deployment frozen translation/layout drift')
    disc=Disc(SOURCE);native_comp=decode(disc.read(COMP))[0];comp_raw=decode(comp)[0];co=bytearray(comp_raw)
    source_stage=disc.read(STAGE);native_stage=decode(source_stage[LO:HI])[0];st=bytearray(native_stage)
    require(stage[44016:]==source_stage[44016:],'Unexpected earlier chapter edits')
    pool=bytearray(pool);entries=[];restored=bytearray(comp_raw)
    for row in cfg['entries']:
        if not row['id'].startswith(('menu/','stage/')):continue
        menu=row['id'].startswith('menu/');native=native_comp if menu else native_stage;owner=co if menu else st
        base=BBASE if menu else STAGE_BASE;at=row['offset'];raw=native[at:].split(b'\0')[0]
        require(sha(raw)==row['source_sha256'],'Deployment source text binding '+row['id'])
        address=POOL_BASE+len(pool);pool.extend(menu_encode(row['text'])+b'\0');pool.extend(bytes(-len(pool)%4))
        for p in row['pointer_sites']:
            require(struct.unpack_from('<I',owner,p)[0]==base+at,'Deployment pointer conflict')
            struct.pack_into('<I',owner,p,address)
        entries.append(dict(row,relocated_address=address))
    for row in entries:
        if row['id'].startswith('menu/'):
            for p in row['pointer_sites']:restored[p:p+4]=co[p:p+4]
    require(restored==co,'COMPDATA changed outside approved pointer sites')
    packed_comp=banlz.compress_record(bytes(co),flags=banlz.parse_header(comp)[1])
    require(decode(packed_comp)[0]==co,'Deployment COMPDATA compression')
    packed_stage=banlz.compress_record(bytes(st),flags=banlz.parse_header(source_stage[LO:HI])[1])
    if len(packed_stage)>HI-LO:
        packed_stage=banlz.compress_record_optimal(bytes(st),flags=banlz.parse_header(source_stage[LO:HI])[1])
    require(len(packed_stage)<=HI-LO and decode(packed_stage)[0]==st,'Tournament compression allocation')
    stage=stage[:LO]+packed_stage+bytes(HI-LO-len(packed_stage))+stage[HI:]
    story=assert_story_preserved(stage,entries);art,graphics,_,_=artwork(cfg['entries'])
    report=dict(menu_entries=96,stage_names=12,graphics=graphics,entries=entries,heading='Squads',
                deferred=cfg['deferred'],target_sha256=file_sha(TARGET),bindings_sha256=file_sha(BINDINGS),
                review_sha256=file_sha(REVIEW),stage_compressed_bytes=len(packed_stage),story=story,
                comp_before_sha256=sha(comp_raw),comp_decoded_sha256=sha(co),art_sha256=sha(art),
                runtime='pending by user choice')
    return bytes(pool),{COMP:packed_comp,STAGE:stage,ART:art},report

def preview(cfg):
    _,rows,old,new=artwork(cfg['entries']);canvas=Image.new('RGB',(840,500),(20,23,26));d=ImageDraw.Draw(canvas)
    d.text((15,10),'Squad word-sheet assets: native / English (not emulator capture)',fill='white')
    for j,p in enumerate((old,new)):
        # Use a neutral ramp to show the shared indices; game selects its color bank.
        im=Image.fromarray((p*17).astype(np.uint8)).convert('RGB').resize((384,384),Image.Resampling.NEAREST)
        canvas.paste(im,(15+j*420,38))
    d.text((15,438),'Heading: Squads     |     <Deploy> Prepare for deployment.',fill='white')
    d.text((15,462),'Tournament: QF Group 1-8 / Round 1 Losers / Argama / Minerva / King Beal',fill='white')
    canvas.save(ROOT/'work/ui/deployment/english-0.2.18.png')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args()
    cfg=prepare();_,rows,_,_=artwork(cfg['entries'])
    print(json.dumps(dict(entries=len(cfg['entries']),graphics=rows,heading_override={'exe/3b1100':'Squads'},
                         samples=[r for r in cfg['entries'] if r['id'] in ('menu/978f0','stage/13/a3c0')]),ensure_ascii=True,indent=2))
    if not a.write:print('DRY RUN: no files written');return
    TARGET.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    path=ROOT/'work/translation/en/system_overrides.json';overrides=json.loads(path.read_text(encoding='utf8'))
    require(overrides.get('exe/3b1100') in (None,'Squads'),'Conflicting heading override')
    overrides['exe/3b1100']='Squads';path.write_text(json.dumps(overrides,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    preview(cfg)

if __name__=='__main__':main()
