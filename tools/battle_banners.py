"""Reuse source-matched SRW-Z formation, attack and warning sprite rectangles.

PSMT4/CT32 address mapping adapted from SRW-Z patch_battle_banners.py.
All other texture nibbles, palettes, animation data and archive offsets survive.
"""
from functools import lru_cache
import json, struct
import numpy as np
from PIL import Image
from sp_disc import ROOT, SOURCE, Disc, sha, require
from library_text import DONOR, ORIGINAL

MEMBER = 'BTL/TRICMN.BIN'
WIDTH, HEIGHT = 512, 256
STARTS = (0x365A0, 0x46CD0)
TARGET = ROOT/'work/translation/en/battle_banners.json'

def gs32(x, y, width):
    """32-bit word address in GS memory (one page = 64x32 pixels)."""
    blocks = (0, 1, 4, 5, 16, 17, 20, 21, 2, 3, 6, 7, 18, 19, 22, 23,
              8, 9, 12, 13, 24, 25, 28, 29, 10, 11, 14, 15, 26, 27, 30, 31)
    columns = (0, 1, 4, 5, 8, 9, 12, 13, 2, 3, 6, 7, 10, 11, 14, 15)
    page = (y // 32) * (width // 64) + x // 64
    block = blocks[(y % 32 // 8) * 8 + x % 64 // 8]
    return page * 2048 + block * 64 + (y % 8 // 2) * 16 + columns[(y % 2) * 8 + x % 8]

def gs4(x, y, width):
    """4-bit texel address in GS memory (one page = 128x128 texels).

    GS block/column layout reference: Victor Suba's GSTextureConvert tables,
    documented at https://github.com/leeao/PS2Textures/blob/main/PS2Textures.py.
    Compose this address with the inverse CT32 upload map; simply treating
    the packed nibbles as a swizzled 8-bit image does not work for this atlas.
    """
    blocks = (0, 2, 8, 10, 1, 3, 9, 11, 4, 6, 12, 14, 5, 7, 13, 15,
              16, 18, 24, 26, 17, 19, 25, 27, 20, 22, 28, 30, 21, 23, 29, 31)
    column = y % 16 // 4
    word = (0, 1, 4, 5, 8, 9, 12, 13)[x % 8] + (y % 2) * 2
    if ((y % 4) // 2) ^ (column % 2):
        word ^= 8
    nibble = (x % 32 // 8) * 2 + (y % 4 // 2)
    page = (y // 128) * (width // 128) + x // 128
    block = blocks[(y % 128 // 16) * 4 + x % 128 // 32]
    return (page * 2048 + block * 64 + column * 16 + word) * 8 + nibble

@lru_cache(None)
def swizzle_map():
    # Native 512x256 PSMT4 is uploaded as a 256x64 CT32 image.
    inverse = {gs32(x, y, 256) * 8 + k: (y * 256 + x) * 8 + k
               for y in range(64) for x in range(256) for k in range(8)}
    result = tuple(inverse[gs4(x, y, WIDTH)]
                   for y in range(HEIGHT) for x in range(WIDTH))
    if sorted(result) != list(range(WIDTH * HEIGHT)):
        raise ValueError('PSMT4 mapping is not a complete permutation')
    return result


def pixels(blob, page):
    header = struct.unpack_from('<IIIHHBBBBHH', blob, STARTS[page]-48)
    expected = ((67376,1792,65536,48,448,0,1,3,4,512,256),
                (65584,0,65536,48,0,0,1,3,4,512,256))[page]
    require(header == expected, 'Battle atlas geometry changed')
    raw = np.frombuffer(blob[STARTS[page]:STARTS[page]+65536],np.uint8)
    return np.stack((raw&15,raw>>4),axis=-1).ravel()[list(swizzle_map())].reshape(256,512)


def build(disc):
    spec = json.loads(TARGET.read_text(encoding='utf-8'))
    old = disc.read(MEMBER)
    native = Disc(SOURCE).read(MEMBER)
    original = (ORIGINAL/'BTL_TRICMN.BIN').read_bytes()
    donor = Disc(DONOR,True).read(MEMBER)
    for name, value in [('special_disc',native),('z_native',original),('z_english',donor)]:
        require(sha(value)==spec['sources'][name], 'Battle banner source drift: '+name)
    require(old==native, 'Battle resource already modified; review before applying')
    # CLUT is shared by all four pictures. Never substitute another game's palette.
    for logical in (23,25):
        for i in range(logical*16,logical*16+16):
            j=(i&~31)|(i&7)|((i&8)<<1)|((i&16)>>1)
            at=0x465a0+j*4
            require(native[at:at+4]==original[at:at+4]==donor[at:at+4],
                    'Used battle palette differs')
    before = [pixels(native,p) for p in range(2)]
    source = [pixels(original,p) for p in range(2)]
    english = [pixels(donor,p) for p in range(2)]
    after = bytearray(old); allowed = bytearray(len(old)); rows=[]
    mapping = swizzle_map(); seen=set()
    for row in spec['entries']:
        page = row['page']; x0,y0,x1,y1 = row['rect']; view=np.s_[y0:y1,x0:x1]
        require(np.array_equal(before[page][view],source[page][view]),'Native sprite mismatch: '+row['text'])
        require(not np.array_equal(source[page][view],english[page][view]),'Untranslated donor sprite')
        for y in range(y0,y1):
            for x in range(x0,x1):
                require((page,x,y) not in seen, 'Overlapping sprite rectangles');seen.add((page,x,y))
                p=mapping[y*512+x];off=STARTS[page]+p//2;shift=(p%2)*4;mask=15<<shift
                after[off]=(after[off]&(255^mask))|(int(english[page][y,x])<<shift)
                allowed[off]|=mask
        rows.append(dict(row,native_pixel_sha256=sha(before[page][view].tobytes()),
                         english_pixel_sha256=sha(english[page][view].tobytes())))
    require(len(rows)==15, 'Incomplete banner category')
    require(all(((a^b)&(255^m))==0 for a,b,m in zip(old,after,allowed)), 'Unrelated texture nibble changed')
    for page in range(2):
        expected=before[page].copy()
        for row in rows:
            if row['page']!=page:continue
            x0,y0,x1,y1=row['rect'];expected[y0:y1,x0:x1]=english[page][y0:y1,x0:x1]
        require(np.array_equal(pixels(after,page),expected),'Texture roundtrip mismatch')
    return bytes(after),dict(entries=rows,source_hashes=spec['sources'],
         before_sha256=sha(old),after_sha256=sha(after),changed_bytes=sum(a!=b for a,b in zip(old,after)),
         source_rectangles_identical=True,palettes_preserved=True,unrelated_nibbles_preserved=True,
         animation_and_sprite_coordinates_preserved=True)


def preview(blob,path):
    canvas=Image.new('RGBA',(512,512),(15,15,30,255))
    for page,pal in enumerate((23,25)):
        ids=[pal*16+i for i in range(16)]
        ids=[(i&~31)|(i&7)|((i&8)<<1)|((i&16)>>1) for i in ids]
        colors=np.frombuffer(blob[0x465a0:0x46ca0],np.uint8).reshape(-1,4)[ids].copy()
        colors[:,3]=np.minimum(colors[:,3].astype(int)*2,255)
        canvas.alpha_composite(Image.fromarray(colors[pixels(blob,page)]),(0,page*256))
    canvas.convert('RGB').save(path)
