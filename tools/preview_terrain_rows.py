"""Preview the exact imported terrain art in its native full-width cells."""
import argparse,json
from PIL import Image,ImageDraw,ImageFont
from sp_disc import Disc,EXE
from terrain_rows import PREVIOUS,FOLDER,inventory,compile_component
from audit_terrain_rows import glyph,check

def prepare():
    before=Disc(PREVIOUS).read(EXE);inv=inventory();exe,_=compile_component(before,inv)
    meta=check(exe,before,inv);im=Image.new('RGB',(760,410),'#161e1e');d=ImageDraw.Draw(im)
    title=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
    grade=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
    d.text((20,16),'v0.2.21 | SRW Z terrain micro-glyphs',font=title,fill='#f0ebd5')
    d.text((20,45),'Exact donor pixels; each abbreviation occupies one native character cell.',font=font,fill='#b4c9c3')
    for i,label in enumerate(('AIR','GND','SEA','SPC')):
        x=28+i*182;mask=Image.frombytes('L',(24,24),glyph(exe,0x85dc+i))
        tile=Image.new('RGB',(24,24),'#1e292a');tile.paste('#57bfcc',(0,0,24,24),mask)
        im.paste(tile.resize((96,96),Image.Resampling.NEAREST),(x,80))
        d.rectangle((x,80,x+95,175),outline='#4a5c5b');d.text((x,183),label+'  /  24 x 24 cell',font=font,fill='#f0ebd5')
    d.text((20,225),'Example rating row at 21-unit cell advance (rank letters are illustrative):',font=font,fill='#b4c9c3')
    row=Image.new('RGB',(176,30),'#6b7471');rd=ImageDraw.Draw(row)
    for i,rank in enumerate('ABAS'):
        x=i*42;mask=Image.frombytes('L',(24,24),glyph(exe,0x85dc+i))
        row.paste('#144b55',(x,2,x+24,26),mask)
        rd.text((x+21,3),rank,font=grade,fill='#161e1e')
    im.paste(row.resize((528,90),Image.Resampling.NEAREST),(25,253))
    d.text((20,363),'Same seven-cell structure in all 11 rows. Native styles control the on-screen scale.',font=font,fill='#b4c9c3')
    d.text((20,386),'Static reconstruction; emulator verification remains pending by user choice.',font=font,fill='#b4c9c3')
    return im,dict(meta,kind='static reconstruction; exact micro-glyph pixels; approximate rank font',
                   cell_storage=[24,24],illustrative_cell_advance=21,version='0.2.21')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    im,meta=prepare();print(json.dumps(meta,indent=2))
    if not a.write:print('DRY RUN: no preview written');return
    im.save(FOLDER/'preview-0.2.21.png');(FOLDER/'layout-0.2.21.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf8')

if __name__=='__main__':main()
