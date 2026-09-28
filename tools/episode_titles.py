"""English episode-entry title cards in VT1 group 9, with pinned source bindings.

Format reference: dyzz/srwz-zh docs/special-disc/STAGE_ENTRY_TITLES_20260920.md.
Only title pixels and the shared ordinal-word pixels are writable.
"""
import argparse
import json
import struct
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from sp_disc import ROOT, source_records, decode, sha, file_sha, require, banlz

TABLE=0x3763e0
BINDINGS=ROOT/'work/ui/episode-titles/native-inventory.json'
REVIEW=ROOT/'work/translation/en/episode_titles_review.json'
TARGET=ROOT/'work/translation/en/episode_titles.json'
FONT=Path('C:/Windows/Fonts/timesbd.ttf')
GROUP_SHA='faf618cf15f4e968e099af5ba72494e4b6769b73314ab0e3349da35535e8ea76'
TABLE_SHA='987d699f091d20630635370e08c4d9b79d8faf83c40151c4e3b6463b60bd4492'

def unpack(raw,w,h):
    require(len(raw)==w*h//2,'Episode texture byte count')
    v=np.frombuffer(raw,np.uint8)
    return np.stack((v&15,v>>4),axis=-1).reshape(h,w).copy()

def pack(pixels):
    require(pixels.dtype==np.uint8 and pixels.ndim==2 and pixels.shape[1]%2==0 and
            int(pixels.max())<=15,'Episode texture pixel format')
    return (pixels[:,::2]|pixels[:,1::2]<<4).tobytes()

def native():
    disc,exe,vt,outer=source_records()
    require(sha(vt[outer[9]:outer[10]])==GROUP_SHA and sha(exe[TABLE:TABLE+112])==TABLE_SHA,
            'Episode archive/table identity')
    offsets=struct.unpack_from('<28I',exe,TABLE)
    require(offsets[0]==0 and offsets[-1]==outer[10]-outer[9], 'Episode archive bounds')
    inv=json.loads(BINDINGS.read_text(encoding='utf-8'))
    require(inv['group_sha256']==GROUP_SHA and inv['table_sha256']==TABLE_SHA,'Episode binding identity')
    rows=[]
    for i,(lo,hi) in enumerate(zip(offsets,offsets[1:])):
        start,end=outer[9]+lo,outer[9]+hi;stored=vt[start:end];raw,used=decode(stored)
        require(not any(stored[used:]),'Episode compressed padding')
        meta=inv['records'][i]
        require((meta['index'],meta['start'],meta['end'],meta['decoded_sha256'])==
                (i,start,end,sha(raw)), 'Episode native record drift')
        if i>=6:
            require(len(raw)==16608 and raw[32:40]==b'TIM2\x04\0\x01\0' and
                    struct.unpack_from('<HH',raw,68)==(512,64),'Episode TIM2 layout')
        rows.append(dict(index=i,start=start,end=end,raw=raw,stored=stored))
    # Bind selectors to typed COMPDATA title fields, not the image's Japanese OCR.
    comp,_=decode(disc.read('DATA/COMPDATA.BN'));actual=[]
    for chunk in range(1,30):
        at=0x68630+(chunk-1)*48;ptr=struct.unpack_from('<I',comp,at)[0]
        name=comp[ptr-0x764f80:].split(b'\0')[0].decode('cp932')
        if name=='予備':continue
        actual.append((chunk,struct.unpack_from('<H',comp,at+28)[0],name))
    require(actual==[(r['chunk'],r['selector'],r['source']) for r in inv['bindings']],
            'Episode COMPDATA selector binding drift')
    require(len(actual)==24 and sorted(set(r[1] for r in actual))==list(range(1,22)),
            'Incomplete episode category')
    return rows,inv

def render(text):
    require(text and text.isascii() and '\n' not in text,'Invalid episode title')
    # Game stretches the texture vertically twice as much as horizontally.
    # Draw square-pixel lettering on a 256-wide canvas, then double columns.
    for size in range(24,16,-1):
        font=ImageFont.truetype(str(FONT),size);box=font.getbbox(text)
        w,h=box[2]-box[0],box[3]-box[1]
        if w<=248 and h<=24:break
    else:raise ValueError('Full episode title exceeds safe area: '+text)
    im=Image.new('L',(256,64));ImageDraw.Draw(im).text(((256-w)//2-box[0],4+(24-h)//2-box[1]),
                                                  text,font=font,fill=255)
    pixels=((np.asarray(im,dtype=np.uint16)*15+127)//255).astype(np.uint8)
    pixels=np.repeat(pixels,2,axis=1)
    require(not pixels[:4].any() and not pixels[28:].any() and
            not pixels[:,:8].any() and not pixels[:,-8:].any(), 'Episode title clipping')
    return pack(pixels),dict(font_size=size,ink_bbox=list(im.getbbox()),double_columns=True,full_text_preserved=True)

def header(raw):
    # Second TIM2 in shared record 4: 416x24; digits occupy x=0..319,
    # the ordinal prefix/suffix each occupy a 48x24 tile. Keep every digit.
    at,end=197376,202368
    require(raw[197312:197320]==b'TIM2\x04\0\x01\0' and
            struct.unpack_from('<HH',raw,197348)==(416,24),'Episode number atlas layout')
    pixels=unpack(raw[at:end],416,24);pixels[:,320:]=0
    font=ImageFont.truetype(str(FONT),18);box=font.getbbox('Ep.')
    im=Image.new('L',(24,24));ImageDraw.Draw(im).text(((24-(box[2]-box[0]))//2-box[0],
                       (24-(box[3]-box[1]))//2-box[1]),'Ep.',font=font,fill=255)
    require(im.getbbox()[0]>=0 and im.getbbox()[2]<=24,'Episode prefix clipping')
    pixels[:,320:368]=np.repeat(((np.asarray(im,dtype=np.uint16)*15+127)//255).astype(np.uint8),2,axis=1)
    out=raw[:at]+pack(pixels)+raw[end:]
    require(np.array_equal(unpack(raw[at:end],416,24)[:,:320],pixels[:,:320]),'Episode digits changed')
    return out

def compress_tail(stored,before,after):
    """Retain complete native LZ groups before the first changed byte.

    The new suffix uses only self-contained references; no old reference can
    cross into it. This avoids recompressing the large shared frame images.
    """
    require(len(before)==len(after),'Episode decoded size changed')
    first=next(i for i,(a,b) in enumerate(zip(before,after)) if a!=b)
    total,flags,cursor=banlz.parse_header(stored);produced=0;cut_in=cursor;cut_out=0
    while produced<total:
        begin=cursor;output_begin=produced
        t=stored[cursor];cursor+=1;lit=t&15;refs=t>>4
        if not lit:lit,cursor=banlz._varint(stored,cursor)
        if not refs:refs,cursor=banlz._varint(stored,cursor)
        cursor+=lit;produced+=lit
        if produced<total:
            for _ in range(refs):
                token=stored[cursor];cursor+=1;dist=token&15;length=token>>4
                while not dist&1:dist=dist<<7|stored[cursor];cursor+=1
                if not length:length,cursor=banlz._varint(stored,cursor)
                produced=min(total,produced+length+1)
                if produced==total:break
        if produced>first:
            cut_in,cut_out=begin,output_begin;break
    require(before[:cut_out]==after[:cut_out],'Episode LZ prefix preservation')
    return stored[:cut_in]+banlz.compress_stream(after[cut_out:],1<<(((flags>>1)&15)+8))

def compile_rows(entries):
    rows,inv=native();changes=[];report=[];previews=[]
    for i,row in enumerate(rows):
        if i<4 or i==5:continue
        raw=row['raw'];layout=None
        if i==4:
            new=header(raw);label='Ep. [number]';selector=None;pixel_sha=sha(new[197376:202368])
        else:
            selector=i-5;entry=entries[selector-1]
            require(entry['selector']==selector,'Episode translation ordering');label=entry['text']
            if selector==15:
                # Native English artwork is already correct and stays byte-identical.
                new=raw;layout=dict(native_english_retained=True)
            else:
                pixels,layout=render(label);new=raw[:96]+pixels+raw[16480:]
            pixel_sha=sha(new[96:16480])
        stored=row['stored'];encoded=stored
        if new!=raw:
            encoded=compress_tail(stored,raw,new) if i==4 else banlz.compress_record(new,flags=banlz.parse_header(stored)[1])
            if i>=6 and len(encoded)>len(stored):
                # Fewer antialias shades preserve every letter at the same size.
                # Only the two tiny original title allocations need this.
                original_pixels=unpack(new[96:16480],512,64).astype(np.uint16)
                for levels in (8,4):
                    reduced=((original_pixels*(levels-1)+7)//15*15//(levels-1)).astype(np.uint8)
                    new=raw[:96]+pack(reduced)+raw[16480:]
                    encoded=banlz.compress_record(new,flags=banlz.parse_header(stored)[1])
                    if len(encoded)<=len(stored):
                        layout['antialias_levels']=levels;break
                pixel_sha=sha(new[96:16480])
            require(len(encoded)<=len(stored),f'Episode compressed slot overflow: {i}, {len(encoded)} > {len(stored)}')
            require(decode(encoded)[0]==new,'Episode strict compression roundtrip')
            changes.append(dict(chunk=f'9/{i}',start=row['start'],end=row['end'],
                                payload=encoded+bytes(len(stored)-len(encoded)),decoded_sha256=sha(new)))
        if i>=6:
            final_pixels=unpack(new[96:16480],512,64)
            if selector!=15:
                yy,xx=np.nonzero(final_pixels[:,::2])
                layout['ink_bbox']=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
            previews.append((selector,label,final_pixels))
        report.append(dict(record=i,selector=selector,text=label,layout=layout,source_sha256=sha(raw),
                           decoded_sha256=sha(new),pixels_sha256=pixel_sha,start=row['start'],end=row['end'],
                           compressed_bytes=len(encoded),headroom=len(stored)-len(encoded),changed=new!=raw))
    return changes,report,previews

def prepare():
    review=json.loads(REVIEW.read_text(encoding='utf-8'))
    require(review['entries_examined']==21 and review['source_inventory_sha256']==file_sha(BINDINGS),
            'Episode translation review mismatch')
    entries=[dict(selector=r['selector'],text=r['text']) for r in review['entries']]
    require([r['selector'] for r in entries]==list(range(1,22)),'Episode meaning review coverage')
    changes,report,previews=compile_rows(entries)
    config=dict(schema_version=1,status='reviewed',font_sha256=file_sha(FONT),bindings_sha256=file_sha(BINDINGS),
                review_sha256=file_sha(REVIEW),entries=entries,frozen_records=report)
    return config,changes,report,previews

def build():
    config=json.loads(TARGET.read_text(encoding='utf-8'));fresh,changes,report,previews=prepare()
    require(config==fresh,'Episode frozen translation/layout drift')
    return changes,dict(count=21,translated_title_images=20,native_english_title_images=1,
                        ordinal_header='Ep. [number]',entries=report,table_sha256=TABLE_SHA,
                        source_group_sha256=GROUP_SHA,target_sha256=file_sha(TARGET),
                        bindings_sha256=file_sha(BINDINGS),review_sha256=file_sha(REVIEW),
                        digits_and_animation_preserved=True,story_dialogue_changed=False,
                        selector_17_native_duplicate_corrected=True,runtime='pending by user choice'),previews

def preview(previews,path):
    canvas=Image.new('RGB',(850,21*126+35),(30,31,20));draw=ImageDraw.Draw(canvas)
    draw.text((12,8),'Episode title textures - aspect-corrected preview, not emulator capture',fill='white')
    for j,(sel,label,pixels) in enumerate(previews):
        y=35+j*126;draw.text((12,y),f'{sel:02d}  {label}',fill=(180,190,160))
        im=Image.fromarray((pixels[:,::2]*17).astype(np.uint8)).crop((0,0,256,32)).resize((768,96))
        canvas.paste(im,(40,y+20))
    canvas.save(path)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--prepare',action='store_true');ap.add_argument('--write',action='store_true');a=ap.parse_args()
    if a.prepare:config,changes,report,previews=prepare()
    else:changes,report,previews=build()
    print(json.dumps(report,indent=2),flush=True)
    if not a.write:print('DRY RUN: no files written');return
    if a.prepare:TARGET.write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
    preview(previews,ROOT/'work/ui/episode-titles/english-0.2.17.png')
    rows,_=native();old=rows[4]['raw'];new=header(old)
    canvas=Image.new('RGB',(850,230),(30,31,20));draw=ImageDraw.Draw(canvas)
    for j,(label,raw) in enumerate((('Native shared number atlas',old),('English shared number atlas',new))):
        draw.text((12,j*105+5),label,fill='white')
        p=unpack(raw[197376:202368],416,24)[:,::2]
        im=Image.fromarray((p*17).astype(np.uint8)).resize((832,72))
        canvas.paste(im,(9,j*105+25))
    canvas.save(ROOT/'work/ui/episode-titles/header-0.2.17.png')

if __name__=='__main__':main()
