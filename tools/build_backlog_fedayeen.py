"""Build v0.3.17: Back Log ASCII conversion + Fedayeen weapon names; dry run unless --write."""
import argparse, hashlib, json, shutil, struct, subprocess
from sp_disc import ROOT, SOURCE, SOURCE_SHA, EXE, Disc, require, file_sha
from backlog_fedayeen import build, COMP
from build_story import reserved_cursor


def plan(disc, members):
    """Same placement rule as build_bonus_results.plan (inlined: that module needs numpy)."""
    cursor, limit = reserved_cursor(disc, {})
    writes, placements = [], {}
    for name, payload in members.items():
        sectors = (len(payload)+2047)//2048
        require(cursor+sectors <= limit, 'Reserved disc area exhausted')
        data, offset = payload+bytes(sectors*2048-len(payload)), cursor*2048
        with disc.path.open('rb') as f:
            f.seek(offset)
            require(f.read(len(data)) == bytes(len(data)), 'Relocation area not empty')
        writes.append((offset, data))
        record = disc.entries[name]['directory_record']
        writes.append((record+2, struct.pack('<I', cursor)+struct.pack('>I', cursor)))
        writes.append((record+10, struct.pack('<I', len(payload))+struct.pack('>I', len(payload))))
        vm = disc.entries['VMAP.DAT']['lba']*2048+disc.runtime[name]['vmap_offset']+40
        writes.append((vm, struct.pack('<II', cursor, sectors)))
        placements[name] = dict(lba=cursor, size=len(payload), sectors=sectors)
        cursor += sectors
    return writes, placements

BASE_SHA = '38199a3be48e759e2b887c369609b404afe9376a6f28a91d02036bfca914f5a7'
VERSION = '0.3.17'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write', action='store_true')
    p.add_argument('--patch', action='store_true')
    args = p.parse_args()
    base = ROOT/'work/output/SRW Z Special Disc English v0.3.16.iso'
    target = ROOT/('work/output/SRW Z Special Disc English v%s.iso' % VERSION)
    disc, runtime = Disc(base), Disc(base, True)
    require(all(disc.read(n) == runtime.read(n) for n in (EXE, COMP)), 'ISO/runtime inputs disagree')
    members, report = build(disc)
    writes, placements = plan(disc, {COMP: members[COMP]})
    exe_at = disc.entries[EXE]['lba']*2048
    for r in report['backlog']['patches']:
        writes.append((exe_at+r['offset'], struct.pack('<I', r['after'])))
    writes.sort()
    require(all(a+len(b) <= c for (a, b), (c, d) in zip(writes, writes[1:])), 'Overlapping disc writes')
    print(json.dumps(dict(version=VERSION, backlog_words=len(report['backlog']['patches']),
                          fedayeen=report['fedayeen'], compdata_bytes=report['compdata_bytes'],
                          placements=placements), indent=2), flush=True)
    if not args.write:
        print('DRY RUN: no game files written')
        return
    require(not target.exists() and not target.with_suffix('.xdelta').exists(), 'Candidate already exists')
    require(file_sha(base) == BASE_SHA, 'Wrong v0.3.16 input image')
    if args.patch:
        require(file_sha(SOURCE) == SOURCE_SHA, 'Wrong clean source image')
    shutil.copyfile(base, target)
    with target.open('r+b') as f:
        for at, data in writes:
            f.seek(at)
            f.write(data)
    patched, running = Disc(target), Disc(target, True)
    for name, data in members.items():
        require(patched.read(name) == running.read(name) == data, 'Member readback '+name)
    h, at = hashlib.sha256(), 0
    with base.open('rb') as a, target.open('rb') as b:
        while True:
            old = a.read(8 << 20)
            if not old:
                require(not b.read(1), 'Output size changed')
                break
            new = b.read(len(old))
            expected = bytearray(old)
            for off, data in writes:
                lo, hi = max(at, off), min(at+len(old), off+len(data))
                if lo < hi:
                    expected[lo-at:hi-at] = data[lo-off:hi-off]
            require(new == expected, 'Unexpected disc change at '+hex(at))
            h.update(new)
            at += len(old)
    result = dict(version=VERSION, base=base.name, base_sha256=BASE_SHA, iso=target.name,
                  iso_sha256=h.hexdigest(), iso_bytes=target.stat().st_size, placements=placements,
                  backlog_fedayeen=report, all_other_bytes_identical=True, emulator='pending')
    if args.patch:
        patch = target.with_suffix('.xdelta')
        check = ROOT/('work/output/verify-%s.iso' % VERSION)
        require(not check.exists(), 'Verification output exists')
        xdelta = ROOT.parent/'SRW Z/xdelta3.exe'
        print('Creating and reconstructing clean-disc patch...', flush=True)
        subprocess.run([str(xdelta), '-e', '-9', '-A', '-s', str(SOURCE), str(target), str(patch)], check=True)
        subprocess.run([str(xdelta), '-d', '-s', str(SOURCE), str(patch), str(check)], check=True)
        require(file_sha(check) == result['iso_sha256'], 'Patch reconstruction mismatch')
        check.unlink()
        result['xdelta'] = dict(name=patch.name, bytes=patch.stat().st_size, sha256=file_sha(patch), roundtrip_verified=True)
    target.with_suffix('.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'backlog_fedayeen'}, indent=2), flush=True)


if __name__ == '__main__':
    main()
