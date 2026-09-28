"""Special Disc source contract and native TIM2 menu access."""
import hashlib
import struct
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent/'shared'))
from disc import Disc, file_sha
import banlz
import banlz_strict

SOURCE = ROOT/'work/source/special-disc.bin'
SOURCE_SHA = 'c3bd8c1af4e411e5ab2ae2d4be877170b6ab1ea9b51fa62bc0b91a51ba1a2952'
EXE = 'SLPS_259.20'
VT1 = 'DATA/VT1.BIN'
VT1_TABLE = 0x353790
VT1_COUNT = 109


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def decode(raw):
    total, flags, start = banlz.parse_header(raw)
    require(total is not None, 'Expected compressed record')
    out, consumed = banlz.decompress_record(raw)
    strict, problems = banlz_strict.verify(raw, start, total)
    require(not problems and strict == out and len(out) == total and consumed <= len(raw),
            'Strict decompression failed')
    return out, consumed


def source_records():
    disc = Disc(SOURCE)
    exe = disc.read(EXE)
    require(sha(exe) == '9c345c4a19e7abd791b00af707fe1f44086da6b1b21b8a4344a5872b307c5101', 'Wrong SP executable')
    archive = disc.read(VT1)
    require(sha(archive) == 'e0867e6187539d8331158b2b04e8a00ea7896e6109229b0fb5f0613615729874', 'Wrong VT1 archive')
    offsets = struct.unpack_from('<%dI' % VT1_COUNT, exe, VT1_TABLE)
    require(offsets[0] == 0 and offsets[-1] == len(archive) and list(offsets) == sorted(set(offsets)), 'Invalid VT1 table')
    return disc, exe, archive, offsets


def swizzle_map(width, height):
    import numpy as np
    y, x = np.indices((height, width))
    swap = (((y+2) >> 2) & 1)*4
    py = (((y & ~3) >> 1)+(y & 1)) & 7
    mapping = (y & ~15)*width+(x & ~15)*2+py*width*2+((x+swap) & 7)*4+((y >> 1) & 1)+((x >> 2) & 2)
    flat = mapping.ravel()
    require(np.array_equal(np.sort(flat), np.arange(width*height)), 'Swizzle mapping is not bijective')
    return flat


def tim2(raw):
    import numpy as np
    require(raw[:8] == b'TIM2\x04\0\x01\0', 'Expected single-picture TIM2 v4')
    total, clut_size, image_size, header, colours, fmt, mip, clut_type, image_type, width, height = struct.unpack_from('<IIIHHBBBBHH', raw, 16)
    require((header, colours, clut_size, image_type, mip) == (48,256,1024,5,1), 'Unsupported TIM2 layout')
    require(image_size == width*height and 16+total <= len(raw), 'TIM2 size drift')
    start = 16+header
    m = swizzle_map(width,height)
    indices = np.frombuffer(raw[start:start+image_size],np.uint8)[m].reshape(height,width).copy()
    palette_raw = np.frombuffer(raw[start+image_size:start+image_size+clut_size],np.uint8).reshape(256,4)
    perm = np.array([(i & 0xE7)|((i & 8)<<1)|((i & 16)>>1) for i in range(256)])
    palette = palette_raw[perm].copy()
    rgba = palette[indices].copy()
    rgba[:,:,3] = np.minimum(rgba[:,:,3].astype(int)*2,255)
    return dict(width=width,height=height,start=start,image_size=image_size,map=m,
                indices=indices,palette=palette,rgba=rgba,permutation=perm)


def replace_indices(raw, indices):
    import numpy as np
    data = tim2(raw)
    require(indices.shape == data['indices'].shape, 'Texture geometry changed')
    require(indices.dtype == np.uint8, 'Expected byte indices')
    out = bytearray(raw)
    payload = np.empty(indices.size,np.uint8)
    payload[data['map']] = indices.ravel()
    a = data['start']; b = a+data['image_size']
    out[a:b] = payload.tobytes()
    require(out[:a] == raw[:a] and out[b:] == raw[b:], 'TIM2 header/palette/trailer changed')
    require(np.array_equal(tim2(out)['indices'], indices), 'TIM2 roundtrip failed')
    return bytes(out)
