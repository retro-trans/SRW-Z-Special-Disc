"""Reconstruct every condition table with the installed Latin glyph atlas."""
import argparse,json,math
from PIL import Image,ImageDraw,ImageFont
from sp_disc import ROOT,sha
from library_text import CHARS
from inspect_english_runtime import CAVE,CAVE_FILE
from save_summary_text import width


def prepare():
    folder=ROOT/'work/ui/mission-conditions'
    inv=json.loads((folder/'native-inventory.json').read_text(encoding='utf8'))
    cfg=json.loads((ROOT/'work/translation/en/mission_conditions.json').read_text(encoding='utf8'))
    bysha={r['source_sha256']:r for r in cfg['entries']}
    donor=(ROOT/'work/cache/english-runtime/english.elf').read_bytes()
    atlas=donor[CAVE_FILE+0x78A5B0-CAVE:CAVE_FILE+0x78A5B0-CAVE+69*72]
    label=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
    small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
    fallback=ImageFont.truetype('C:/Windows/Fonts/msgothic.ttc',23)
    glyphs={}
    for index,code in enumerate(CHARS):
        raw=atlas[index*72:(index+1)*72];mask=Image.new('L',(12,24))
        mask.putdata([(raw[y*3+x//4]>>(6-2*(x%4))&3)*85 for y in range(24) for x in range(12)])
        glyphs[chr(code)]=mask
    def draw(im,value,x,y,color):
        for char in value:
            if char in glyphs:im.paste(color,(x,y,x+12,y+24),glyphs[char])
            elif char!=' ':ImageDraw.Draw(im).text((x,y),char,font=fallback,fill=color)
            x+=width(char)
    pages=[];layouts=[]
    for ch in inv['chunks']:
        im=Image.new('RGB',(640,504),'#172018');d=ImageDraw.Draw(im)
        d.text((18,10),f"v0.2.19 | Stage module {ch['chunk']} | all condition table entries",font=label,fill='#ece9c5')
        for group in ch['tables']:
            y={'victory':36,'defeat':203,'extra':370}[group['kind']]
            bottom=y+154 if group['kind']!='extra' else 462
            d.rectangle((62,y,592,bottom),fill='#111918',outline='#8c895e',width=2)
            d.text((76,y+6),group['kind'].title(),font=label,fill='#d2c76a')
            d.line((74,y+28,582,y+28),fill='#545747')
            rownum=0
            for number,src in enumerate(group['entries'],1):
                row=bysha[src['source_sha256']]
                draw(im,str(number)+'.',88,y+34+rownum*28,'#d07b74')
                for line in row['lines']:
                    draw(im,line,118,y+34+rownum*28,'#d07b74');rownum+=1
            layouts.append(dict(chunk=ch['chunk'],kind=group['kind'],rows=rownum))
        d.text((18,472),'Reconstruction; emulator pending. A stage may select only some entries.',font=small,fill='#c1ccbf')
        d.text((18,488),'Latin glyphs/advances exact; frame and native punctuation approximated.',font=small,fill='#c1ccbf')
        pages.append((f'chunk-{ch["chunk"]:02d}-0.2.19.png',im))
    sheets=[]
    for number,start in enumerate(range(0,len(pages),12),1):
        batch=pages[start:start+12];sheet=Image.new('RGB',(1920,504*math.ceil(len(batch)/3)),'#080e0b')
        for i,(_,im) in enumerate(batch):sheet.paste(im,((i%3)*640,(i//3)*504))
        sheets.append((f'contact-{number}-0.2.19.png',sheet))
    meta=dict(version='0.2.19',kind='Static reconstruction, not emulator capture',pages=len(pages),
              atlas_sha256=sha(atlas),body_x=118,line_limit=460,row_limit=4,row_pitch_pixels=28,
              native_punctuation='Approximate Windows font; encoding verified separately',groups=layouts)
    return pages+sheets,meta


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    images,meta=prepare();print(json.dumps(dict(meta,groups=meta['groups'][:3],files=len(images)),indent=2))
    if not a.write:print('DRY RUN: no previews written');return
    folder=ROOT/'work/ui/mission-conditions'
    for name,im in images:im.save(folder/name)
    (folder/'layout-0.2.19.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf8')


if __name__=='__main__':main()
