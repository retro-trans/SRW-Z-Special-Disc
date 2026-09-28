"""Render narration line-layout previews, explicitly separate from emulator captures."""
import argparse
import json
import struct
from PIL import Image,ImageDraw,ImageFont
from sp_disc import ROOT,require
from library_text import CHARS
from inspect_english_runtime import CAVE,CAVE_FILE
from narration_format import native_records
from narration_text import width,LINE_LIMIT


def prepare():
    rows=json.loads((ROOT/'work/translation/en/narration_reviewed.json').read_text(encoding='utf-8'))['entries']
    donor=(ROOT/'work/cache/english-runtime/english.elf').read_bytes()
    atlas=donor[CAVE_FILE+0x78a5b0-CAVE:CAVE_FILE+0x78a5b0-CAVE+69*72]
    caption=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
    fallback=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
    images={};entries=[]
    for row,(_,_,info)in zip(rows,native_records()[-1]):
        i=row['id'];require(info['prefix'][14:18]==bytes((25,12,25,14)),'Narration font size/pitch drift')
        xy=struct.unpack_from('<hh',info['prefix'],18);clip=struct.unpack_from('<hhhh',info['suffix'],48)
        require(xy==(-285,-92) and clip==(-320,-112,640,224),'Narration text bounds drift')
        im=Image.new('RGBA',(680,512),(20,24,32,255));draw=ImageDraw.Draw(im)
        draw.text((20,10),f'NARRATION {i:02d} - LAYOUT PREVIEW; EMULATOR PENDING',font=caption,fill='#9aead3')
        draw.rectangle((20,44,659,491),outline='#626976')
        x0=20+xy[0]-clip[0];y0=44+2*(xy[1]-clip[1])
        draw.rectangle((x0-2,y0-2,x0+LINE_LIMIT+2,y0+12*28+25),outline='#3e474f')
        for n,line in enumerate(row['lines']):
            x=x0;y=y0+n*28
            for char in line:
                if ord(char)in CHARS:
                    index=CHARS.index(ord(char));raw=atlas[index*72:(index+1)*72];glyph=Image.new('RGBA',(12,24))
                    for py in range(24):
                        for px in range(12):
                            val=(raw[py*3+px//4]>>(6-2*(px%4)))&3
                            if val:glyph.putpixel((px,py),(235,230,170,val*85))
                    im.alpha_composite(glyph,(x,y))
                elif char!=' ':draw.text((x,y),char,font=fallback,fill='#ebe6aa')
                x+=width(char)
        name=f'narration-{i:02d}-preview.png';images[name]=im
        entries.append(dict(id=i,preview='english/'+name,position=list(xy),clip=list(clip),rows=13,
            source_font_parameters=[25,12,25,14],line_limit_font_units=LINE_LIMIT,line_widths=list(map(width,row['lines'])),
            duration_ms=info['duration_ms'],text_active_ms=list(struct.unpack_from('<II',info['prefix'],6))))
    meta=dict(kind='Reconstructed layout previews; not in-game screenshots',canvas_units=[640,224],
        preview_vertical_scale=2,latin_glyphs='Actual donor atlas; fallback symbols use Arial',
        timing_and_animation='Not simulated',runtime_acceptance='pending by user choice',entries=entries)
    return images,meta


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    images,meta=prepare()
    print(json.dumps(dict(images={k:list(v.size)for k,v in images.items()},sample=meta['entries'][6]),indent=2))
    if a.write:
        for name,im in images.items():im.save(ROOT/'work/ui/english'/name)
        (ROOT/'work/ui/narration-layout.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no files written')


if __name__=='__main__':main()
