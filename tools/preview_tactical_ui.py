"""Static diagnostic preview using installed Latin glyphs; not an emulator capture."""
import argparse,json
from PIL import Image,ImageDraw,ImageFont
from sp_disc import ROOT,Disc,EXE,sha
from library_text import CHARS,text
from inspect_english_runtime import CAVE,CAVE_FILE
from save_summary_text import width
from prepare_tactical_ui import PREVIOUS,FOLDER,inventory
from tactical_ui import compile_component
from audit_tactical_ui import movement,encoded_width,layout_checks
from menu_encoding import menu_encode

def prepare():
    inv,rows=inventory();exe,_=compile_component(Disc(PREVIOUS).read(EXE),inv,rows)
    donor=(ROOT/'work/cache/english-runtime/english.elf').read_bytes()
    atlas=donor[CAVE_FILE+0x78a5b0-CAVE:CAVE_FILE+0x78a5b0-CAVE+69*72];glyphs={}
    for index,code in enumerate(CHARS):
        raw=atlas[index*72:(index+1)*72];im=Image.new('L',(12,24))
        im.putdata([(raw[y*3+x//4]>>(6-2*(x%4))&3)*85 for y in range(24) for x in range(12)])
        glyphs[chr(code)]=im
    label=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
    native=ImageFont.truetype('C:/Windows/Fonts/msgothic.ttc',23)
    im=Image.new('RGB',(660,690),'#14201b');d=ImageDraw.Draw(im)
    def draw(raw,x,y,color='#eeeecc'):
        i=0
        while i<len(raw):
            b=raw[i];n=2 if 0x81<=b<=0x9f or 0xe0<=b<=0xfc else 1;chunk=raw[i:i+n];char=text(chunk)
            if b==0x85 or n==1:
                if char in glyphs:im.paste(color,(x,y,x+12,y+24),glyphs[char])
                elif char!=' ':d.text((x,y),char,font=native,fill=color)
            else:d.text((x,y),chunk.decode('cp932'),font=native,fill=color)
            x+=encoded_width(chunk);i+=n
    d.text((15,10),'v0.2.20 | Tactical UI layout reconstruction',font=label,fill='#e5e6d6')
    d.text((15,32),'Latin atlas + conservative advances; native wide glyphs approximated.',font=label,fill='#a5b1a7')
    for y,counts in ((62,(15,14)),(107,(999,999))):
        d.rectangle((62,y-2,320,y+30),outline='#77714b')
        draw(menu_encode('Forces'),96,y,'#c4bb6e')
        for number,right,color in ((counts[0],204,'#57b5d1'),(counts[1],288,'#d86b68')):
            draw(menu_encode(str(number)),right-len(str(number))*12,y,color)
            draw(b'Sq',right,y,color)
        draw('／'.encode('cp932'),227,y)
    for i,(num,kind,mask) in enumerate(((6,1,0),(99,2,0),(99,3,0),(99,0,5),(None,0,0))):
        y=178+i*43;d.rectangle((18,y-2,630,y+29),fill='#4c5250',outline='#969e98')
        draw(b'Move',24,y,'#d7ce79');draw(movement(exe,num,kind,mask),76,y)
        draw(b'Pilot',280,y,'#d7ce79');draw(b'Hyzaemon',338,y)
        draw(b'Lv',464,y,'#d7ce79');draw(menu_encode('33'),492,y)
        draw(b'Will',536,y,'#d7ce79');draw(menu_encode('100'),574,y)
    d.text((18,405),'Verified selector outputs (already included in v0.2.18 / v0.2.19):',font=label,fill='#a5b1a7')
    labels=['Tri Formation','Center Formation','Wide Formation','<Group Formation> Set all squad formations.',
            '<Play unit music during battle animations.>','~[Allied Forces] Select Unit~']
    for i,value in enumerate(labels):draw(menu_encode(value),25,432+i*32,'#54b8c5')
    d.text((18,638),'Static reconstruction only. PCSX2 validation remains pending by user choice.',font=label,fill='#c3bca4')
    d.text((18,659),'A = Air; G = Ground; S = Sea/Water. Sq = Squads. Will = Morale.',font=label,fill='#c3bca4')
    return im,dict(version='0.2.20',kind='static reconstruction, not emulator capture',atlas_sha256=sha(atlas),layout=layout_checks(exe))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    im,report=prepare();print(json.dumps(report,indent=2))
    if not a.write:print('DRY RUN: no preview written');return
    im.save(FOLDER/'preview-0.2.20.png');(FOLDER/'layout-0.2.20.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')

if __name__=='__main__':main()
