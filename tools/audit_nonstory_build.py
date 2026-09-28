"""Read the finished ISO and independently validate English memory/text targets."""
import argparse
import json
import struct
from sp_disc import *
from library_text import fields,text,TABLES,CHARS
from glossary_terms import canonicalize
from reuse_compdata import cstring
from inspect_english_runtime import CAVE,CAVE_FILE,s16
import port_menu_runtime


def audit(version):
    path=ROOT/'work/output'/f'SRW Z Special Disc English v{version}.iso'
    receipt=json.loads(path.with_suffix('.json').read_text());disc=Disc(path,True);exe=disc.read(EXE)
    require(file_sha(path)==receipt['output_sha256'],'Finished ISO identity')
    squad_followup_result=None;squad_report=ROOT/'work/analysis'/f'build-{version}-squad_followup.json'
    if squad_report.exists():
        from audit_squad_followup import audit as audit_squad
        squad_followup_result,disc=audit_squad(disc,exe,json.loads(squad_report.read_text(encoding='utf8')))
        exe=disc.read(EXE)
    prompt=None;comparison_disc=disc;comparison_exe=exe
    setup=None;setup_report=ROOT/'work/analysis'/f'build-{version}-setup_art.json'
    if setup_report.exists():
        from audit_setup_art import audit as audit_setup
        slogan_report=ROOT/'work/analysis'/f'build-{version}-bazaar_slogan.json'
        setup,comparison_disc=audit_setup(disc,exe,json.loads(setup_report.read_text(encoding='utf8')),json.loads(slogan_report.read_text(encoding='utf8')))
        comparison_exe=comparison_disc.read(EXE)
    prompt_report=ROOT/'work/analysis'/f'build-{version}-mission_prompt.json'
    if prompt_report.exists():
        from audit_mission_prompt import audit as audit_prompt
        prompt,comparison_disc=audit_prompt(comparison_disc,comparison_exe,json.loads(prompt_report.read_text(encoding='utf8')))
        comparison_exe=comparison_disc.read(EXE)
    po=struct.unpack_from('<I',exe,28)[0];es,n=struct.unpack_from('<HH',exe,42)
    segments=[struct.unpack_from('<8I',exe,po+i*es)for i in range(n)]
    cave=next(s for s in segments if s[0]==1 and s[2]==port_menu_runtime.NEW_CAVE)
    native=Disc(SOURCE).read(EXE);np=struct.unpack_from('<I',native,28)[0];ns,nn=struct.unpack_from('<HH',native,42)
    native_segments=[struct.unpack_from('<8I',native,np+i*ns)for i in range(nn)]
    native_end=max(s[2]+s[5]for s in native_segments if s[0]==1)
    require(native_end<=cave[2] and cave[1]+cave[4]<=len(exe),'New English segment overlaps native memory/file')
    heap=struct.unpack_from('<I',exe,port_menu_runtime.BREAK_OFFSET)[0]
    require(cave[2]+cave[5]<=heap,'English pool overlaps heap')
    def loaded(address):
        matches=[s for s in segments if s[0]==1 and s[2]<=address<s[2]+s[4]]
        require(len(matches)==1,'Text pointer not in one loaded segment')
        s=matches[0];return s[1]+address-s[2]
    relocation_count=0
    for component in ('menu_names','system_text'):
        report=json.loads((ROOT/'work/analysis'/f'build-{version}-{component}.json').read_text(encoding='utf-8'))
        owner=decode(disc.read('DATA/COMPDATA.BN'))[0]if component=='menu_names'else exe
        for row in report['changes']:
            require(canonicalize(row['text'])==row['text'],'Unapplied name correction')
            if 'relocated_address'not in row:continue
            address=row['relocated_address'];at=loaded(address)
            require(cstring(exe,at)[1]==row['text'],'Relocated English text mismatch')
            for site in row.get('pointer_sites',[]):require(struct.unpack_from('<I',owner,site)[0]==address,'Final data pointer mismatch')
            for hi,lo in row.get('instruction_pairs',[]):
                h,l=struct.unpack_from('<I',exe,hi)[0],struct.unpack_from('<I',exe,lo)[0]
                value=((h&65535)<<16)+((l&65535)if l>>26==13 else s16(l))
                require(value==address,'Final instruction pointer mismatch')
            relocation_count+=1
    library=json.loads((ROOT/'work/translation/en/library_complete.json').read_text(encoding='utf-8'))['entries']
    index={r['id']:r for r in library};checked=0;lines=0
    donor=(ROOT/'work/cache/english-runtime/english.elf').read_bytes();widths=donor[CAVE_FILE+0x78b960-CAVE:CAVE_FILE+0x78b960-CAVE+69]
    for key,(offset,_,count)in TABLES.items():
        blob=disc.read('DATA/MTVZKN'+key+'.BIN');pointers=struct.unpack_from('<%dI'%count,exe,offset)
        for i,pointer in enumerate(pointers):
            for tag,value in fields(decode(blob[pointer:])[0])[1]:
                row=index.get(f'{key}/{i}/{tag}')
                if not row:continue
                require(text(value)==row['text'],'Final Library text mismatch '+row['id'])
                require(canonicalize(row['text'])==row['text'],'Library name inconsistency')
                if tag in ('DSCR','DSC2'):
                    for line in row['text'].splitlines():
                        width=sum(widths[CHARS.index(ord(c))]+2 if ord(c)in CHARS else 13 if c==' 'else 24 for c in line)
                        require(width<={'RT':560,'PT':280,'KW':544}[key],'Library line exceeds measured bound');lines+=1
                checked+=1
    require(checked==len(library),'Library audit omitted fields')
    reference_count=0;chart_count=0
    reference_report=ROOT/'work/analysis'/f'build-{version}-reference_names.json'
    if reference_report.exists():
        reference=json.loads(reference_report.read_text(encoding='utf-8'))
        starts=struct.unpack_from('<8I',exe,0x384a00);archive=disc.read('DATA/NISVDATA.BIN')
        squad=decode(archive[starts[4]:starts[5]])[0];maps=disc.read('MAP/MAPNAME.BIN')
        native_squad=decode(Disc(SOURCE).read('DATA/NISVDATA.BIN')[struct.unpack_from('<I',native,0x384a10)[0]:])[0]
        protected=bytearray(squad)
        for row in reference['entries']:
            owner=squad if row['id'].startswith('squad/')else maps;at=row['offset'];size=row['capacity']
            require(text(owner[at:at+size].split(b'\0')[0])==row['text'],'Reference name mismatch '+row['id'])
            require(canonicalize(row['text'])==row['text'],'Reference glossary inconsistency')
            if owner is squad:protected[at:at+size]=native_squad[at:at+size]
            reference_count+=1
        require(protected==native_squad,'Squad gameplay data changed')
        chart=json.loads((ROOT/'work/analysis'/f'build-{version}-chart.json').read_text(encoding='utf-8'))
        stage=comparison_disc.read('DATA/STAGE.BIN');clean_stage=Disc(SOURCE).read('DATA/STAGE.BIN')
        if (ROOT/'work/analysis'/f'build-{version}-deployment_ui.json').exists():
            from audit_deployment_ui import protect_stage
            protect_stage(stage,clean_stage,(ROOT/'work/analysis'/f'build-{version}-mission_conditions.json').exists())
        else:require(stage[44016:]==clean_stage[44016:],'Story dialogue chunks changed')
        raw=decode(stage)[0];clean_raw=decode(clean_stage)[0];protected=bytearray(raw)
        if 'main_synopses'in chart:
            require(chart['main_synopses']==110 and chart['sp_synopses']==21,'Chart synopsis inventory')
            require({r['id']for r in chart['entries']if r['id'].startswith('main-synopsis/')}==
                    {'main-synopsis/'+str(i)for i in range(110)},'Missing main chart synopsis')
        for row in chart['entries']:
            if 'relocated_address'in row:
                address=row['relocated_address'];at=loaded(address)
                require(cstring(exe,at)[1]==row['text'],'Chart synopsis pool readback')
                for site in row['pointer_sites']:require(struct.unpack_from('<I',raw,site)[0]==address,'Chart synopsis pointer')
                if row.get('native_source_preserved'):
                    lo=row['offset'];hi=lo+row['capacity']
                    require(raw[lo:hi]==clean_raw[lo:hi],'Preserved chart source bytes changed')
                relocation_count+=1
                require(len(row['text'].splitlines())<=11,'Chart synopsis row overflow')
                for line in row['text'].splitlines():
                    width=sum(widths[CHARS.index(ord(c))]+2 if ord(c)in CHARS else 13 if c==' 'else 24 for c in line)
                    require(width<=560,'Chart synopsis width overflow')
            else:
                at=row['offset'];size=row['capacity']
                require(text(raw[at:at+size].split(b'\0')[0])==row['text'],'Chart field readback')
            require(canonicalize(row['text'])==row['text'],'Chart glossary inconsistency')
            chart_count+=1
        for lo,hi in chart['write_ranges']:protected[lo:hi]=clean_raw[lo:hi]
        require(protected==clean_raw,'Nontext chart bytes changed')
    else:
        require(disc.read('DATA/STAGE.BIN')==Disc(SOURCE).read('DATA/STAGE.BIN'),'Unexpected story change in legacy build')
    recap_count=0;recap_native=[]
    recap_report=ROOT/'work/analysis'/f'build-{version}-save_summaries.json'
    if recap_report.exists():
        recap=json.loads(recap_report.read_text(encoding='utf-8'))
        require(recap['records']==66 and recap['row_limit']==3 and recap['cell_bytes']==256,'Save recap inventory/shape')
        require([r['id']for r in recap['entries']]==list(range(66)),'Missing save recap')
        words=struct.unpack_from('<11I',exe,0x43cb60-0xff680)
        require(words[:6]==(0x30a5ffff,0x2ca30043,0x14600002,0,0x00002821,0x00051880)
                and words[6]>>16==0x3c02 and words[7]>>16==0x2442
                and words[8:]==(0x00431021,0x03e00008,0x8c420000),'Save recap getter instructions')
        table=((words[6]&65535)<<16)+s16(words[7])
        require(table==recap['pointer_table'],'Save recap getter table address')
        table_at=loaded(table);require(loaded(table+267)==table_at+267,'Save recap pointer table crosses memory bounds')
        pointers=struct.unpack_from('<67I',exe,table_at)
        empty=loaded(pointers[0]);require(loaded(pointers[0]+767)==empty+767 and not any(exe[empty:empty+768]),'Save recap empty fallback')
        require(struct.unpack_from('<I',exe,0x43cc54-0xff680)[0]==0x24640100
                and struct.unpack_from('<I',exe,0x43cc78-0xff680)[0]==0x24640200,'Save recap line strides')
        native_recap=decode(Disc(SOURCE).read('DATA/HSFC.BIN'))[0];unique={}
        for row in recap['entries']:
            i=row['id'];address=pointers[i+1];at=loaded(address)
            require(address==row['relocated_address'] and loaded(address+767)==at+767,'Save recap pointer bounds')
            source=native_recap[0xe6+i*198:0xe6+(i+1)*198];digest=sha(source)
            require(digest==row['source_sha256'],'Save recap native source binding')
            if not row['translated']:
                for j in range(3):
                    cell=exe[at+j*256:at+(j+1)*256];original=source[j*66:(j+1)*66]
                    require(cell[:66]==original and not any(cell[66:]),'Deferred native recap changed')
                recap_native.append(i)
                if digest in unique:require(unique[digest]==address,'Duplicate native recap mapping differs')
                unique[digest]=address
                continue
            actual=[]
            for j in range(3):
                cell=exe[at+j*256:at+(j+1)*256];nul=cell.find(b'\0')
                require(nul>=0 and not any(cell[nul:]),'Save recap unterminated cell or nonzero tail')
                line=text(cell[:nul]);actual.append(line)
                width=sum(widths[CHARS.index(ord(c))]+2 if ord(c)in CHARS else 13 if c==' 'else 24 for c in line)
                require(width<=520,'Save recap line width overflow')
            require(actual==row['lines']+['']*(3-len(row['lines'])),'Save recap English readback')
            require(' '.join(line for line in actual if line)==row['text'],'Save recap missing words')
            require(canonicalize(row['text'])==row['text'],'Save recap glossary inconsistency')
            if digest in unique:require(unique[digest]==address,'Duplicate native recap mapping differs')
            unique[digest]=address;recap_count+=1;relocation_count+=1
        require(len(unique)==52,'Save recap unique inventory')
        require(recap_count==recap['translated_records'] and recap_native==recap['deferred_ids'],'Save recap coverage mismatch')
    narration_count=0
    narration_report=ROOT/'work/analysis'/f'build-{version}-narration.json'
    if narration_report.exists():
        report=json.loads(narration_report.read_text(encoding='utf-8'))
        archive=disc.read('DATA/MTZSPROS.BIN');source=Disc(SOURCE).read('DATA/MTZSPROS.BIN')
        offsets=struct.unpack_from('<11I',exe,0x387880);sizes=struct.unpack_from('<10I',exe,0x387850)
        old_offsets=struct.unpack_from('<11I',native,0x387880)
        require(offsets[0]==0 and offsets[-1]==len(archive) and all(x%16==0 for x in offsets),'Narration archive bounds/alignment')
        require(list(offsets)==report['compressed_offsets'] and list(sizes)==report['decoded_sizes'],'Narration runtime tables')
        require(sha(archive)==report['output_sha256'] and sha(source)==report['source_sha256'],'Narration member identity')
        require([r['id']for r in report['entries']]==list(range(10)),'Narration report inventory')
        approved=json.loads((ROOT/'work/translation/en/narration_reviewed.json').read_text(encoding='utf-8'))['entries']
        def commands(blob):
            require(struct.unpack_from('<8I',blob)==(1,32,0,len(blob)-32,len(blob)-32,0,0,0),'Narration wrapper sizes')
            end=60+struct.unpack_from('<I',blob,56)[0];pos=60;chunks=[]
            require(blob[32:36]==b'vpro' and end<=len(blob) and len(blob)-end<16 and not any(blob[end:]),'Narration nested extent')
            while pos<end:
                size=struct.unpack_from('<I',blob,pos+4)[0];chunk=blob[pos:pos+8+size]
                require(len(chunk)==8+size and pos+8+size<=end,'Narration child extent')
                chunks.append(chunk);pos+=8+size
            require(pos==end and [c[:4]for c in chunks]==[b'pict',b'text',b'bgm_'],'Narration child inventory')
            chunk=chunks[1];require(chunk[38:42]==b'rawt','Narration rawt position')
            size=struct.unpack_from('<I',chunk,42)[0];payload=chunk[46:46+size]
            require(len(payload)==size and b'\0'not in payload,'Narration rawt extent/NUL')
            return chunks,chunk[8:38],payload,chunk[46+size:]
        for row,(lo,hi),size,reviewed in zip(report['entries'],zip(offsets,offsets[1:]),sizes,approved):
            i=row['id'];raw,used=decode(archive[lo:hi]);old=decode(source[old_offsets[i]:old_offsets[i+1]])[0]
            require(len(raw)==size and not any(archive[lo+used:hi]) and sha(raw)==row['decoded_sha256'],'Narration decoded extent')
            require(sha(old)==row['source_record_sha256'],'Narration source record identity')
            c,p,value,s=commands(raw);oc,op,original,os=commands(old)
            require(raw[32:56]==old[32:56] and c[0]==oc[0] and c[2]==oc[2] and p==op and s==os,'Narration picture/music/timing/format changed')
            require(sha(original)==row['source_text_sha256'],'Narration source text identity')
            actual=text(value);rows=actual.split('\n')
            require(actual==row['text'] and rows==reviewed['lines'] and len(rows)==13,'Narration English readback/line count')
            require(' '.join(actual.split())==' '.join(reviewed['text'].split()),'Narration missing words')
            require(canonicalize(actual)==actual,'Narration glossary inconsistency')
            for line in rows:
                span=sum(widths[CHARS.index(ord(c))]+2 if ord(c)in CHARS else 13 if c==' 'else 24 for c in line)
                require(span<=550,'Narration line width overflow')
            paragraphs=[p for p in reviewed['text'].splitlines()if p.strip()]
            if i in (4,5,6,7):require(rows[0]==paragraphs[0] and rows[-1]==paragraphs[-1],'Narration journal date/signature')
            if i==9:require(' '.join(rows[-2:])==paragraphs[-1],'Narration book attribution')
            narration_count+=1
        require(narration_count==10,'Narration audit omitted records')
    else:
        require(disc.read('DATA/MTZSPROS.BIN')==Disc(SOURCE).read('DATA/MTZSPROS.BIN'),'Unexpected legacy narration change')
    battle_report=ROOT/'work/analysis'/f'build-{version}-battle.json';battle=None
    if battle_report.exists():
        from audit_battle import audit as audit_captions
        battle=audit_captions(disc,exe,loaded,json.loads(battle_report.read_text(encoding='utf-8')))
    else:
        for name in ('BTL/SRVC.BIN','BTL/SRVC.SEG'):
            require(disc.read(name)==Disc(SOURCE).read(name),'Unexpected legacy caption changes')
    for name in ('DATA/HSFC.BIN',):
        require(sha(disc.read(name))==sha(Disc(SOURCE).read(name)),'Dialogue/narration unexpectedly changed')
    demo=None;demo_report=ROOT/'work/analysis'/f'build-{version}-attract_demo.json'
    if demo_report.exists():
        from audit_attract_demo import audit as audit_demo
        demo=audit_demo(disc,json.loads(demo_report.read_text(encoding='utf-8')))
    panel=None;panel_report=ROOT/'work/analysis'/f'build-{version}-panel_alignment.json'
    if panel_report.exists():
        from audit_story_panel_alignment import audit as audit_panels
        panel=audit_panels(disc,exe,loaded,json.loads(panel_report.read_text(encoding='utf-8')))
    locations=None;location_report=ROOT/'work/analysis'/f'build-{version}-world_map_titles.json'
    if location_report.exists():
        from audit_world_map_titles import audit as audit_locations
        locations=audit_locations(disc,json.loads(location_report.read_text(encoding='utf-8')))
    episodes=None;episode_report=ROOT/'work/analysis'/f'build-{version}-episode_titles.json'
    if episode_report.exists():
        from audit_episode_titles import audit as audit_episodes
        episodes=audit_episodes(disc,json.loads(episode_report.read_text(encoding='utf-8')))
    conditions=None;condition_report=ROOT/'work/analysis'/f'build-{version}-mission_conditions.json'
    if condition_report.exists():
        from audit_mission_conditions import audit as audit_conditions
        conditions=audit_conditions(comparison_disc,exe,loaded,json.loads(condition_report.read_text(encoding='utf-8')))
    deployment=None;deployment_report=ROOT/'work/analysis'/f'build-{version}-deployment_ui.json'
    if deployment_report.exists():
        from audit_deployment_ui import audit as audit_deployment
        deployment=audit_deployment(comparison_disc,comparison_exe,loaded,json.loads(deployment_report.read_text(encoding='utf-8')),conditions is not None)
    terrain=None;terrain_spans=();terrain_report=ROOT/'work/analysis'/f'build-{version}-terrain_rows.json'
    if terrain_report.exists():
        from audit_terrain_rows import audit as audit_terrain
        terrain_data=json.loads(terrain_report.read_text(encoding='utf8'))
        terrain=audit_terrain(comparison_disc,comparison_exe,terrain_data);terrain_spans=terrain_data['spans']
    tactical=None;tactical_report=ROOT/'work/analysis'/f'build-{version}-tactical_ui.json'
    if tactical_report.exists():
        from audit_tactical_ui import audit as audit_tactical
        tactical=audit_tactical(comparison_disc,comparison_exe,loaded,json.loads(tactical_report.read_text(encoding='utf8')),terrain_spans)
    require(receipt['patch']['roundtrip_verified'],'Patch not reconstructed')
    return dict(version=version,iso_sha256=receipt['output_sha256'],library_fields_read_back=checked,
        library_lines_within_bounds=lines,relocated_texts_read_back=relocation_count,native_memory_end=hex(native_end),
        english_segment=[hex(cave[2]),hex(cave[2]+cave[5])],heap_base=hex(heap),
        reference_names_read_back=reference_count,chart_fields_read_back=chart_count,save_summaries_read_back=recap_count,
        save_summary_ids_retained_native=recap_native,
        narration_records_read_back=narration_count,narration_nontext_commands_identical=True if narration_count else None,
        story_dialogue_unchanged=True,story_chunks_compressed_identical=deployment is None,battle_member_identical=battle is None,battle_captions=battle,narration_member_identical=not narration_count,
        native_save_archive_identical=True,attract_demo=demo,panel_alignment=panel,world_map_titles=locations,episode_titles=episodes,deployment_ui=deployment,mission_conditions=conditions,
        tactical_ui=tactical,terrain_rows=terrain,mission_prompt=prompt,setup_art=setup,squad_followup=squad_followup_result,patch_reconstruction_verified=True,runtime_validation='pending by user choice')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--version',default='0.2.17');p.add_argument('--write',action='store_true');args=p.parse_args()
    report=audit(args.version);print(json.dumps(report,indent=2))
    if args.write:(ROOT/'work/analysis'/f'build-{args.version}-independent-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    else:print('DRY RUN: no report written')

if __name__=='__main__':main()
