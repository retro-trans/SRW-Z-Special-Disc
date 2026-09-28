"""Author the four linear 512x64 mode titles with their native palettes."""
import argparse
import json
import struct
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from sp_disc import *

LABELS={36:'EXTRA STAGE',38:'STORY MODE',45:'CHALLENGE BATTLE',57:'BATTLE VIEWER'}
FONT=Path('C:/Windows/Fonts/arialbi.ttf')

def build():
    disc,exe,archive,offsets=source_records();result=[];previews=[]
    for i,label in LABELS.items():
        lo,hi=offsets[i:i+2];raw=decode(archive[lo:hi])[0];meta=tim2(raw)
        require((meta['width'],meta['height'],meta['start'])==(512,64,64),'Heading geometry')
        idx=np.frombuffer(raw[64:32832],np.uint8).reshape(64,512).copy()
        rgba=meta['palette'][idx].copy();rgba[:,:,3]=np.minimum(rgba[:,:,3].astype(int)*2,255)
        im=Image.fromarray(rgba);draw=ImageDraw.Draw(im)
        # Keep the native plate's screws, bevel, and silhouette. Its old title
        # is confined to this interior; use a clean neutral panel behind type.
        box=(45,5,388,44)
        for y in range(box[1],box[3]+1):
            shade=int(122-(y-5)*1.5);draw.line((box[0],y,box[2],y),fill=(shade,shade,shade,255))
        font=ImageFont.truetype(str(FONT),31);bounds=draw.textbbox((0,0),label,font=font)
        require(bounds[2]-bounds[0]<=330,'Heading text width')
        x=(box[0]+box[2]-(bounds[2]-bounds[0]))//2-bounds[0];y=(box[1]+box[3]-(bounds[3]-bounds[1]))//2-bounds[1]
        draw.text((x+1,y+2),label,font=font,fill=(20,20,20,255),stroke_width=1,stroke_fill=(20,20,20,255))
        draw.text((x,y),label,font=font,fill=(235,235,235,255))
        palette=meta['palette'].astype(np.int32);palette[:,3]=np.minimum(palette[:,3]*2,255)
        arr=np.array(im);region=arr[5:45,45:389].astype(np.int32)
        distances=((region[:,:,None,:]-palette[None,None,:,:])**2).sum(3)
        idx[5:45,45:389]=distances.argmin(2).astype(np.uint8)
        modified=raw[:64]+idx.tobytes()+raw[32832:]
        packed=banlz.compress_record(modified,flags=banlz.parse_header(archive[lo:hi])[1])
        require(len(packed)<=hi-lo,'Heading exceeds native slot')
        require(decode(packed)[0]==modified,'Heading readback')
        payload=packed+bytes(hi-lo-len(packed))
        result.append(dict(chunk=i,label=label,start=lo,end=hi,payload=payload,source_sha256=sha(raw),
            decoded_sha256=sha(modified),compressed_bytes=len(packed),headroom=hi-lo-len(packed),
            text_bounds=[x+bounds[0],y+bounds[1],x+bounds[2],y+bounds[3]],label_rect=list(box),layout='linear'))
        check=meta['palette'][idx].copy();check[:,:,3]=np.minimum(check[:,:,3].astype(int)*2,255)
        previews.append(Image.fromarray(check))
    return result,previews

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args()
    rows,images=build();report=dict(font_sha256=file_sha(FONT),entries=[{k:v for k,v in r.items()if k!='payload'}for r in rows])
    print(json.dumps(report,indent=2))
    if a.write:
        dest=ROOT/'work/ui/english';canvas=Image.new('RGBA',(512,len(images)*80),(24,24,28,255))
        for row,im in zip(rows,images):
            (dest/('heading-%d.bin'%row['chunk'])).write_bytes(row['payload'])
            canvas.alpha_composite(im,(0,list(LABELS).index(row['chunk'])*80))
        canvas.save(dest/'headings.png');(dest/'headings.json').write_text(json.dumps(report,indent=2)+'\n')
    else:print('DRY RUN: no files written')

if __name__=='__main__':main()
