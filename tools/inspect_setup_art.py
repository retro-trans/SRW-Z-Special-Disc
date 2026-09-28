"""Preview native and donor setup/Bazaar sheets without modifying game data."""
import argparse,json,struct
import numpy as np
from PIL import Image,ImageDraw
from sp_disc import *
from library_text import ORIGINAL,DONOR
from reuse_menu_graphics import images
from inspect_archive_graphics import picture
from inspect_episode_titles import pictures,picture as multi_picture

FOLDER=ROOT/'work/ui/setup-art'

def preview(raw):
    if raw[35]==1:
        w,h=struct.unpack_from('<HH',raw,36);hs=struct.unpack_from('<H',raw,28)[0]
        v=np.frombuffer(raw[16+hs:16+hs+w*h*2],'<u2').reshape(h,w)
        return Image.fromarray(np.stack([((v>>s&31)*255//31).astype(np.uint8) for s in (0,5,10)],axis=-1))
    return picture(raw)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args()
    blobs={'sp':Disc(SOURCE).read('KURODATA/KVMDATA.BIN'),
           'original':(ORIGINAL/'KURODATA_KVMDATA.BIN').read_bytes(),
           'donor':Disc(DONOR,True).read('KURODATA/KVMDATA.BIN')}
    sheets={key:list(images(raw)) for key,raw in blobs.items()}
    jtim=list(images(Disc(SOURCE).read('DATA/JTIM.BIN')))
    extras=[]
    disc,exe,vt,offs=source_records()
    for name,raw in [('JTIM',disc.read('DATA/JTIM.BIN'))]+[(f'VT{i}',decode(vt[offs[i]:offs[i+1]])[0]) for i in (8,9,10,11,12,13,15,26,27,28,29)]:
        for p in pictures(raw):
            extras.append((name,p,raw))
    print('extra images',[(n,p['picture'],p['width'],p['height'])for n,p,r in extras])
    for name in ('DATA/MTV_ITEM.BIN','DATA/NISVDATA.BIN'):
        blobs2=[disc.read(name)] if 'MTV' in name else [b for p,b in banlz.decompress_all(disc.read(name))]
        for i,b in enumerate(blobs2):
            for at,r in images(b):extras.append((name+str(i),next(pictures(r)),r))
    print('JTIM preview:',[(i,hex(at)) for i,(at,raw) in enumerate(jtim)])
    print(json.dumps({key:[dict(index=i,offset=at,size=len(raw),dimensions=struct.unpack_from('<HH',raw,36))
                          for i,(at,raw) in enumerate(rows)] for key,rows in sheets.items()},indent=2))
    if not a.write:print('DRY RUN: no previews written');return
    FOLDER.mkdir(parents=True,exist_ok=True)
    for key in ('original','donor'):
        canvas=Image.new('RGB',(1024,560),(25,25,25));d=ImageDraw.Draw(canvas)
        for j,i in enumerate((4,5,6,10)):
            at,raw=sheets[key][i];x=j%2*512;y=j//2*280
            d.text((x+4,y+3),f'{key} sheet {i} @ {at:x}',fill='white')
            canvas.paste(picture(raw).resize((256,256)),(x,y+20))
        canvas.save(FOLDER/f'{key}-words.png')
    for i in (5,6,10,21):
        at,raw=sheets['sp'][i];picture(raw).save(FOLDER/f'sp-{i}.png')
    canvas=Image.new('RGB',(1200,600),(25,25,25));d=ImageDraw.Draw(canvas)
    for j,i in enumerate(range(11,22)):
        at,raw=sheets['sp'][i];im=picture(raw);im.thumbnail((200,170));x=j%6*200;y=j//6*300
        d.text((x+4,y+3),f'SP {i} @ {at:x}',fill='white');canvas.paste(im,(x,y+20))
    canvas.save(FOLDER/'sp-other.png')
    canvas=Image.new('RGB',(1200,800),(25,25,25));d=ImageDraw.Draw(canvas)
    for j,(at,raw) in enumerate(jtim):
        im=preview(raw);im.thumbnail((200,170));x=j%6*200;y=j//6*200
        d.text((x+4,y+3),f'JTIM {j} @ {at:x}',fill='white');canvas.paste(im,(x,y+20))
    canvas.save(FOLDER/'sp-jtim.png')
    from episode_titles import unpack
    for i in (8,12,13,27):
        r=decode(vt[offs[i]:offs[i+1]])[0]
        for w,h in [(256,256),(512,256)]:
            if len(r)>=w*h//2:
                Image.fromarray(unpack(r[:w*h//2],w,h)*17).save(FOLDER/f'raw-{i}-{w}.png')
    r=decode(vt[offs[13]:offs[14]])[0]
    Image.frombytes('L',(512,512),r[512:512+512*512]).save(FOLDER/'raw-13-byte.png')
    for n,p,r in extras:
        if (n=='VT11' or n.startswith('DATA/NISVDATA.BIN1')) and p['image_type']==5:
            arr=np.asarray(multi_picture(r,p)).reshape(-1,3)
            Image.fromarray(arr[swizzle_map(p['width'],p['height'])].reshape(p['height'],p['width'],3)).save(FOLDER/(f'swizzled-{sha(r)[:8]}.png'))
            print('SWIZZLED',n,sha(r)[:8])
        if n in ('VT28','VT29'):
            w,h=p['width'],p['height'];arr=np.asarray(multi_picture(r,p)).reshape(-1,3)
            Image.fromarray(arr[swizzle_map(w,h)].reshape(h,w,3)).save(FOLDER/f'{n}-{p["picture"]}-mapped.png')
    for start in range(0,len(extras),24):
        canvas=Image.new('RGB',(1200,800),(25,25,25));d=ImageDraw.Draw(canvas)
        for j,(n,p,r) in enumerate(extras[start:start+24]):
            im=multi_picture(r,p);im.thumbnail((200,170));x=j%6*200;y=j//6*200
            d.text((x+4,y+3),f'{n} {p["picture"]} @{p["start"]:x}',fill='white');canvas.paste(im,(x,y+20))
        canvas.save(FOLDER/f'extra-{start//24}.png')


if __name__=='__main__':main()
