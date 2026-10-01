"""Static font-atlas proof of longest and reported battle captions."""
import json
from PIL import Image,ImageDraw,ImageFont
from sp_disc import ROOT
from complete_battle import INPUT
from library_text import CHARS
from inspect_english_runtime import CAVE,CAVE_FILE
from battle_text import width

rows=json.loads(INPUT.read_text(encoding='utf-8'))['entries']
chosen=sorted(rows,key=lambda r:max(r['line_widths']),reverse=True)[:4]
chosen += [next(r for r in rows if r['id']==i) for i in (14417,21072)]
donor=(ROOT/'work/cache/english-runtime/english.elf').read_bytes()
atlas=donor[CAVE_FILE+0x78a5b0-CAVE:CAVE_FILE+0x78a5b0-CAVE+69*72]
im=Image.new('RGBA',(680,len(chosen)*138),'#111923');draw=ImageDraw.Draw(im)
label=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
fallback=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
for n,row in enumerate(chosen):
    top=n*138;draw.text((20,top+7),f"Caption {row['id']} - static atlas preview; emulator pending",font=label,fill='#91e0d3')
    draw.rectangle((20,top+30,659,top+118),outline='#67727f')
    draw.rectangle((180,top+57,640,top+112),outline='#424d59')
    for j,line in enumerate(row['lines']):
        x=180;y=top+62+j*24
        for char in line:
            if ord(char) in CHARS:
                raw=atlas[CHARS.index(ord(char))*72:][:72];glyph=Image.new('RGBA',(12,24))
                for gy in range(24):
                    for gx in range(12):
                        v=raw[gy*3+gx//4]>>(6-2*(gx%4))&3
                        if v:glyph.putpixel((gx,gy),(240,238,219,v*85))
                im.alpha_composite(glyph,(x,y))
            elif char!=' ':draw.text((x,y),char,font=fallback,fill='#f0eedb')
            x+=width(char)
im.save(ROOT/'work/ui/battle-complete/preview-0.3.15.png')
