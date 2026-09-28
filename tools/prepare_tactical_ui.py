"""Inventory the small tactical UI fields and their fixed-byte layout contract."""
import argparse,json,struct,shutil
from sp_disc import ROOT,Disc,SOURCE,EXE,sha,file_sha,require
from library_text import CHARS,text

BASE=0xff680
FOLDER=ROOT/'work/ui/tactical'
BINDINGS=FOLDER/'native-inventory.json'
DRAFT=ROOT/'work/translation/en/tactical_ui_draft.json'
PREVIOUS=ROOT/'work/output/SRW Z Special Disc English v0.2.19.iso'
SPECS=[
    (0x3b3678,8,'Squad','Sq','squad naming suffix'),
    (0x3b3688,8,'Squad','Sq','squad naming suffix'),
    (0x3b36e0,8,'Squad','Sq','squad naming suffix'),
    (0x3beb88,8,'Squads','Sq','deployment count suffix'),
    (0x3c0380,8,'Squads','Sq','tactical ally/enemy count suffix'),
    (0x3b8738,8,'Morale','Will','compact footer stat label'),
    (0x3bfdd0,24,'[--/---]','［－－／－－－］','no-unit movement template'),
    (0x3bfdf0,24,'[  /---]','［　　／－－－］','movement template: number at bytes 2..5, slash at 6..7'),
    (0x3bfe08,8,']','］','movement closing bracket'),
    (0x3bfe10,8,'---','－－－','three terrain cells, two bytes each'),
    (0x39d518,8,'Air','A','two-byte terrain cell'),
    (0x39d520,8,'Ground','G','two-byte terrain cell'),
    (0x39d528,8,'Sea / Water','S','two-byte terrain cell'),
]
COORDS=[
    (0x3a2a2c,0x2406ff44,0x2406ff20,'Forces label: x132 to x96; room for three-digit count'),
    (0x3a2b90,0x2405ffa1,0x2405ffa3,'Force-count slash: x225 to x227'),
    (0x3a2ce4,0x2405ffc8,0x2405ffe0,'Enemy count suffix: x264 to x288'),
    (0x3a2d00,0x2405ffc8,0x2405ffe0,'Enemy count right edge: x264 to x288'),
    (0x34fc30,0x26060054,0x26060018,'Move label: x84 to x24'),
    (0x350064,0x26050080,0x2605004c,'Movement value: x128 to x76'),
    (0x34fc54,0x26060110,0x26060118,'Pilot label: x272 to x280; clear GndOnly movement'),
]
SCREENSHOTS=[
    ('a0f60e68-6596-4621-8476-c2295610fcbd','tactical-situation'),
    ('61919b10-c85c-4d0a-b171-789d4beb321e','formation'),
    ('0446c0bd-f4c3-4ec5-97e0-032f7c21a13e','system-help'),
    ('6ee049d3-e743-4e52-9c0d-7c9d181ead2b','allied-unit-list'),
]

def inventory():
    native=Disc(SOURCE).read(EXE);before=Disc(PREVIOUS).read(EXE);entries=[];draft=[]
    for off,cap,full,value,role in SPECS:
        source=native[off:off+cap].split(b'\0')[0].decode('cp932')
        payload=(bytes((0x85,0x40+CHARS.index(ord(value)))) if role=='two-byte terrain cell' else value.encode('cp932'))
        require(len(payload)+1<=cap,'Tactical field exceeds allocation')
        row=dict(id=f'exe/{off:x}',offset=off,capacity=cap,source=source,role=role,
                 native_hex=native[off:off+cap].hex(),prior_hex=before[off:off+cap].hex())
        entries.append(row)
        draft.append(dict(id=row['id'],source=source,full_text=full,text=text(payload),
                          encoded_hex=payload.hex(),role=role))
    coordinates=[]
    for va,old,new,note in COORDS:
        require(struct.unpack_from('<I',native,va-BASE)[0]==old and
                struct.unpack_from('<I',before,va-BASE)[0]==old,'Coordinate source drift')
        coordinates.append(dict(va=va,offset=va-BASE,before_word=old,after_word=new,note=note))
    guards=[]
    for lo,hi in ((0x392b00,0x392cd0),(0x3d4800,0x3d4b00)):
        require(native[lo-BASE:hi-BASE]==before[lo-BASE:hi-BASE],'Movement formatter changed')
        guards.append(dict(va=lo,offset=lo-BASE,size=hi-lo,sha256=sha(native[lo-BASE:hi-BASE])))
    inv=dict(schema_version=1,baseline='0.2.19',entries=entries,coordinates=coordinates,
             formatter_guards=guards,terrain_scratch_bytes=8,number_bytes=4,
             prefix_bytes=8,unit_footer_movement_buffer_bytes=24,smallest_movement_buffer_bytes=18,
             native_exe_sha256=sha(native),prior_exe_sha256=sha(before))
    return inv,draft

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    inv,rows=inventory()
    print(json.dumps(dict(entries=rows,coordinates=inv['coordinates']),ensure_ascii=True,indent=2))
    if not a.write:print('DRY RUN: no inventory, draft or screenshots written');return
    FOLDER.mkdir(parents=True,exist_ok=True)
    BINDINGS.write_text(json.dumps(inv,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    DRAFT.write_text(json.dumps(dict(bindings_sha256=file_sha(BINDINGS),entries=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    for key,label in SCREENSHOTS:
        src=ROOT.__class__(__import__('tempfile').gettempdir())/f'codex-clipboard-{key}.png'
        dst=FOLDER/f'user-{label}.png'
        if dst.exists():require(file_sha(dst)==file_sha(src),'Screenshot name already in use')
        else:shutil.copyfile(src,dst)

if __name__=='__main__':main()
