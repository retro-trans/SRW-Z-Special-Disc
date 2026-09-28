"""Read-only suspend token and copy-size audit; does not approve storage/layout."""
import argparse
import json
import struct
from sp_disc import ROOT, sha, require
from suspend_format import native_records, FILE_BASE, EXE_SHA
from menu_encoding import menu_encode
from library_text import text

SOURCE = ROOT / 'work/cache/english-runtime/special.elf'
REVIEW = ROOT / 'work/translation/en/suspend_reviewed.json'
REVIEW_SHA = '05edb8c96ec18f9e37317b0220f0eee2d81ca58916ae1ded3dcfbf8507e43818'
OUT = ROOT / 'work/analysis/suspend-substitution-audit.json'
# Fixed key literals used by native dictionary setup 0x205760. 0x4B0128
# is the native name separator and is deliberately not a substitution key.
KEY_VAS = tuple(range(0x4B0100, 0x4B0128, 8)) + tuple(range(0x4B0130, 0x4B0178, 8))
EXPECTED_KEYS = ['$n', '$f', '$l', '$c', '$u', '$F', '$A', '$B', '$C', '$D', '$G', '$H', '$I', '$J']
GUARDS = {
    0x20571C: 0x0C06948E,  # strcpy before substitution
    0x205730: 0x0C0816A8,  # jal 0x205AA0
    0x205B04: 0x0C081570,  # classifier before token matching
    0x205B28: 0x80C20000,  # dictionary key byte 0
    0x205B38: 0x80C20001,  # dictionary key byte 1
    0x205B5C: 0x24440029,  # replacement value offset
    0x205C14: 0x26520002,  # matched token consumes 2 source bytes
    0x205C1C: 0x2A22000E,  # 14 entries
    0x205C24: 0x24C60052,  # 82-byte entry stride
    0x205C50: 0x26520002,  # multibyte copy consumes 2 bytes
    0x205C78: 0xA2C00000,  # output NUL
}


def prepare():
    exe = SOURCE.read_bytes()
    require(sha(exe) == EXE_SHA, 'Native executable changed')
    require(sha(REVIEW.read_bytes()) == REVIEW_SHA, 'Reviewed suspend meanings changed')
    for va, word in GUARDS.items():
        require(struct.unpack_from('<I', exe, va-FILE_BASE)[0] == word, 'Substitution opcode changed')
    keys = []
    for va in KEY_VAS:
        at = va-FILE_BASE
        raw = exe[at:exe.index(0, at)]
        require(len(raw) == 2 and raw[0] == ord('$'), 'Unexpected substitution key')
        keys.append(raw)
    require([k.decode('ascii') for k in keys] == EXPECTED_KEYS, 'Key inventory changed')
    _, native, scenes = native_records(exe)
    reviewed = json.loads(REVIEW.read_bytes())['entries']
    require([r['id'] for r in reviewed] == list(range(296)), 'Review inventory changed')
    rows = []
    for r, n in zip(reviewed, native):
        require(r['source_sha256'] == n['source_sha256'] and r['occurrences'] == n['occurrences'],
                'Source or reference mismatch')
        require(r['meaning_reviewed'] is True, 'Unreviewed meaning')
        encoded = menu_encode(r['text'])
        require(text(encoded) == r['text'] and b'\0' not in encoded, 'Encoding readback')
        # A zero raw-dollar count is stronger than a character-boundary scan:
        # no key can match even if a classifier were to choose a different path.
        require(b'$' not in encoded, 'English could invoke native substitution')
        require(all(k not in n['raw'] for k in keys), 'Native source has a token; review it explicitly')
        speaker, sep, body = encoded.partition(b'\n')
        require(speaker and sep and body.startswith(b'\x81\x75') and body.endswith(b'\x81\x76'),
                'Speaker or native quote wrappers changed')
        rows.append(dict(id=r['id'], source_sha256=n['source_sha256'],
                         encoded_sha256=sha(encoded), native_bytes_including_nul=len(n['raw'])+1,
                         initial_copy_bytes_including_nul=len(encoded)+1,
                         post_substitution_bytes_including_nul=len(encoded)+1,
                         largest_unwrapped_line_bytes=max(map(len, encoded.split(b'\n'))),
                         raw_dollar_bytes=encoded.count(b'$'),
                         dictionary_key_matches={k.decode('ascii'): encoded.count(k) for k in keys}))
    evidence = []
    for lo, hi, finding in [
        (0x2056E0, 0x205758, 'Initial strcpy, then dictionary substitution, then strlen.'),
        (0x205760, 0x205A94, 'Dictionary setup uses fixed two-byte keys and runtime values.'),
        (0x205AA0, 0x205CAC, '14-key loop; values at +0x29, entries 0x52 bytes; two-byte pair copy and NUL termination.'),
        (0x4B0100, 0x4B0178, 'Key literal region; 0x4B0128 is a separator, not a key.')]:
        raw = exe[lo-FILE_BASE:hi-FILE_BASE]
        evidence.append(dict(va_start=hex(lo), va_end_exclusive=hex(hi), file_offset=hex(lo-FILE_BASE),
                             preimage_hex=raw.hex(), sha256=sha(raw), finding=finding))
    return dict(schema_version=1, source_executable_sha256=EXE_SHA, reviewed_sha256=REVIEW_SHA,
        input_sha256={str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in
                      (SOURCE, REVIEW, ROOT/'tools/menu_encoding.py', ROOT/'tools/library_text.py',
                       ROOT/'tools/suspend_format.py', ROOT/'tools/audit_suspend_substitution.py')},
        method='Static instruction inspection and exhaustive native/English encoded-corpus scan; no game execution.',
        dictionary_keys=EXPECTED_KEYS, key_addresses=list(map(hex, KEY_VAS)),
        records=len(rows), scenes=len(scenes), references=sum(len(r['occurrences']) for r in native),
        raw_dollar_count=sum(r['raw_dollar_bytes'] for r in rows),
        maximum_initial_and_final_bytes_including_nul=max(r['initial_copy_bytes_including_nul'] for r in rows),
        maximum_ids=[r['id'] for r in rows if r['initial_copy_bytes_including_nul'] ==
                     max(x['initial_copy_bytes_including_nul'] for x in rows)],
        dictionary_expansion_for_current_corpus=False,
        conclusion='None of the 296 encoded drafts contains a dollar byte, so none can match any of the 14 keys from native setup. Runtime replacement-value length is irrelevant for this corpus under that dictionary.',
        limits=[
            'This establishes the native setup dictionary, not exclusion of every possible later memory mutation.',
            'A future edit adding a dollar byte or changing encoding must fail this guard and receive a new audit.',
            'The 174-byte peak is a copy-size requirement, not proof of owned message-buffer capacity.',
            'No wrapping, visible panel capacity, relocation, emulator or runtime acceptance is approved here.'
        ], evidence=evidence, entries=rows, runtime='pending by user choice')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = prepare()
    print(json.dumps({k: result[k] for k in ('records', 'scenes', 'references', 'dictionary_keys',
                     'raw_dollar_count', 'maximum_initial_and_final_bytes_including_nul', 'maximum_ids',
                     'dictionary_expansion_for_current_corpus', 'limits')}, indent=2))
    print(json.dumps([r for r in result['entries'] if r['id'] in (0, 85, 295)], indent=2))
    if args.write:
        require(not OUT.exists(), 'Refusing to overwrite an existing audit')
        OUT.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
        require(json.loads(OUT.read_bytes()) == result, 'Audit readback')
    else:
        print('DRY RUN: no files written')


if __name__ == '__main__':
    main()
