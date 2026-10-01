"""Build a story-dialogue test ISO on top of an existing English build.

Base: the latest verified non-story English ISO (default: newest
work/output/*.iso with a JSON receipt). The following components change:

* The existing English story converter is enabled and relocated for native layout.
* DATA/STAGE.BIN is rebuilt from the base's chunks: story chunks that
  compile_story.py installs are recompressed, every other chunk keeps its
  exact compressed bytes. Chunks are re-laid end to end (16-byte aligned).
* HEDBDY/HB.BIN's 69-word chunk table at 0x5170 gets the new boundaries
  (the executable holds no copy of this table).
* If STAGE.BIN outgrows its extent it moves to empty reserved space after
  every existing placement in DMY/DMY.BIN; its ISO9660 extent and VMAP.DAT
  entry are rewritten (the game reads VMAP.DAT, not the ISO directory).

Checks: every other byte equals the base ISO; STAGE/HB read back through
both the ISO directory and the runtime VMAP; every chunk decodes, installed
chunks match their compiled bytes, untouched chunks match the base.

  python -B tools/build_story.py --version 0.3.0              dry run
  python -B tools/build_story.py --version 0.3.0 --write      ISO + receipt
  python -B tools/build_story.py --version 0.3.0 --write --patch   also xdelta vs clean BIN
"""
import argparse
import json
import shutil
import struct
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sp_disc import ROOT, SOURCE, EXE, Disc, decode, require, sha, banlz, file_sha
from story_runtime import apply as apply_story_runtime
import compile_story

OUT = ROOT/'work/output'
STAGE, HB = 'DATA/STAGE.BIN', 'HEDBDY/HB.BIN'
TABLE, CHUNKS = 0x5170, 68
XDELTA = ROOT.parent/'SRW Z'/'xdelta3.exe'


def latest_base():
    isos = sorted((p for p in OUT.glob('SRW Z Special Disc English v*.iso') if p.with_suffix('.json').exists()),
                  key=lambda p: tuple(int(x) for x in p.stem.split(' v')[-1].split('.')[:3]))
    return isos[-1]


def repack(stage, hb, decoded):
    offs = struct.unpack_from('<%dI' % (CHUNKS+1), hb, TABLE)
    require(offs[0] == 0 and offs[-1] == len(stage), 'Base STAGE table')
    out, new_offs, sizes = bytearray(), [], {}
    for i in range(CHUNKS):
        lo, hi = offs[i], offs[i+1]
        new_offs.append(len(out))
        if i in decoded:
            flags = banlz.parse_header(stage[lo:hi])[1]
            packed = banlz.compress_record(decoded[i], flags=flags)
            require(decode(packed)[0] == decoded[i], 'Story compression readback %d' % i)
            out += packed
            sizes[i] = (hi-lo, len(packed))
        else:
            out += stage[lo:hi]                 # exact base bytes, padding included
        out += bytes((-len(out)) % 16)
    new_offs.append(len(out))
    new_hb = bytearray(hb)
    struct.pack_into('<%dI' % (CHUNKS+1), new_hb, TABLE, *new_offs)
    return bytes(out), bytes(new_hb), sizes


def reserved_cursor(base_disc, receipt):
    """First sector after every member already placed inside DMY.BIN's extent."""
    dummy = base_disc.entries['DMY/DMY.BIN']
    lo, hi = dummy['lba'], dummy['lba']+(dummy['size']+2047)//2048
    end = lo+8192                               # same reserve as build_nonstory.plan
    for name, e in base_disc.entries.items():
        if name != 'DMY/DMY.BIN' and lo <= e['lba'] < hi:
            end = max(end, e['lba']+(e['size']+2047)//2048)
    for p in receipt.get('placements', {}).values():
        if lo <= p['lba'] < hi:
            end = max(end, p['lba']+(p['size']+2047)//2048)
    return end, hi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--version', required=True)
    ap.add_argument('--base', help='base ISO (default: newest verified build)')
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--patch', action='store_true')
    args = ap.parse_args()
    base = Path(args.base) if args.base else latest_base()
    receipt = json.loads(base.with_suffix('.json').read_text(encoding='utf-8'))
    target = OUT/('SRW Z Special Disc English v%s.iso' % args.version)
    require(not target.exists(), 'Refusing to overwrite '+target.name)
    disc, runtime = Disc(base), Disc(base, True)
    stage, hb = runtime.read(STAGE), runtime.read(HB)
    exe = runtime.read(EXE)
    require(exe == disc.read(EXE), 'Base executable ISO/runtime mapping disagree')
    new_exe, story_runtime = apply_story_runtime(exe)
    require(stage == disc.read(STAGE) and hb == disc.read(HB), 'Base ISO/runtime mapping disagree')
    decoded, reports = compile_story.compile_stage(stage)
    new_stage, new_hb, sizes = repack(stage, hb, decoded)
    installed = sorted(decoded)
    skipped = [r for r in reports if r['status'] != 'ok']
    entry = disc.entries[STAGE]
    old_sectors = (entry['size']+2047)//2048
    moves = len(new_stage) > old_sectors*2048
    print(json.dumps(dict(base=base.name, target=target.name, installed_chunks=len(installed),
                          skipped=[(r['chunk'], r['need'], r['capacity']) for r in skipped],
                          stage_bytes=[len(stage), len(new_stage)], relocate=moves,
                          story_runtime_words=len(story_runtime['patches'])), indent=1))
    if not args.write:
        print('DRY RUN: no files written')
        return
    writes = [(disc.entries[EXE]['lba']*2048+r['offset'], struct.pack('<I', r['after']))
              for r in story_runtime['patches']]
    if moves:
        cursor, limit = reserved_cursor(disc, receipt)
        at = cursor*2048
        stored = new_stage+bytes((-len(new_stage)) % 2048)
        require(cursor+len(stored)//2048 <= limit, 'Reserved area exhausted')
        with base.open('rb') as f:
            f.seek(at)
            require(not any(f.read(len(stored))), 'Relocation area not empty')
        rec = entry['directory_record']
        writes += [(rec+2, struct.pack('<I', cursor)+struct.pack('>I', cursor)),
                   (rec+10, struct.pack('<I', len(new_stage))+struct.pack('>I', len(new_stage)))]
        vm = disc.entries['VMAP.DAT']['lba']*2048+disc.runtime[STAGE]['vmap_offset']+40
        writes.append((vm, struct.pack('<II', cursor, len(stored)//2048)))
        writes.append((at, stored))
    else:
        rec = entry['directory_record']
        writes.append((entry['lba']*2048, new_stage+bytes(old_sectors*2048-len(new_stage))))
        writes.append((rec+10, struct.pack('<I', len(new_stage))+struct.pack('>I', len(new_stage))))
    writes.append((disc.entries[HB]['lba']*2048, new_hb))
    print('copying base ISO...', flush=True)
    shutil.copyfile(base, target)
    with target.open('r+b') as f:
        for at, data in writes:
            f.seek(at)
            f.write(data)
    # verification
    t, tr = Disc(target), Disc(target, True)
    require(t.read(STAGE) == new_stage == tr.read(STAGE), 'STAGE readback (ISO/VMAP)')
    require(t.read(HB) == new_hb == tr.read(HB), 'HB readback')
    require(t.read(EXE) == new_exe == tr.read(EXE), 'Story runtime readback')
    offs = struct.unpack_from('<%dI' % (CHUNKS+1), new_hb, TABLE)
    boffs = struct.unpack_from('<%dI' % (CHUNKS+1), hb, TABLE)
    for i in range(CHUNKS):
        got = decode(new_stage[offs[i]:offs[i+1]])[0]
        want = decoded[i] if i in decoded else decode(stage[boffs[i]:boffs[i+1]])[0]
        require(got == want, 'chunk %d readback' % i)
    ranges = sorted((at, at+len(d)) for at, d in writes)
    with base.open('rb') as a, target.open('rb') as b:
        cursor = 0
        for lo, hi in ranges+[(t.size, t.size)]:
            a.seek(cursor)
            b.seek(cursor)
            left = lo-cursor
            while left > 0:
                n = min(left, 8 << 20)
                require(a.read(n) == b.read(n), 'bytes outside planned writes differ near 0x%x' % cursor)
                left -= n
            cursor = max(cursor, hi)
    iso_sha = file_sha(target)
    out = dict(version=args.version, base=base.name, base_receipt=base.with_suffix('.json').name,
               iso=target.name, iso_sha256=iso_sha, story_runtime=story_runtime, stage=dict(sha256=sha(new_stage), bytes=len(new_stage),
               relocated=moves, lba=t.entries[STAGE]['lba']), hb_sha256=sha(new_hb),
               installed_chunks=installed, skipped_chunks=skipped, chunk_reports=reports,
               compressed_sizes={str(k): v for k, v in sizes.items()})
    if args.patch:
        patch = target.with_suffix('.xdelta')
        subprocess.run([str(XDELTA), '-e', '-9', '-f', '-s', str(SOURCE), str(target), str(patch)], check=True)
        check = OUT/'_xdelta_check.iso'
        subprocess.run([str(XDELTA), '-d', '-f', '-s', str(SOURCE), str(patch), str(check)], check=True)
        require(file_sha(check) == iso_sha, 'xdelta reconstruction mismatch')
        check.unlink()
        out['xdelta'] = dict(name=patch.name, bytes=patch.stat().st_size, sha256=file_sha(patch))
    target.with_suffix('.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
    print('built', target.name, iso_sha)


if __name__ == '__main__':
    main()
