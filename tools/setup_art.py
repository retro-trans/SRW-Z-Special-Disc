"""Native indexed artwork for intermission, Bazaar and the scrolling banner."""
import argparse,json,math,struct
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from sp_disc import ROOT,Disc,SOURCE,EXE,sha,file_sha,require
from library_text import ORIGINAL,DONOR
from episode_titles import unpack,pack
from inspect_archive_graphics import picture

MEMBER='KURODATA/KVMDATA.BIN'
PREVIOUS=ROOT/'work/output/SRW Z Special Disc English v0.2.22.iso'
FOLDER=ROOT/'work/ui/setup-art'
BINDINGS=FOLDER/'native-inventory.json'
DRAFT=ROOT/'work/translation/en/setup_art_draft.json'
REVIEW=ROOT/'work/translation/en/setup_art_review.json'
FONT=ROOT.__class__('C:/Windows/Fonts/georgiab.ttf')
MENU_FONT=ROOT.__class__('C:/Windows/Fonts/arialbd.ttf')
PAGES={5:0x28b40,6:0x30d80,10:0x52080}
# Exclusive bounds. Reuse requires both the Japanese tile and palette to match.
DONOR_TILES=[
 (6,[4,1,208,31],'インターミッション','INTERMISSION'),
 (6,[2,107,210,134],'インターミッション','INTERMISSION'),
 (6,[2,138,61,157],'機体系','Units'),
 (6,[139,138,233,157],'パイロット系','Pilots'),
 (6,[4,163,59,181],'バザー','Bazaar'),
 (6,[65,162,159,181],'次のマップへ','Next Map'),
 (6,[3,187,97,205],'オプション','Options'),
 (6,[5,210,85,229],'小隊編成','Squads'),
 (6,[5,234,107,253],'データ管理','Data'),
 (5,[0,96,64,128],'購入','Buy'),(5,[0,128,64,160],'売却','Sell'),
 (5,[0,160,80,184],'強化パーツ','Parts'),(5,[0,184,56,208],'アイテム','Items'),
 (5,[0,208,40,232],'機体','Units'),
 (5,[142,2,166,30],'第','EP'),(5,[208,0,255,32],'資金','Funds'),
 (5,[148,40,235,63],'ＳＲポイント','SR Points')]
TABLE=0x3a0440
MARQUEE=[(0,'第','Cleared through EP '),(1,'話「',' "'),(2,'」までクリア！','"'),
         (3,'NEXT. 出撃','NEXT: Deploy '),(4,'小隊',' squads'),(6,'遂行中','In progress')]
CODE=[(0x3fd104,0x24060023,0x2406001b),(0x3fd108,0x3c024060,0x3c020000),
      (0x3fd0f4,0x3c024080,0x3c020000),(0x3fd128,0x3c024080,0x3c020000),
      (0x3ff088,0x02a0a02d,0x2414ffff),(0x3ff098,0x2412000a,0x2412000e),
      (0x3ff0c4,0x24130010,0x2413000c),(0x3ff0c8,0x2412000d,0x2412000e),
      (0x3ff0e4,0x0000a02d,0x2414ffff),(0x3ff0e8,0x0012943f,0x2412000e),
      (0x3ff0ec,0x24130014,0x2413000c)]

def pixels(blob,page):
    p=PAGES[page]
    require(blob[p:p+8]==b'TIM2\x04\0\x01\0' and struct.unpack_from('<HH',blob,p+36)==(256,256),'Word sheet layout')
    return unpack(blob[p+64:p+32832],256,256)

def render(value,w=None,h=24,size=20):
    font=ImageFont.truetype(str(FONT),size*4)
    if w is None:w=math.ceil((font.getlength(value)/4+4)/3)*3
    require(w<256,'Artwork exceeds sheet')
    while font.getlength(value)>(w-4)*4:
        size-=1;require(size>=10,'Artwork too small');font=ImageFont.truetype(str(FONT),size*4)
    im=Image.new('L',(w*4,h*4));d=ImageDraw.Draw(im)
    baseline=18 if h==24 else (h+size)//2-3
    xy=(8,baseline*4);bounds=d.textbbox(xy,value,font=font,anchor='ls')
    require(bounds[0]>=0 and bounds[1]>=0 and bounds[2]<w*4 and bounds[3]<h*4,'Artwork clipped')
    d.text(xy,value,font=font,anchor='ls',fill=255)
    alpha=np.asarray(im.resize((w,h),Image.Resampling.LANCZOS))
    out=np.zeros((h,w),np.uint8);out[1:,1:]=np.where(alpha[:-1,:-1]>=128,4,0)
    out=np.where(alpha>=160,15,np.where(alpha>=56,11,out)).astype(np.uint8)
    return out

def intermission_tile(box):
    # Keep the semantic split of the source: INTER | MISSION. The latter
    # occupies the Japanese MISSION subregion, so cropped heading consumers
    # do not receive the middle of a proportionally spaced English word.
    x,y,r,b=box;w,h=r-x,b-y;scale=4;font=ImageFont.truetype(str(MENU_FONT),22*scale)
    fill=Image.new('L',(w*scale,h*scale));edge=Image.new('L',fill.size)
    boundary=96-x;baseline=(h+16)//2
    for value,px in [('INTER',(boundary-2)*scale-font.getlength('INTER')),('MISSION',(boundary+1)*scale)]:
        pos=(px,baseline*scale)
        bounds=ImageDraw.Draw(fill).textbbox(pos,value,font=font,anchor='ls',stroke_width=scale)
        require(bounds[0]>=0 and bounds[2]<w*scale and bounds[1]>=0 and bounds[3]<h*scale,'Split heading bounds')
        ImageDraw.Draw(fill).text(pos,value,font=font,anchor='ls',fill=255)
        ImageDraw.Draw(edge).text(pos,value,font=font,anchor='ls',fill=255,stroke_width=scale,stroke_fill=255)
    a=np.asarray(fill.resize((w,h),Image.Resampling.LANCZOS));s=np.asarray(edge.resize((w,h),Image.Resampling.LANCZOS))
    return np.where(a>=160,14,np.where(a>=48,7,np.where(s>=48,8,0))).astype(np.uint8)

def inventory():
    native=Disc(SOURCE);prior=Disc(PREVIOUS);b=native.read(MEMBER)
    orig=(ORIGINAL/'KURODATA_KVMDATA.BIN').read_bytes();donor=Disc(DONOR,True).read(MEMBER)
    entries=[]
    for i,(page,box,jp,en) in enumerate(DONOR_TILES):
        x,y,r,t=box;old=pixels(b,page)[y:t,x:r];a=pixels(orig,page)[y:t,x:r];c=pixels(donor,page)[y:t,x:r]
        require(np.array_equal(old,a),'Native donor tile differs: '+en)
        p=PAGES[page];require(b[p+32832:p+33344]==orig[p+32832:p+33344]==donor[p+32832:p+33344],'Palette differs')
        if i<2:c=intermission_tile(box)
        entries.append(dict(id=f'donor/{i}',page=page,box=box,source=jp,text=en,native_pixel_sha256=sha(old.tobytes()),english_pixel_sha256=sha(c.tobytes()),technique='split INTER / MISSION artwork' if i<2 else 'matched donor tile'))
    entries.append(dict(id='bazaar/title',page=5,box=[0,0,142,64],source='バザー',text='BAZAAR'))
    for j,(record,jp,en) in enumerate(MARQUEE):
        tile=render(en);h,w=tile.shape;y=104+j*24
        require(not np.any(pixels(b,10)[y:y+h,:w]),'Banner destination occupied')
        entries.append(dict(id=f'marquee/{record}',page=10,box=[0,y,w,y+h],record=record,source=jp,text=en))
    entries.append(dict(id='marquee/11',page=10,box=[144,24,255,48],record=11,source='プロローグ',text='Prologue'))
    w=render('Cleared through "').shape[1]
    entries.append(dict(id='marquee/10',page=10,box=[24,128,24+w,152],record=10,source='「 (prologue prefix)',text='Cleared through "'))
    for row in entries:
        if 'english_pixel_sha256' not in row:
            x,y,r,bottom=row['box'];tile=render(row['text'],r-x,bottom-y,36 if row['id']=='bazaar/title' else 20)
            row['english_pixel_sha256']=sha(tile.tobytes())
    return dict(schema_version=1,baseline='0.2.22',native_sha256=sha(b),prior_sha256=sha(prior.read(MEMBER)),
        prior_exe_sha256=sha(prior.read(EXE)),original_sha256=sha(orig),donor_sha256=sha(donor),
        font_sha256=file_sha(FONT),menu_font_sha256=file_sha(MENU_FONT),table_offset=TABLE,native_table_hex=native.read(EXE)[TABLE:TABLE+168].hex(),
        entries=entries,code=[dict(va=va,before=old,after=new)for va,old,new in CODE])

def compile_component(exe,kvm,inv):
    oldexe=bytes(exe);out=bytearray(exe);result=bytearray(kvm);pages={p:pixels(kvm,p) for p in PAGES}
    allowed={p:np.zeros((256,256),bool) for p in PAGES};donor=Disc(DONOR,True).read(MEMBER);spans=[];tiles=[]
    require(exe[TABLE:TABLE+168].hex()==inv['native_table_hex'],'Banner table preimage')
    for row in inv['entries']:
        page=row['page'];x,y,r,b=row['box'];value=row['text'];allowed[page][y:b,x:r]=True
        if row['id'].startswith('donor/'):
            tile=intermission_tile(row['box']) if row['id'] in ('donor/0','donor/1') else pixels(donor,page)[y:b,x:r];require(sha(pages[page][y:b,x:r].tobytes())==row['native_pixel_sha256'],'Donor tile preimage')
            require(sha(tile.tobytes())==row['english_pixel_sha256'],'Donor tile lock')
        else:tile=render(value,r-x,b-y,36 if row['id']=='bazaar/title' else 20)
        pages[page][y:b,x:r]=tile
        tiles.append(dict(row,pixel_sha256=sha(tile.tobytes())))
        if row['id'].startswith('marquee/'):
            at=TABLE+row['record']*14
            payload=struct.pack('<4B3h',x,y,r,b,(r-x)*2//3,16,-1)
            out[at:at+10]=payload
            spans.append(dict(offset=at,before_hex=oldexe[at:at+10].hex(),after_hex=payload.hex()))
    for va,old,new in CODE:
        at=va-0xff680;require(struct.unpack_from('<I',exe,at)[0]==old,'Banner instruction preimage')
        struct.pack_into('<I',out,at,new);spans.append(dict(offset=at,before_hex=struct.pack('<I',old).hex(),after_hex=struct.pack('<I',new).hex()))
    # Existing Latin MISSION/NORMAL/HARD/EX-HARD fragments share the same
    # baseline and aspect ratio as the new gold mission-status fragment.
    for record in (5,7,8,9):
        at=TABLE+record*14;x,y,r,b=struct.unpack_from('<4B',exe,at)
        payload=struct.pack('<3h',(r-x)*2//3,16,-1)
        out[at+4:at+10]=payload
        spans.append(dict(offset=at+4,before_hex=exe[at+4:at+10].hex(),after_hex=payload.hex()))
    restored=bytearray(out)
    for row in spans:at=row['offset'];v=bytes.fromhex(row['before_hex']);restored[at:at+len(v)]=v
    require(restored==oldexe,'Unapproved executable edit')
    for page in pages:
        p=PAGES[page];require(np.array_equal(pages[page][~allowed[page]],pixels(kvm,page)[~allowed[page]]),'Unapproved word pixels')
        result[p+64:p+32832]=pack(pages[page])
    return bytes(out),bytes(result),dict(tiles=tiles,exe_spans=spans,before_sha256=sha(kvm),after_sha256=sha(result),
        indexed_palettes_and_animation_unchanged=True,story_dialogue_unchanged=True,runtime='pending by user choice')

def prepare():
    inv=json.loads(BINDINGS.read_text(encoding='utf8'));draft=json.loads(DRAFT.read_text(encoding='utf8'));review=json.loads(REVIEW.read_text(encoding='utf8'))
    require(inv==inventory(),'Setup artwork input drift')
    require(draft['bindings_sha256']==file_sha(BINDINGS) and review['draft_sha256']==file_sha(DRAFT),'Setup review binding')
    require(review['verdict']=='pass' and review['entries_examined']==review['entries_in_slice']==len(inv['entries']),'Setup meaning review incomplete')
    require(review['entries']==draft['entries'],'Setup reviewed text differs')
    return inv

def build(exe,kvm):
    a,b,report=compile_component(exe,kvm,prepare())
    return a,b,dict(report,bindings_sha256=file_sha(BINDINGS),draft_sha256=file_sha(DRAFT),review_sha256=file_sha(REVIEW))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepare',action='store_true');p.add_argument('--write',action='store_true');a=p.parse_args()
    inv=inventory();prior=Disc(PREVIOUS);_,kvm,report=compile_component(prior.read(EXE),prior.read(MEMBER),inv)
    print(json.dumps(dict(entries=[dict(id=r['id'],source=r['source'],text=r['text'],box=r['box'])for r in inv['entries']],changed_tiles=len(report['tiles']),changed_exe_spans=len(report['exe_spans'])),ensure_ascii=True,indent=2))
    if a.write:
        require(a.prepare,'Use main builder to write game data')
        BINDINGS.write_text(json.dumps(inv,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        entries=[dict(id=r['id'],source=r['source'],text=r['text'])for r in inv['entries']]
        DRAFT.write_text(json.dumps(dict(bindings_sha256=file_sha(BINDINGS),entries=entries),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        for page,offset in PAGES.items():picture(kvm[offset:offset+33344]).resize((768,768)).save(FOLDER/f'english-{page}.png')
    else:print('DRY RUN: no game files or metadata written')

if __name__=='__main__':main()
