"""Render English asset and layout previews; these are not emulator captures."""
import argparse
import json
from PIL import Image,ImageDraw,ImageFont
from sp_disc import *
from library_text import CHARS
from inspect_english_runtime import CAVE,CAVE_FILE
import reuse_help_book


def make():
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
    caption=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',22)
    donor=(ROOT/'work/cache/english-runtime/english.elf').read_bytes()
    atlas=donor[CAVE_FILE+0x78a5b0-CAVE:CAVE_FILE+0x78a5b0-CAVE+69*72]
    widths=donor[CAVE_FILE+0x78b960-CAVE:CAVE_FILE+0x78b960-CAVE+69]
    def glyph_line(canvas,xy,value,color):
        x,y=xy
        for c in value:
            if ord(c)in CHARS:
                i=CHARS.index(ord(c));raw=atlas[i*72:(i+1)*72]
                glyph=Image.new('RGBA',(12,24))
                for py in range(24):
                    for px in range(12):
                        val=(raw[py*3+px//4]>>(6-2*(px%4)))&3
                        if val:glyph.putpixel((px,py),(*color,val*85))
                canvas.alpha_composite(glyph,(x,y));x+=widths[i]+2
            elif c==' ':x+=13
            else:ImageDraw.Draw(canvas).text((x,y),c,font=font,fill=(*color,255));x+=24
    result={}
    library=json.loads((ROOT/'work/translation/en/library_complete.json').read_text(encoding='utf-8'))['entries']
    sample=next(r for r in library if r['id']=='RT/0/DSCR')
    im=Image.new('RGBA',(660,470),(22,24,34,255));dr=ImageDraw.Draw(im)
    dr.text((22,16),'LIBRARY TEXT LAYOUT PREVIEW',font=caption,fill='#7ee5d0')
    dr.text((22,48),'Mazinger Z - actual English glyphs; runtime pending',font=font,fill='#b2b7c6')
    dr.rectangle((22,92,606,441),outline='#616976',width=1)
    for i,line in enumerate(sample['text'].splitlines()[:11]):glyph_line(im,(34,100+i*29),line,(236,233,213))
    result['library-text-preview.png']=im
    archive=(ROOT/'work/cache/nonstory/help-NISVDATA.BIN').read_bytes();raw=reuse_help_book.records(archive)[0]
    texture=tim2(raw[0xd2d00:0xd2d00+66624])
    tex=Image.fromarray(texture['rgba']).resize((512,512),Image.Resampling.NEAREST)
    im=Image.new('RGBA',(660,580),(22,24,34,255));ImageDraw.Draw(im).text((22,16),'LIBRARY BUTTON ATLAS - PREVIEW',font=caption,fill='#7ee5d0');im.alpha_composite(tex,(74,56))
    result['library-buttons-preview.png']=im
    entries=json.loads((ROOT/'work/translation/en/help_book.json').read_text(encoding='utf-8'))
    for index in (60,93):
        row=next(r for r in entries if r['id']==f'page/{index}')
        height=max(r['y'] for r in row['runs'])*2+95
        im=Image.new('RGBA',(660,height),(22,24,34,255));d=ImageDraw.Draw(im)
        d.text((22,12),f'Q&A PAGE {index} - POSITION PREVIEW',font=caption,fill='#7ee5d0')
        for r in row['runs']:
            color='#ebd887'if r['attr']in(6,14)else '#e6e9ee'
            # Positions are exact. The preview uses a substitute font for legibility.
            d.text((r['x']+22,r['y']*2+54),r['text'],font=font,fill=color)
        result[f'help-page-{index}-preview.png']=im
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    images=make();print(json.dumps({k:list(v.size)for k,v in images.items()},indent=2))
    if a.write:
        for name,im in images.items():im.save(ROOT/'work/ui/english'/name)
    else:print('DRY RUN: no images written')

if __name__=='__main__':main()
