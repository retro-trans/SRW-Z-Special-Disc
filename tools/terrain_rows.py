"""Use SRW Z's full-width micro-glyph technique for all terrain rating rows."""
import argparse,json,struct,shutil
from pathlib import Path
from sp_disc import ROOT,Disc,SOURCE,EXE,sha,file_sha,require
from inspect_english_runtime import CAVE,CAVE_FILE
from port_menu_runtime import NEW_FILE

FOLDER=ROOT/'work/ui/terrain-rows'
BINDINGS=FOLDER/'native-inventory.json'
DRAFT=ROOT/'work/translation/en/terrain_rows_draft.json'
REVIEW=ROOT/'work/translation/en/terrain_rows_review.json'
PREVIOUS=ROOT/'work/output/SRW Z Special Disc English v0.2.20.iso'
NATIVE=bytes.fromhex('8bf3814097a481408a43814089460000')
REPLACEMENT=bytes.fromhex('85dc85db85dd85db85de85db85df0000')
OFFSETS=(0x3b0460,0x3b2d48,0x3b2eb8,0x3b3038,0x3b3198,0x3b32f8,
         0x3b3c10,0x3b4258,0x3b5068,0x3c0a58,0x3c0dc8)
LABELS=[('空','Air','AIR',0x85dc),('陸','Ground','GND',0x85dd),
        ('海','Sea','SEA',0x85de),('宇','Space','SPC',0x85df)]
DONOR=ROOT/'work/cache/english-runtime/english.elf'
PEER=Path('E:/Projects/SRW Z/_work/tools')

def inventory():
    native=Disc(SOURCE).read(EXE);prior=Disc(PREVIOUS).read(EXE);donor=DONOR.read_bytes()
    hits=[];pos=0
    while True:
        pos=native.find(NATIVE,pos)
        if pos<0:break
        hits.append(pos);pos+=len(NATIVE)
    require(tuple(hits)==OFFSETS,'Terrain row inventory changed')
    rows=[]
    for p in hits:
        require(prior[p:p+16]==b'Air Gnd Sea Spc\0','Previous terrain row preimage')
        rows.append(dict(id=f'exe/{p:x}',offset=p,capacity=16,native_hex=NATIVE.hex(),
                         before_hex=prior[p:p+16].hex(),after_hex=REPLACEMENT.hex()))
    # These assets and the installed renderer already came from the peer game.
    guards=[]
    for va,size,label in ((0x78bcd0,420,'all five donor terrain micro-images'),
                          (0x78be80,23*8,'private terrain, spirit and blank dispatch table'),
                          (0x78bf40,0x1d0,'installed relocated micro-glyph renderer'),
                          (0x78c110,72,'full-width blank artwork')):
        p=NEW_FILE+va-CAVE
        if va in (0x78bcd0,0x78c110):
            require(prior[p:p+size]==donor[CAVE_FILE+va-CAVE:CAVE_FILE+va-CAVE+size], 'Donor art mismatch')
        guards.append(dict(offset=p,bytes=size,sha256=sha(prior[p:p+size]),label=label))
    for i,(_,_,_,code) in enumerate(LABELS):
        row=struct.unpack_from('<HBBHH',prior,NEW_FILE+0x78be80-CAVE+i*8)
        source_row=struct.unpack_from('<HBBHH',donor,CAVE_FILE+0x78be80-CAVE+i*8)
        require(row[0]==code and row[1:]==source_row[1:],'Private glyph dispatch geometry')
    return dict(schema_version=1,baseline='0.2.20',native_exe_sha256=sha(native),
        prior_exe_sha256=sha(prior),donor_elf_sha256=sha(donor),rows=rows,runtime_guards=guards,
        source_scripts={str(PEER/name):file_sha(PEER/name) for name in ('patch_micro_glyphs.py','fix_terrain_spacing.py')},
        technique='One full-width micro-image per label; full-width blank cells preserve rating positions',
        source_character_cells=7,slot_bytes=16,blank_code='85db',new_code=False,new_art=False)

def prepare():
    inv=json.loads(BINDINGS.read_text(encoding='utf8'));draft=json.loads(DRAFT.read_text(encoding='utf8'))
    review=json.loads(REVIEW.read_text(encoding='utf8'))
    require(inv==inventory(),'Terrain inventory drift')
    require(draft['bindings_sha256']==file_sha(BINDINGS) and review['draft_sha256']==file_sha(DRAFT)
            and review['bindings_sha256']==file_sha(BINDINGS),'Terrain meaning review is stale')
    require(review['entries_examined']==review['entries_in_slice']==4,'Terrain review coverage')
    require([r['id'] for r in review['entries']]==[r['id'] for r in draft['entries']],'Terrain review inventory')
    for r,s in zip(review['entries'],draft['entries']):
        require(r['verdict']=='pass' and r['full_text']==s['full_text'] and r['text']==s['text'], 'Terrain meaning not approved')
    return inv

def compile_component(exe,inv):
    out=bytearray(exe)
    require([r['offset'] for r in inv['rows']]==list(OFFSETS),'Terrain field ownership')
    for g in inv['runtime_guards']:
        p=g['offset'];require(sha(exe[p:p+g['bytes']])==g['sha256'],'Terrain renderer/art drift')
    for row in inv['rows']:
        p=row['offset'];require(exe[p:p+16].hex()==row['before_hex'],'Terrain row conflicts with earlier patch')
        require(row['after_hex']==REPLACEMENT.hex(),'Terrain cell/blank encoding drift')
        out[p:p+16]=REPLACEMENT
    restored=bytearray(out)
    for row in inv['rows']:restored[row['offset']:row['offset']+16]=bytes.fromhex(row['before_hex'])
    require(restored==exe,'Terrain edit escaped its eleven fields')
    return bytes(out),dict(rows=len(inv['rows']),spans=inv['rows'],slot_bytes=16,
        labels=[x[2] for x in LABELS],private_blank_code='85db',runtime_and_art_unchanged=True,
        rating_values_and_positions_unchanged=True,movement_only_labels_unchanged=True)

def build(exe):
    out,report=compile_component(exe,prepare())
    return out,dict(report,bindings_sha256=file_sha(BINDINGS),draft_sha256=file_sha(DRAFT),review_sha256=file_sha(REVIEW))

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--prepare',action='store_true');ap.add_argument('--write',action='store_true');a=ap.parse_args()
    require(not a.write or a.prepare,'Only --prepare writes metadata; executable assembly belongs to build_nonstory')
    if a.prepare:
        inv=inventory();rows=[dict(id=f'terrain/{word}',source=jp,full_text=full,text=word,code=f'{code:04x}') for jp,full,word,code in LABELS]
        print(json.dumps(dict(labels=rows,rows=inv['rows'],technique=inv['technique']),ensure_ascii=True,indent=2))
        if a.write:
            FOLDER.mkdir(parents=True,exist_ok=True)
            BINDINGS.write_text(json.dumps(inv,indent=2)+'\n',encoding='utf8')
            DRAFT.write_text(json.dumps(dict(bindings_sha256=file_sha(BINDINGS),entries=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
            for key,label in [('a5e89882-9f5f-40bd-9f55-bd2607c12dfd','pilot'),('99c458a2-9393-4a3c-89b7-905713203788','mech'),('e44daf84-6d5d-49e2-8ef1-59eabe7d3639','weapon')]:
                src=Path(__import__('tempfile').gettempdir())/f'codex-clipboard-{key}.png';dst=FOLDER/f'user-{label}.png'
                if dst.exists():require(file_sha(dst)==file_sha(src),'Screenshot destination conflict')
                else:shutil.copyfile(src,dst)
        else:print('DRY RUN: no metadata or screenshots written')
    else:
        _,report=build(Disc(PREVIOUS).read(EXE));print(json.dumps(report,indent=2));print('DRY RUN: no executable written')

if __name__=='__main__':main()
