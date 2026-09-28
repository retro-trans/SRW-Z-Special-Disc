"""Read tactical fields from the finished disc and model native byte assembly."""
import json,struct
from sp_disc import ROOT,Disc,SOURCE,EXE,decode,sha,file_sha,require
from library_text import text,CHARS,japanese
from save_summary_text import width
from prepare_tactical_ui import BASE,BINDINGS,DRAFT,PREVIOUS

def string(exe,at):return exe[at:].split(b'\0')[0]

def encoded_width(raw):
    """Native fullwidth cells stay 24; private donor glyphs use Latin advances."""
    total=0;i=0
    while i<len(raw):
        b=raw[i]
        if b==0x85:
            total+=width(text(raw[i:i+2]));i+=2
        elif 0x81<=b<=0x9f or 0xe0<=b<=0xfc:total+=24;i+=2
        else:total+=width(chr(b));i+=1
    return total

def movement(exe,number=None,terrain_type=0,mask=0):
    """Model 392b00/392bb0, including the two-byte stores and byte-8 NUL."""
    if number is None:return string(exe,0x3bfdd0)
    require(0<=number<100,'Movement uses a native two-digit field')
    digits=[]
    for c in str(number):
        ptr=struct.unpack_from('<I',exe,0x49df00-BASE+int(c)*4)[0]
        digits.append(string(exe,ptr-BASE))
    numeric=(string(exe,0x4c0eb0-BASE) if number<10 else b'')+b''.join(digits)
    require(len(numeric)==4,'Native two-digit string size changed')
    temp=bytearray(string(exe,0x3bfe10)+b'\0')
    if terrain_type:
        temp=bytearray(string(exe,{1:0x3bfe18,2:0x3bfe20,3:0x3bfe28}[terrain_type])+b'\0')
    else:
        for i,off in enumerate((0x39d518,0x39d520,0x39d528)):
            if mask&(1<<i):temp[i*2:i*2+2]=exe[off:off+2]
    require(len(temp)<=8 and temp[-1]==0,'Native terrain scratch buffer overflow')
    result=bytearray(string(exe,0x3bfdf0)+b'\0')
    result[2:6]=numeric;result[8]=0
    result=result.split(b'\0')[0]+temp.split(b'\0')[0]+string(exe,0x3bfe08)
    require(len(result)+1<=18,'Smallest native movement field overflow')
    return bytes(result)

def layout_checks(exe):
    maximum=0;cases=0
    for number in range(100):
        for kind,mask in [(0,m) for m in range(8)]+[(k,0) for k in (1,2,3)]:
            raw=movement(exe,number,kind,mask);actual=text(raw)
            require(actual.startswith('[') and actual.endswith(']') and '/' in actual,'Movement bracket/slash corruption')
            require(actual[1:3]==str(number).rjust(2),'Movement numeric overwrite')
            expected={1:'AirOnly',2:'GndOnly',3:'AirSea'}.get(kind,''.join(c if mask&(1<<i) else '-' for i,c in enumerate('AGS')))
            require(actual[4:-1]==expected and not japanese(actual),'Terrain cell overwrite or untranslated glyph')
            maximum=max(maximum,encoded_width(raw));cases+=1
    require(text(movement(exe))=='[--/---]','No-unit movement template')
    maximum=max(maximum,encoded_width(movement(exe)));cases+=1
    require(24+width('Move')<76 and 76+maximum<280,'Movement/footer label overlap')
    require(280+width('Pilot')<338 and 338+width('Hyzaemon')<464,'Screenshot pilot-name overlap')
    require(464+width('Lv')<516-2*12,'Level overlap')
    require(536+width('Will')<610-3*12,'Will/three-digit value overlap')
    # Native numeric draw uses 12-unit cells; cover up to three digits per side.
    require(96+width('Forces')<204-3*12,'Forces/ally count overlap')
    require(204+width('Sq')<227 and 227+24<288-3*12 and 288+width('Sq')<320,'Count separator/panel overflow')
    return dict(movement_cases=cases,max_movement_width=maximum,movement_value_x=76,
                movement_label_x=24,pilot_label_x=280,movement_minimum_buffer_bytes=18,
                movement_scratch_bytes=8,force_label_x=96,force_count_right_edges=[204,288],
                force_suffix_x=[204,288],force_slash_x=227,force_digits_checked=3,
                status_stat='Will',emulator='pending by user choice')

def selector_checks(disc,exe,loaded):
    co=decode(disc.read('DATA/COMPDATA.BN'))[0];native=Disc(SOURCE).read(EXE)
    # These native routines read pointer arrays. Japanese source strings are
    # deliberately retained; the selected pointers must resolve to English.
    routes=[
        ('formation',0x363d20,0x363d28,0x6a170,3,0x363d20,0x363e0c),
        ('diagram',0x363f24,0x363f34,0x6a180,3,0x363f24,0x363f58),
        ('settings-help',0x3c0e9c,0x3c0ea4,0x6a0e0,36,0x3c0e98,0x3c0f10),
        ('unit-squad-heading',0x34dd6c,0x34dd80,0x6a1d0,15,0x34dd6c,0x34ddd8),
        ('group-formation-hint',0x365b78,0x365b80,0x6a198,1,0x365b78,0x365b8c),
    ]
    approved={r['id']:r['text'] for r in json.loads((ROOT/'work/translation/en/deployment_ui.json').read_text(encoding='utf8'))['entries']}
    source=decode(Disc(SOURCE).read('DATA/COMPDATA.BN'))[0];results=[]
    for category,hi,lo,offset,count,start,end in routes:
        require(exe[start-BASE:end-BASE]==native[start-BASE:end-BASE],'UI selector instructions changed')
        h,l=(struct.unpack_from('<I',exe,va-BASE)[0] for va in (hi,lo))
        require(h>>26==15 and l>>26 in (9,35),'UI selector load changed')
        address=((h&65535)<<16)+struct.unpack('<h',struct.pack('<H',l&65535))[0]
        require(address==0x764f80+offset,'UI selector array base')
        selected=[]
        for i in range(count):
            p=offset+4*i;original=struct.unpack_from('<I',source,p)[0]
            if not original:continue
            key=f'menu/{original-0x764f80:x}'
            if original==0x7eeee0:
                require(source[0x89f60]==co[0x89f60]==0 and co[p:p+4]==source[p:p+4], 'Empty settings slot changed')
                continue
            require(key in approved,'UI selector has an unreviewed target')
            ptr=struct.unpack_from('<I',co,p)[0];raw=string(exe,loaded(ptr));actual=text(raw)
            require(actual==approved[key] and not japanese(actual),'UI selector still resolves to Japanese')
            selected.append(dict(index=i,pointer_site=p,id=key,text=actual))
        results.append(dict(category=category,slots=count,selections=selected))
    require(next(r for r in results if r['category']=='settings-help')['selections'][3]['text']
            =='<Play unit music during battle animations.>','Screenshot help routing')
    return results

def audit(disc,exe,loaded,report,later_terrain_spans=()):
    inv=json.loads(BINDINGS.read_text(encoding='utf8'))
    require(file_sha(BINDINGS)==report['bindings_sha256'] and file_sha(DRAFT)==report['draft_sha256'], 'Tactical build input binding')
    review_path=ROOT/'work/translation/en/tactical_ui_review.json'
    review=json.loads(review_path.read_text(encoding='utf8'))
    require(file_sha(review_path)==report['review_sha256'] and review['entries_examined']==13,'Tactical review binding')
    approved={r['id']:r for r in review['entries']};restored=bytearray(exe)
    require(len(report['spans'])==20 and report['fields']==13,'Tactical span coverage')
    for r in report['spans']:
        p=r['offset'];n=r['size'];require(exe[p:p+n].hex()==r['after_hex'],'Tactical final byte readback')
        if r['id'] in approved:
            raw=string(exe,p);a=approved[r['id']]
            require(raw.hex()==a['encoded_hex'] and text(raw)==a['text'],'Tactical reviewed text readback')
        restored[p:p+n]=bytes.fromhex(r['before_hex'])
    previous=Disc(PREVIOUS)
    # A later component may replace rating rows outside this component's fields.
    # The parent must independently validate it before passing its exact spans.
    if later_terrain_spans:
        from terrain_rows import OFFSETS,REPLACEMENT
        require([r['offset'] for r in later_terrain_spans]==list(OFFSETS),'Later terrain scope')
        for r in later_terrain_spans:
            p=r['offset'];require(exe[p:p+16]==REPLACEMENT and r['before_hex']==b'Air Gnd Sea Spc\0'.hex(),'Later terrain preimage')
            restored[p:p+16]=bytes.fromhex(r['before_hex'])
    require(bytes(restored)==previous.read(EXE),'Executable changed outside the 20 tactical spans')
    for g in inv['formatter_guards']:
        require(sha(exe[g['offset']:g['offset']+g['size']])==g['sha256'],'Native formatter changed')
    # Compare every earlier translated member and the texture archive directly.
    old_receipt=json.loads(PREVIOUS.with_suffix('.json').read_text())
    for name in old_receipt['members']:
        if name!=EXE:require(disc.read(name)==previous.read(name),'Unplanned payload change in '+name)
    require(disc.read('DATA/VT1.BIN')==previous.read('DATA/VT1.BIN'),'Earlier texture archive changed')
    return dict(fields_read_back=13,coordinate_words=7,exe_changed_spans=20,later_terrain_spans=len(later_terrain_spans),
                all_other_exe_bytes_identical_to='0.2.19',other_translation_members_identical=True,texture_archive_identical=True,
                layout=layout_checks(exe),selectors=selector_checks(disc,exe,loaded),
                source_strings_retained=True,runtime_validation='pending by user choice')
