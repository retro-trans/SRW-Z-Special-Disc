"""Map the two native caption buffers to larger storage in the English segment.

Only four call instructions change. Their delay slots and the original
structures remain intact. Unknown object addresses retain native behavior.
"""
import struct
from sp_disc import Disc, SOURCE, EXE, require
from reuse_compdata import POOL_BASE

FILE_BASE = 0xff680
ORIGINAL_BUFFERS = (0x6899c8, 0x68ab18)
CALLS = ((0x2f198c, 'fill', 0x2f1760), (0x2f1bac, 'fill', 0x2f1760),
         (0x2f2128, 'draw', 0x2fd9a0), (0x2f21c0, 'clear', 0x1a23d8))


def load(reg, value):
    require(0 <= value < 2**32, 'Caption helper immediate')
    return [0x3c000000 | reg << 16 | value >> 16,
            0x34000000 | reg << 21 | reg << 16 | (value & 65535)]


def helper_code(argument, buffers, target, capacity=None):
    require(argument in (4, 5) and len(buffers) == 2, 'Caption helper arguments')
    require(target % 4 == 0 and 0 < target < 0x10000000, 'Caption helper tail target')
    words = []; branches = []; labels = []
    for old in ORIGINAL_BUFFERS:
        words.extend(load(25, old))
        branches.append(len(words))
        words.extend([0x10000000 | argument << 21 | 25 << 16, 0])
    # Non-caption users, if any, continue through the original function.
    words.extend([0x08000000 | target >> 2, 0])
    for new in buffers:
        labels.append(len(words)); words.extend(load(argument, new))
        if capacity is not None: words.extend(load(6, capacity))
        words.extend([0x08000000 | target >> 2, 0])
    for at, dest in zip(branches, labels): words[at] |= dest - at - 1
    return struct.pack('<%dI' % len(words), *words)


def build(exe, pool, capacity):
    require(type(capacity) is int and capacity >= 96 and capacity % 16 == 0,
            'Caption buffer capacity must include terminator and alignment')
    native = Disc(SOURCE).read(EXE)
    out = bytearray(exe); pool = bytearray(pool)
    pool.extend(bytes((-len(pool)) % 16)); buffers = []
    for _ in range(2):
        buffers.append(POOL_BASE + len(pool)); pool.extend(bytes(capacity))
    helpers = {}
    for kind, argument, target in [('fill', 4, 0x2f1760), ('draw', 5, 0x2fd9a0), ('clear', 4, 0x1a23d8)]:
        code = helper_code(argument, buffers, target, capacity if kind == 'clear' else None)
        address = POOL_BASE + len(pool); pool.extend(code)
        helpers[kind] = dict(address=address, bytes=len(code), payload_hex=code.hex(), tail_target=target)
    patches = []
    for va, kind, original in CALLS:
        at = va - FILE_BASE; before = struct.pack('<I', 0x0c000000 | original >> 2)
        require(native[at:at+4] == out[at:at+4] == before, 'Caption buffer call preimage ' + hex(va))
        address = helpers[kind]['address']
        require(address % 4 == 0 and address < 0x10000000, 'Caption helper JAL range')
        after = struct.pack('<I', 0x0c000000 | address >> 2); out[at:at+4] = after
        patches.append(dict(address=va, offset=at, source_hex=before.hex(), payload_hex=after.hex(), helper=kind))
    restored = bytearray(out)
    for row in patches: restored[row['offset']:row['offset']+4] = bytes.fromhex(row['source_hex'])
    require(restored == exe, 'Caption helper changed unrelated executable bytes')
    return bytes(out), bytes(pool), dict(capacity=capacity, original_capacity=96,
        original_buffers=list(ORIGINAL_BUFFERS), buffers=buffers, helpers=helpers, patches=patches,
        unknown_object_fallback='Original pointer and clear length', emulator='pending by user choice')
