"""Read-only Special Disc audit using the local SRW-Z readers.

Default is a dry run. --write saves hashes/counts only, never source dialogue.
This is an inspection tool, not a patcher or a Special Disc build pipeline.
"""
import argparse
import collections
import hashlib
import json
import struct
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ISO = 'c3bd8c1af4e411e5ab2ae2d4be877170b6ab1ea9b51fa62bc0b91a51ba1a2952'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def words(data):
    if len(data) % 4:
        raise ValueError('Unaligned integer table')
    return struct.unpack('<%dI' % (len(data) // 4), data)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--image', type=Path, default=ROOT/'work/source/special-disc.bin')
    ap.add_argument('--srwz-tools', type=Path, default=Path('E:/Projects/SRW-Z/tools'))
    ap.add_argument('--inventory', type=Path, default=ROOT/'work/analysis/upstream-disc-inventory.json')
    ap.add_argument('--captions', type=Path, default=Path('E:/Projects/SRW-Z/analysis/srvc_en_by_hash.json'))
    ap.add_argument('--caption-work', type=Path, default=Path('E:/Projects/SRW Z/_work/analysis/srvc_work.json'))
    ap.add_argument('--caption-english', type=Path, default=Path('E:/Projects/SRW Z/_work/analysis/srvc_en.json'))
    ap.add_argument('--report', type=Path, default=ROOT/'work/analysis/special-disc-audit.json')
    ap.add_argument('--write', action='store_true', help='Save metadata report; input image remains read-only')
    args = ap.parse_args()
    sys.path[:0] = [str(args.srwz_tools/'best_adapter'), str(args.srwz_tools)]
    from disc import Disc, file_sha
    import banlz
    import banlz_strict
    import subtitles
    from srvc_work import inner

    image = Disc(args.image)
    reference = json.loads(args.inventory.read_text(encoding='utf-8'))
    expected = {m['path']: m for m in reference['sp']['members']}
    paths = sorted(image.entries)
    preview = dict(image=str(args.image.resolve()), input_bytes=image.size,
                   member_count=len(paths), save_report=str(args.report.resolve()),
                   sample_members={p: image.entries[p] for p in paths if
                                   p in ('SLPS_259.20', 'DATA/STAGE.BIN', 'DATA/VT1.BIN')})
    print(json.dumps(preview, indent=2))
    if not args.write:
        print('DRY RUN: will hash all members, compare upstream locks, decode font/STAGE/COMPDATA, '
              'measure exact caption-hash matches, and save metadata only.')
        return
    if args.report.resolve() == args.image.resolve() or args.report.suffix.lower() != '.json':
        raise ValueError('Report must be a separate JSON file')
    print('Hashing source and members...', flush=True)
    iso_hash = file_sha(args.image)
    hashes = image.fingerprints()
    mismatches = []
    for name in sorted(set(hashes) | set(expected)):
        a, b = hashes.get(name), expected.get(name)
        if a is None or b is None or (a['lba'], a['size'], a['sha256']) != (b['extent_lba'], b['size'], b['sha256']):
            mismatches.append(name)
    if mismatches or iso_hash != EXPECTED_ISO:
        raise ValueError('Source identity mismatch: ISO=%s members=%s' % (iso_hash, mismatches))

    comparisons = {}
    for edition in ('original', 'best'):
        other = {m['path']: m for m in reference[edition]['members']}
        common = sorted(set(hashes) & set(other))
        same = [n for n in common if hashes[n]['sha256'] == other[n]['sha256']]
        comparisons[edition] = dict(common_paths=len(common), identical_files=same,
                                    changed_files=[n for n in common if n not in same],
                                    sp_only_paths=sorted(set(hashes)-set(other)))

    def decode(raw):
        total, flags, begin = banlz.parse_header(raw)
        if total is None:
            return None, 0
        output, used = banlz.decompress_record(raw)
        strict, problems = banlz_strict.verify(raw, begin, total)
        if problems or strict != output or len(output) != total or used > len(raw):
            raise ValueError('Strict codec verification failed: %s' % problems)
        return output, used

    exe = image.read('SLPS_259.20')
    vt1_entry = image.entries['DATA/VT1.BIN']
    vt1_offsets = []
    for offset in range(0x353790, len(exe)-3, 4):
        v = struct.unpack_from('<I', exe, offset)[0]
        vt1_offsets.append(v)
        if v == vt1_entry['size']:
            break
        if len(vt1_offsets) > 512:
            raise ValueError('Missing VT1 terminal offset')
    if vt1_offsets[0] != 0 or vt1_offsets[-1] != vt1_entry['size'] or sorted(set(vt1_offsets)) != vt1_offsets:
        raise ValueError('Invalid VT1 table')
    a, b = vt1_offsets[3:5]
    with args.image.open('rb') as stream:
        stream.seek(vt1_entry['lba']*2048+a)
        font, font_used = decode(stream.read(b-a))
    font_report = dict(chunk=3, table_file_offset='0x353790', chunk_count=len(vt1_offsets)-1,
                       slot_bytes=b-a, compressed_bytes=font_used, decoded_bytes=len(font),
                       decoded_sha256=digest(font), matches_upstream_main_game_font=
                       digest(font)=='e68a24df2daaf16f472e55e0ba9b2282752bb70225aedc0bbb8aeef7713662bd')
    comp, comp_used = decode(image.read('DATA/COMPDATA.BN'))
    hb = image.read('HEDBDY/HB.BIN')
    bounds = words(hb[0x5170:0x5284])
    stage = image.read('DATA/STAGE.BIN')
    if bounds[0] != 0 or bounds[-1] != len(stage) or list(bounds) != sorted(bounds):
        raise ValueError('Invalid STAGE bounds')
    stages = []
    for i, (a,b) in enumerate(zip(bounds,bounds[1:])):
        data, used = decode(stage[a:b])
        name = data[0x30:0x50].split(b'\0')[0].decode('ascii', 'replace') if data is not None else None
        stages.append(dict(index=i, start=a, slot=b-a, consumed=used,
                           decoded_bytes=len(data) if data is not None else 0, name=name))

    print('Measuring caption reuse...', flush=True)
    captions = json.loads(args.captions.read_text(encoding='utf-8'))['lines']
    srvc = image.read('BTL/SRVC.BIN')
    offsets = words(image.read('BTL/SRVC.SEG'))
    if offsets[0] != 0 or offsets[-1] != len(srvc) or list(offsets) != sorted(offsets):
        raise ValueError('Invalid SRVC bounds')
    counts = collections.Counter()
    raw_text_hashes = set()
    headers = collections.Counter()
    for a,b in zip(offsets,offsets[1:]):
        raw = srvc[a:b]
        headers[raw[:2].hex()] += 1
        if raw[:2] != b'\x01O':
            raise ValueError('Unknown Special Disc SRVC header')
        # Adapt only a temporary read buffer. The SP source never changes.
        index, rows, end = subtitles.native_layout(b'\0'+raw[1:])
        for metadata, txt in rows:
            raw_text_hashes.add(digest(txt[:-1]))
            normalized = inner(txt[:-1].decode('cp932')).encode('cp932')
            key = hashlib.sha1(normalized).hexdigest()[:16]
            counts[key] += 1
    matches = set(counts) & {k for k,v in captions.items() if v}
    work = json.loads(args.caption_work.read_text(encoding='utf-8'))
    english = json.loads(args.caption_english.read_text(encoding='utf-8'))
    regenerated = {hashlib.sha1(r['jp'].encode('cp932', 'ignore')).hexdigest()[:16]:english[str(r['i'])]
                   for r in work if english.get(str(r['i']))}
    changed = {k for k in set(captions) & set(regenerated) if captions[k] != regenerated[k]}
    caption_report = dict(blocks=len(offsets)-1, header_counts=dict(headers),
                          records=sum(counts.values()), raw_unique_texts=len(raw_text_hashes),
                          normalized_unique_texts=len(counts),
                          exact_export_matches=len(matches),
                          matching_records=sum(counts[k] for k in matches),
                          missing_unique_texts=len(set(counts)-matches),
                          missing_records=sum(counts[k] for k in set(counts)-matches),
                          missing_source_hashes=sorted(set(counts)-matches),
                          export=str(args.captions.resolve()), export_sha256=file_sha(args.captions),
                          export_drift=dict(changed_values=len(changed),
                                            changed_values_present_in_sp=len(changed & set(counts)),
                                            added_keys=len(set(regenerated)-set(captions)),
                                            removed_keys=len(set(captions)-set(regenerated))),
                          regeneration_sources={str(p.resolve()):file_sha(p) for p in
                                                (args.caption_work, args.caption_english)},
                          note='Matches use the original export normalization: remove quote wrapper and fullwidth padding around literal backslash-n. These are reuse candidates; context, runtime fit and ambiguous translations are not verified.')
    report = dict(schema_version=1, status='source_audit_only_no_build',
                  upstream_repository=reference['repository'], upstream_commit=reference['commit'],
                  image=dict(path=str(args.image.resolve()), bytes=image.size, sha256=iso_hash),
                  system_cnf=image.read('SYSTEM.CNF').decode('ascii'),
                  members=hashes, upstream_member_mismatches=mismatches,
                  comparisons_to_upstream_native_inventories=comparisons,
                  font=font_report, compdata=dict(decoded_bytes=len(comp), compressed_consumed=comp_used),
                  stage=dict(chunks=len(stages), strict_decode_passed=True, records=stages),
                  captions=caption_report,
                  reader_sources={str(p.resolve()):file_sha(p) for p in
                                  [args.srwz_tools/'banlz.py', args.srwz_tools/'banlz_strict.py',
                                   args.srwz_tools/'srvc.py',args.srwz_tools/'srvc_work.py',
                                   args.srwz_tools/'best_adapter/disc.py',args.srwz_tools/'best_adapter/subtitles.py']})
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=True)+'\n', encoding='utf-8')
    print(json.dumps(dict(source_sha256=iso_hash, members_verified=len(hashes), font=font_report,
                         stage_chunks=len(stages), captions={k:v for k,v in caption_report.items()
                         if k != 'missing_source_hashes'}), indent=2))


if __name__ == '__main__':
    main()
