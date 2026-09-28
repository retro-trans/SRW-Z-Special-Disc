"""Independent finished-disc checks for deployment text, roster ownership and art."""
import json,struct
import numpy as np
from sp_disc import ROOT,Disc,SOURCE,decode,sha,file_sha,require
from library_text import text
from glossary_terms import canonicalize
from menu_encoding import menu_encode

def protect_stage(current,native,include_conditions=False):
    lo,hi=173296,189648
    if include_conditions:
        from stage_ui_guard import check
        check(current,True)
    else:
        require(len(current)==len(native) and current[44016:lo]==native[44016:lo] and current[hi:]==native[hi:],
                'Unexpected story archive change')
    old=decode(native[lo:hi])[0];new,used=decode(current[lo:hi]);copy=bytearray(new)
    require(len(new)==len(old)==42256 and not any(current[lo+used:hi]),'Tournament chunk length/padding')
    sites=[base+i*32+28 for base,count in ((0x3fa0,12),(0x4140,3),(0x41c0,12)) for i in range(count)]
    for p in sites:copy[p:p+4]=old[p:p+4]
    if not include_conditions:require(copy==old,'Tournament dialogue or gameplay data changed')
    return old,new,sites

def audit(disc,exe,loaded,report,include_conditions=False):
    folder=ROOT/'work/translation/en';cfg=json.loads((folder/'deployment_ui.json').read_text(encoding='utf8'))
    require(file_sha(folder/'deployment_ui.json')==report['target_sha256'],'Deployment target drift')
    review=json.loads((folder/'deployment_ui_review.json').read_text(encoding='utf8'))
    require(file_sha(folder/'deployment_ui_review.json')==report['review_sha256']==cfg['review_sha256'],
            'Deployment review binding')
    approved={r['id']:canonicalize(r['text']) for r in review['entries']}
    require(len(approved)==113 and len(report['entries'])==108,'Deployment coverage')
    clean=Disc(SOURCE);co=decode(disc.read('DATA/COMPDATA.BN'))[0];native_co=decode(clean.read('DATA/COMPDATA.BN'))[0]
    restored=bytearray(co);old,st,sites=protect_stage(disc.read('DATA/STAGE.BIN'),clean.read('DATA/STAGE.BIN'),include_conditions)
    stage_sites=[];menu_count=0
    for row in report['entries']:
        key=row['id'];require(row['text']==approved[key],'Deployment text differs from reviewed meaning')
        address=row['relocated_address'];at=loaded(address);encoded=menu_encode(row['text'])+b'\0'
        require(loaded(address+len(encoded)-1)==at+len(encoded)-1 and exe[at:at+len(encoded)]==encoded,
                'Deployment English pool readback')
        is_menu=key.startswith('menu/');owner=co if is_menu else st;source=native_co if is_menu else old
        require(sha(source[row['offset']:].split(b'\0')[0])==row['source_sha256'],'Deployment native binding')
        for p in row['pointer_sites']:
            require(struct.unpack_from('<I',owner,p)[0]==address,'Deployment UI pointer readback')
            if is_menu:
                require(0x6a000<=p<0x6a238,'Deployment menu-table scope')
                restored[p:p+4]=native_co[p:p+4]
            else:stage_sites.append(p)
        if is_menu:menu_count+=1
    require(menu_count==96 and sorted(stage_sites)==sorted(sites),'Deployment typed pointer coverage')
    require(sha(restored)==report['comp_before_sha256'],'Other translated COMPDATA bytes changed')
    require(text(exe[0x3b1100:].split(b'\0')[0])==approved['heading']=='Squads','Squad heading readback')
    for row in cfg['deferred']:
        offset=int(row['id'].split('/')[1],16)
        for p in range(0x6a000,0x6a238,4):
            if struct.unpack_from('<I',native_co,p)[0]==0x764f80+offset:
                require(co[p:p+4]==native_co[p:p+4],'Deferred dynamic fragment changed')
    art=disc.read('KURODATA/KVMDATA.BIN');before=clean.read('KURODATA/KVMDATA.BIN');start=0x38fc0+64;end=start+32768
    require(len(art)==len(before) and art[:start]==before[:start] and art[end:]==before[end:],
            'Squad palettes, headers or other sheets changed')
    def pixels(raw):
        b=np.frombuffer(raw[start:end],np.uint8)
        a=np.empty(65536,np.uint8);a[0::2]=b&15;a[1::2]=b>>4;return a.reshape(256,256)
    orig=pixels(before);current=pixels(art);mask=np.zeros((256,256),bool)
    require(len(report['graphics'])==4,'Squad graphic coverage')
    for row in report['graphics']:
        key=row['id'];x,y,r,b=cfg['boxes'][key];tile=current[y:b,x:r];mask[y:b,x:r]=True
        require(row['text']==approved[key] and row['box']==cfg['boxes'][key], 'Squad graphic review/geometry')
        require(sha(tile.tobytes())==cfg['layouts'][key]['pixel_sha256']==row['pixel_sha256'],'Squad final pixels')
        yy,xx=np.nonzero(tile);require(len(xx)>0 and xx.min()>0 and yy.min()>0 and xx.max()<r-x-1 and yy.max()<b-y-1,
                                      'Squad graphic clipped')
    require(np.array_equal(current[~mask],orig[~mask]),'Adjacent squad sprites changed')
    return dict(menu_entries_read_back=96,tournament_names_read_back=12,tournament_pointer_words=27,
                graphic_tiles_read_back=4,heading='Squads',deferred_dynamic_fragments=5,
                story_dialogue_and_gameplay_unchanged=True,other_story_chunks_compressed_identical=28 if include_conditions else 66,
                palette_and_other_sprites_identical=True)
