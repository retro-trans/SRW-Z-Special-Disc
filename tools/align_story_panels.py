"""Align episode introductions and the cleared-stage confirmation panel."""
import json
import struct
from sp_disc import ROOT, require, sha
from reuse_compdata import POOL_BASE
from menu_encoding import menu_encode
from save_summary_text import WIDTHS
from library_text import CHARS
from battle_buffer import load

BASE = 0xFF680
INTRO_LIMIT = 500
LEFT = -256
STATUS_X = 128
APPEND = 0x37D8B0
MEASURE = 0x13A5A0
QUESTIONS = ('Link the data?', 'Play this episode?', 'Claim bonuses for these cleared stages?')
MARGINS = (0x43755C, 0x4375B0, 0x4377A8, 0x437918)
STATUS_CALLS = (0x437980, 0x437BB0)
CENTER_CALLS = (0x43761C, 0x437C54)


class Code:
    def __init__(self):
        self.words = []
        self.labels = {}
        self.branches = []

    def emit(self, *words):
        self.words.extend(words)

    def label(self, name):
        require(name not in self.labels, 'Duplicate helper label')
        self.labels[name] = len(self.words)

    def branch(self, op, left, right, label):
        self.branches.append((len(self.words), label))
        self.emit(op << 26 | left << 21 | right << 16, 0)

    def finish(self):
        for at, label in self.branches:
            delta = self.labels[label]-at-1
            require(-32768 <= delta < 32768, 'Helper branch overflow')
            self.words[at] |= delta & 65535
        return struct.pack('<%dI' % len(self.words), *self.words)


def status_code(clear_address, dash_address):
    c = Code()
    # s4 is the guarded caller's reward-detail mode. Only mode 0 is the
    # cleared-stage confirmation; other modes retain the native append path.
    c.branch(5, 20, 0, 'fallback')
    c.emit(0x27BDFFE0, 0x7FB00000, 0xFFBF0010, 0x0080802D)
    # t0 is the fifth native argument (style); use t4 as scratch instead.
    c.emit(*load(12, 0x4C3990))
    c.branch(5, 5, 12, 'dash')
    c.emit(*load(5, clear_address))
    c.branch(4, 0, 0, 'append')
    c.label('dash')
    c.emit(*load(5, dash_address))
    c.label('append')
    c.emit(0x0C000000 | APPEND >> 2, 0)
    c.emit(0x8608252A, 0x2508FFFF, 0x2D090010)
    c.branch(4, 9, 0, 'done')
    # Native row stride = 594; last row's second text segment starts at +0x56.
    c.emit(0x00084940, 0x01094021, 0x000848C0, 0x01094021,
           0x00084040, 0x02084021, 0x8509000A, 0x240A0002)
    c.branch(5, 9, 10, 'done')
    c.emit(0x24090000 | STATUS_X, 0xA5090098)
    c.label('done')
    c.emit(0xDFBF0010, 0x7BB00000, 0x03E00008, 0x27BD0020)
    c.label('fallback')
    c.emit(0x08000000 | APPEND >> 2, 0)
    return c.finish()


def actual_width(value):
    require(set(value) <= set(map(chr, CHARS)) | {' '}, 'Unmeasured panel glyph')
    return sum(WIDTHS[CHARS.index(ord(ch))]+1 if ch != ' ' else 13 for ch in value)


def center_code(addresses):
    c = Code()
    c.branch(5, 5, 0, 'fallback')
    for i, (address, phrase) in enumerate(zip(addresses, QUESTIONS)):
        c.emit(0x0080402D, *load(9, address))  # preserve a0 for fallback
        c.label('compare'+str(i))
        c.emit(0x910A0000, 0x912B0000)
        c.branch(5, 10, 11, 'next'+str(i))
        c.branch(4, 11, 0, 'match'+str(i))
        c.emit(0x25080001, 0x25290001)
        c.branch(4, 0, 0, 'compare'+str(i))
        c.label('match'+str(i))
        c.emit(0x24020000 | ((-(actual_width(phrase)//2)) & 65535), 0x03E00008, 0)
        c.label('next'+str(i))
    c.label('fallback')
    c.emit(0x08000000 | MEASURE >> 2, 0)
    return c.finish()


def build(exe, pool):
    native = (ROOT/'work/cache/english-runtime/special.elf').read_bytes()
    require(sha(native) == '9c345c4a19e7abd791b00af707fe1f44086da6b1b21b8a4344a5872b307c5101',
            'Panel executable identity')
    intros = json.loads((ROOT/'work/translation/en/briefings.json').read_text(encoding='utf-8'))['intro']
    require([r['question'] for r in intros] == [QUESTIONS[0]] + [QUESTIONS[1]]*5,
            'Episode question text changed; remeasure it')
    system = json.loads((ROOT/'work/translation/en/system.json').read_text(encoding='utf-8'))
    require(next(r['text'] for r in system if r['id'] == 'exe/3b51a0') == QUESTIONS[2],
            'Clear confirmation changed; remeasure it')
    # Bind the native segment fields/stride and caller mode without relying
    # solely on the individual patched call opcodes.
    guarded = {0x437714: 0x0080A02D, 0x4377C0: 0x24020004,
               0x37D968: 0x0003082A, 0x37D8F4: 0x000418C0,
               0x37D934: 0x00021040, 0x37D9B8: 0xA6720042,
               0x37D9C0: 0xA6630044}
    for va, word in guarded.items():
        require(struct.unpack_from('<I', exe, va-BASE)[0] == word, 'Panel structure guard '+hex(va))
    out = bytearray(exe); expanded = bytearray(pool)
    strings = []
    for value in ('CLEAR!', '---') + QUESTIONS:
        encoded = menu_encode(value)+b'\0'
        address = POOL_BASE+len(expanded)
        expanded.extend(encoded)
        strings.append(dict(text=value, address=address, bytes_hex=encoded.hex()))
    expanded.extend(bytes((-len(expanded)) % 16))
    helpers = []
    for kind, payload in (
        ('status', status_code(strings[0]['address'], strings[1]['address'])),
        ('center', center_code([r['address'] for r in strings[2:]]))):
        address = POOL_BASE+len(expanded)
        expanded.extend(payload)
        helpers.append(dict(kind=kind, address=address, payload_hex=payload.hex(), sha256=sha(payload)))
    patches = []
    def patch(va, before, after, purpose):
        at = va-BASE
        require(struct.unpack_from('<I', native, at)[0] == before and
                struct.unpack_from('<I', out, at)[0] == before, 'Panel patch preimage '+hex(va))
        struct.pack_into('<I', out, at, after)
        patches.append(dict(address=va, offset=at, before=before, after=after, purpose=purpose))
    for va in MARGINS:
        patch(va, 0x2406FF1C, 0x24060000 | (LEFT & 65535), 'Shared left margin')
    for va in STATUS_CALLS:
        patch(va, 0x0C000000 | APPEND >> 2, 0x0C000000 | helpers[0]['address'] >> 2,
              'Fixed cleared-stage marker column in confirmation mode only')
    for va in CENTER_CALLS:
        patch(va, 0x0C000000 | MEASURE >> 2, 0x0C000000 | helpers[1]['address'] >> 2,
              'Center known English questions using their actual font advances')
    restored = bytearray(out)
    for p in patches:
        struct.pack_into('<I', restored, p['offset'], p['before'])
        require(out[p['offset']+4:p['offset']+8] == exe[p['offset']+4:p['offset']+8],
                'Panel delay slot changed')
    require(restored == exe, 'Unrelated executable bytes changed')
    return bytes(out), bytes(expanded), dict(
        source_executable_sha256=sha(native), left_x=LEFT, absolute_left_x=320+LEFT,
        status_x=STATUS_X, absolute_status_x=320+STATUS_X, intro_line_limit=INTRO_LIMIT,
        question_center_x=316, questions=[dict(text=q, actual_width=actual_width(q),
            absolute_x=316-actual_width(q)//2) for q in QUESTIONS],
        strings=strings, helpers=helpers, patches=patches,
        guard_words={hex(k):hex(v) for k,v in guarded.items()},
        preserved='Original row/segment allocation, status flags, colors, rewards and non-confirmation append path',
        runtime='pending by user choice')
