"""Translate only the Scenario Chart overlay; preserve every story chunk.

SP structure corroborated against dyzz/srwz-zh at
f6673b1edf697df3501fba3889e930815fd1b001. English prose is authored locally.
Long synopses use the loaded English pool instead of their Japanese byte slots.
"""
import argparse
import json
import re
import struct
from collections import defaultdict
from library_text import *
from glossary_terms import canonicalize,PATH as GLOSSARY_PATH
from battle_terms import canonicalize as scoped_names, PATH as SPELLING_PATH
from menu_encoding import menu_encode
from reuse_compdata import pointers,cstring,ABASE,POOL_BASE
from inspect_english_runtime import CAVE,CAVE_FILE

MEMBER='DATA/STAGE.BIN'
BASE=0x8045f0
SOURCE_SHA='a9ceff1a5dbdfff457b34686eed6cd2453b5d2e2c1c89a24a1006a0edf8d4ae7'
KEYS=[(0x17eb0,7,[97568,97584]),(0x17eb8,7,[97572,97588]),
      (0x17ec0,15,[97576,97592]),(0x17ed0,39,[97580]),(0x17f00,25,[97596])]


def wrap(value):
    # Use the donor font's unscaled coordinates and the wider bold advance.
    # 560 units is conservative against the upstream 29-cell panel estimate
    # (696 at the font's native 24-unit cell size). Eleven rows is its measured
    # visible limit. Runtime acceptance remains pending.
    donor=(ROOT/'work/cache/english-runtime/english.elf').read_bytes()
    widths=donor[CAVE_FILE+0x78b960-CAVE:CAVE_FILE+0x78b960-CAVE+69]
    def px(s):return sum(widths[CHARS.index(ord(c))]+2 if ord(c)in CHARS else 13 if c==' 'else 24 for c in s)
    lines=[];line=''
    for word in canonicalize(value).split():
        candidate=(line+' '+word).strip()
        if line and px(candidate)>560:lines.append(line);line=word
        else:line=candidate
        require(px(line)<=560,'Chart word exceeds line width')
    if line:lines.append(line)
    require(len(lines)<=11,'Chart synopsis needs '+str(len(lines))+' rows: '+value[:60])
    return '\n'.join(lines),[px(line)for line in lines]


def build(pool):
    disc=Disc(SOURCE);archive=disc.read(MEMBER);native,_=decode(archive)
    require(sha(native)==SOURCE_SHA and len(native)==98192,'Chart overlay identity')
    slot=struct.unpack_from('<I',disc.read('HEDBDY/HB.BIN'),0x5174)[0]
    require(slot==44016,'Chart compressed slot drift')
    cfg=json.loads((ROOT/'work/translation/en/chart_overrides.json').read_text(encoding='utf-8'))
    require(len(cfg['synopses'])==21 and len(cfg['keys'])==5,'Chart authored inventory')
    out=bytearray(native);pool=bytearray(pool);entries=[];ranges=[];name_changes=[]
    def named(value, source, id_):
        result=scoped_names(value,text(source),literal_breaks=False)
        if result!=value:
            name_changes.append(dict(id=id_,source_sha256=sha(source),before=value,after=result))
        return result
    # Reuse main-game titles by pointed-to source bytes, never chart row id.
    a=decode((ORIGINAL/'DATA_COMPDATA.BN').read_bytes())[0]
    c=decode(Disc(DONOR,True).read('DATA/COMPDATA.BN'))[0];answers=defaultdict(set)
    for site,at in pointers(a,ABASE):
        if not 0x5e150<=site<0x60790:continue
        new=struct.unpack_from('<I',c,site)[0]-ABASE
        src=cstring(a,at);en=cstring(c,new)if 0<=new<len(c)else None
        if src and en and not japanese(en[1]):answers[sha(src[0])].add(en[1])
    local=json.loads((ROOT/'work/translation/en/compdata.json').read_text(encoding='utf-8'))
    for row in local:answers[row['source_sha256']].add(row['text'])
    def patch(at,size,value,id_):
        source=native[at:at+size];raw=source.split(b'\0')[0]
        require(len(raw)<size and not any(source[len(raw):]),'Chart field ownership '+id_)
        value=named(canonicalize(value),raw,id_);encoded=menu_encode(value)
        require(not japanese(value) and len(encoded)<size,'Chart field overflow '+id_+': '+value)
        out[at:at+size]=encoded+bytes(size-len(encoded));ranges.append((at,at+size))
        require(text(out[at:at+size].split(b'\0')[0])==value,'Chart fixed readback')
        entries.append(dict(id=id_,offset=at,capacity=size,source_sha256=sha(source),text=value))
    for table_index,(kind,at,count)in enumerate((('sp',0x7510,21),('z',0x14b20,110))):
        require(struct.unpack_from('<I',native,0x17c90+4*table_index)[0]==BASE+at,'Chart node table pointer')
        require(struct.unpack_from('<h',native,at+count*112+0x50)[0]==70,'Chart node terminator')
        for i in range(count):
            pos=at+i*112;label=text(native[pos:pos+16].split(b'\0')[0]);id_=kind+'/'+str(i)
            match=re.fullmatch('第([0-9]+)話',label)
            require(match or label in ('最終話',''),'Unknown chart episode label')
            if label:patch(pos,16,'Ep. '+match[1]if match else 'Final','label/'+id_)
            raw=native[pos+16:pos+80].split(b'\0')[0]
            if id_ in cfg['title_overrides']:value=cfg['title_overrides'][id_]
            elif not japanese(text(raw)):value=text(raw)
            else:
                options={canonicalize(x)for x in answers[sha(raw)]}
                require(len(options)==1,'Missing/ambiguous chart title '+id_+': '+str(options));value=next(iter(options))
            patch(pos+16,64,value,'title/'+id_)
    for i,(at,size,sites)in enumerate(KEYS):
        found=[p for p in range(0,len(native)-3,4)if struct.unpack_from('<I',native,p)[0]==BASE+at]
        require(found==sites,'Chart key pointer inventory')
        patch(at,size,cfg['keys'][i],'key/'+str(i))
    for i,value in enumerate(cfg['synopses']):
        site=0x74b4+i*4;at=struct.unpack_from('<I',native,site)[0]-BASE
        end=native.index(0,at)+1;source=native[at:end]
        # Module text is 0x90..0x3650. R5900 register instructions there can
        # resemble pointers numerically; only the module data holds pointers.
        require(struct.unpack_from('<I',native,0x1c)[0]==0x35c0 and struct.unpack_from('<I',native,0x24)[0]==0x80,'Chart code span')
        found=[p for p in range(0x3650,len(native)-3,4)if at<=struct.unpack_from('<I',native,p)[0]-BASE<end]
        require(found==[site],'Chart synopsis has unknown/aliased references')
        value,widths=wrap(named(value,source[:-1],'synopsis/'+str(i)));encoded=menu_encode(value)+b'\0'
        require(not japanese(value),'Untranslated chart synopsis')
        address=POOL_BASE+len(pool);pool.extend(encoded);pool.extend(bytes((-len(pool))%4))
        struct.pack_into('<I',out,site,address);out[at:end]=bytes(end-at)
        ranges.extend([(site,site+4),(at,end)])
        entries.append(dict(id='synopsis/'+str(i),offset=at,capacity=end-at,source_sha256=sha(source),text=value,
            relocated_address=address,pointer_sites=[site],line_widths=widths))
    main=json.loads((ROOT/'work/translation/en/chart_main_reviewed.json').read_text(encoding='utf-8'))
    require(main['source_sha256']==SOURCE_SHA and main['reviewed_ids']==list(range(110)),'Main chart review incomplete')
    require(main['glossary_sha256']==sha(GLOSSARY_PATH.read_bytes()),'Refresh main chart glossary pass')
    for name,digest in main['review_inputs'].items():
        require(sha((ROOT/'work/translation/en'/name).read_bytes())==digest,'Stale main chart meaning review '+name)
    require([r['id']for r in main['entries']]==list(range(110)),'Main chart inventory')
    for row in main['entries']:
        i=row['id'];site=0x14864+i*4;at=struct.unpack_from('<I',native,site)[0]-BASE
        require(0x7eb0<=at<0x14860,'Main chart source bounds')
        end=native.index(0,at)+1;source=native[at:end]
        require((site,at,end-at,sha(source))==(row['pointer_site'],row['offset'],row['capacity'],row['source_sha256']),
                'Main chart source binding '+str(i))
        value=canonicalize(row['text'],'chart_main',i)
        require(row['meaning_reviewed'] and value==row['text'],'Main chart editorial gate')
        value=named(value,source[:-1],'main-synopsis/'+str(i))
        value,widths=wrap(value);encoded=menu_encode(value)+b'\0'
        require(not japanese(value),'Untranslated main chart synopsis')
        address=POOL_BASE+len(pool);pool.extend(encoded);pool.extend(bytes((-len(pool))%4))
        struct.pack_into('<I',out,site,address);ranges.append((site,site+4))
        # Retain native strings: packed non-text words before 0x4a60 can look
        # like interior pointers. Only the typed synopsis pointer table changes.
        require(out[at:end]==source,'Native main chart fallback bytes changed')
        entries.append(dict(id='main-synopsis/'+str(i),offset=at,capacity=end-at,source_sha256=sha(source),text=value,
            relocated_address=address,pointer_sites=[site],line_widths=widths,native_source_preserved=True))
    protected=bytearray(out)
    for lo,hi in ranges:protected[lo:hi]=native[lo:hi]
    require(protected==native,'Non-text chart bytes changed')
    packed=banlz.compress_record(bytes(out),flags=banlz.parse_header(archive)[1])
    if len(packed)>slot:packed=banlz.compress_record_optimal(bytes(out),flags=banlz.parse_header(archive)[1])
    require(len(packed)<=slot,'Chart compressed slot overflow')
    require(decode(packed)[0]==out,'Chart compression readback')
    result=packed+bytes(slot-len(packed))+archive[slot:]
    require(result[slot:]==archive[slot:] and len(result)==len(archive),'Story chunks changed')
    report=dict(titles=131,episode_labels=128,synopses=131,sp_synopses=21,main_synopses=110,key_hints=5,entries=entries,
        source_sha256=SOURCE_SHA,compressed_bytes=len(packed),slot_bytes=slot,
        spelling_sha256=sha(SPELLING_PATH.read_bytes()),name_changes=name_changes,
        upstream_panel_estimate_native_cells=29,line_limit_font_units=560,row_limit=11,
        story_chunks_1_through_67_unchanged=True,nontext_chart_bytes_unchanged=True,
        decoded_buffer_size_unchanged=True,write_ranges=ranges)
    return result,bytes(pool),report


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    _,_,report=build(b'')
    # Standalone compilation has no assembled pool prefix. Export text bindings
    # without provisional addresses; the build report carries final addresses.
    for row in report['entries']:row.pop('relocated_address',None)
    print(json.dumps({k:v for k,v in report.items()if k not in ('entries','write_ranges')},indent=2))
    print(json.dumps([r for r in report['entries']if r['id']in ('synopsis/0','main-synopsis/0','main-synopsis/109')],indent=2))
    if args.write:
        (ROOT/'work/translation/en/chart_bound.json').write_text(json.dumps(report,indent=2)+'\n')
    else:print('DRY RUN: no files written')


if __name__=='__main__':main()
