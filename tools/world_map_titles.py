"""Translate the 13 pre-dialogue globe captions, preserving map data and scripts.

The titles are vertically flipped, linear 4bpp images, not TIM2 or text.
Format reference: dyzz/srwz-zh tools/special_disc/writeback/world_map_titles.py.
English artwork is independently authored from reviewed full translations.
"""
import argparse
import json
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from sp_disc import ROOT, Disc, SOURCE, EXE, decode, banlz, sha, file_sha, require

MEMBER = 'MAP/MAPMODEL.BIN'
TABLE = 0x3542F0
COUNT = 201
WIDTH, HEIGHT, BYTES = 512, 32, 8192
SOURCE_SHA = 'a104ef2ef8daaf122ffdcb6fd5b143940d5ab11515a4d5c25598636a5f0bca79'
IDS = (102,111,118,119,138,139,140,160,163,193,195,196,197)
FONT = Path('C:/Windows/Fonts/arialn.ttf')
TARGET = ROOT/'work/translation/en/world_map_titles.json'
BINDINGS = ROOT/'work/ui/location-cards/world-map-bindings.json'
REVIEW = ROOT/'work/translation/en/world_map_titles_review.json'


def unpack(raw):
    require(len(raw) == BYTES, 'Location title byte count')
    values = np.frombuffer(raw, np.uint8)
    return np.stack((values & 15, values >> 4), axis=-1).reshape(HEIGHT,WIDTH)[::-1].copy()


def pack(pixels):
    require(pixels.shape == (HEIGHT,WIDTH) and pixels.dtype == np.uint8 and
            int(pixels.max()) <= 15, 'Location title pixel format')
    rows = pixels[::-1]
    return (rows[:,::2] | rows[:,1::2] << 4).tobytes()


def native():
    disc = Disc(SOURCE)
    archive = disc.read(MEMBER)
    require(sha(archive) == SOURCE_SHA, 'Location archive source identity')
    table = disc.read(EXE)[TABLE:TABLE+4*(COUNT+1)]
    offsets = struct.unpack('<202I', table)
    require(offsets[0] == 0 and offsets[-1] == len(archive) and
            list(offsets) == sorted(set(offsets)) and all(v%16 == 0 for v in offsets),
            'Location archive offset table')
    rows = []
    for i in range(81,COUNT):
        lo,hi = offsets[i:i+2]
        raw,used = decode(archive[lo:hi])
        require(not any(archive[lo+used:hi]), 'Location compressed padding')
        if len(raw) == 6736:
            require(i not in IDS, 'Expected location is a dummy')
            continue
        require(i in IDS, 'Uninventoried world-map location')
        at = 1200 if i == 102 else 1101920 if i == 193 else 1134944
        require(at+2*BYTES+96 <= len(raw), 'Location texture outside map')
        # The native GIF transfer descriptor explicitly describes 512 x 32.
        require(raw[at-8:at] == bytes.fromhex('0002200008000200'), 'Location texture descriptor')
        require(pack(unpack(raw[at:at+BYTES])) == raw[at:at+BYTES], 'Location native pixel roundtrip')
        rows.append(dict(chunk=i,offset=at,stored_start=lo,stored_end=hi,
                         decoded_sha256=sha(raw),source_raw_sha256=sha(raw[at:at+BYTES]),
                         subtitle_sha256=sha(raw[at+BYTES+96:at+2*BYTES+96]),
                         descriptor_sha256=sha(raw[at-32:at]),raw=raw))
    require(tuple(r['chunk'] for r in rows) == IDS, 'Location category coverage')
    return archive, offsets, table, rows


def render(text):
    require(text and text.isascii() and '\n' not in text, 'Invalid location title')
    # Use the full declared texture width; no change to its screen position/UVs.
    # All words remain intact. Long names use smaller type, never truncation.
    for size in range(28,17,-1):
        font = ImageFont.truetype(str(FONT),size)
        bounds = font.getbbox(text)
        width,height = bounds[2]-bounds[0],bounds[3]-bounds[1]
        if width <= 496 and height <= 28:
            break
    else:
        raise ValueError('Full location caption does not fit: '+text)
    im = Image.new('L',(WIDTH,HEIGHT),0)
    x=(WIDTH-width)//2-bounds[0];y=(HEIGHT-height)//2-bounds[1]
    ImageDraw.Draw(im).text((x,y),text,font=font,fill=255)
    pixels = ((np.asarray(im,dtype=np.uint16)*15+127)//255).astype(np.uint8)
    require(not pixels[:2].any() and not pixels[-2:].any() and
            not pixels[:,:8].any() and not pixels[:,-8:].any(), 'Location caption leaves safe area')
    return pack(pixels),dict(font_size=size,ink_bbox=list(im.getbbox()),full_text_preserved=True)


def build():
    config=json.loads(TARGET.read_text(encoding='utf-8'))
    bindings=json.loads(BINDINGS.read_text(encoding='utf-8'))
    require(config['status']=='reviewed' and config['review_sha256']==file_sha(REVIEW),
            'Location translation review identity')
    require(config['font_sha256']==file_sha(FONT), 'Location font identity')
    require(config['bindings_sha256']==file_sha(BINDINGS), 'Location binding identity')
    require(tuple(r['chunk'] for r in config['entries'])==IDS, 'Location translation coverage')
    review=json.loads(REVIEW.read_text(encoding='utf-8'))
    require(file_sha(ROOT/review['draft_path'])==review['draft_sha256'] and
            review['entries_examined']==13, 'Location reviewed draft identity')
    require([(r['chunk'],r['text']) for r in config['entries']]==
            [(r['chunk'],r['text'].replace('Dome Polis','Domepolis')) for r in review['entries']],
            'Unapproved location meaning change')
    archive,offsets,table,rows=native();out=bytearray(archive);reports=[];previews=[]
    require(bindings['archive_sha256']==SOURCE_SHA and bindings['table_sha256']==sha(table),
            'Location archive binding drift')
    require(bindings['entries']==[{k:v for k,v in r.items() if k!='raw'} for r in rows],
            'Location native ownership drift')
    for row,target in zip(rows,config['entries']):
        require(row['chunk']==target['chunk'], 'Location target order')
        pixels,layout=render(target['text']);at=row['offset'];raw=row['raw']
        require(sha(pixels)==target['frozen_raw_sha256'] and layout==target['layout'],
                'Location frozen layout drift')
        changed=raw[:at]+pixels+raw[at+BYTES:]
        lo,hi=row['stored_start'],row['stored_end']
        encoded=banlz.compress_record(changed,flags=banlz.parse_header(archive[lo:hi])[1])
        require(len(encoded)<=hi-lo, 'Location compressed allocation overflow')
        require(decode(encoded)[0]==changed, 'Location strict compression readback')
        out[lo:hi]=encoded+bytes(hi-lo-len(encoded))
        require(changed[:at]==raw[:at] and changed[at+BYTES:]==raw[at+BYTES:],
                'Location map data or subtitle changed')
        reports.append(dict(chunk=row['chunk'],text=target['text'],offset=at,
                            source_raw_sha256=row['source_raw_sha256'],output_raw_sha256=sha(pixels),
                            decoded_sha256=sha(changed),stored_start=lo,stored_end=hi,
                            output_stored_sha256=sha(out[lo:hi]),compressed_bytes=len(encoded),
                            headroom=hi-lo-len(encoded),layout=layout))
        previews.append((row['chunk'],unpack(raw[at:at+BYTES]),unpack(pixels)))
    # Byte-exact protection for every other compressed member, including all maps.
    for i,(lo,hi) in enumerate(zip(offsets,offsets[1:])):
        if i not in IDS:require(out[lo:hi]==archive[lo:hi], 'Non-title map member changed')
    report=dict(count=len(reports),entries=reports,font=str(FONT),font_sha256=file_sha(FONT),
                target_sha256=file_sha(TARGET),review_sha256=file_sha(REVIEW),
                bindings_sha256=file_sha(BINDINGS),source_sha256=SOURCE_SHA,
                output_sha256=sha(out),bytes=len(out),offset_table_sha256=sha(table),
                other_188_members_byte_identical=True,all_non_title_decoded_bytes_identical=True,
                palettes_descriptors_and_subtitles_identical=True,story_dialogue_changed=False,
                runtime='pending by user choice')
    return bytes(out),report,previews


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    archive,report,previews=build()
    print(json.dumps(report,indent=2),flush=True)
    if not args.write:
        print('DRY RUN passed; no files written');return
    canvas=Image.new('RGB',(1080,len(previews)*54),(20,20,20));draw=ImageDraw.Draw(canvas)
    for i,(chunk,before,after) in enumerate(previews):
        y=i*54;draw.text((2,y+12),str(chunk),fill='white')
        canvas.paste(Image.fromarray(before*17),(50,y+6))
        canvas.paste(Image.fromarray(after*17),(565,y+6))
    dest=ROOT/'work/ui/location-cards'
    canvas.save(dest/'world-map-titles-english-0.2.16.png')
    (dest/'world-map-title-layout-0.2.16.json').write_text(json.dumps(report,indent=2)+'\n')
    path=ROOT/'work/cache/nonstory/MAP/MAPMODEL.BIN';path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(archive)
    print('Wrote reviewed location component and native/English preview')


if __name__=='__main__':main()
