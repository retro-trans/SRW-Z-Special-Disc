"""Native title branding and Special Theater artwork for v0.3.18."""
import json, struct, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from sp_disc import ROOT, EXE, VT1, VT1_TABLE, Disc, require, sha, decode, swizzle_map
from inspect_episode_titles import pictures
from battle_banners import swizzle_map as map4

DEST = ROOT/'work/ui/title-theater'
DONOR = ROOT.parent/'SRW Z/_work/logo-v0.9.82/glow-aligned/title-bank.bin'
PACKER = ROOT.parent/'SRW Z/_work/title-branding/banlz_pack_fast.exe'
AID = 'AID_DATA/AIDDATA.BIN'
FONT = 'C:/Windows/Fonts/arialbi.ttf'
SPEC = json.loads((ROOT/'work/translation/en/public/title_theater.json').read_text(encoding='utf-8'))
LABELS = [e['text'] for e in SPEC['entries'] if e['id'].startswith('theater/banner/')]
PREIMAGES = {
    'title-intro':'a7798be839a72416d358b7f3f2e0ae9d95c866cd4226ba6d8305a14ca8a3559a',
    'title-menu':'49222bcb2b054c701f5b922a43ede951694640b73fff5ce4569e4bdc98310e2a',
    'special-disc':'7e7133668e43b92b9d78cc668386034805a1aaa790785aba8bb1a9de8fb8c731',
    'special-theater':'698eb0becd5ec21a94df44947e2ed736c1348f03822acec8adcb8cfb05216406',
}

def palette(raw, at, count=256):
    p=np.frombuffer(raw[at:at+count*4],np.uint8).reshape(count,4).copy()
    p=p[[(i&~31)|(i&7)|((i&8)<<1)|((i&16)>>1) for i in range(count)]]
    p[:,3]=np.minimum(p[:,3].astype(int)*2,255)
    return p

def indices(raw, p):
    w,h=p['width'],p['height'];a=np.frombuffer(raw[p['start']:p['end']],np.uint8)
    if p['image_type']==4:
        require((w,h)==(512,256),'4bpp geometry')
        return np.stack((a&15,a>>4),axis=-1).ravel()[list(map4())].reshape(h,w).copy()
    return a[swizzle_map(w,h)].reshape(h,w).copy()

def put(raw,p,idx):
    a=np.empty(idx.size,np.uint8)
    if p['image_type']==4:
        require(idx.max()<16,'4bpp index range');a[list(map4())]=idx.ravel();a=a[::2]|(a[1::2]<<4)
    else:a[swizzle_map(p['width'],p['height'])]=idx.ravel()
    raw[p['start']:p['end']]=a.tobytes()
    require(np.array_equal(indices(raw,p),idx),'Pixel roundtrip')

def quantize(im,pal):
    a=np.array(im).astype(np.int32);p=pal.astype(np.int32)
    # Premultiplication makes transparent palette RGB immaterial.
    a[:,:,:3]=a[:,:,:3]*a[:,:,3:4]//255;p[:,:3]=p[:,:3]*p[:,3:4]//255
    result=np.empty(a.shape[:2],np.uint8)
    for y in range(a.shape[0]):result[y]=((a[y,:,None,:]-p[None,:,:])**2).sum(2).argmin(1)
    return result

def text_layer(text,size,max_width):
    f=ImageFont.truetype(FONT,size);b=f.getbbox(text)
    im=Image.new('L',(b[2]-b[0]+4,b[3]-b[1]+4));ImageDraw.Draw(im).text((2-b[0],2-b[1]),text,font=f,fill=255)
    if im.width>max_width:im=im.resize((max_width,im.height),Image.Resampling.LANCZOS)
    return im

def logo(raw, donor):
    ps=list(pictures(raw)); ps=[p for p in ps if p['width']==512 and p['height']==256 and p['image_type']==5]
    ds=[p for p in pictures(donor) if p['width']==512 and p['height']==256 and p['image_type']==5]
    require(len(ps)==len(ds)==6,'Logo picture count')
    out=bytearray(raw)
    for k,rect,palno in [(2,(0,0,512,256),2),(3,(0,0,96,256),3),(4,(0,0,416,192),4)]:
        x0,y0,x1,y1=rect;a=indices(raw,ps[k]);b=indices(donor,ds[k]);v=np.s_[y0:y1,x0:x1]
        src=palette(donor,ds[0]['end']+palno*1024);dst=palette(raw,ps[0]['end']+palno*1024)
        used=np.unique(b[v]);remap=np.arange(256,dtype=np.uint8)
        for i in used:
            if np.array_equal(src[i],dst[i]):continue
            matches=np.where(np.all(src[i]==dst,axis=1))[0]
            if src[i,3]==0:matches=np.where(dst[:,3]==0)[0]
            require(len(matches)>0,'No exact native logo color for '+str((palno,int(i))))
            remap[i]=matches[0]
        a[v]=remap[b[v]];put(out,ps[k],a)
    return bytes(out)

def subtitle(raw):
    p=list(pictures(raw))[0];idx=indices(raw,p);pal=palette(raw,p['end'],64)[:16]
    im=Image.fromarray(pal[idx]);draw=ImageDraw.Draw(im)
    # Keep the native parallelogram border and the separate orange tail.
    draw.polygon([(58,21),(324,21),(309,44),(43,44)],fill=(0,0,0,0))
    idx[18:47,40:327]=quantize(im.crop((40,18,327,47)),pal)
    for box,text,size in [((63,21,306,43),'SPECIAL DISC',24),((354,0,506,29),'SPECIAL',25),((356,31,479,62),'DISC',25)]:
        x0,y0,x1,y1=box;draw.rectangle((x0,y0,x1-1,y1-1),fill=(0,0,0,0))
        mask=text_layer(text,size,x1-x0-4);x=x0+(x1-x0-mask.width)//2;y=y0+(y1-y0-mask.height)//2
        draw.bitmap((x+1,y+1),mask,fill=(180,60,0,255));draw.bitmap((x,y),mask,fill=(255,205,0,255))
        idx[y0:y1,x0:x1]=quantize(im.crop(box),pal)
    out=bytearray(raw);put(out,p,idx)
    Image.fromarray(pal[idx]).save(DEST/'english-subtitle.png')
    return bytes(out)

def theater(raw):
    ps=list(pictures(raw));out=bytearray(raw);previews=[]
    require(len(ps)==8,'Theater texture count')
    for k,label in enumerate(LABELS):
        p=ps[k+1];idx=indices(raw,p);pal=palette(raw,ps[1]['end']+k*1024)
        im=Image.fromarray(pal[idx]);box=[(270,32,564,64),(382,32,563,64),(358,32,563,64),(365,30,606,63),(398,32,565,64)][k]
        x0,y0,x1,y1=box
        # Fill only the old glyph silhouettes from their neighbouring glow.
        # The fixed pixels around each mask constrain a harmonic fill, avoiding
        # rectangular replacement plates over the native banner illustration.
        crop=im.crop(box).convert('RGB')
        a=np.array(crop).astype(float);lum=a.mean(2)
        holes=Image.fromarray(np.uint8((lum>150 if k==4 else lum<105)*255)).filter(ImageFilter.MaxFilter(5))
        holes=np.array(holes)>0
        fill=np.array(crop.filter(ImageFilter.MinFilter(25) if k==4 else ImageFilter.MaxFilter(25))).astype(float)
        a[holes]=fill[holes]
        for _ in range(350):
            pad=np.pad(a,((1,1),(1,1),(0,0)),mode='edge')
            avg=(pad[:-2,1:-1]+pad[2:,1:-1]+pad[1:-1,:-2]+pad[1:-1,2:])/4
            a[holes]=avg[holes]
        im.paste(Image.fromarray(np.uint8(np.clip(a,0,255))),box)
        edit=(240 if k<4 else 350,24,610 if k==3 else 590,64 if k!=3 else 63)
        mask=text_layer(label,31,300 if k<4 else 210);x=(603 if k==3 else 565)-mask.width;y=32
        glow=Image.new('L',im.size);glow.paste(mask,(x,y));glow=glow.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(3)).point(lambda a:a*0.65)
        tint=Image.new('RGBA',im.size,(230,230,210,255) if k<4 else (25,25,30,255))
        im=Image.composite(tint,im,glow)
        ImageDraw.Draw(im).bitmap((x,y),mask,fill=(245,245,250,255) if k==4 else (0,0,0,255))
        x0,y0,x1,y1=edit;idx[y0:y1,x0:x1]=quantize(im.crop(edit),pal);put(out,p,idx)
        final=Image.fromarray(pal[idx]);final.save(DEST/f'english-banner-{k}.png');previews.append(final.crop((0,0,624,80)))
    p=ps[6];idx=indices(raw,p);pal=palette(raw,p['end']);im=Image.fromarray(pal[idx]);dr=ImageDraw.Draw(im);box=(45,5,388,44)
    for y in range(5,44):
        c=int(122-(y-5)*1.5);dr.line((45,y,387,y),fill=(c,c,c,255))
    mask=text_layer('SPECIAL THEATER',31,330);x=45+(343-mask.width)//2;y=5+(39-mask.height)//2
    dr.bitmap((x+1,y+2),mask,fill=(20,20,20,255));dr.bitmap((x,y),mask,fill=(235,235,235,255))
    idx[5:44,45:388]=quantize(im.crop(box),pal);put(out,p,idx)
    head=Image.fromarray(pal[idx]);head.save(DEST/'english-theater-header.png')
    canvas=Image.new('RGBA',(640,520),(32,32,32,255));canvas.alpha_composite(head,(12,0))
    for k,im in enumerate(previews):canvas.alpha_composite(im,(8,75+k*87))
    canvas.convert('RGB').save(DEST/'english-theater-preview.png')
    return bytes(out)

def pack(raw,slot,label):
    plain=DEST/(label+'.decoded');packed=DEST/(label+'.banlz');plain.write_bytes(raw)
    subprocess.run([str(PACKER),str(plain),str(packed),'96','optimal'],check=True,capture_output=True)
    b=packed.read_bytes();require(decode(b)[0]==raw,'Strict compressed readback '+label)
    require(len(b)<=len(slot),f'{label} exceeds native slot: {len(b)} > {len(slot)}')
    return b+bytes(len(slot)-len(b)),len(b)

def title_preview(raw, sub):
    ps=list(pictures(raw));clut=ps[0]['end']
    def page(k,palno):return Image.fromarray(palette(raw,clut+palno*1024)[indices(raw,ps[k])])
    canvas=Image.new('RGBA',(640,330),(22,58,70,255))
    canvas.alpha_composite(page(2,2),(16,0))
    canvas.alpha_composite(page(3,3).crop((0,0,96,256)),(528,0))
    canvas.alpha_composite(page(5,4).crop((0,0,288,208)),(336,0))
    canvas.alpha_composite(page(4,4).crop((0,0,416,192)),(16,32))
    p=list(pictures(sub))[0];im=Image.fromarray(palette(sub,p['end'],64)[:16][indices(sub,p)])
    canvas.alpha_composite(im.crop((0,0,340,54)),(20,250))
    canvas.convert('RGB').save(DEST/'english-title-preview.png')

def verify_pixels(old,new,label):
    """Guard all palettes, texture headers and artwork outside explicit boxes."""
    ps=list(pictures(old));allowed=np.zeros(len(old),bool)
    if label.startswith('title-'):
        ps=[p for p in ps if p['width']==512 and p['height']==256 and p['image_type']==5]
        edits=[(ps[2],[(0,0,512,256)]),(ps[3],[(0,0,96,256)]),(ps[4],[(0,0,416,192)])]
    elif label=='special-disc':edits=[(ps[0],[(40,18,327,47),(354,0,506,29),(356,31,479,62)])]
    else:edits=[(ps[k+1],[(240 if k<4 else 350,24,610 if k==3 else 590,64 if k!=3 else 63)]) for k in range(5)]+[(ps[6],[(45,5,388,44)])]
    for p,rects in edits:
        a=indices(old,p);b=indices(new,p);mask=np.zeros(a.shape,bool)
        for x0,y0,x1,y1 in rects:mask[y0:y1,x0:x1]=True
        require(np.array_equal(a[~mask],b[~mask]),'Protected texel changed '+label)
        allowed[p['start']:p['end']]=True
    a=np.frombuffer(old,np.uint8);b=np.frombuffer(new,np.uint8)
    require(np.array_equal(a[~allowed],b[~allowed]),'Non-pixel data changed '+label)

def build(disc):
    DEST.mkdir(parents=True,exist_ok=True);donor=DONOR.read_bytes()
    require(sha(donor)=='fed49ccb59cffe2ddbf0f7de6cbaede647a03aa51fe372941b429f0c4e2ba6b5','English logo donor drift')
    vt=disc.read(VT1);aid=disc.read(AID);offsets=struct.unpack_from('<109I',disc.read(EXE),VT1_TABLE)
    members={VT1:bytearray(vt),AID:bytearray(aid)};rows=[]
    for n,lo,hi,label,fn in [(VT1,*offsets[7:9],'title-intro',lambda r:logo(r,donor)),(VT1,*offsets[28:30],'special-disc',subtitle),(VT1,*offsets[29:31],'title-menu',lambda r:logo(r,donor)),(AID,0xc5f0,0x63b50,'special-theater',theater)]:
        source=bytes(members[n][lo:hi]);raw=decode(source)[0]
        require(sha(raw)==PREIMAGES[label],'Native artwork preimage '+label)
        modified=fn(raw)
        require(len(raw)==len(modified) and raw!=modified,'No artwork changes '+label)
        verify_pixels(raw,modified,label)
        replacement,size=pack(modified,source,label);members[n][lo:hi]=replacement
        rows.append(dict(member=n,start=lo,end=hi,label=label,source_sha256=sha(raw),decoded_sha256=sha(modified),compressed_bytes=size,headroom=hi-lo-size))
    title_preview(decode(members[VT1][offsets[29]:offsets[30]])[0],decode(members[VT1][offsets[28]:offsets[29]])[0])
    return {n:bytes(v) for n,v in members.items()},dict(entries=rows,logo_reference_sha256=sha(donor),font_sha256=sha(Path(FONT).read_bytes()),labels=['SUPER ROBOT WARS Z','SPECIAL DISC','SPECIAL THEATER']+LABELS,protected_texels_headers_palettes_identical=True,emulator='pending')

if __name__=='__main__':
    members,report=build(Disc(ROOT/'work/output/SRW Z Special Disc English v0.3.17.iso'))
    (DEST/'authoring.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
