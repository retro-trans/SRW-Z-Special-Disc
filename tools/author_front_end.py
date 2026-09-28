"""Compile English labels into native menu textures; no executable/text changes.

Dry-run prints the proposed labels and measured bounds. --write saves frozen
indices, previews, and the source/asset/font locks used by the build.
"""
import argparse
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from sp_disc import ROOT, source_records, decode, tim2, sha, require, file_sha

TEXT = ROOT/'work/translation/en/front_end.json'
OUT = ROOT/'work/ui/english'
SCALE = 4
BUTTONS = [(0,0),(0,1),(1,0),(1,1)]
RECT = (29,4,237,34)


def label_mask(text, font_path, size):
    font=ImageFont.truetype(str(font_path),size*SCALE)
    box=font.getbbox(text)
    w,h=box[2]-box[0],box[3]-box[1]
    require(w <= 200*SCALE and h <= 26*SCALE, 'Label too large: '+text)
    canvas=Image.new('L',(256*SCALE,40*SCALE))
    ImageDraw.Draw(canvas).text(((256*SCALE-w)//2-box[0],(40*SCALE-h)//2-box[1]-SCALE),text,font=font,fill=255)
    mask=canvas.resize((256,40),Image.Resampling.LANCZOS)
    return mask, dict(text=text,ink_width=round(w/SCALE,2),ink_height=round(h/SCALE,2),box=mask.getbbox())


def blank_plate(reference,state):
    # The short TRI label leaves native background on both sides. Reconstruct
    # only its central text area; the original frame is never used as replacement.
    tile=reference[200+40*state:240+40*state,:256].copy()
    left,right=86,178
    for y in range(4,34):
        a=tile[y,left-3:left,:3].astype(float).mean(0)
        b=tile[y,right:right+3,:3].astype(float).mean(0)
        for x in range(left,right):
            t=(x-left)/(right-left-1)
            tile[y,x,:3]=np.clip(a*(1-t)+b*t,0,255).astype(np.uint8)
    return tile


def closest_palette(rgb, palette):
    candidates=np.flatnonzero(palette[:,3]>=120)
    require(len(candidates)>0,'No opaque palette colours')
    pixels=rgb.astype(np.int32).reshape(-1,3)
    colors=palette[candidates,:3].astype(np.int32)
    out=np.empty(len(pixels),np.uint8)
    for start in range(0,len(pixels),1024):
        dist=((pixels[start:start+1024,None,:]-colors[None,:,:])**2).sum(2)
        out[start:start+1024]=candidates[np.argmin(dist,axis=1)]
    return out.reshape(rgb.shape[:2])


def render(raw,labels,reference,config):
    info=tim2(raw); result=info['indices'].copy();before=result.copy()
    # Native states intentionally include light and almost-invisible transition frames.
    fills=[(12,14,12),(54,80,26),(238,255,210),(125,185,46),(6,15,2)]
    rims=[(175,180,171),(220,242,164),(248,255,225),(161,214,72),(81,135,24)]
    rows=[];allowed=np.zeros(result.shape,bool)
    for (col,row),text in zip(BUTTONS,labels):
        mask,bounds=label_mask(text,config['font'],config['font_size'])
        rows.append(dict(bounds,col=col,row=row))
        m=np.array(mask,dtype=float)/255.0
        rim=np.array(mask.filter(ImageFilter.MaxFilter(3)),dtype=float)/255.0
        for state in range(5):
            plate=blank_plate(reference,state)[:,:,:3].astype(float)
            plate=plate*(1-rim[:,:,None])+np.array(rims[state])*rim[:,:,None]
            plate=plate*(1-m[:,:,None])+np.array(fills[state])*m[:,:,None]
            x0,y0,x1,y1=RECT
            q=closest_palette(np.clip(plate[y0:y1,x0:x1],0,255),info['palette'])
            ys=slice(row*200+state*40+y0,row*200+state*40+y1)
            xs=slice(col*256+x0,col*256+x1)
            result[ys,xs]=q;allowed[ys,xs]=True
    require(np.array_equal(result[~allowed],before[~allowed]),'Pixels outside labels changed')
    rgba=info['palette'][result].copy();rgba[:,:,3]=np.minimum(rgba[:,:,3].astype(int)*2,255)
    return result,rgba,rows,int((result!=before).sum())


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    config=json.loads(TEXT.read_text(encoding='utf-8'))
    disc,exe,archive,offsets=source_records()
    reference=tim2(decode(archive[offsets[53]:offsets[54]])[0])['rgba']
    report=dict(schema_version=1,scope=config['scope'],translation_sha256=file_sha(TEXT),
                font_path=config['font'],font_sha256=file_sha(config['font']),
                palette_policy='preserve native palette bytes',label_rect=RECT,atlases=[])
    for atlas in config['atlases']:
        i=atlas['chunk'];raw,used=decode(archive[offsets[i]:offsets[i+1]])
        indices,rgba,labels,changed=render(raw,atlas['labels'],reference,config)
        item=dict(atlas,source_sha256=sha(raw),indices_sha256=sha(indices.tobytes()),
                  changed_pixels=changed,labels_measured=labels)
        report['atlases'].append(item)
        print(json.dumps(item),flush=True)
        if args.write:
            OUT.mkdir(parents=True,exist_ok=True)
            Image.fromarray(rgba).save(OUT/(atlas['id']+'.png'))
            np.save(OUT/(atlas['id']+'.npy'),indices,allow_pickle=False)
    if args.write:(OUT/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no assets written; pass --write to freeze these exact menu labels.')


if __name__=='__main__':main()
