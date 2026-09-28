"""Reconstruct aligned panel layouts with the installed Latin atlas."""
import argparse
import json
from PIL import Image, ImageDraw, ImageFont
from sp_disc import ROOT, sha, require
from inspect_english_runtime import CAVE, CAVE_FILE
from library_text import CHARS
from align_story_panels import actual_width, QUESTIONS
from compile_briefings import build


def prepare():
    _, report = build()
    donor = (ROOT/'work/cache/english-runtime/english.elf').read_bytes()
    atlas = donor[CAVE_FILE+0x78A5B0-CAVE:CAVE_FILE+0x78A5B0-CAVE+69*72]
    labels = json.loads((ROOT/'work/translation/en/system.json').read_text(encoding='utf-8'))
    wanted = [f'exe/{x:x}' for x in range(0x3C4BD0,0x3C4C90,32)]
    names = [next(r['text'] for r in labels if r['id']==i) for i in wanted]+['???']
    body = next(p for p in report['pages'] if p['id']=='40/3')
    footer = ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
    def frame():
        im = Image.new('RGB',(1280,944),'#101727');d=ImageDraw.Draw(im)
        d.rectangle((84,104,1190,782),fill='#09143b',outline='#147bbb',width=4)
        d.polygon([(88,132),(116,112),(1180,112),(1180,754),(1164,768),(88,768)],fill='#b5bfc0',outline='#74aaca')
        d.line((116,232,1152,232),fill='#929e9f',width=4)
        d.line((116,608,1152,608),fill='#929e9f',width=4)
        d.text((30,906),'Layout reconstruction with the game Latin atlas; emulator testing remains pending.',font=footer,fill='#cee1e6')
        return im
    def draw_text(im,value,x,y,color='#111819',spacing=None):
        for char in value:
            if ord(char) in CHARS:
                index = CHARS.index(ord(char));raw=atlas[index*72:(index+1)*72]
                glyph=Image.new('RGBA',(12,24));rgb=tuple(bytes.fromhex(color[1:]))
                for gy in range(24):
                    for gx in range(12):
                        a=(raw[gy*3+gx//4] >> (6-2*(gx%4)) & 3)*85
                        if a:glyph.putpixel((gx,gy),rgb+(a,))
                glyph=glyph.resize((24,48),Image.Resampling.NEAREST)
                im.paste(glyph,(int(x*2),int(y*4)),glyph)
            x += spacing if spacing is not None else actual_width(char)
        return x
    images=[]
    for kind,title,question in (('intro',body['lines'][0],QUESTIONS[1]),('clear','Glory Star Report',QUESTIONS[2])):
        im=frame();draw_text(im,title,64,46)
        if kind=='intro':
            for i,line in enumerate(body['lines'][1:8]):draw_text(im,line,64,64+i*12)
        else:
            for i,name in enumerate(names):
                end=draw_text(im,name,64,64+i*12,spacing=22 if i==6 else None)
                require(end<448,'Bonus label reaches status column')
                draw_text(im,'---',448,64+i*12)
        draw_text(im,question,316-actual_width(question)//2,156)
        draw_text(im,'Yes',236,168,color='#21428a');draw_text(im,'No',364,168)
        d=ImageDraw.Draw(im);d.line((222*2,183*4,286*2,183*4),fill='#a8ab37',width=3)
        images.append((kind,im))
    metadata=dict(kind='Reconstructed preview, not an emulator capture',version='0.2.15',
        screenshot_viewport=[111,0,938,620],logical_canvas=[640,224],
        left_x=64,right_text_limit=564,divider_right=576,status_column_x=448,
        body_y=[64+i*12 for i in range(7)],title_y=46,question_y=156,
        inputs={'latin_atlas_sha256':sha(atlas),'briefings_sha256':sha((ROOT/'work/translation/en/briefings.json').read_bytes())},
        sample_intro=body,clear_labels=names,rendering='Latin atlas exact; frame reconstructed; hidden native question-mark spacing approximated at 22 units.',
        runtime='pending by user choice')
    return images,metadata


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    images,meta=prepare();print(json.dumps(meta,indent=2))
    if a.write:
        for name,im in images:im.save(ROOT/f'work/ui/english/story-panel-{name}-0.2.15.png')
        (ROOT/'work/ui/story-panel-layout-0.2.15.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no preview files written')


if __name__=='__main__':main()
