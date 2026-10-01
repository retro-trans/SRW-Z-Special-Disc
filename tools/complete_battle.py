"""Complete source-bound battle captions and Battle Theater speaker names.

Reuses the project's inherited SRW-Z English corpus. Automated source/layout
verification is recorded separately from editorial review and emulator testing.
"""
import json,struct
from collections import defaultdict,Counter
from sp_disc import ROOT,Disc,SOURCE,EXE,sha,file_sha,require
from battle_format import BIN,SEG,native,unique_sources,blocks,indexed
from battle_text import layout,width,LINE_LIMIT,ROWS
from battle_terms import canonicalize
from menu_encoding import menu_encode
from library_text import text,japanese
from battle_placeholder import verify as verify_placeholder

THEATER='BTL/ST.BIN';THEATER_SEG='BTL/ST.SEG'
INPUT=ROOT/'work/translation/en/battle_complete.json'
NAMES=ROOT/'work/translation/en/battle_theater_names.json'
REUSE=ROOT/'work/translation/en/battle_reuse.json'
PILOTS=ROOT/'work/analysis/build-0.2.9-menu_names.json'
EDITS={14417:"Newtype... Power sealed in the Black\\nHistory's darkness... What is it?!",
       21072:"I'll have to get a little rough!"}


def theater_names():
    disc=Disc(SOURCE);raw=disc.read(THEATER);seg=disc.read(THEATER_SEG)
    require(len(seg)==57*4,'Theater segment count');off=struct.unpack('<57I',seg)
    require(off[0]==0 and off[-1]==len(raw) and list(off)==sorted(set(off)),'Theater segment bounds')
    answers={r['id']:r for r in json.loads(PILOTS.read_text(encoding='utf-8'))['changes']
             if r['id'].startswith('pilot/') and r['id'].endswith('/display')}
    names=[];scenes=0
    for bank in range(28):
        head,base,end=off[bank*2:bank*2+3];count=struct.unpack_from('<I',raw,base)[0]
        require(head+4+(count+2)*4<=base and not any(raw[base+4:base+16]),'Theater bank header')
        ptr=struct.unpack_from('<%dI'%(count+2),raw,head+4)
        require(ptr[0]==ptr[1]==16 and base+ptr[-1]==end and list(ptr[1:])==sorted(set(ptr[1:])),'Theater scene pointers')
        for scene in range(count):
            scenes+=1;start=base+ptr[scene+1];stop=base+ptr[scene+2];cursor=start+16
            require(raw[start] in (0,1),'Theater scene kind')
            for side in range(2):
                cursor+=16
                for unit in range(8):
                    require(cursor+16<=stop,'Theater unit header boundary')
                    crew=struct.unpack_from('<I',raw,cursor+4)[0];require(0<=crew<=7,'Theater crew count')
                    for slot in range(crew):
                        pilot=struct.unpack_from('<I',raw,cursor+16+slot*32)[0];at=cursor+28+slot*32
                        require(at+20<=stop and not any(raw[at-8:at]),'Theater crew metadata')
                        cell=raw[at:at+20];source=cell.split(b'\0')[0]
                        require(source and len(source)<20 and not any(cell[len(source):]),'Theater name cell')
                        key=f'pilot/{pilot}/display';answer=answers.get(key)
                        if pilot==947:
                            require(source=='ＡＩ'.encode('cp932'),'AI identity');value='AI';origin='Explicit AI label'
                        else:
                            require(answer and answer['source_sha256']==sha(source),'Theater pilot identity')
                            value=answer['text'];origin=key
                        encoded=menu_encode(value);require(len(encoded)<20 and not japanese(value) and text(encoded)==value,'Theater name capacity')
                        names.append(dict(bank=bank,scene=scene,side=side,unit=unit,slot=slot,offset=at,
                            pilot_id=pilot,text=value,source_sha256=sha(source),cell_sha256=sha(cell),reused_display_id=origin))
                    cursor+=16+crew*32
            require(cursor+raw[start+2]*16==stop,'Theater scene/event boundary')
    require(scenes==1031 and len(names)==4297 and len({r['offset'] for r in names})==4297,'Theater inventory')
    return dict(version='0.3.15',source_sha256=sha(raw),segment_sha256=sha(seg),pilot_translation_sha256=file_sha(PILOTS),
        banks=28,scenes=scenes,entries=names)


def current_records(data,seg):
    parsed=native()[4];_,chunks=blocks(data,seg)
    rows=[indexed(chunk,p['index'],len(p['rows'])) if p['rows'] else [] for chunk,p in zip(chunks,parsed)]
    return parsed,chunks,rows


def prepare(disc):
    data,seg=disc.read(BIN),disc.read(SEG);parsed,chunks,current=current_records(data,seg)
    sources=unique_sources();reuse=json.loads(REUSE.read_text(encoding='utf-8'))
    inherited={r['id']:r for r in reuse['entries']};entries=[];statuses=Counter();retained=0
    verify_placeholder(disc.read(EXE))
    for source in sources:
        if source['id']==444:continue
        old=[current[o['block']][o['record']] for o in source['occurrences']]
        needs=[japanese(text(r['raw'])) for r in old]
        if not any(needs):retained+=1;continue
        require(all(needs),'Mixed English/native occurrence set')
        for o,r in zip(source['occurrences'],old):
            require(sha(r['raw'])==o['raw_sha256'] and r['metadata']==o['metadata'],'Remaining caption differs from native')
        row=inherited[source['id']]
        require(row['source_sha256']==source['source_sha256'] and row.get('text'),'Missing source-bound inherited English')
        value=canonicalize(EDITS.get(source['id'],row['text']),source['text'])
        lines=layout(value);require(lines and len(lines)<=ROWS and max(map(width,lines))<=LINE_LIMIT,'Caption layout')
        encoded=menu_encode('\\n'.join(lines))
        require(len(encoded)+1<=96 and text(encoded)=='\\n'.join(lines) and not japanese(value),'Caption encoding/buffer')
        origin='Explicit source-reviewed correction' if source['id'] in EDITS else row['status']
        statuses[origin]+=1
        entries.append(dict(id=source['id'],source_sha256=source['source_sha256'],text=value,lines=lines,
            line_widths=list(map(width,lines)),encoded_bytes=len(encoded),occurrences=len(source['occurrences']),provenance=origin))
    require(len(entries)==23359 and retained==2162,'Complete caption coverage changed')
    return dict(version='0.3.15',base_bin_sha256=sha(data),base_seg_sha256=sha(seg),reuse_sha256=file_sha(REUSE),
        existing_english_sources_retained=retained,hidden_native_source=444,inherited_provenance=dict(statuses),entries=entries,
        editorial_status='Inherited English reused with source, spelling, encoding and layout checks; not a new full manual review.')


def build(disc):
    inv=json.loads(INPUT.read_text(encoding='utf-8'));names=json.loads(NAMES.read_text(encoding='utf-8'))
    require(inv==prepare(disc) and names==theater_names(),'Complete battle inventory drift')
    parsed,chunks,old=current_records(disc.read(BIN),disc.read(SEG));sources=unique_sources();changes=defaultdict(dict)
    for e in inv['entries']:
        value=menu_encode('\\n'.join(e['lines']))
        for o in sources[e['id']]['occurrences']:changes[o['block']][o['record']]=value
    result=[];offsets=[0];changed_records=0
    for bank,chunk in enumerate(chunks):
        p=parsed[bank];selected=changes.get(bank,{})
        if not selected:result.append(chunk);offsets.append(offsets[-1]+len(chunk));continue
        out=bytearray(chunk);seen={}
        if out[-1]:out.append(0)
        for record,value in sorted(selected.items()):
            if value not in seen:seen[value]=len(out);out.extend(value+b'\0')
            struct.pack_into('<I',out,p['index']+record*8+4,seen[value]-p['pool'])
        out.extend(bytes((-len(out))%16));after=indexed(out,p['index'],len(p['rows']));restore=bytearray(out[:len(chunk)])
        for record in selected:
            at=p['index']+record*8+4;restore[at:at+4]=chunk[at:at+4]
        require(restore==chunk,'Changed original bank data beyond selected offset words')
        for a,b in zip(old[bank],after):
            require(a['metadata']==b['metadata'] and b['raw']==selected.get(a['record'],a['raw']),'Caption and voice readback')
        changed_records+=len(selected);result.append(bytes(out));offsets.append(offsets[-1]+len(out))
    data=b''.join(result);seg=struct.pack('<%dI'%len(offsets),*offsets)
    require(blocks(data,seg)[1]==result,'Caption archive readback')
    # Exhaustively inspect every final indexed caption, not opaque archive tails.
    hidden={(o['block'],o['record']) for o in sources[444]['occurrences']};visible=0
    for bank,(p,chunk) in enumerate(zip(parsed,result)):
        if not p['rows']:continue
        for r in indexed(chunk,p['index'],len(p['rows'])):
            if (bank,r['record']) in hidden:
                require(r['raw']==old[bank][r['record']]['raw'],'Hidden production record changed')
            else:
                require(not japanese(text(r['raw'])),'Untranslated player-facing indexed caption');visible+=1
    require(visible==58880,'Visible caption record count')
    theater=disc.read(THEATER);native_theater=Disc(SOURCE).read(THEATER)
    require(sha(theater)==names['source_sha256'] and disc.read(THEATER_SEG)==Disc(SOURCE).read(THEATER_SEG),'Theater input identity')
    out=bytearray(theater)
    for e in names['entries']:
        at=e['offset'];value=menu_encode(e['text']);require(sha(theater[at:at+20])==e['cell_sha256'],'Theater name preimage')
        out[at:at+20]=value+bytes(20-len(value));require(text(out[at:at+20].split(b'\0')[0])==e['text'],'Theater name readback')
    restored=bytearray(out)
    for e in names['entries']:
        at=e['offset'];restored[at:at+20]=theater[at:at+20]
    require(restored==theater,'Theater scene/gameplay data changed')
    report=dict(version='0.3.15',new_caption_sources=len(inv['entries']),new_caption_records=changed_records,
        final_player_facing_records=visible,final_player_facing_sources=25521,hidden_native_records=len(hidden),
        unchanged_hidden_source=444,banks_checked=352,changed_banks=len(changes),theater_names=len(names['entries']),
        theater_scenes=names['scenes'],theater_banks=28,provenance=inv['inherited_provenance'],
        editorial_status=inv['editorial_status'],caption_buffer_capacity=96,maximum_rows=2,line_limit=460,
        all_other_captions_voice_metadata_and_opaque_tails_preserved=True,
        theater_non_name_bytes_preserved=True,emulator='pending')
    return {BIN:data,SEG:seg,THEATER:bytes(out)},report
