"""Translate the four Story Mode bonus summaries and align appended columns.

Incremental component for the guarded v0.3.1 executable. No reward values,
selection logic, story text, or existing font code are modified.
"""
import struct
from sp_disc import ROOT, SOURCE, Disc, decode, banlz, require, sha
from reuse_compdata import BBASE
from menu_encoding import menu_encode
from library_text import text
from align_story_panels import Code, APPEND, BASE, actual_width, status_code
from squad_followup import loaded

MEMBER = 'DATA/COMPDATA.BN'
EXE_SHA = '18e347b139bcbe44dea2323226decd4cf6af04f27cb928dd10e5c2fa0244cf22'
HEAD_CALLS = (0x43780C, 0x437838, 0x437860, 0x437888)
TOTAL_CALLS = (0x437D30, 0x437D98, 0x437E28, 0x437E90, 0x437F20, 0x437F88)
FIELDS = (
    (0x98128,16,'Funds'), (0x98138,16,'BS'), (0x98148,16,'PP'), (0x98158,16,'Parts'),
    (0x98170,32,'Starting Funds'), (0x98190,32,'Total Funds'),
    (0x981B0,32,'Starting BS'), (0x981D0,32,'Total BS'),
    (0x981F0,32,'Starting PP'), (0x98210,32,'Total PP'),
    (0x98230,56,'Added the above parts to your starting parts.'),
)


def append_column(x):
    c = Code()
    c.emit(0x27BDFFE0,0x7FB00000,0xFFBF0010,0x0080802D)
    c.emit(0x0C000000 | APPEND >> 2,0)
    c.emit(0x8608252A,0x2508FFFF,0x2D090010)
    c.branch(4,9,0,'done')
    c.emit(0x00084940,0x01094021,0x000848C0,0x01094021,
           0x00084040,0x02084021,0x8509000A,0x240A0002)
    c.branch(5,9,10,'done')
    c.emit(0x24090000 | (x & 65535),0xA5090098)
    c.label('done')
    c.emit(0xDFBF0010,0x7BB00000,0x03E00008,0x27BD0020)
    return c.finish()


def build(exe, packed):
    require(sha(exe)==EXE_SHA,'Expected unmodified v0.3.1 executable')
    raw=decode(packed)[0]; native=decode(Disc(SOURCE).read(MEMBER))[0]
    co=bytearray(raw); out=bytearray(exe); fields=[]; patches=[]
    for i,(at,cap,value) in enumerate(FIELDS):
        pointer=0x6A298+i*4
        require(raw[at:at+cap]==native[at:at+cap],'Bonus field preimage '+hex(at))
        require(struct.unpack_from('<I',raw,pointer)[0]==BBASE+at,'Bonus field pointer')
        encoded=menu_encode(value)
        require(len(encoded)<cap and text(encoded)==value,'Bonus text encoding/slot')
        width=actual_width(value); x=432 if i<4 else 92
        require(x+width<=576,'Bonus text exceeds panel margin')
        co[at:at+cap]=encoded+bytes(cap-len(encoded))
        fields.append(dict(offset=at,capacity=cap,pointer=pointer,text=value,
                           width=width,absolute_x=x,source_hex=raw[at:at+cap].hex()))
    restored=bytearray(co)
    for at,cap,_ in FIELDS: restored[at:at+cap]=raw[at:at+cap]
    require(restored==raw,'Changes outside bonus text slots')
    # Extend only the existing English executable segment, below the unchanged heap.
    po=struct.unpack_from('<I',exe,28)[0]; es,n=struct.unpack_from('<HH',exe,42)
    ph=po+(n-2)*es; s=struct.unpack_from('<8I',exe,ph)
    require(s[:4]==(1,0x3CB770,0x81C970,0x81C970) and
            s[4]==s[5] and s[1]+s[4]==len(exe),'English segment extent')
    heap=struct.unpack_from('<I',exe,0x34F0B4)[0]
    require(struct.unpack_from('<I',exe,0x1001D0-BASE)[0]==0x3C040000|((heap+0x8000)>>16) and
            struct.unpack_from('<I',exe,0x1001D8-BASE)[0]==0x24840000|(heap&65535),'Heap initializer')
    helpers=[]
    for kind,x,calls in [('heading',112,HEAD_CALLS),('total',80,TOTAL_CALLS)]:
        out.extend(bytes((-len(out))%16))
        address=s[2]+len(out)-s[1]; payload=append_column(x); out.extend(payload)
        helpers.append(dict(kind=kind,address=address,x=x,absolute_x=x+320,
                            payload_hex=payload.hex()))
        for va in calls:
            at=loaded(exe,va); before=struct.unpack_from('<I',exe,at)[0]
            require(before==0x0C000000 | APPEND>>2,'Append call preimage '+hex(va))
            after=0x0C000000 | address>>2
            struct.pack_into('<I',out,at,after)
            patches.append(dict(offset=at,address=va,before=before,after=after))
    # Both calls already use the bounded CLEAR!/--- helper. Remove its mode-0
    # restriction so every result page shares the same second-segment column.
    pointers=[(struct.unpack_from('<I',exe,va-BASE)[0]&0x3FFFFFF)<<2 for va in (0x437980,0x437BB0)]
    require(pointers[0]==pointers[1],'Status calls differ')
    at=loaded(exe,pointers[0]); words=struct.unpack_from('<41I',exe,at)
    clear=((words[10]&65535)<<16)|(words[11]&65535)
    dash=((words[14]&65535)<<16)|(words[15]&65535)
    payload=status_code(clear,dash)
    require(exe[at:at+len(payload)]==payload,'Existing status helper drift')
    for addr,value in [(clear,'CLEAR!'),(dash,'---')]:
        pos=loaded(exe,addr); b=menu_encode(value)+b'\0'
        require(exe[pos:pos+len(b)]==b,'Existing status string changed')
    patches.append(dict(offset=at,address=pointers[0],before=words[0],after=0))
    struct.pack_into('<I',out,at,0)  # its existing delay slot is already nop
    count=len(out)-s[1]; end=s[2]+count
    require(end<=heap,'English helper would overlap heap')
    for at,value in [(ph+16,count),(ph+20,count),(ph+es+4,len(out))]:
        before=struct.unpack_from('<I',exe,at)[0]
        patches.append(dict(offset=at,before=before,after=value))
        struct.pack_into('<I',out,at,value)
    restored=bytearray(out[:len(exe)])
    for p in patches: struct.pack_into('<I',restored,p['offset'],p['before'])
    require(restored==exe,'Unplanned executable changes')
    result=banlz.compress_record(bytes(co),flags=banlz.parse_header(packed)[1])
    require(decode(result)[0]==co,'Bonus compression roundtrip')
    return bytes(out),result,dict(fields=fields,helpers=helpers,patches=patches,
        status_helper=pointers[0],status_x=128,heap_base=heap,segment_end=end,
        source_executable_sha256=sha(exe),executable_sha256=sha(out),
        decoded_before_sha256=sha(raw),decoded_after_sha256=sha(co),
        unplanned_changes=False,emulator='pending')
