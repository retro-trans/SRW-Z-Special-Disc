"""Extract only native menu textures for visual inspection. Dry-run by default."""
import argparse
import json
from sp_disc import ROOT, VT1, source_records, decode, tim2, sha

# Only these 512x512 atlases have a visually verified pixel layout. Smaller
# heading textures need a separate layout check before they can be exported.
CHUNKS = {16:'title-menu',30:'extra-stage-menu',53:'battle-viewer-menu'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write',action='store_true')
    args=ap.parse_args()
    disc,exe,archive,offsets=source_records()
    rows=[]
    for i,name in CHUNKS.items():
        raw,used=decode(archive[offsets[i]:offsets[i+1]])
        info=tim2(raw)
        row=dict(chunk=i,name=name,width=info['width'],height=info['height'],
                 slot=offsets[i+1]-offsets[i],compressed_bytes=used,decoded_sha256=sha(raw),
                 start=offsets[i],end=offsets[i+1],palette_sha256=sha(info['palette'].tobytes()))
        rows.append(row)
        print(json.dumps(row))
        if args.write:
            from PIL import Image
            out=ROOT/'work/ui/native';out.mkdir(parents=True,exist_ok=True)
            Image.fromarray(info['rgba']).save(out/(name+'.png'))
    if args.write:
        (ROOT/'work/ui/native/menu-assets.json').write_text(json.dumps(rows,indent=2)+'\n')
    else: print('DRY RUN: would save three native menu atlas PNGs and their metadata.')


if __name__=='__main__':main()
