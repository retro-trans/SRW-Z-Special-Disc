"""Inspect native VT1 full-screen cards; --write saves labelled contact sheets."""
import argparse
import json
import numpy as np
from PIL import Image, ImageDraw
from sp_disc import ROOT, source_records, decode, tim2, sha


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write', action='store_true')
    args = p.parse_args()
    _, _, archive, offsets = source_records()
    rows, images = [], []
    for i in [21,22,23,24,25,35,37,44,56] + list(range(58,108)):
        raw = decode(archive[offsets[i]:offsets[i+1]])[0]
        meta = tim2(raw)
        linear = np.frombuffer(raw[64:64+640*448], np.uint8).reshape(448,640)
        rgba = meta['palette'][linear].copy()
        rgba[:,:,3] = np.minimum(rgba[:,:,3].astype(int)*2,255)
        images.append(Image.fromarray(rgba))
        rows.append(dict(chunk=i,source_sha256=sha(raw),size=[640,448]))
    print(json.dumps(dict(cards=rows,output='work/ui/location-cards/native-contact-*.png'),indent=2))
    if not args.write:
        print('DRY RUN: no files written')
        return
    dest = ROOT/'work/ui/location-cards'
    dest.mkdir(exist_ok=True)
    for start in range(0,len(images),12):
        canvas = Image.new('RGB',(960,984),(30,30,30))
        draw = ImageDraw.Draw(canvas)
        for j,(im,row) in enumerate(zip(images[start:start+12],rows[start:start+12])):
            x,y = j%3*320,j//3*246
            draw.text((x+6,y+4),'VT1 '+str(row['chunk']),fill='white')
            canvas.paste(im.resize((320,224)),(x,y+22))
        canvas.save(dest/f'native-contact-{start//12}.png')
    (dest/'native-card-inventory.json').write_text(json.dumps(rows,indent=2)+'\n')


if __name__ == '__main__':
    main()
