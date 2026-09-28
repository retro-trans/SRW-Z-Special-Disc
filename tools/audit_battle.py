"""Read final SRVC members and helper code independently of the writer."""
import json
import struct
from collections import defaultdict
from sp_disc import ROOT, SOURCE, Disc, require, sha
from library_text import text
from save_summary_text import width


def audit(disc, exe, loaded, report):
    clean = Disc(SOURCE); data = disc.read('BTL/SRVC.BIN'); seg = disc.read('BTL/SRVC.SEG')
    old_data = clean.read('BTL/SRVC.BIN'); old_seg = clean.read('BTL/SRVC.SEG')
    require(sha(data) == report['output_bin_sha256'] and sha(seg) == report['output_seg_sha256'], 'Final caption members')
    offsets = struct.unpack('<353I', seg); old_offsets = struct.unpack('<353I', old_seg)
    require(offsets[0] == 0 and offsets[-1] == len(data) and all(a < b and a % 16 == 0 for a, b in zip(offsets, offsets[1:])), 'Final caption segment bounds')
    expected = {}; checked = 0; native_count = 0
    for row in report['entries']:
        require(row['lines'] == row['text'].split('\\n') and len(row['lines']) <= 2
                and all(width(s) <= 460 for s in row['lines']), 'Final caption layout')
        for occurrence in row['occurrences']:
            key = (occurrence['block'], occurrence['record'])
            require(key not in expected, 'Duplicate final caption'); expected[key] = (row, occurrence)
    for block, (lo, hi, old_lo, old_hi) in enumerate(zip(offsets, offsets[1:], old_offsets, old_offsets[1:])):
        raw = data[lo:hi]; old = old_data[old_lo:old_hi]
        require(len(raw) >= len(old) and raw[:8] == old[:8], 'Caption header changed')
        count = struct.unpack_from('<H', old, 6)[0]
        index = 8 + old[1]*4 + struct.unpack_from('<H', old, 4)[0]*8 + old[2]*8 + old[3]*4
        pool = index+count*8; restored = bytearray(raw[:len(old)])
        for record in range(count):
            at = index+record*8; meta, off = struct.unpack_from('<II', raw, at)
            old_meta, old_off = struct.unpack_from('<II', old, at)
            require(meta == old_meta, 'Voice clip metadata changed')
            start = pool+off; end = raw.find(b'\0', start)
            require(pool <= start <= end < len(raw) and (start == pool or raw[start-1] == 0), 'Final caption pointer/terminator')
            value = raw[start:end]; item = expected.get((block, record))
            if item:
                row, occurrence = item; original = old[pool+old_off:old.index(0, pool+old_off)]
                require(sha(original) == occurrence['raw_sha256'] and meta == occurrence['metadata'], 'Final caption source identity')
                require(start >= len(old) and text(value) == row['text'] and sha(value) == row['encoded_sha256'], 'Final relocated caption mismatch')
                require(len(value.replace(b'\\n', b'\n'))+1 <= report['buffer']['capacity'], 'Caption buffer overflow')
                restored[at+4:at+8] = old[at+4:at+8]; checked += 1
            else:
                require(off == old_off and value == old[pool+old_off:old.index(0, pool+old_off)], 'Unapproved caption changed')
                native_count += 1
        require(restored == old, 'Caption changed original header, sequences, conditions, text or tail')
    require(checked == report['translated_records'] == len(expected) and checked+native_count == 59262, 'Final caption coverage')
    buffers = report['buffer']
    if report.get('runtime_dispositions'):
        from battle_placeholder import verify as verify_placeholder
        require(report['runtime_dispositions']==[verify_placeholder(exe)],'Final placeholder suppression evidence')
        require(not any(r['id']==444 for r in report['entries']),'Final hidden production caption changed')
    if not buffers['enabled']:
        for va, target in ((0x2f198c, 0x2f1760), (0x2f1bac, 0x2f1760), (0x2f2128, 0x2fd9a0), (0x2f21c0, 0x1a23d8)):
            require(struct.unpack_from('<I', exe, va-0xff680)[0] == 0x0c000000 | target >> 2, 'Unnecessary caption display hook')
    for address in buffers['buffers']:
        at = loaded(address); size = buffers['capacity']
        require(loaded(address+size-1) == at+size-1 and not any(exe[at:at+size]), 'Caption buffer storage/bounds')
    for kind, helper in buffers['helpers'].items():
        at = loaded(helper['address']); code = bytes.fromhex(helper['payload_hex'])
        require(loaded(helper['address']+len(code)-1) == at+len(code)-1 and exe[at:at+len(code)] == code, 'Final caption helper readback')
    for patch in buffers['patches']:
        actual = struct.unpack_from('<I', exe, patch['offset'])[0]
        require(actual >> 26 == 3 and (actual & 0x3ffffff) << 2 == buffers['helpers'][patch['helper']]['address'], 'Final caption call target')
    return dict(translated_captions=len(report['entries']), translated_records=checked, native_records=native_count,
        all_original_block_bytes_preserved_except_selected_offset_words=True, voice_metadata_preserved=True,
        buffer_capacity=buffers['capacity'], buffer_hook_enabled=buffers['enabled'], helper_code_read_back=True, runtime='pending by user choice')
