"""Independently compare the final map archive to native and frozen title pixels."""
import json
import struct
import numpy as np
from sp_disc import ROOT, Disc, SOURCE, EXE, decode, sha, file_sha, require


def audit(disc, report):
    config=json.loads((ROOT/'work/translation/en/world_map_titles.json').read_text(encoding='utf-8'))
    bindings=json.loads((ROOT/'work/ui/location-cards/world-map-bindings.json').read_text(encoding='utf-8'))
    require(report['target_sha256']==file_sha(ROOT/'work/translation/en/world_map_titles.json') and
            report['bindings_sha256']==file_sha(ROOT/'work/ui/location-cards/world-map-bindings.json'),
            'Final location approval inputs differ')
    require(report['review_sha256']==config['review_sha256']==file_sha(ROOT/'work/translation/en/world_map_titles_review.json'),
            'Final location review differs')
    native=Disc(SOURCE);name='MAP/MAPMODEL.BIN';old=native.read(name);new=disc.read(name)
    require(sha(old)==bindings['archive_sha256']==report['source_sha256'] and
            sha(new)==report['output_sha256'] and len(old)==len(new), 'Final location archive identity')
    at=0x3542F0;table=native.read(EXE)[at:at+808]
    require(disc.read(EXE)[at:at+808]==table and sha(table)==bindings['table_sha256'],
            'Final location offset table changed')
    offsets=struct.unpack('<202I',table)
    wanted={r['chunk']:r for r in config['entries']}
    expected={r['chunk']:r for r in bindings['entries']}
    logged={r['chunk']:r for r in report['entries']}
    require(set(wanted)==set(expected)==set(logged) and len(wanted)==13, 'Final location inventory')
    checked=[];protected=0
    for i,(lo,hi) in enumerate(zip(offsets,offsets[1:])):
        if i not in wanted:
            require(new[lo:hi]==old[lo:hi], 'Final unrelated map member changed');protected+=1;continue
        before,_=decode(old[lo:hi]);after,used=decode(new[lo:hi]);row=expected[i];target=wanted[i]
        start=row['offset'];end=start+8192;pixels=after[start:end]
        require(len(before)==len(after) and not any(new[lo+used:hi]), 'Final location allocation/padding')
        require(sha(before)==row['decoded_sha256'] and sha(before[start:end])==row['source_raw_sha256'],
                'Final location source binding')
        require(after[:start]==before[:start] and after[end:]==before[end:],
                'Final terrain, subtitle, palette or geometry changed')
        require(sha(pixels)==target['frozen_raw_sha256']==logged[i]['output_raw_sha256'] and
                target['text']==logged[i]['text'], 'Final location English artwork readback')
        # Decode pixels independently from the writer and measure the actual ink.
        values=np.frombuffer(pixels,np.uint8).reshape(32,256)[::-1]
        indexes=np.empty((32,512),np.uint8);indexes[:,::2]=values%16;indexes[:,1::2]=values//16
        y,x=np.nonzero(indexes)
        box=[int(x.min()),int(y.min()),int(x.max())+1,int(y.max())+1]
        require(box==target['layout']['ink_bbox'] and box[0]>=8 and box[2]<=504 and
                box[1]>=2 and box[3]<=30, 'Final location ink clipping')
        checked.append(dict(chunk=i,text=target['text'],ink_bbox=box))
    require(protected==188 and len(checked)==13,'Final location category coverage')
    return dict(titles_read_back=13,other_members_byte_identical=protected,entries=checked,
                palette_geometry_subtitle_and_map_bytes_identical=True,
                offset_table_identical=True,runtime='pending by user choice')
