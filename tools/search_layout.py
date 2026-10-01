"""Install measured Search header and three-line ability descriptions."""
import json,struct
from sp_disc import ROOT,SOURCE,EXE,Disc,decode,banlz,sha,require
from library_text import text
from menu_encoding import menu_encode
from reuse_compdata import BBASE
from squad_followup import loaded
from save_summary_text import width
MEMBER='DATA/COMPDATA.BN'
SPEC=ROOT/'work/translation/en/search_layout.json'

def build(disc):
    cfg=json.loads(SPEC.read_text(encoding='utf-8'))
    originals={EXE:disc.read(EXE),MEMBER:disc.read(MEMBER)}
    for name,blob in originals.items():require(sha(blob)==cfg['source_members'][name],'Search base drift '+name)
    old={'exe':originals[EXE],'comp':decode(originals[MEMBER])[0]}
    out={k:bytearray(v) for k,v in old.items()};spans={'exe':[],'comp':[]}
    for row in cfg['rows']:
        kind,at,cap=row['kind'],row['offset'],row['capacity'];before=bytes.fromhex(row['before_hex'])
        require(old[kind][at:at+cap]==before and text(before[:-1])==row['before'],'Search field preimage')
        p=row['pointer']
        if p is not None:
            require(struct.unpack_from('<I',old['comp'],p)[0]==row['address'],'Search pointer preimage')
            require(at==(loaded(old['exe'],row['address']) if kind=='exe' else row['address']-BBASE),'Search field address')
        encoded=menu_encode(row['text']);require(len(encoded)<cap,'Search slot overflow')
        require(not any(lo<at+cap and at<hi for lo,hi in spans[kind]),'Overlapping Search slots')
        out[kind][at:at+cap]=encoded+bytes(cap-len(encoded));spans[kind].append((at,at+cap))
        require(text(out[kind][at:at+cap].split(b'\0')[0])==row['text'],'Search text readback')
    for kind,blob in out.items():
        restored=bytearray(blob)
        for lo,hi in spans[kind]:restored[lo:hi]=old[kind][lo:hi]
        require(restored==old[kind],'Changes outside Search text fields')
    for row in cfg['ability_descriptions_checked']:
        address=struct.unpack_from('<I',out['comp'],row['pointer'])[0]
        value=(out['comp'][address-BBASE:] if BBASE<=address<BBASE+len(out['comp'])
               else out['exe'][loaded(out['exe'],address):]).split(b'\0')[0]
        value=text(value)
        require(value==row['text'] and len(value.splitlines())<=3 and max(map(width,value.splitlines()))<=510,'Ability panel overflow')
    require(len(cfg['ability_descriptions_checked'])==57 and len(cfg['rows'])==29,'Search inventory drift')
    packed=banlz.compress_record(bytes(out['comp']),flags=banlz.parse_header(originals[MEMBER])[1])
    packed+=bytes((-len(packed))%16)
    require(decode(packed)[0]==out['comp'],'Search compression readback')
    return {EXE:bytes(out['exe']),MEMBER:packed},dict(fields=cfg['rows'],descriptions_checked=57,
        description_changes=26,header_changes=3,max_rows=3,max_width=510,
        executable_code_and_pointers_unchanged=True,all_other_decoded_bytes_identical=True,
        source_hashes=cfg['source_members'],emulator='pending')
