"""Stage title-card label and guarded native number composition patches."""
import json, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from sp_disc import ROOT, EXE, VT1, require, decode, sha
from episode_titles import TABLE, FONT, unpack, pack, compress_tail

# Native output is 160x24 at 4bpp, with doubled horizontal texels.
# Combine the two former 48-texel ordinal tiles. No allocation or stride change.
PATCHES = [
    (0x1d60ac, 0x24080018, 0x24080030), # single-digit prefix: 48 bytes
    (0x1d60c8, 0x24060020, 0x24060038), # single digit follows label
    (0x1d60f8, 0x0c0757b8, 0),          # remove suffix blit
    (0x1d6124, 0x24080018, 0x24080030), # two-digit prefix
    (0x1d6164, 0x24060018, 0x24060030), # tens
    (0x1d61a8, 0x24060028, 0x24060040), # units
    (0x1d61d8, 0x0c0757b8, 0),          # remove suffix blit
]

def artwork():
    font=ImageFont.truetype(str(FONT),24)
    im=Image.new('L',(80,40));ImageDraw.Draw(im).text((0,0),'Stage',font=font,fill=255)
    # Same 16-row capital height and y=20 baseline as native digit 1.
    # Fit only the descender to the four rows below that baseline.
    ink=im.crop((1,6,56,27)); fitted=Image.new('L',(55,20))
    fitted.paste(ink.crop((0,0,55,16)),(0,0))
    fitted.paste(ink.crop((0,16,55,21)).resize((55,4),Image.Resampling.LANCZOS),(0,16))
    im=Image.new('L',(48,24));im.paste(fitted.resize((46,20),Image.Resampling.LANCZOS),(1,4))
    return ((np.asarray(im,dtype=np.uint16)*15+127)//255).astype(np.uint8)

def compose(pixels,number,updated):
    require(0<=number<=99,'Stage number outside native two-digit range')
    out=np.zeros((24,160),np.uint8)
    def blit(dst,src,size):
        require(dst+size<=80 and src+size<=208,'Stage blit exceeds buffer')
        out[:,dst*2:(dst+size)*2]=pixels[:,src*2:(src+size)*2]
    if number<10:
        blit(8,160,48 if updated else 24)
        blit(56 if updated else 32,number*16,16)
        if not updated:blit(48,184,24)
    else:
        blit(0,160,48 if updated else 24)
        blit(48 if updated else 24,(number//10)*16,16)
        blit(64 if updated else 40,(number%10)*16,16)
        if not updated:blit(56,184,24)
    return out

def build(disc):
    exe=disc.read(EXE);vt=disc.read(VT1)
    outer=struct.unpack_from('<109I',exe,0x353790)
    nested=struct.unpack_from('<28I',exe,TABLE)
    lo,hi=outer[9]+nested[4],outer[9]+nested[5]
    stored=vt[lo:hi];raw,used=decode(stored)
    require(not any(stored[used:]),'Unexpected title slot tail')
    require(raw[197312:197320]==b'TIM2\x04\0\x01\0' and
            struct.unpack_from('<HH',raw,197348)==(416,24),'Title atlas changed')
    original=unpack(raw[197376:202368],416,24)
    from episode_titles import header
    require(header(raw)==raw,'Input no longer has expected Ep. label')
    pixels=original.copy();pixels[:,320:]=np.repeat(artwork(),2,axis=1)
    changed=raw[:197376]+pack(pixels)+raw[202368:]
    require(np.array_equal(original[:,:320],pixels[:,:320]),'Native digits changed')
    packed=compress_tail(stored,raw,changed)
    # Reduce antialias shades only on the new label if the native slot is tight.
    levels=16
    if len(packed)>hi-lo:
        levels=8
        label=pixels[:,320:].astype(np.uint16)
        pixels[:,320:]=((label*7+7)//15*15//7).astype(np.uint8)
        changed=raw[:197376]+pack(pixels)+raw[202368:]
        packed=compress_tail(stored,raw,changed)
    require(len(packed)<=hi-lo,'Title compressed slot overflow')
    require(decode(packed)[0]==changed,'Title compression roundtrip failed')
    result=bytearray(exe);edits=[]
    for va,before,after in PATCHES:
        at=va-0xff680
        require(struct.unpack_from('<I',exe,at)[0]==before,'Title instruction drift '+hex(va))
        struct.pack_into('<I',result,at,after)
        edits.append(dict(va=hex(va),offset=at,before=hex(before),after=hex(after)))
    # Pin all dimensions used by the native blitter and output clear loop.
    for va,word in [(0x1d5f94,0x29630018),(0x1d5f98,0x24a500d0),
                    (0x1d5fa0,0x24840050),(0x1d607c,0x28620780)]:
        require(struct.unpack_from('<I',exe,va-0xff680)[0]==word,'Blitter dimension drift')
    for number in range(100):
        out=compose(pixels,number,True)
        start=56 if number<10 else 48
        for j,digit in enumerate(str(number)):
            require(np.array_equal(out[:,(start+j*16)*2:(start+j*16+16)*2],
                       original[:,int(digit)*32:(int(digit)+1)*32]),'Digit composition changed')
    report=dict(label='Stage',font='Times New Roman Bold',font_size=24,
        capital_height=16,baseline_y=20,label_logical_width=48,antialias_levels=levels,
        horizontal_ink_fit=46,descender_rows=4,number_cases_checked=100,
        decoded_before_sha256=sha(raw),decoded_after_sha256=sha(changed),
        compressed_bytes=len(packed),slot_bytes=hi-lo,exe_edits=edits,
        texture_span=dict(start=lo,end=hi),native_digits_preserved=True,
        title_art_and_animation_preserved=True,runtime='pending')
    outdir=ROOT/'work/ui/stage-label';outdir.mkdir(parents=True,exist_ok=True)
    canvas=Image.new('RGB',(720,440),(36,37,20));draw=ImageDraw.Draw(canvas)
    draw.text((16,12),'Title label preview - reconstructed pixels, not emulator capture',fill='white')
    for i,number in enumerate((1,9,10,24)):
        for j,(src,new) in enumerate(((original,False),(pixels,True))):
            a=compose(src,number,new)[:,::2]
            mask=Image.fromarray(a*17).resize((320,96),Image.Resampling.NEAREST)
            canvas.paste((255,255,230),(20+j*350,38+i*100),mask)
    canvas.save(outdir/'preview-0.3.16.png')
    (outdir/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return {EXE:bytes(result),VT1:vt[:lo]+packed+bytes(hi-lo-len(packed))+vt[hi:]},report
