"""Back Log fix: convert ASCII before the Back Log's native row renderer.

Root cause (SRW Z main game, live PINE session 2026-08-19; same engine): the
Back Log draws RAW story strings, never passed through MessageWindow setText.
Its blit treats bytes 0x2E-0x3D as control codes before any ASCII handling,
so '.' (0x2E) acts as a newline and digits/':'/';' corrupt rows: every
English row broke at its first period and overprinted the next row.

The main game's fix (SRW-Z tools/patch_backlog.py) hooks the two row-buffer
copies with a converting copy (ASCII 0x20-0x7E -> the installed two-byte
glyph codes; Shift-JIS and control bytes pass through; NUL-terminated at the
converted length) and NOPs the caller's source-length NUL writes. Special
Disc already carries that routine and the path-A sprite-width stub in the
ported English runtime, and the width stub is hooked at 0x13B8FC. This patch:

* relocates the routine's glyph-table pointer from the donor's 0x78A1BC to
  the Special Disc table at 0x81CABC (two words);
* hooks the Back Log row copies at 0x2263C4/0x2263D8 (native target
  0x1A5640, signature-matched to the main game's 0x1A1190);
* NOPs the two source-length terminators at 0x2263F0/0x2263F4.

Six instruction words change. Every pre-image is checked; applying twice is a
no-op. Already-converted text passes through unchanged.
"""
import struct
from sp_disc import ROOT, require, sha
from inspect_english_runtime import B_BASE, CAVE, CAVE_FILE, u32
from port_menu_runtime import NEW_CAVE, NEW_FILE

DONOR_CONV = 0x78BAF0
CONV = NEW_CAVE+(DONOR_CONV-CAVE)                 # 0x81E3F0
TABLE = NEW_CAVE+0x14c                            # 0x81CABC, 95 two-byte codes
DONOR_TABLE = CAVE+0x14c                          # 0x78A1BC
CONV_WORDS = 44
WIDTH_HOOK, WIDTH_STUB = 0x13B8FC, NEW_CAVE+(0x78BAC0-CAVE)
COPY_HELPER = 0x1A5640
HOOKS = {0x2263C4: 0x0C000000 | COPY_HELPER >> 2, 0x2263D8: 0x0C000000 | COPY_HELPER >> 2}
NULS = {0x2263F0: 0xA0600330, 0x2263F4: 0xA0600120}


def jal(target):
    return 0x0C000000 | (target >> 2) & 0x3FFFFFF


def planned(exe):
    donor = (ROOT/'work/cache/english-runtime/english.elf').read_bytes()
    conv_file = NEW_FILE+(CONV-NEW_CAVE)
    body = [u32(exe, conv_file+4*i) for i in range(CONV_WORDS)]
    ref = [u32(donor, CAVE_FILE+(DONOR_CONV-CAVE)+4*i) for i in range(CONV_WORDS)]
    lui, ori = 13, 14
    require(ref[lui] == 0x3C0E0000 | DONOR_TABLE >> 16 and ref[ori] == 0x35CE0000 | DONOR_TABLE & 0xFFFF,
            'Donor converting copy table pair changed')
    require(all(b == r for i, (b, r) in enumerate(zip(body, ref)) if i not in (lui, ori)),
            'Special Disc converting copy differs from donor')
    require(exe[NEW_FILE+0x14c:NEW_FILE+0x14c+190] == donor[CAVE_FILE+0x14c:CAVE_FILE+0x14c+190],
            'Glyph table drift')
    require(u32(exe, WIDTH_HOOK-B_BASE) == 0x08000000 | WIDTH_STUB >> 2, 'Path-A width stub not hooked')
    plan = {conv_file+4*lui: (ref[lui], 0x3C0E0000 | TABLE >> 16),
            conv_file+4*ori: (ref[ori], 0x35CE0000 | TABLE & 0xFFFF)}
    for va, native in HOOKS.items():
        plan[va-B_BASE] = (native, jal(CONV))
    for va, native in NULS.items():
        plan[va-B_BASE] = (native, 0)
    return plan


def apply(exe):
    out, changes = bytearray(exe), []
    for at, (before, after) in sorted(planned(exe).items()):
        now = u32(exe, at)
        require(now in (before, after), 'Back Log preimage mismatch at file 0x%x: %08x' % (at, now))
        if now != after:
            struct.pack_into('<I', out, at, after)
            changes.append(dict(offset=at, before=before, after=after))
    return bytes(out), dict(converter=hex(CONV), table=hex(TABLE), hooks=[hex(v) for v in HOOKS],
                            nops=[hex(v) for v in NULS], patches=changes, sha256=sha(bytes(out)))


def run_conv(exe, raw, dst_size=600):
    """Execute the installed converting copy (a0=dst, a1=src, a2=len) with delay slots."""
    mem, regs = {}, [0]*32
    src, dst = 0x900000, 0xA00000
    for i, b in enumerate(raw+b'\0'):
        mem[src+i] = b
    tbl = exe[NEW_FILE+0x14c:NEW_FILE+0x14c+190]
    for i, b in enumerate(tbl):
        mem[TABLE+i] = b
    regs[4], regs[5], regs[6], regs[31] = dst, src, len(raw), 0xDEAD0
    code = {CONV+4*i: u32(exe, NEW_FILE+(CONV-NEW_CAVE)+4*i) for i in range(CONV_WORDS)}
    pc, branch = CONV, None
    for _ in range(200000):
        if pc == 0xDEAD0:
            out = bytearray()
            while mem.get(dst+len(out), 0xCC) != 0:
                out.append(mem[dst+len(out)])
                require(len(out) < dst_size, 'unterminated output')
            return bytes(out)
        w = code[pc]
        op, rs, rt, rd = w >> 26, w >> 21 & 31, w >> 16 & 31, w >> 11 & 31
        imm = w & 0xFFFF
        simm = imm-0x10000 if imm & 0x8000 else imm
        nxt = branch if branch is not None else pc+4
        branch = None
        if w == 0:
            pass
        elif op == 0 and w & 63 == 0x21:
            regs[rd] = (regs[rs]+regs[rt]) & 0xFFFFFFFF
        elif op == 0 and w & 63 == 0x2B:
            regs[rd] = int(regs[rs] < regs[rt])
        elif op == 0 and w & 63 == 0:
            regs[rd] = regs[rt] << (w >> 6 & 31) & 0xFFFFFFFF
        elif op == 0 and w & 63 == 8:
            branch = regs[rs]
        elif op == 9:
            regs[rt] = (regs[rs]+simm) & 0xFFFFFFFF
        elif op == 11:
            regs[rt] = int(regs[rs] < (simm & 0xFFFFFFFF))
        elif op == 15:
            regs[rt] = imm << 16
        elif op == 13:
            regs[rt] = regs[rs] | imm
        elif op == 36:
            regs[rt] = mem.get((regs[rs]+simm) & 0xFFFFFFFF, 0)
        elif op == 40:
            mem[(regs[rs]+simm) & 0xFFFFFFFF] = regs[rt] & 255
        elif op in (4, 5):
            if (regs[rs] == regs[rt]) == (op == 4):
                branch = pc+4+simm*4
        else:
            raise ValueError('unhandled instruction %08x at %x' % (w, pc))
        regs[0] = 0
        pc = nxt
    raise ValueError('converter did not return')
