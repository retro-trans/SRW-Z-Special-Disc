"""Decode labelled contact sheets for locating native archive artwork."""
import argparse
import collections
import struct
import numpy as np
from PIL import Image, ImageDraw
from sp_disc import ROOT, Disc, SOURCE, banlz
from reuse_menu_graphics import images


def picture(raw):
    _,cs,isz,h,cc,_,_,ct,it,w,height=struct.unpack_from('<IIIHHBBBBHH',raw,16)
    pixels=raw[16+h:16+h+isz]
    if it==2:
        return Image.frombytes('RGB',(w,height),pixels)
    if it==3:
        return Image.frombytes('RGBA',(w,height),pixels)
    idx=np.frombuffer(pixels,np.uint8)
    if it==4:idx=np.stack([idx&15,idx>>4],axis=-1).ravel()
    idx=idx.reshape(height,w)
    palraw=raw[16+h+isz:16+h+isz+cs]
    if ct&7==3:
        pal=np.frombuffer(palraw,np.uint8).reshape(-1,4)[:256].copy()
        pal[:,3]=np.minimum(pal[:,3].astype(int)*2,255)
    else:
        v=np.frombuffer(palraw,'<u2')[:256]
        pal=np.stack([*((v>>s&31)*255//31 for s in (0,5,10)),np.full(len(v),255)],axis=1).astype(np.uint8)
    if it==5 and len(pal)>=256:
        pal=pal[[(x&0xe7)|((x&8)<<1)|((x&16)>>1)for x in range(256)]]
    im=Image.fromarray(pal[idx]);bg=Image.new('RGBA',im.size,(35,35,35,255))
    return Image.alpha_composite(bg,im).convert('RGB')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--member',required=True)
    p.add_argument('--prefix',required=True)
    p.add_argument('--sample',action='store_true')
    p.add_argument('--write',action='store_true')
    args=p.parse_args()
    cards=[];dimensions=collections.Counter()
    records=banlz.decompress_all(Disc(SOURCE).read(args.member))
    for i,(at,b)in enumerate(records):
        assert b is not None,(i,at)
        for j,(offset,raw)in enumerate(images(b)):
            dimensions[struct.unpack_from('<HH',raw,36)]+=1
            if args.sample and i>=36 and i%25:continue
            cards.append((f'{i}/{j}',picture(raw)))
    print(args.member,'records',len(records),'dimensions',dict(dimensions),'preview cards',len(cards),flush=True)
    if not args.write:
        print('DRY RUN: no files written');return
    dest=ROOT/'work/ui/location-cards'
    for start in range(0,len(cards),48):
        canvas=Image.new('RGB',(1200,1120),(25,25,25));draw=ImageDraw.Draw(canvas)
        for j,(label,im)in enumerate(cards[start:start+48]):
            x,y=j%6*200,j//6*140
            draw.text((x+5,y+3),label,fill='white');im.thumbnail((200,120))
            canvas.paste(im,(x,y+20))
        canvas.save(dest/f'{args.prefix}-{start//48}.png')


if __name__=='__main__':main()
