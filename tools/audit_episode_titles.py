"""Independent final-disc checks for episode artwork and untouched animation data."""
import json
import struct
import numpy as np
from sp_disc import ROOT, SOURCE, Disc, EXE, VT1, decode, file_sha, sha, require

def pixels(raw,w,h):
    a=np.frombuffer(raw,np.uint8).reshape(h,w//2);out=np.empty((h,w),np.uint8)
    out[:,::2]=a%16;out[:,1::2]=a//16
    return out

def audit(disc,report):
    target=ROOT/'work/translation/en/episode_titles.json'
    bindings=ROOT/'work/ui/episode-titles/native-inventory.json'
    review=ROOT/'work/translation/en/episode_titles_review.json'
    cfg=json.loads(target.read_text(encoding='utf-8'));inv=json.loads(bindings.read_text(encoding='utf-8'))
    require(file_sha(target)==report['target_sha256'] and file_sha(bindings)==report['bindings_sha256']==cfg['bindings_sha256'] and
            file_sha(review)==report['review_sha256']==cfg['review_sha256'],'Episode approval identity')
    require(cfg['frozen_records']==report['entries'],'Episode frozen records mismatch')
    native=Disc(SOURCE);old=native.read(VT1);new=disc.read(VT1);exe=native.read(EXE)
    require(len(old)==len(new),'Episode archive size changed')
    require(disc.read(EXE)[0x3763e0:0x376450]==exe[0x3763e0:0x376450], 'Episode runtime table changed')
    expected={r['record']:r for r in cfg['frozen_records']};checked=[];unchanged=[]
    for row in inv['records']:
        i=row['index'];lo,hi=row['start'],row['end'];a=old[lo:hi];b=new[lo:hi]
        if i not in expected or i==20:
            require(a==b,'Episode animation/native English slot changed');unchanged.append(i)
            if i==20:checked.append(15)
            continue
        before,_=decode(a);after,used=decode(b);r=expected[i]
        require(len(before)==len(after) and sha(before)==r['source_sha256'] and
                sha(after)==r['decoded_sha256'] and not any(b[used:]),'Episode decoded bytes/padding mismatch')
        if i==4:
            start,end=197376,202368;p=pixels(after[start:end],416,24);q=pixels(before[start:end],416,24)
            require(np.array_equal(p[:,:320],q[:,:320]) and not p[:,368:].any() and p[:,320:368].any(),
                    'Episode digit/prefix/suffix scope violation')
        else:
            start,end=96,16480;p=pixels(after[start:end],512,64)
            require(np.array_equal(p[:,::2],p[:,1::2]),'Episode double-column aspect mismatch')
            y,x=np.nonzero(p);box=[int(x.min())//2,int(y.min()),int(x.max()+1)//2,int(y.max()+1)]
            require(box==r['layout']['ink_bbox'] and box[0]>=4 and box[2]<=252 and box[1]>=4 and box[3]<=28,
                    'Episode title clipped or wrong orientation')
            require(cfg['entries'][i-6]['text']==r['text'],'Episode text/report disagreement');checked.append(i-5)
        require(before[:start]==after[:start] and before[end:]==after[end:],'Episode palette/frame/animation changed')
        require(sha(after[start:end])==r['pixels_sha256'],'Episode frozen pixels mismatch')
    require(sorted(checked)==list(range(1,22)) and unchanged==[0,1,2,3,5,20], 'Episode category coverage')
    return dict(titles_read_back=21,translated_images=20,native_english_images=1,header='Ep. [number]',
                untouched_records=unchanged,digits_palettes_frames_and_animations_identical=True,
                offset_table_identical=True,runtime='pending by user choice')
