"""Read-only deployment UI inventory and native word-sheet contact sheets."""
import argparse,json,struct
from PIL import Image,ImageDraw
from sp_disc import *
from reuse_compdata import pointers,cstring,BBASE
from reuse_menu_graphics import images
from inspect_archive_graphics import picture

DEST=ROOT/'work/ui/deployment'

def inventory():
    d=Disc(SOURCE);comp=decode(d.read('DATA/COMPDATA.BN'))[0];rows={}
    for p,v in pointers(comp,BBASE):
        if not 0x6a000<=p<0x6a238:continue
        parsed=cstring(comp,v)
        if not parsed:continue
        if v not in rows:rows[v]=dict(offset=v,source=parsed[1],source_sha256=sha(parsed[0]),pointer_sites=[])
        rows[v]['pointer_sites'].append(p)
    # These 32-byte squad records have a name pointer as their final word.
    # Inventory only exact known pointers initially; no dialogue is exported.
    stage=banlz.decompress_all(d.read('DATA/STAGE.BIN'))[13][1];names=[]
    for at in range(0xa3b0,0xa470,16):
        raw=stage[at:].split(b'\0')[0]
        refs=[p for p,v in pointers(stage,0x8045f0) if v==at]
        names.append(dict(chunk=13,offset=at,source=raw.decode('cp932'),source_sha256=sha(raw),pointer_sites=refs))
    return dict(menu_entries=list(rows.values()),stage_names=names)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args()
    inv=inventory();print(json.dumps(inv,ensure_ascii=True,indent=2))
    sheets=list(images(Disc(SOURCE).read('KURODATA/KVMDATA.BIN')))[:11]
    print('Would export',len(sheets),'native word sheets and UI-only bindings')
    if not a.write:print('DRY RUN: no files written');return
    DEST.mkdir(parents=True,exist_ok=True)
    (DEST/'native-inventory.json').write_text(json.dumps(inv,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    canvas=Image.new('RGB',(1040,3*280),(30,30,30));draw=ImageDraw.Draw(canvas)
    for j,(at,raw) in enumerate(sheets):
        im=picture(raw);x,y=j%4*260,j//4*280
        draw.text((x+4,y+3),f'{j} @ {at:06x}',fill='white');canvas.paste(im,(x,y+20))
        im.save(DEST/f'word-sheet-{j}.png')
    canvas.save(DEST/'native-word-sheets.png')

if __name__=='__main__':main()
