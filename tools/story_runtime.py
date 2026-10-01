"""Enable the donor's ASCII-to-glyph conversion before native story layout.

The font-only port already reserved and copied this converter, but deliberately
left it unreachable. Relocate only its reachable instructions and setText hook.
No new memory, heap shift, text shortening, or archive relocation is needed.
"""
import json
import struct
from sp_disc import ROOT, require, sha
from inspect_english_runtime import A_BASE, B_BASE, CAVE, CAVE_FILE, normal, u32, s16, hi_pair
from port_menu_runtime import NEW_CAVE, NEW_FILE

SETTEXT = 0x2112d0
HELPERS = {0x200f80: 0x205490, 0x2011d0: 0x2056e0, 0x1a0d88: 0x1a5238}
CODE_BYTES = 0x14c
TABLE_BYTES = 190


def inputs():
    folder = ROOT / 'work/cache/english-runtime'
    a, b, c = [(folder / name).read_bytes() for name in ('original.elf', 'special.elf', 'english.elf')]
    report = json.loads((ROOT / 'work/analysis/english-runtime-map.json').read_text())
    for data, key in ((a, 'original_sha256'), (b, 'source_sha256'), (c, 'donor_sha256')):
        require(sha(data) == report[key], 'Story runtime input drift: ' + key)
    return a, b, c


def apply(exe):
    a, native, donor = inputs()
    # These 24-word signatures are unique in the native executable; calls in
    # setText independently confirm the three helper addresses and argument ABI.
    for old, new in {0x20c9b0: SETTEXT, **HELPERS}.items():
        require(all(normal(u32(a, old-A_BASE+i)) == normal(u32(native, new-B_BASE+i))
                    for i in range(0, 96, 4)), 'Story helper signature mismatch')
    for call, dest in ((0x2112ec, 0x205490), (0x211300, 0x2056e0), (0x211314, 0x1a5238)):
        require(u32(exe, call-B_BASE) == 0x0c000000 | dest >> 2, 'Story helper call changed')
    def mapped(pc):
        if CAVE <= pc < CAVE+CODE_BYTES+TABLE_BYTES:
            return pc+NEW_CAVE-CAVE
        require(pc in HELPERS, 'Unexpected story converter target: ' + hex(pc))
        return HELPERS[pc]
    def word(pc): return u32(donor, CAVE_FILE+pc-CAVE)
    seen, pending, external = set(), [CAVE], set()
    while pending:
        pc = pending.pop()
        if pc in seen: continue
        if not CAVE <= pc < CAVE+CODE_BYTES:
            external.add(pc); continue
        seen.add(pc); w = word(pc); op = w >> 26
        if op in (2, 3):
            pending.append((w & 0x3ffffff) << 2); seen.add(pc+4)
            if op == 3: pending.append(pc+8)
        elif op in (4, 5):
            pending.extend((pc+8, pc+4+s16(w)*4)); seen.add(pc+4)
        elif op == 0 and w & 63 == 8:
            seen.add(pc+4)
        else: pending.append(pc+4)
    require(external == set(HELPERS) and seen == set(range(CAVE, CAVE+CODE_BYTES, 4)), 'Story converter graph changed')
    expected = {}
    for pc in sorted(seen):
        w = word(pc); op = w >> 26
        if op in (2, 3): w = (w & 0xfc000000) | mapped((w & 0x3ffffff) << 2) >> 2
        # All relative branches stay inside the converter, so their displacements are unchanged.
        if op in (4, 5): require(pc+4+s16(w)*4 in seen, 'Story branch escapes converter')
        expected[NEW_FILE+pc-CAVE] = w
    for pc in sorted(seen):
        w = word(pc)
        if w >> 26 != 13: continue
        pair = hi_pair(word, pc, w, CAVE)
        if pair:
            hp, hw = pair; value = (hw & 65535) << 16 | w & 65535
            require(value == CAVE+CODE_BYTES, 'Story table pointer changed')
            dest = mapped(value)
            expected[NEW_FILE+hp-CAVE] = hw & 0xffff0000 | dest >> 16
            expected[NEW_FILE+pc-CAVE] = w & 0xffff0000 | dest & 65535
    table = donor[CAVE_FILE+CODE_BYTES:CAVE_FILE+CODE_BYTES+TABLE_BYTES]
    require(exe[NEW_FILE+CODE_BYTES:NEW_FILE+CODE_BYTES+TABLE_BYTES] == table, 'Story conversion table drift')
    expected[SETTEXT-B_BASE] = 0x08000000 | NEW_CAVE >> 2
    expected[SETTEXT-B_BASE+4] = 0
    out = bytearray(exe); changes = []
    for at, after in sorted(expected.items()):
        before = u32(exe, at)
        original = u32(native, at) if at < NEW_FILE else u32(donor, CAVE_FILE+at-NEW_FILE)
        require(before in (original, after), 'Story converter preimage mismatch: ' + hex(at))
        if before != after:
            struct.pack_into('<I', out, at, after)
            changes.append(dict(offset=at, before=before, after=after))
    require(len(out) == len(exe), 'Story runtime must not grow the executable')
    return bytes(out), dict(settext=hex(SETTEXT), converter=hex(NEW_CAVE),
                           mapped_helpers={hex(k):hex(v) for k,v in HELPERS.items()},
                           code_words=len(seen), patches=changes, sha256=sha(out))


def convert(raw, table):
    """Reference only; tests execute the actual relocated instructions too."""
    out = bytearray(); i = 0
    while i < len(raw):
        b = raw[i]
        if 0x81 <= b <= 0x9f or 0xe0 <= b <= 0xfc:
            out.extend(raw[i:i+2]); i += 2
        else:
            out.extend(table[(b-32)*2:(b-31)*2] if 32 <= b <= 126 else bytes([b])); i += 1
    return bytes(out)
