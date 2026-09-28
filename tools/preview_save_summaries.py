"""Preview five approved recaps with donor glyphs; not an emulator capture."""
import argparse
import io
import json
import struct

from PIL import Image, ImageDraw, ImageFont
from inspect_english_runtime import CAVE, CAVE_FILE
from library_text import CHARS
from save_summary_text import LINE_LIMIT, ROWS, WIDTHS, width, wrap
from sp_disc import ROOT, Disc, SOURCE, EXE, decode, require, sha

VERSION = '0.2.9'
IDS = [2, 13, 17, 44, 53]
INPUT = ROOT / 'work/translation/en' / f'save_summaries_release_{VERSION}.json'
OUTPUT = ROOT / 'work/ui/english' / f'save-summary-layout-{VERSION}.png'
REPORT = ROOT / 'work/ui' / f'save-summary-layout-{VERSION}.json'
ATLAS_SHA = '894b111ca2fca7ff43e871cab8426f2ae4b89d12c77029323521606c66e2115a'
WIDTHS_SHA = '8d966500280819b5efd43834735b6f70b10d9591790c0c22f79b697f948fc06a'
# Only these disclosed symbols may use a preview substitute, never silently.
SUBSTITUTES = {';': [13, 53], '+': [44]}
GUARDS = {0x43cbc0: 0x24040010, 0x43cbc8: 0x24050008,
          0x43cbf8: 0x24040010, 0x43cbfc: 0x24050008,
          0x43cc1c: 0x2405ff14, 0x43cc20: 0x24060040,
          0x43cc40: 0x2405ff14, 0x43cc44: 0x2406004a,
          0x43cc64: 0x2405ff14, 0x43cc68: 0x24060054}


def prepare():
    input_bytes = INPUT.read_bytes()
    cfg = json.loads(input_bytes)
    require(cfg['followup_approved_ids'] == IDS, 'Approved recap set changed')
    require(cfg['layout']['line_limit_font_units'] == LINE_LIMIT == 520
            and cfg['layout']['row_limit'] == ROWS == 3, 'Recap bounds drift')
    disc = Disc(SOURCE)
    exe = disc.read(EXE)
    raw, _ = decode(disc.read('DATA/HSFC.BIN'))
    require(sha(raw) == cfg['source_sha256'], 'Native HSFC source changed')
    for va, expected in GUARDS.items():
        require(struct.unpack_from('<I', exe, va - 0xff680)[0] == expected,
                'Native recap display setup changed at ' + hex(va))
    donor = (ROOT / 'work/cache/english-runtime/english.elf').read_bytes()
    offset = CAVE_FILE + 0x78a5b0 - CAVE
    atlas = donor[offset:offset + 69 * 72]
    require(sha(atlas) == ATLAS_SHA and sha(WIDTHS) == WIDTHS_SHA,
            'Donor glyph atlas or width table changed')
    glyphs = {}
    for index, code in enumerate(CHARS):
        glyph = Image.new('RGBA', (12, 24))
        data = atlas[index * 72:(index + 1) * 72]
        for y in range(24):
            for x in range(12):
                value = data[y * 3 + x // 4] >> (6 - 2 * (x % 4)) & 3
                if value:
                    glyph.putpixel((x, y), (240, 238, 219, value * 85))
        glyphs[chr(code)] = glyph
    label = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 14)
    symbol_font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 22)
    image = Image.new('RGBA', (680, 870), '#111923')
    draw = ImageDraw.Draw(image)
    draw.text((20, 12), 'SAVE RECAPS 0.2.9 - RECONSTRUCTED LAYOUT; EMULATOR PENDING',
              font=label, fill='#91e0d3')
    draw.text((20, 35), 'Actual Latin atlas; orange ; and + are disclosed preview substitutes.',
              font=label, fill='#ffca89')
    draw.text((20, 56), '520-unit line bound. Native vertical spacing expanded for inspection.',
              font=label, fill='#a9bdcd')
    entries, fallback = [], []
    for panel, record_id in enumerate(IDS):
        row = next(r for r in cfg['entries'] if r['id'] == record_id)
        source_offset = 0xe6 + record_id * 198
        require(row['offset'] == source_offset and row['source_sha256'] ==
                sha(raw[source_offset:source_offset + 198]), 'Native recap binding drift')
        require(row['meaning_reviewed'] and row['layout_approved'], 'Unapproved recap')
        lines, widths = wrap(row['text'])
        require(lines == row['lines'] and widths == row['line_widths'], 'Layout drift')
        require(' '.join(lines) == row['text'], 'Preview would change recap prose')
        top = 92 + panel * 154
        x0, y0 = 104, top + 37
        draw.text((20, top), f'RECAP {record_id} | widths {widths} / 520 | 3 rows',
                  font=label, fill='#91e0d3')
        draw.rectangle((20, top + 24, 659, top + 127), outline='#67727f')
        draw.rectangle((x0 - 1, y0 - 2, x0 + LINE_LIMIT, y0 + 81), outline='#455260')
        line_metadata = []
        for line_index, line in enumerate(lines):
            x, y = x0, y0 + line_index * 28
            for char_index, char in enumerate(line):
                if char in glyphs:
                    image.alpha_composite(glyphs[char], (x, y))
                elif char != ' ':
                    require(record_id in SUBSTITUTES.get(char, []),
                            'Undisclosed preview glyph: ' + repr(char))
                    require(width(char) == 24, 'Substitute width changed')
                    draw.text((x, y), char, font=symbol_font, fill='#ffca89')
                    fallback.append(dict(id=record_id, line=line_index,
                                         character_index=char_index, character=char,
                                         preview_xy=[x, y], advance=24))
                x += width(char)
            require(x - x0 == widths[line_index] <= LINE_LIMIT, 'Preview overflow')
            line_metadata.append(dict(text=line, width=widths[line_index],
                                      preview_xy=[x0, y], preview_end_x=x,
                                      native_centered_xy=[-236, 64 + line_index * 10]))
        entries.append(dict(id=record_id, source_offset=source_offset,
                            source_sha256=row['source_sha256'], lines=line_metadata,
                            preview_text_bounds_xywh=[x0, y0, LINE_LIMIT, 80]))
    require([(r['id'], r['character']) for r in fallback] ==
            [(13, ';'), (44, '+'), (53, ';')], 'Disclosed substitute inventory changed')
    metadata = dict(version=VERSION, kind='Reconstructed static layout, not an in-game screenshot',
        input=str(INPUT.relative_to(ROOT)).replace('\\', '/'), input_sha256=sha(input_bytes),
        native_hsfc_chunk_sha256=sha(raw), source_executable_sha256=sha(exe),
        donor_executable_sha256=sha(donor), latin_atlas_sha256=sha(atlas),
        width_table_sha256=sha(WIDTHS), atlas_glyph_size=[12, 24],
        atlas_address='0x78a5b0', width_table_address='0x78b960',
        native_canvas_width=640, native_centered_x=-236, native_left_x=84,
        native_row_y=[64, 74, 84], native_font_setup=[16, 8],
        line_limit=LINE_LIMIT, maximum_rows=ROWS, native_right_margin=36,
        preview=str(OUTPUT.relative_to(ROOT / 'work/ui')).replace('\\', '/'),
        preview_canvas_size=list(image.size), preview_horizontal_scale=1,
        preview_row_stride_y=28, preview_vertical_policy='Unscaled 12x24 atlas glyphs; rows separated for inspection, not a simulation of native vertical geometry.',
        advance_policy='Actual donor per-glyph table plus 2; space 13; disclosed native punctuation 24.',
        guarded_native_words={hex(k): hex(v) for k, v in GUARDS.items()},
        substitute_glyphs=fallback,
        substitute_note='Only ; and + use orange Arial preview glyphs. Their game glyph shape is not certified; their conservative 24-unit advance is unchanged. Labels also use Arial.',
        entries=entries, runtime='Pending by user choice; no playback or native vertical-layout acceptance claimed.')
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    png = buffer.getvalue()
    metadata['preview_png_sha256'] = sha(png)
    return png, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    png, metadata = prepare()
    print(json.dumps(metadata, indent=2))
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(png)
        REPORT.write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
        print('WROTE', OUTPUT, REPORT)
    else:
        print('DRY RUN: no preview or metadata files written')


if __name__ == '__main__':
    main()
