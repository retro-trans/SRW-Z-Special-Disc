"""Guarded v0.3.7 fix for the panel token reader's ASCII byte stride."""
import struct
from sp_disc import require, sha
from squad_followup import loaded
from align_story_panels import Code
from bonus_results import append_column

EXE_SHA = 'a29a969033279e74a67411a576f20b6978dc5f5a4b681e4c6876f9a3eaafe69c'
HOOK = 0x3638B0
TOTAL = 0x83D270


def reader_code():
    c = Code()
    # a0 is the sign-extended current byte, already copied by 0x3638ac.
    # ASCII consumes one byte. Keep the native second-byte path for SJIS.
    c.emit(0x2C830080)  # sltiu v1,a0,128
    c.branch(4, 3, 0, 'pair')
    c.emit(0x26940001, 0x8FA201CC, 0x24420001,
           0x08000000 | (0x3638EC >> 2), 0)
    c.label('pair')
    c.emit(0x24420001, 0x08000000 | (0x3638B8 >> 2), 0x8FA401CC)
    return c.finish()


def build(exe):
    require(sha(exe) == EXE_SHA, 'Expected unmodified v0.3.6 executable')
    out = bytearray(exe); patches = []
    def patch(at, before, after, purpose):
        require(struct.unpack_from('<I', out, at)[0] == before, purpose+' preimage')
        struct.pack_into('<I', out, at, after)
        patches.append(dict(offset=at, before=before, after=after, purpose=purpose))
    po = struct.unpack_from('<I', exe, 28)[0]
    es, n = struct.unpack_from('<HH', exe, 42)
    ph = po+(n-2)*es
    s = struct.unpack_from('<8I', exe, ph)
    require(s[:4] == (1, 0x3CB770, 0x81C970, 0x81C970) and
            s[4] == s[5] and s[1]+s[4] == len(exe), 'English segment layout')
    out.extend(bytes((-len(out)) % 16))
    address = s[2]+len(out)-s[1]
    payload = reader_code(); out.extend(payload)
    patch(loaded(exe, HOOK), 0x24420001, 0x08000000 | address >> 2, 'ASCII reader hook')
    patch(loaded(exe, HOOK+4), 0x8FA401CC, 0, 'Reader hook delay slot')
    # Native numeric formatting emits 12 cells for funds, 10 for BS/PP.
    # Move the existing totals column 48 units left, leaving room for padding.
    at = loaded(exe, TOTAL); old = append_column(80); new = append_column(32)
    require(exe[at:at+len(old)] == old, 'Existing total helper drift')
    for i in range(0, len(old), 4):
        a, b = struct.unpack_from('<I', old, i)[0], struct.unpack_from('<I', new, i)[0]
        if a != b: patch(at+i, a, b, 'Totals column x400 to x352')
    size = len(out)-s[1]; end = s[2]+size
    heap = struct.unpack_from('<I', exe, 0x34F0B4)[0]
    require(end <= heap, 'Reader helper overlaps heap')
    for at, value in ((ph+16, size), (ph+20, size), (ph+es+4, len(out))):
        patch(at, struct.unpack_from('<I', exe, at)[0], value, 'English segment extent')
    restored = bytearray(out[:len(exe)])
    for p in patches: struct.pack_into('<I', restored, p['offset'], p['before'])
    require(restored == exe, 'Unplanned executable change')
    return bytes(out), dict(source_executable_sha256=sha(exe), executable_sha256=sha(out),
        patches=patches, helper_address=address, helper_bytes=len(payload), payload_hex=payload.hex(),
        segment_end=end, heap_base=heap, totals_x=352, prior_totals_x=400,
        scope='Shared token-aware panel text reader; ASCII one byte, native pairs unchanged',
        emulator='pending')
