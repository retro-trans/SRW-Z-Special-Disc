"""Static Search layout reconstruction, not an emulator screenshot."""
import json
from PIL import Image,ImageDraw,ImageFont
from sp_disc import ROOT
from library_text import CHARS
from save_summary_text import width
from inspect_english_runtime import CAVE,CAVE_FILE
from search_layout import SPEC

def main():
    cfg=json.loads(SPEC.read_text(encoding='utf-8'))
    donor=(ROOT/'work/cache/english-runtime/english.elf').read_bytes()
    atlas=donor[CAVE_FILE+0x78a5b0-CAVE:CAVE_FILE+0x78a5b0-CAVE+69*72];glyphs={}
    for i,c in enumerate(CHARS):
        raw=atlas[i*72:(i+1)*72];im=Image.new('L',(12,24))
        im.putdata([(raw[y*3+x//4]>>(6-2*(x%4))&3)*85 for y in range(24) for x in range(12)])
        glyphs[chr(c)]=im
    selected=[next(r for r in cfg['rows'] if r['pointer']==p) for p in (0x54b0c,0x54b08,0x54b7c)]
    canvas=Image.new('RGB',(660,600),'#17181d');draw=ImageDraw.Draw(canvas)
    small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13)
    fallback=ImageFont.truetype('C:/Windows/Fonts/msgothic.ttc',23)
    def line(value,x,y,color):
        for char in value:
            if char in glyphs:canvas.paste(color,(x,y,x+12,y+24),glyphs[char])
            elif char!=' ':draw.text((x,y-1),char,font=fallback,fill=color)
            x+=width(char)
    draw.text((12,8),'v0.3.11: static font reconstruction; emulator review pending',font=small,fill='#c9d0db')
    line('Search Filter',22,32,'#d6b94e')
    draw.ellipse((208,32,226,50),outline='#f976a6',width=2);line('OK',233,32,'#24d4ea')
    for i,row in enumerate(selected):
        top=95+i*165
        draw.text((22,top-19),('Repair Module','Supply Module','Longest effect list')[i],font=small,fill='#d8e2e4')
        draw.rounded_rectangle((22,top,636,top+100),radius=8,fill='#828987',outline='#ccd0ce',width=2)
        line('Eff',30,top+12,'#d5cb74')
        for j,value in enumerate(row['text'].splitlines()):
            y=top+12+j*24
            draw.line((86,y+24,619,y+24),fill='#6d7371')
            line(value,86,y,'#111111')
        draw.text((86,top+109),'Conservative widths: '+', '.join(map(str,row['line_widths']))+' / 510',font=small,fill='#abbabc')
    folder=ROOT/'work/ui/search-layout';folder.mkdir(parents=True,exist_ok=True)
    canvas.save(folder/'preview-0.3.11.png')

if __name__=='__main__':main()
