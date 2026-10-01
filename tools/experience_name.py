"""Translate the six scripted Grendizer squad presets used by result UI."""
import struct
from sp_disc import ROOT,SOURCE,Disc,decode,sha,require
from build_story import STAGE,HB,TABLE,repack
from menu_encoding import menu_encode
from library_text import text

BINDINGS=((18,0x6509),(19,0x3de9),(19,0x40a9),(20,0x45a9),(20,0x4835),(21,0x6c45))
SOURCE_NAME='グレンダイザー'
ENGLISH='Grendizer'


def build(disc):
    native=Disc(SOURCE);ns=native.read(STAGE);no=struct.unpack_from('<69I',native.read(HB),TABLE)
    stage=disc.read(STAGE);hb=disc.read(HB);offs=struct.unpack_from('<69I',hb,TABLE)
    before={};changed={};rows=[]
    expected=SOURCE_NAME.encode('cp932')+b'\0';replacement=menu_encode(ENGLISH)
    require(len(replacement)<len(expected) and text(replacement)==ENGLISH,'Name encoding')
    replacement+=bytes(len(expected)-len(replacement))
    # The displayed label is a 33-byte area after the preset index in a
    # 52-byte record. Only the original name and its terminator are written;
    # the remainder, six member IDs, flags and other record bytes stay intact.
    for c,at in BINDINGS:
        original=decode(ns[no[c]:no[c+1]])[0]
        if c not in before:
            before[c]=decode(stage[offs[c]:offs[c+1]])[0];changed[c]=bytearray(before[c])
        raw=before[c]
        require(raw[at-1:at+51]==original[at-1:at+51],'Preset record preimage changed')
        require(raw[at:at+len(expected)]==expected and not any(raw[at+len(expected):at+33]),'Name field identity')
        require(raw[at-5:at-1]==b'\xff'*4 and raw[at+47:at+51]==b'\xff'*4,'Preset record boundary')
        require(raw[at-1] in (4,5),'Grendizer preset index')
        changed[c][at:at+len(expected)]=replacement
        rows.append(dict(chunk=c,offset=at,source=SOURCE_NAME,text=ENGLISH,
                         record_sha256=sha(raw[at-1:at+51]),write_bytes=len(expected),
                         squad_index=raw[at-1],member_ids=list(struct.unpack_from('<6H',raw,at+33))))
    # Check every native stage for additional copies in this exact record form.
    found=[]
    for c in range(1,68):
        raw=decode(ns[no[c]:no[c+1]])[0];at=0
        while True:
            at=raw.find(expected,at)
            if at<0:break
            if raw[at-5:at-1]==b'\xff'*4 and raw[at+47:at+51]==b'\xff'*4 and not any(raw[at+len(expected):at+33]):found.append((c,at))
            at+=len(expected)
    require(tuple(found)==BINDINGS,'Scripted Grendizer inventory changed')
    for c,out in changed.items():
        restored=bytearray(out)
        for row in rows:
            if row['chunk']==c:
                at=row['offset'];restored[at:at+len(expected)]=expected
                require(text(out[at:at+33].split(b'\0')[0])==ENGLISH,'Name readback')
        require(restored==before[c],'Changed bytes outside name field')
    newstage,newhb,sizes=repack(stage,hb,{c:bytes(r) for c,r in changed.items()})
    newoffs=struct.unpack_from('<69I',newhb,TABLE)
    for c in range(68):
        old=stage[offs[c]:offs[c+1]];new=newstage[newoffs[c]:newoffs[c+1]]
        require(decode(new)[0]==changed[c] if c in changed else old==new,'Stage readback '+str(c))
    restored=bytearray(newhb);restored[TABLE:TABLE+276]=hb[TABLE:TABLE+276]
    require(restored==hb,'HB change outside stage table')
    return {STAGE:newstage,HB:newhb},dict(fields=rows,chunks=sorted(changed),
        unchanged_gameplay_and_dialogue=True,all_68_chunks_verified=True,
        stage_sha256=sha(newstage),hb_sha256=sha(newhb),emulator='pending')
