"""Source-bound Special Theatre suspend scenes; native prose stays in memory."""
import argparse
from collections import Counter, defaultdict
import json
import struct
from sp_disc import ROOT, Disc, SOURCE, EXE, decode, sha, require

EXE_SHA = '9c345c4a19e7abd791b00af707fe1f44086da6b1b21b8a4344a5872b307c5101'
FILE_BASE = 0xff680
TEXT_START, TEXT_END = 0x3b8be0, 0x3be6f0
SCRIPT_START, SCRIPT_END = 0x38ca90, 0x39ad10
SCENE_TABLE, SCENE_COUNT = 0x39ad10, 57
COLLISION = 0x353aac
MAIN_NATIVE = ROOT.parent/'SRW Z/_work/extracted/DATA_STAGE.BIN'
MAIN_DONOR = ROOT.parent/'SRW Z/SRW Z English Original v0.9.85.iso'
MAIN_NATIVE_SHA = 'cadf3047a803c862a5210434179372bab15c08073afbc74401628db8704cba82'
MAIN_DONOR_SHA = '8cdcd8355a1ff4cb89cbbf5f33f92b79dd6325e8f3a9832bb6b738d812574178'
OUTPUT = ROOT/'work/translation/en/suspend_candidates.json'


def native_records(exe=None):
    exe = Disc(SOURCE).read(EXE) if exe is None else exe
    require(sha(exe) == EXE_SHA, 'Suspend executable identity')
    rows = []
    p = TEXT_START
    while p < TEXT_END:
        if exe[p] == 0:
            p += 1
            continue
        end = exe.find(b'\0', p, TEXT_END)
        require(end >= 0, 'Unterminated suspend text')
        raw = exe[p:end]
        value = raw.decode('cp932')
        require(value.encode('cp932') == raw, 'Suspend encoding identity')
        speaker, sep, body = value.partition('\n')
        require(sep and speaker and body.startswith('\u300c') and body.endswith('\u300d'),
                'Suspend speaker/body boundary')
        require(all(c >= 32 or c == 10 for c in raw), 'Unexpected suspend control byte')
        rows.append(dict(id=len(rows), offset=p, address=p+FILE_BASE, raw=raw,
                         text=value, speaker=speaker, source_sha256=sha(raw), occurrences=[]))
        p = end + 1
    require(len(rows) == 296 and len({r['raw'] for r in rows}) == 296,
            'Suspend text inventory')
    require(rows[-1]['offset'] == 0x3be6c0 and rows[-1]['offset']+len(rows[-1]['raw'])+1 == 0x3be6e2,
            'Suspend final text boundary')
    by_address = {r['address']: r for r in rows}
    starts = []
    for i in range(SCENE_COUNT):
        va, index = struct.unpack_from('<2I', exe, SCENE_TABLE+i*8)
        require(index == i, 'Suspend scene table index')
        starts.append(va-FILE_BASE)
    require(starts == sorted(set(starts)) and starts[0] == SCRIPT_START,
            'Suspend scene starts')
    require(exe[SCENE_TABLE+SCENE_COUNT*8:SCENE_TABLE+(SCENE_COUNT+1)*8] == bytes(8),
            'Suspend scene table terminator')
    scenes = []
    for i, (lo, hi) in enumerate(zip(starts, starts[1:]+[SCRIPT_END])):
        require((hi-lo)%32 == 0, 'Suspend VM command alignment')
        commands = [(at, struct.unpack_from('<8I', exe, at)) for at in range(lo, hi, 32)]
        require([w[0] for _, w in commands[:3]] == [0x4b, 0x63, 0x62]
                and [w[0] for _, w in commands[-2:]] == [0x16, 0x7e],
                'Suspend scene boundary commands')
        text_ids = []
        for at, words in commands:
            require(words[0] in (6, 0x3a, 0x3b, 0x3e, 0x4b, 0x63, 0x62, 0x16, 0x7e, 0x37),
                    'Unknown suspend VM command')
            if words[0] != 6:
                continue
            require(words[4] in by_address and words[5:] == (0, 0, 0), 'Suspend text command')
            row = by_address[words[4]]
            row['occurrences'].append(dict(scene=i, scene_row=len(text_ids),
                command_offset=at, pointer_offset=at+16, command_words=list(words)))
            text_ids.append(row['id'])
        scenes.append(dict(id=i, start=lo, end=hi, text_ids=text_ids,
                           source_sha256=sha(exe[lo:hi])))
    references = {o['pointer_offset'] for r in rows for o in r['occurrences']}
    require(len(references) == 379 and all(r['occurrences'] for r in rows), 'Suspend reference inventory')
    matches = {at for at in range(0x34e000, 0x3c5180, 4)
               if struct.unpack_from('<I', exe, at)[0] in by_address}
    require(matches == references | {COLLISION}, 'Unclassified suspend address match')
    require(struct.unpack_from('<I', exe, COLLISION)[0] == rows[122]['address'],
            'Suspend numeric collision guard')
    return exe, rows, scenes


def donor_candidates(rows):
    native, _ = decode(MAIN_NATIVE.read_bytes())
    donor, _ = decode(Disc(MAIN_DONOR, True).read('DATA/STAGE.BIN'))
    require(sha(native) == MAIN_NATIVE_SHA and sha(donor) == MAIN_DONOR_SHA,
            'Suspend main-game reuse input identity')
    base = struct.unpack_from('<I', native, 24)[0]-16
    require(base == struct.unpack_from('<I', donor, 24)[0]-16, 'Main suspend base agreement')
    pointers = defaultdict(list)
    for p in range(16, len(native)-15, 4):
        words = struct.unpack_from('<8I', native, p-16)
        if words[0] == 6 and words[5:] == (0, 0, 0):
            pointers[words[4]-base].append(p)
    results = []
    for row in rows:
        matches = []
        at = native.find(row['raw']+b'\0')
        while at >= 0:
            for p in pointers.get(at, []):
                before = struct.unpack_from('<8I', native, p-16)
                after = struct.unpack_from('<8I', donor, p-16)
                require(before[:4] == after[:4] and before[5:] == after[5:],
                        'Main donor text command changed outside pointer')
                target = after[4]-base
                end = donor.find(b'\0', target)
                require(0 <= target < end < len(donor), 'Main donor text bounds')
                value = donor[target:end].decode('cp932')
                require(value.encode('cp932') == donor[target:end], 'Main donor encoding roundtrip')
                matches.append(dict(native_text_offset=at, command_offset=p-16,
                                    donor_text_offset=target, text=value))
            at = native.find(row['raw']+b'\0', at+1)
        results.append(matches)
    require(sum(bool(r) for r in results) == 289, 'Suspend reuse match inventory')
    return results


def prepare():
    exe, rows, scenes = native_records()
    donors = donor_candidates(rows)
    entries = []
    for row, candidates in zip(rows, donors):
        entry = {k:v for k,v in row.items() if k not in ('raw', 'text', 'speaker')}
        entry['donor_candidates'] = candidates
        entry['meaning_reviewed'] = False
        entries.append(entry)
    return dict(schema_version=1, status='reference candidates only; not release-approved',
        source_executable_sha256=EXE_SHA,
        text_region_sha256=sha(exe[TEXT_START:TEXT_END]),
        script_region_sha256=sha(exe[SCRIPT_START:SCRIPT_END]),
        main_native_chunk_sha256=MAIN_NATIVE_SHA, main_english_chunk_sha256=MAIN_DONOR_SHA,
        text_records=len(rows), occurrences=379, scene_count=len(scenes),
        exact_native_matches=289, unmatched_ids=[r['id'] for r in entries if not r['donor_candidates']],
        excluded_numeric_collision=dict(offset=COLLISION, word=rows[122]['address']),
        scenes=scenes, entries=entries)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = prepare()
    print(json.dumps({k:v for k,v in result.items() if k not in ('entries', 'scenes')}, indent=2))
    print(json.dumps([result['entries'][i] for i in (0, 122, 281, 295)], ensure_ascii=True, indent=2))
    if args.write:
        OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    else:
        print('DRY RUN: validated source, all VM references, and reuse candidates; no files written')


if __name__ == '__main__':
    main()
