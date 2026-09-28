"""Reconstruct caption layout with the actual Latin atlas; not emulator capture."""
import argparse
import json
import struct
from PIL import Image, ImageDraw, ImageFont
from sp_disc import ROOT, Disc, SOURCE, EXE, require
from library_text import CHARS
from inspect_english_runtime import CAVE, CAVE_FILE
from battle_text import width, LINE_LIMIT
from review_battle_release_0_2_14 import OUT as INPUT

VERSION='0.2.14'


def prepare():
    rows = json.loads(INPUT.read_text(encoding='utf-8'))['entries']
    exe = Disc(SOURCE).read(EXE); base = 0xff680
    guards = {0x303354: 0x240500a0, 0x30335c: 0x240701e0, 0x303360: 0x24080050,
              0x303368: 0x240a0001, 0x303374: 0x080bf64c, 0x303378: 0x24840740,
              0x13a3b4: 0x24060016, 0x13a3bc: 0x2405000b}
    for va, word in guards.items(): require(struct.unpack_from('<I', exe, va-base)[0] == word, 'Caption layout setup drift')
    y = [struct.unpack_from('<H', exe, 0x487848-base+i*32)[0] for i in range(3)]
    require(y == [184,184,72], 'Caption origin drift')
    donor = (ROOT/'work/cache/english-runtime/english.elf').read_bytes()
    atlas = donor[CAVE_FILE+0x78a5b0-CAVE:CAVE_FILE+0x78a5b0-CAVE+69*72]
    label = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 14)
    fallback = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 22)
    chosen = sorted((r for r in rows if r['layout_approved']), key=lambda r: max(r['line_widths']), reverse=True)[:5]
    chosen += [next(r for r in rows if r['id'] == special) for special in (754,768,855,906,931,935,948,22375)]
    im = Image.new('RGBA', (680, len(chosen)*138), '#111923'); draw = ImageDraw.Draw(im)
    for n, row in enumerate(chosen):
        top = n*138
        draw.text((20,top+7), f"CAPTION {row['id']} - RECONSTRUCTED LAYOUT; EMULATOR PENDING", font=label, fill='#91e0d3')
        draw.rectangle((20,top+30,659,top+118), outline='#67727f')
        draw.rectangle((180,top+57,180+LINE_LIMIT,top+112), outline='#424d59')
        draw.text((180,top+35), 'Speaker row', font=label, fill='#a9bdcd')
        for j, line in enumerate(row['lines']):
            x = 180; py = top+62+j*24
            for char in line:
                if ord(char) in CHARS:
                    index = CHARS.index(ord(char)); raw = atlas[index*72:(index+1)*72]
                    glyph = Image.new('RGBA', (12,24))
                    for gy in range(24):
                        for gx in range(12):
                            v = raw[gy*3+gx//4] >> (6-2*(gx%4)) & 3
                            if v: glyph.putpixel((gx,gy), (240,238,219,v*85))
                    im.alpha_composite(glyph, (x,py))
                elif char != ' ': draw.text((x,py),char,font=fallback,fill='#f0eedb')
                x += width(char)
    metadata = dict(kind='Reconstructed static layout, not an in-game screenshot', canvas_units=[640,224],
        x=160, native_width=480, conservative_width=460, maximum_caption_rows=2,
        speaker_y=y, default_native_glyph_size=[22,11], row_stride_y=12,
        caption_y=[196,208], split_view_caption_y=[84,96],
        guarded_words={hex(a):hex(b) for a,b in guards.items()},
        preview=f'english/battle-caption-layout-{VERSION}.png', preview_ids=[r['id'] for r in chosen],
        punctuation_note='Latin atlas is exact. Tilde uses a substitute preview glyph; game maps ASCII 7E to native CP932 8160. Conservative 24-unit width exceeds its 13-unit ASCII advance.',
        entries=[dict(id=r['id'], lines=r['lines'], line_widths=r['line_widths']) for r in rows if r['layout_approved']],
        runtime='Pending by user choice; no claim of playback or timing acceptance')
    return im, metadata


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args()
    im, metadata = prepare()
    print(json.dumps({k:v for k,v in metadata.items() if k != 'entries'}, indent=2))
    print(json.dumps([r for r in metadata['entries'] if r['id'] in metadata['preview_ids']],indent=2))
    if args.write:
        im.save(ROOT/'work/ui'/metadata['preview'])
        (ROOT/'work/ui'/f'battle-caption-layout-{VERSION}.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    else: print('DRY RUN: no files written')


if __name__ == '__main__': main()
