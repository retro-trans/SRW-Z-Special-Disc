"""Relocate approved indexed SRVC captions and expand their display buffers."""
import argparse
import json
import struct
from collections import defaultdict
from sp_disc import ROOT, require, sha, Disc, SOURCE, EXE
from battle_format import native, indexed, blocks, BIN, SEG, BIN_SHA, SEG_SHA, unique_sources
from battle_relocation import relocate
from battle_text import LINE_LIMIT, ROWS
from library_text import text, CHARS
from menu_encoding import menu_encode
from review_battle_release_0_2_14 import prepare, OUT as INPUT
from inspect_battle_runtime import inspect
from inspect_english_runtime import CAVE, CAVE_FILE
import battle_buffer


def build(exe, pool):
    cfg = json.loads(INPUT.read_text(encoding='utf-8'))
    require(cfg == prepare(), 'Refresh reviewed caption release before building')
    contract = inspect()
    data, seg, offsets, chunks, parsed = native(); source = unique_sources()
    # The donor's ASCII mapper includes the native wave dash even though the
    # custom Latin atlas has only 69 glyphs. Preserve this vocal inflection.
    donor=(ROOT/'work/cache/english-runtime/english.elf').read_bytes()
    tilde_at=CAVE_FILE+0x78a1bc-CAVE+(ord('~')-32)*2
    require(donor[tilde_at:tilde_at+2]==b'\x81\x60','Tilde native glyph mapping drift')
    changes = defaultdict(dict); entries = []; max_converted = 0
    for row in cfg['entries']:
        require(row['source_sha256'] == source[row['id']]['source_sha256']
                and row['occurrences'] == source[row['id']]['occurrences'], 'Caption source binding drift')
        if not row['layout_approved']: continue
        require(row['meaning_reviewed'], 'Caption meaning gate')
        value = '\\n'.join(row['lines']); encoded = menu_encode(value)
        require(not(set(''.join(row['lines']))-set(map(chr,CHARS))-{' ','~'}),'Unreviewed caption glyph')
        require(text(encoded) == value and b'\0' not in encoded, 'Caption encoding readback')
        require(0 < len(row['lines']) <= ROWS and max(row['line_widths']) <= LINE_LIMIT, 'Caption layout gate')
        max_converted = max(max_converted, len(encoded.replace(b'\\n', b'\n'))+1)
        for occurrence in row['occurrences']:
            block = occurrence['block']; record = occurrence['record']; original = parsed[block]['rows'][record]
            require(sha(original['raw']) == occurrence['raw_sha256'] and original['metadata'] == occurrence['metadata'], 'Caption voice/text identity')
            require(record not in changes[block], 'Duplicate caption replacement')
            changes[block][record] = encoded
        entries.append(dict(id=row['id'], text=value, lines=row['lines'], line_widths=row['line_widths'],
                            encoded_sha256=sha(encoded), occurrences=row['occurrences']))
    require(entries and len(entries) == cfg['translated_captions'], 'Caption release inventory')
    # Both managers also display the untranslated records. Include every native
    # string when deriving capacity; the terminator is part of the requirement.
    native_max = max(len(r['raw'].replace(b'\\n', b'\n'))+1 for p in parsed for r in p['rows'])
    capacity = (max(96, native_max, max_converted)+15)//16*16
    if capacity > 96:
        exe, pool, buffers = battle_buffer.build(exe, pool, capacity)
        buffers['enabled'] = True
    else:
        # Avoid a runtime patch when the complete, approved text already fits.
        # Future releases derive a larger capacity from actual encoded text.
        buffers = dict(enabled=False, capacity=96, original_capacity=96,
            original_buffers=list(battle_buffer.ORIGINAL_BUFFERS), buffers=[], helpers={}, patches=[],
            reason='All native and approved English captions fit, including NUL')
    out_chunks = []; out_offsets = [0]
    for block, raw in enumerate(chunks):
        out = relocate(raw, changes.get(block, {})); out_chunks.append(out); out_offsets.append(out_offsets[-1]+len(out))
    out_data = b''.join(out_chunks); out_seg = struct.pack('<%dI' % len(out_offsets), *out_offsets)
    got, got_chunks = blocks(out_data, out_seg)
    require(got == tuple(out_offsets) and got_chunks == out_chunks, 'Caption container readback')
    report = dict(source_bin_sha256=BIN_SHA, source_seg_sha256=SEG_SHA, output_bin_sha256=sha(out_data),
        output_seg_sha256=sha(out_seg), source_bytes=len(data), output_bytes=len(out_data),
        blocks=len(chunks), indexed_records=59262, translated_captions=len(entries),
        translated_records=sum(len(v) for v in changes.values()), changed_blocks=len(changes), entries=entries,
        deferred_ids=cfg['deferred_ids'], buffer=buffers, native_maximum_converted_bytes=native_max,
        english_maximum_converted_bytes=max_converted, original_blocks_preserved_except_selected_offset_words=True,
        opaque_tails_preserved=True, voice_metadata_preserved=True, line_limit=LINE_LIMIT, row_limit=ROWS,
        unbound_tail_texts=contract['stats']['distinct_unbound_tail_texts'],
        release_sha256=sha(INPUT.read_bytes()), runtime='pending by user choice')
    report['native_punctuation']={'~':dict(ascii='7e',mapped_cp932='8160',conservative_advance=24)}
    from battle_placeholder import verify as verify_placeholder
    require(not any(r['id']==444 for r in entries),'Hidden production caption was translated')
    report['runtime_dispositions']=[verify_placeholder(exe)]
    return exe, pool, {BIN: out_data, SEG: out_seg}, report


def main():
    p = argparse.ArgumentParser(description=__doc__); p.parse_args()
    _, _, _, report = build(Disc(SOURCE).read(EXE), b'')
    print(json.dumps({k: v for k, v in report.items() if k != 'entries'}, indent=2))
    print('DRY RUN: no files written; final pool addresses depend on the full build')


if __name__ == '__main__': main()
