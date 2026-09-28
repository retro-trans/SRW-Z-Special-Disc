"""Independently inspect compact terrain cells and preserve every other byte."""
import json,struct
from sp_disc import ROOT,Disc,SOURCE,EXE,sha,file_sha,require
from inspect_english_runtime import CAVE,CAVE_FILE
from port_menu_runtime import NEW_FILE

def glyph(exe,code):
    """Expand the installed table's two 12-pixel 2bpp halves to a 24x24 cell."""
    table=NEW_FILE+0x78be80-CAVE;atlas=NEW_FILE+0x78a5b0-CAVE
    rows=[struct.unpack_from('<HBBHH',exe,table+i*8) for i in range(23)]
    found=[r for r in rows if r[0]==code];require(len(found)==1,'Missing/ambiguous terrain glyph')
    _,count,y0,left,right=found[0];require(y0+count<=24,'Glyph rows outside cell')
    pixels=bytearray(24*24)
    for side,offset in enumerate((left,right)):
        for y in range(count):
            bits=int.from_bytes(exe[atlas+offset+3*y:atlas+offset+3*y+3],'big')
            for x in range(12):pixels[(y+y0)*24+side*12+x]=((bits>>(22-2*x))&3)*85
    return bytes(pixels)

def check(exe,prior,inv):
    native=Disc(SOURCE).read(EXE);donor=(ROOT/'work/cache/english-runtime/english.elf').read_bytes()
    require(sha(prior)==inv['prior_exe_sha256'] and sha(donor)==inv['donor_elf_sha256'], 'Terrain donor/baseline binding')
    original=bytes.fromhex('8bf3814097a481408a43814089460000')
    expected=bytes.fromhex('85dc85db85dd85db85de85db85df0000')
    hits=[];pos=0
    while True:
        pos=native.find(original,pos)
        if pos<0:break
        hits.append(pos);pos+=len(original)
    require(len(hits)==11 and hits==[r['offset'] for r in inv['rows']],'Terrain category coverage')
    restored=bytearray(exe)
    for row in inv['rows']:
        p=row['offset']
        require(exe[p:p+16]==expected and native[p:p+16]==original,'Terrain row byte readback')
        require(prior[p:p+16]==bytes.fromhex(row['before_hex']),'Terrain prior field identity')
        restored[p:p+16]=prior[p:p+16]
    require(restored==prior,'Unexpected change outside terrain rows')
    for g in inv['runtime_guards']:
        p=g['offset'];require(sha(exe[p:p+g['bytes']])==g['sha256'],'Existing glyph renderer/art changed')
    # All five terrain images remain exact copies of the donor's artwork.
    start=NEW_FILE+0x78bcd0-CAVE;source=CAVE_FILE+0x78bcd0-CAVE
    require(exe[start:start+420]==donor[source:source+420],'Terrain pixels differ from SRW Z')
    require(not any(glyph(exe,0x85db)),'Full-width spacer contains visible ink')
    images=[]
    for code,label in zip(range(0x85dc,0x85e0),('AIR','GND','SEA','SPC')):
        pixels=glyph(exe,code);ink=[(i%24,i//24) for i,v in enumerate(pixels) if v]
        require(ink and min(x for x,y in ink)>0 and max(x for x,y in ink)<=20,'Micro label crowds the following rank')
        require(min(y for x,y in ink)>=8 and max(y for x,y in ink)<=21,'Micro label vertical bounds')
        images.append(dict(label=label,code=f'{code:04x}',pixel_sha256=sha(pixels),
                           ink_bbox=[min(x for x,y in ink),min(y for x,y in ink),max(x for x,y in ink)+1,max(y for x,y in ink)+1]))
    # Preserve seven full-width cells, with rating overlays in the blank cells.
    # Native style/scaling determines pixel pitch; no English word spaces occur.
    codes=struct.unpack('>7H',expected[:14])
    require(codes==(0x85dc,0x85db,0x85dd,0x85db,0x85de,0x85db,0x85df),'Terrain cell sequence')
    require(all(c>0x85c9 for c in codes),'A terrain cell entered the variable-width Latin range')
    return dict(rows_read_back=11,labels_per_row=4,full_width_blanks_per_row=3,
                native_cell_positions_preserved=True,ratings_and_draw_coordinates_unchanged=True,
                donor_art_byte_identical=True,images=images,blank_glyph_empty=True,
                only_changed_spans=11,all_other_exe_bytes_identical_to='0.2.20',runtime='pending by user choice')

def audit(disc,exe,report):
    bindings=ROOT/'work/ui/terrain-rows/native-inventory.json'
    draft=ROOT/'work/translation/en/terrain_rows_draft.json';review=ROOT/'work/translation/en/terrain_rows_review.json'
    require(file_sha(bindings)==report['bindings_sha256'] and file_sha(draft)==report['draft_sha256'] and
            file_sha(review)==report['review_sha256'],'Terrain receipt bindings')
    inv=json.loads(bindings.read_text(encoding='utf8'));approved=json.loads(review.read_text(encoding='utf8'))
    require(approved['entries_examined']==approved['entries_in_slice']==4 and
            [r['text'] for r in approved['entries']]==['AIR','GND','SEA','SPC'] and
            all(r['verdict']=='pass' for r in approved['entries']),'Terrain meaning review')
    require(report['spans']==inv['rows'] and report['rows']==11,'Terrain report inventory')
    previous=Disc(ROOT/'work/output/SRW Z Special Disc English v0.2.20.iso')
    result=check(exe,previous.read(EXE),inv)
    old=json.loads((ROOT/'work/output/SRW Z Special Disc English v0.2.20.json').read_text())
    for name in old['members']:
        if name!=EXE:require(disc.read(name)==previous.read(name),'Other archive changed: '+name)
    require(disc.read('DATA/VT1.BIN')==previous.read('DATA/VT1.BIN'),'Unrelated texture changes')
    return dict(result,all_other_translation_archives_identical=True,texture_archive_identical=True)
