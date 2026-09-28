"""Translate the pre-title battle demo's separate names and title textures."""
import argparse
import json
import struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from sp_disc import ROOT, SOURCE, Disc, sha, file_sha, require, tim2, replace_indices
from library_text import text, japanese
from menu_encoding import menu_encode

MEMBER = 'BTL/OP.BIN'
SEG = 'BTL/OP.SEG'
SOURCE_SHA = 'e2c7f59a6ae5723da16adb090f9d8cd8f12201d3a39da95cdcef838ed4b77489'
OFFSETS = (0, 48, 266224, 266272, 532096, 532144, 798496)
INPUT = ROOT/'work/translation/en/attract_demo.json'
REVIEW = ROOT/'work/translation/en/attract_demo_review.json'
SYSTEM_FONT = ROOT.__class__('C:/Windows/Fonts/timesbi.ttf')
TITLES = [
    ['Mobile Suit Gundam SEED DESTINY', 'Mazinger Z', 'Super Dimension Century Orguss',
     'Space Warrior Baldios', 'Mobile Suit Zeta Gundam', 'Invincible Steel Man Daitarn 3', 'Genesis of Aquarion'],
    ['The Big O', 'Great Mazinger', 'Invincible Superman Zambot 3', 'Combat Mecha Xabungle',
     "Char's Counterattack", 'Overman King Gainer'],
    ['Gravion', 'UFO Robo Grendizer', 'After War Gundam X', 'Getter Robo G',
     'Space Emperor God Sigma', 'Turn A Gundam', 'Eureka Seven'],
]


def native():
    disc = Disc(SOURCE); data = disc.read(MEMBER); seg = disc.read(SEG)
    require(sha(data) == SOURCE_SHA and seg == struct.pack('<7I', *OFFSETS), 'Demo source drift')
    banks = []; names = []
    for bank in range(3):
        header, base, end = OFFSETS[bank*2:bank*2+3]
        count = struct.unpack_from('<I', data, base)[0]
        require(count == len(TITLES[bank]) and not any(data[base+4:base+16]), 'Demo scene count/header')
        pointers = struct.unpack_from('<%dI' % (count+2), data, header+4)
        require(pointers[0] == 16 and pointers[-1]+base == end, 'Demo internal pointer bounds')
        require(list(pointers) == sorted(set(pointers)), 'Demo pointer order')
        image_at = base+16; image_end = base+pointers[1]
        texture = data[image_at:image_end]; meta = tim2(texture)
        require(len(texture) == 263232 and (meta['width'], meta['height']) == (512, 512), 'Demo title geometry')
        banks.append(dict(bank=bank, offset=image_at, bytes=len(texture), source_sha256=sha(texture)))
        for scene in range(count):
            start = base+pointers[scene+1]; stop = base+pointers[scene+2]
            require(data[start+1] == scene and data[start+2] in (1, 2), 'Demo scene identity/event count')
            cursor = start+16
            for side in range(2):
                crew = struct.unpack_from('<I', data, cursor+20)[0]
                require(1 <= crew <= 7, 'Demo crew count')
                for slot in range(crew):
                    pilot = struct.unpack_from('<I', data, cursor+32+slot*32)[0]
                    require(not any(data[cursor+36+slot*32:cursor+44+slot*32]), 'Demo crew reserved words')
                    at = cursor+44+slot*32; cell = data[at:at+20]; raw = cell.split(b'\0')[0]
                    require(raw and not any(cell[len(raw):]) and japanese(raw.decode('cp932')), 'Demo name cell')
                    names.append(dict(id=f'{bank}/{scene}/{side}/{slot}', offset=at, capacity=20,pilot_id=pilot,
                        source_sha256=sha(raw), source_cell_sha256=sha(cell), raw=raw))
                require(not any(data[cursor+32+crew*32:cursor+144+crew*32]), 'Demo reserved unit tail')
                cursor += 144+crew*32
            require(cursor+data[start+2]*16 == stop, 'Demo event/record boundary')
    require(len(names) == 61, 'Demo name inventory')
    return data, banks, names


def prepare():
    data, banks, names = native()
    # Reuse only display-name fields, never family/given fields whose English
    # order is reversed. These translations already ship in the regular UI.
    path = ROOT/'work/analysis/build-0.2.9-menu_names.json'; source = json.loads(path.read_text(encoding='utf-8'))
    answers = {}
    for row in source['changes']:
        if row['id'].startswith('pilot/') and row['id'].endswith('/display'):
            answers[row['id']] = row
    entries = []
    for row in names:
        key = f"pilot/{row['pilot_id']}/display"; reused = answers[key]
        require(reused['source_sha256'] == row['source_sha256'], 'Demo pilot/display identity mismatch')
        value = reused['text']; require(value and not japanese(value), 'Untranslated demo name')
        encoded = menu_encode(value); require(len(encoded)+1 <= row['capacity'], 'Demo name slot overflow')
        entries.append(dict({k:v for k,v in row.items() if k != 'raw'}, text=value,
            reused_display_ids=[key]))
    library_path = ROOT/'work/translation/en/library_complete.json'
    library = json.loads(library_path.read_text(encoding='utf-8'))['entries']; titles = []
    for bank, labels in enumerate(TITLES):
        for scene, value in enumerate(labels):
            matches = [r['id'] for r in library if r['tag'] == 'PRDC' and r['text'] == value]
            require(matches, 'Demo title lacks reviewed Library correspondence')
            titles.append(dict(bank=bank, scene=scene, text=value, rect=[0,scene*40,512,40],
                library_field_ids=matches, source_texture_sha256=banks[bank]['source_sha256']))
    return dict(schema_version=1, source_member=MEMBER, source_sha256=SOURCE_SHA,
        source_seg_sha256=sha(Disc(SOURCE).read(SEG)), banks=banks, names=entries, titles=titles,
        reuse_inputs={str(p.relative_to(ROOT)):file_sha(p) for p in (path,library_path)},
        font_sha256=file_sha(SYSTEM_FONT), font='Windows Times New Roman Bold Italic; local dependency, not redistributed',
        screenshot=dict(bank=0,scene=1,name_offset=0x4064c,title_rect=[0,40,512,40],
            caption_source_id=22375,caption_bank=301,caption_record=6,
            evidence='User confirms pre-title demo on v0.2.9; native title pixels and separate name match supplied screenshot'),
        runtime='Pending by user choice')


def render_title(value, palette):
    # This is the game's indexed UI atlas, rendered through the same font/CLUT
    # authoring approach as author_headings.py. Preserve its native CLUT.
    factor = 4; sample = ImageDraw.Draw(Image.new('RGBA',(1,1)))
    for size in range(34, 19, -1):
        font = ImageFont.truetype(str(SYSTEM_FONT), size*factor)
        box = sample.textbbox((0,0), value, font=font, stroke_width=2*factor)
        w,h = box[2]-box[0],box[3]-box[1]
        if w <= 504*factor and h <= 36*factor: break
    require(w <= 504*factor and h <= 36*factor, 'Demo title does not fit')
    canvas = Image.new('RGBA',(512*factor,40*factor)); draw = ImageDraw.Draw(canvas)
    x=4*factor-box[0]; y=(40*factor-h)//2-box[1]
    draw.text((x,y),value,font=font,fill=(246,246,255,255),stroke_width=2*factor,stroke_fill=(6,3,67,255))
    draw.text((x,y),value,font=font,fill=(246,246,255,255),stroke_width=factor,stroke_fill=(18,15,216,255))
    canvas = canvas.resize((512,40),Image.Resampling.LANCZOS)
    pixels = np.asarray(canvas).astype(np.int32); pal = palette.astype(np.int32).copy()
    pal[:,3] = np.minimum(255,pal[:,3]*2)
    # Compare premultiplied RGB to avoid transparent green causing a fringe.
    pixels[:,:,:3] = pixels[:,:,:3]*pixels[:,:,3:4]//255
    pal[:,:3] = pal[:,:3]*pal[:,3:4]//255
    distance = ((pixels[:,:,None,:]-pal[None,None,:,:])**2).sum(3)
    indices = distance.argmin(2).astype(np.uint8)
    indices[np.asarray(canvas)[:,:,3] == 0] = 0
    yy,xx = np.nonzero(indices)
    require(len(xx) and xx.min() >= 0 and xx.max() < 512 and yy.min() >= 0 and yy.max() < 40, 'Demo title clipping')
    return indices,dict(font_size=size,ink_bounds=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)])


def build():
    cfg = json.loads(INPUT.read_text(encoding='utf-8')); fresh=prepare()
    # Preserve the original meaning review when unrelated Library descriptions
    # change. Every reviewed label, native identity, source cell, title reference,
    # coordinate and font must still match the freshly derived manifest exactly.
    require({k:v for k,v in cfg.items() if k!='reuse_inputs'}
            =={k:v for k,v in fresh.items() if k!='reuse_inputs'}, 'Demo reviewed content changed')
    require(set(cfg['reuse_inputs'])==set(fresh['reuse_inputs']), 'Demo reuse input inventory changed')
    library_key=str((ROOT/'work/translation/en/library_complete.json').relative_to(ROOT))
    require(all(value==fresh['reuse_inputs'][key] for key,value in cfg['reuse_inputs'].items()
                if key!=library_key), 'Demo display-name reuse source changed')
    review = json.loads(REVIEW.read_text(encoding='utf-8'))
    require(review['status'] == 'approved' and not review['corrections']
            and review['input_sha256'] == file_sha(INPUT) and review['source_sha256'] == SOURCE_SHA
            and review['source_seg_sha256'] == cfg['source_seg_sha256'] and review['reuse_inputs'] == cfg['reuse_inputs'],
            'Stale/unapproved demo meaning review')
    require(review['reviewed_name_ids'] == [r['id'] for r in cfg['names']]
            and review['reviewed_title_ids'] == [f"{r['bank']}/{r['scene']}" for r in cfg['titles']], 'Incomplete demo meaning review')
    require(len(review['name_decisions']) == 61 and len(review['title_decisions']) == 20, 'Demo review decision coverage')
    for row,decision in zip(cfg['names'],review['name_decisions']):
        require(all(row[k] == decision[k] for k in ('id','pilot_id','text','source_sha256','source_cell_sha256'))
                and decision['decision'] == 'approved' and [decision['reused_display_id']] == row['reused_display_ids'],
                'Demo name review differs from input')
    for row,decision in zip(cfg['titles'],review['title_decisions']):
        require(all(row[k] == decision[k] for k in ('bank','scene','text','source_texture_sha256'))
                and decision['decision'] == 'approved' and decision['native_rect'] == row['rect']
                and decision['library_reference_id'] in row['library_field_ids'], 'Demo title review differs from input')
    data,banks,names = native(); out = bytearray(data); images=[]; changes=[]; ranges=[]
    for row in cfg['names']:
        at=row['offset']; cap=row['capacity']; raw=menu_encode(row['text'])
        out[at:at+cap] = raw+bytes(cap-len(raw)); ranges.append((at,at+cap))
        require(text(out[at:at+cap].split(b'\0')[0]) == row['text'], 'Demo name readback')
    for bank in banks:
        at=bank['offset']; end=at+bank['bytes']; old=data[at:end]; meta=tim2(old); idx=meta['indices'].copy()
        for row in cfg['titles']:
            if row['bank'] != bank['bank']: continue
            y=row['scene']*40; patch,metrics=render_title(row['text'],meta['palette']);idx[y:y+40,:]=patch
            changes.append(dict(row,indices_sha256=sha(patch.tobytes()),**metrics))
        updated=replace_indices(old,idx);out[at:end]=updated
        # Header and palette are protected by replace_indices as well as audit.
        ranges.append((at+meta['start'],at+meta['start']+meta['image_size']))
        rgba=meta['palette'][idx].copy();rgba[:,:,3]=np.minimum(rgba[:,:,3].astype(int)*2,255)
        images.append(Image.fromarray(rgba))
    cursor=0
    for lo,hi in sorted(ranges):require(out[cursor:lo]==data[cursor:lo], 'Demo nontext data changed');cursor=hi
    require(out[cursor:]==data[cursor:] and len(out)==len(data), 'Demo size/tail changed')
    report=dict(source_sha256=SOURCE_SHA,output_sha256=sha(out),source_bytes=len(data),output_bytes=len(out),
        banks=banks,names=cfg['names'],titles=changes,translated_names=len(names),translated_titles=len(changes),
        scene_count=20,write_ranges=sorted(ranges),font_sha256=file_sha(SYSTEM_FONT),input_sha256=file_sha(INPUT),
        review_sha256=file_sha(REVIEW),
        current_reuse_inputs=fresh['reuse_inputs'],reviewed_reuse_inputs=cfg['reuse_inputs'],
        reviewed_content_matches_current_dependencies=True,
        commands_and_voice_selection_unchanged=True,segment_table_unchanged=True,palettes_unchanged=True,
        runtime='Pending by user choice')
    return bytes(out),report,images


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepare',action='store_true');p.add_argument('--write',action='store_true');args=p.parse_args()
    if args.prepare:
        report=prepare();print(json.dumps(dict(names=report['names'],titles=report['titles'],screenshot=report['screenshot']),indent=2))
        if args.write:INPUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    else:
        output,report,images=build();print(json.dumps(report,indent=2))
        if args.write:
            dest=ROOT/'work/ui/english';dest.mkdir(parents=True,exist_ok=True)
            for i,im in enumerate(images):im.save(dest/f'attract-demo-{i}.png')
            (ROOT/'work/ui/attract-demo-layout.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if not args.write:print('DRY RUN: no files written')


if __name__=='__main__':main()
