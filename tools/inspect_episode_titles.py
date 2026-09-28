"""Inventory the native Special Disc episode-card textures; read-only by default."""
import argparse
import json
import struct
import numpy as np
from PIL import Image, ImageDraw
from sp_disc import ROOT, source_records, Disc, SOURCE, decode, sha

DEST=ROOT/'work/ui/episode-titles'
TABLE=0x3763e0

def pictures(raw):
    at=0
    while True:
        at=raw.find(b'TIM2',at)
        if at<0:return
        count=struct.unpack_from('<H',raw,at+6)[0]
        p=at+16
        for i in range(count):
            total,cs,sz,hs,cc,fmt,mip,ct,it,w,h=struct.unpack_from('<IIIHHBBBBHH',raw,p)
            yield dict(tim2=at,picture=i,header=p,start=p+hs,end=p+hs+sz,
                       total=total,clut_size=cs,colours=cc,clut_type=ct,image_type=it,width=w,height=h)
            p+=total
        at=p

def picture(raw,p):
    a,b=p['start'],p['end'];w,h=p['width'],p['height'];it=p['image_type']
    v=np.frombuffer(raw[a:b],np.uint8)
    if it==1:
        v=np.frombuffer(raw[a:b],'<u2').reshape(h,w)
        return Image.fromarray(np.stack([*((v>>s&31)*255//31 for s in (0,5,10)),np.full((h,w),255)],axis=-1).astype(np.uint8)).convert('RGB')
    if it in (2,3):return Image.frombytes('RGB' if it==2 else 'RGBA',(w,h),raw[a:b]).convert('RGB')
    if it==4:v=np.stack((v&15,v>>4),axis=-1).ravel()
    idx=v.reshape(h,w)
    if not p['clut_size']:
        pal=np.stack([np.arange(256,dtype=np.uint8)]*3+[np.full(256,255,np.uint8)],axis=-1)
    elif p['clut_type']&7==3:
        pal=np.frombuffer(raw[b:b+p['clut_size']],np.uint8).reshape(-1,4).copy()
        pal[:,3]=np.minimum(pal[:,3].astype(int)*2,255)
    else:
        v=np.frombuffer(raw[b:b+p['clut_size']],'<u2')
        pal=np.stack([*((v>>s&31)*255//31 for s in (0,5,10)),np.full(len(v),255)],axis=-1).astype(np.uint8)
    if it==5 and len(pal)>=256:pal=pal[[(i&0xe7)|((i&8)<<1)|((i&16)>>1) for i in range(256)]]
    im=Image.fromarray(pal[idx]);return Image.alpha_composite(Image.new('RGBA',im.size,(32,32,32,255)),im).convert('RGB')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    disc,exe,vt,outer=source_records();offsets=struct.unpack_from('<28I',exe,TABLE);base=outer[9]
    comp,_=decode(disc.read('DATA/COMPDATA.BN'))
    stage,_=decode(disc.read('DATA/STAGE.BIN'))
    targets=json.loads((ROOT/'work/translation/en/chart_bound.json').read_text(encoding='utf-8'))['entries']
    titles={stage[r['offset']:].split(b'\0')[0].decode('cp932'):r for r in targets if r['id'].startswith('title/sp/')}
    bindings=[]
    for chunk in range(1,30):
        at=0x68630+48*(chunk-1);ptr=struct.unpack_from('<I',comp,at)[0];sel=struct.unpack_from('<H',comp,at+28)[0]
        jp=comp[ptr-0x764f80:].split(b'\0')[0].decode('cp932')
        if jp=='予備':continue
        bindings.append(dict(chunk=chunk,selector=sel,source=jp,text=titles[jp]['text'],chart_id=titles[jp]['id']))
    result=dict(table_sha256=sha(exe[TABLE:TABLE+112]),group_sha256=sha(vt[outer[9]:outer[10]]),bindings=bindings,records=[])
    cards=[]
    for i,(lo,hi) in enumerate(zip(offsets,offsets[1:])):
        raw,_=decode(vt[base+lo:base+hi]);pics=list(pictures(raw))
        result['records'].append(dict(index=i,start=base+lo,end=base+hi,decoded_bytes=len(raw),decoded_sha256=sha(raw),pictures=pics))
        for p in pics:cards.append((f'{i}/{p["picture"]}',picture(raw,p)))
    print(json.dumps(result,ensure_ascii=True,indent=2))
    if not args.write:print('DRY RUN: no files written');return
    DEST.mkdir(parents=True,exist_ok=True)
    (DEST/'native-inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for label,im in cards:im.save(DEST/('native-'+label.replace('/','-')+'.png'))
    canvas=Image.new('RGB',(1040,21*84),(32,32,32));draw=ImageDraw.Draw(canvas)
    for j,(label,im) in enumerate((c for c in cards if int(c[0].split('/')[0])>=6)):
        draw.text((5,j*84+8),label,fill='white');canvas.paste(im,(60,j*84))
        canvas.paste(im.resize((256,64)),(600,j*84))
    canvas.save(DEST/'native-titles.png')

if __name__=='__main__':main()
