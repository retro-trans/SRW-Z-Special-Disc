"""Build English reference screens and menus, preserving story dialogue."""
import argparse
import json
import shutil
import struct
import subprocess
from pathlib import Path
from sp_disc import *
import port_menu_runtime
import compile_library
import reuse_menu_graphics
import reuse_compdata
import reuse_system_text
import port_compact_labels
import build_front_end
import author_headings
import reuse_help_book
import compile_briefings
import compile_reference_names
import compile_chart
import compile_save_summaries
import compile_narration
import compile_battle
import attract_demo
import align_story_panels
import world_map_titles
import episode_titles
import deployment_ui
import mission_conditions
import stage_ui_guard
import tactical_ui
import terrain_rows
import mission_prompt
import setup_art
import bazaar_slogan
import squad_followup

VERSION='0.2.24'
OUT=ROOT/'work/output'/('SRW Z Special Disc English v'+VERSION+'.iso')

def seal_pool(exe,pool):
    out=bytearray(exe);start=port_menu_runtime.NEW_FILE
    po=struct.unpack_from('<I',out,28)[0];es,n=struct.unpack_from('<HH',out,42)
    at=po+(n-2)*es;segment=struct.unpack_from('<8I',out,at)
    require(segment[2]==port_menu_runtime.NEW_CAVE and segment[2]+segment[4]==reuse_compdata.POOL_BASE,'Pool placement')
    require(len(out)==start+segment[4],'Unexpected runtime trailer')
    out.extend(pool);count=segment[4]+len(pool)
    struct.pack_into('<II',out,at+16,count,count)
    struct.pack_into('<I',out,at+es+4,len(out))
    end=segment[2]+count
    heap=port_menu_runtime.SP_END+((end-port_menu_runtime.SP_END+4095)//4096)*4096
    struct.pack_into('<I',out,0x1001d0-0xff680,0x3c040000|((heap+0x8000)>>16))
    struct.pack_into('<I',out,0x1001d8-0xff680,0x24840000|(heap&65535))
    struct.pack_into('<I',out,port_menu_runtime.BREAK_OFFSET,heap)
    require(end<=heap and heap%4096==port_menu_runtime.SP_END%4096,'Heap overlap/alignment')
    return bytes(out),dict(pool_base=reuse_compdata.POOL_BASE,pool_bytes=len(pool),segment_end=end,heap_base=heap)

def components():
    disc,native,vt1,offsets=source_records();reports={};members={}
    exe,reports['runtime']=port_menu_runtime.build(native)
    exe,files,reports['library']=compile_library.build(exe);members.update(files)
    exe,files,reports['graphics']=reuse_menu_graphics.build(exe);members.update(files)
    exe,help_archive,reports['help']=reuse_help_book.build(exe,members[reuse_help_book.MEMBER]);members[reuse_help_book.MEMBER]=help_archive
    exe,files,reports['reference_names']=compile_reference_names.build(exe,help_archive);members.update(files)
    data,pool,reports['menu_names']=reuse_compdata.build();members[reuse_compdata.MEMBER]=data
    # The system compiler reads a stable prefix for cross-component addresses.
    require((ROOT/'work/cache/nonstory/menu-pool.bin').read_bytes()==pool,'Refresh menu-pool cache before building')
    exe,pool,reports['system_text']=reuse_system_text.build(exe)
    exe,pool,reports['compact_labels']=port_compact_labels.build(exe,pool)
    members[compile_chart.MEMBER],pool,reports['chart']=compile_chart.build(pool)
    exe,pool,reports['save_summaries']=compile_save_summaries.build(exe,pool)
    exe,members[compile_narration.MEMBER],reports['narration']=compile_narration.build(exe)
    exe,pool,files,reports['battle']=compile_battle.build(exe,pool);members.update(files)
    members[attract_demo.MEMBER],reports['attract_demo'],_=attract_demo.build()
    exe,pool,reports['panel_alignment']=align_story_panels.build(exe,pool)
    members[world_map_titles.MEMBER],reports['world_map_titles'],_=world_map_titles.build()
    pool,files,reports['deployment_ui']=deployment_ui.build(pool,members[deployment_ui.COMP],members[deployment_ui.STAGE]);members.update(files)
    pool,members[mission_conditions.MEMBER],reports['mission_conditions']=mission_conditions.build(pool,members[mission_conditions.MEMBER])
    exe,reports['tactical_ui']=tactical_ui.build(exe)
    exe,reports['terrain_rows']=terrain_rows.build(exe)
    exe,members[mission_prompt.MEMBER],reports['mission_prompt']=mission_prompt.build(exe,members[mission_prompt.MEMBER])
    exe,members[setup_art.MEMBER],reports['setup_art']=setup_art.build(exe,members[setup_art.MEMBER])
    members[bazaar_slogan.MEMBER],reports['bazaar_slogan']=bazaar_slogan.build(members[bazaar_slogan.MEMBER])
    exe,reports['memory']=seal_pool(exe,pool)
    exe,members[squad_followup.COMP],members[squad_followup.ART],reports['squad_followup']=squad_followup.build(exe,members[squad_followup.COMP],members[squad_followup.ART])
    members[EXE]=exe
    _,_,front=build_front_end.components();headings,_=author_headings.build()
    briefing_changes,reports['briefings']=compile_briefings.build()
    episode_changes,reports['episode_titles'],_=episode_titles.build()
    texture_changes=front+headings+briefing_changes+episode_changes
    # Keep VT1 as small write spans; its intervening video and graphic payloads
    # are read and compared but never reconstructed.
    reports['vt1']=[{k:v for k,v in row.items()if k!='payload'}for row in texture_changes]
    return disc,members,texture_changes,reports

def plan(disc,members,textures):
    writes=[];placements={};dummy=disc.entries['DMY/DMY.BIN'];cursor=(dummy['lba']+8192)*2048
    for name,payload in members.items():
        entry=disc.entries[name];old=entry['lba']*2048
        if len(payload)<=entry['size']:
            at=old;stored=payload+bytes(entry['size']-len(payload));size=entry['size']
        else:
            at=cursor;size=len(payload);stored=payload+bytes((-len(payload))%2048);cursor+=len(stored)
            require(cursor<=dummy['lba']*2048+dummy['size'],'Reserved disc area exhausted')
            with SOURCE.open('rb') as f:f.seek(at);require(not any(f.read(len(stored))),'Relocation area is not empty')
            rec=entry['directory_record']
            writes.extend([(rec+2,struct.pack('<I',at//2048)+struct.pack('>I',at//2048),name+' ISO extent'),
                           (rec+10,struct.pack('<I',size)+struct.pack('>I',size),name+' ISO size')])
            if name in disc.runtime:
                p=disc.entries['VMAP.DAT']['lba']*2048+disc.runtime[name]['vmap_offset']+40
                writes.append((p,struct.pack('<II',at//2048,(size+2047)//2048),name+' VMAP'))
        writes.append((at,stored,name))
        placements[name]=dict(lba=at//2048,size=size,payload_bytes=len(payload),sha256=sha(payload),relocated=at!=old)
    base=disc.entries[VT1]['lba']*2048
    for row in textures:writes.append((base+row['start'],row['payload'],VT1+' '+str(row['chunk'])))
    writes.sort(key=lambda r:r[0])
    for a,b in zip(writes,writes[1:]):require(a[0]+len(a[1])<=b[0],'Overlapping disc write ranges')
    return writes,placements

def verify(path,writes,members,textures,placements):
    target=Disc(path);runtime=Disc(path,True)
    require(target.size==Disc(SOURCE).size,'ISO size changed')
    with Path(path).open('rb') as f:
        for at,payload,label in writes:
            f.seek(at);require(f.read(len(payload))==payload,'ISO write readback: '+label)
    # Stream every byte outside explicit write ranges against the clean image.
    protected=0;cursor=0
    with SOURCE.open('rb') as before,Path(path).open('rb') as after:
        for lo,hi in [(at,at+len(payload))for at,payload,label in writes]+[(target.size,target.size)]:
            before.seek(cursor);after.seek(cursor);left=lo-cursor
            while left:
                count=min(left,8<<20);require(before.read(count)==after.read(count),'Protected disc bytes differ')
                protected+=count;left-=count
            cursor=hi
    for name,payload in members.items():
        require(target.read(name)[:len(payload)]==payload and runtime.read(name)[:len(payload)]==payload,'ISO/runtime mapping disagreement: '+name)
        require(target.entries[name]['lba']==placements[name]['lba'],'ISO placement readback')
    exe=target.read(EXE)
    help_archive=target.read(reuse_help_book.MEMBER)
    starts=struct.unpack_from('<8I',exe,reuse_help_book.TABLE)
    sizes=struct.unpack_from('<7I',exe,reuse_help_book.TABLE+32)
    for i in range(7):
        decoded,_=decode(help_archive[starts[i]:starts[i+1]])
        require(len(decoded)==sizes[i],'Help runtime size mismatch')
        if i==6:require(len(reuse_help_book.parse(decoded))==103,'Help runtime index mismatch')
    for key,(off,sz,count) in compile_library.TABLES.items():
        blob=target.read('DATA/MTVZKN'+key+'.BIN');offsets=struct.unpack_from('<%dI'%count,exe,off);sizes=struct.unpack_from('<%dI'%count,exe,sz)
        for at,expected in zip(offsets,sizes):
            plain,_=decode(blob[at:]);require(len(plain)==expected,'Runtime encyclopedia size mismatch');compile_library.fields(plain)
    vt=target.read(VT1)
    for r in textures:require(sha(decode(vt[r['start']:r['end']])[0])==r['decoded_sha256'],'Final texture mismatch')
    clean=Disc(SOURCE);native=clean.read(EXE);require(exe[0x3b8be0:0x3be700]==native[0x3b8be0:0x3be700],'Suspend dialogue changed')
    stage=target.read('DATA/STAGE.BIN');stage_ui_guard.check(stage,True,True)
    require(target.read('BTL/SRVC.BIN')==members[compile_battle.BIN] and target.read('BTL/SRVC.SEG')==members[compile_battle.SEG], 'Battle caption members differ from reviewed output')
    require(target.read('DATA/HSFC.BIN')==clean.read('DATA/HSFC.BIN'),'Native save archive changed')
    require(target.read(world_map_titles.MEMBER)==members[world_map_titles.MEMBER],
            'Final location-title archive differs from reviewed artwork')
    narration=target.read(compile_narration.MEMBER)
    offsets=struct.unpack_from('<11I',exe,compile_narration.OFFSET_TABLE)
    sizes=struct.unpack_from('<10I',exe,compile_narration.SIZE_TABLE)
    require(offsets[-1]==len(members[compile_narration.MEMBER]),'Narration archive end')
    for lo,hi,size in zip(offsets,offsets[1:],sizes):
        raw,consumed=decode(narration[lo:hi]);info=compile_narration.parse(raw)
        require(len(raw)==size and not any(narration[lo+consumed:hi]) and info['text'].count(b'\n')==12,'Narration tables/readback')
    return dict(protected_bytes=protected,all_bytes_outside_planned_ranges_identical=True,
        iso_and_runtime_maps_agree=True,encyclopedia_tables_read_back=True,help_tables_read_back=True,
        story_dialogue_unchanged=True,story_only_typed_ui_fields_changed=True,battle_caption_members_read_back=True,suspend_dialogue_unchanged=True,
        native_save_archive_unchanged=True,narration_tables_read_back=True)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');ap.add_argument('--patch',action='store_true');args=ap.parse_args()
    disc,members,textures,reports=components();writes,placements=plan(disc,members,textures)
    summary=dict(version=VERSION,library_fields=reports['library']['fields'],menu_name_fields=reports['menu_names']['translated_fields'],
        system_fields=reports['system_text']['translated_fields'],help_pages=reports['help']['pages'],help_chapter_fields=reports['help']['chapter_fields'],briefing_panels=len(reports['briefings']['pages']),
        reference_name_fields=len(reports['reference_names']['entries']),chart_fields=len(reports['chart']['entries']),
        save_summaries=reports['save_summaries']['translated_records'],save_summaries_deferred=reports['save_summaries']['deferred_ids'],
        narration_records=reports['narration']['records'],
        battle_captions=reports['battle']['translated_captions'],battle_records=reports['battle']['translated_records'],
        demo_titles=reports['attract_demo']['translated_titles'],demo_names=reports['attract_demo']['translated_names'],
        world_map_titles=reports['world_map_titles']['count'],
        episode_titles=reports['episode_titles']['count'],
        deployment_menu_entries=reports['deployment_ui']['menu_entries'],tournament_names=reports['deployment_ui']['stage_names'],
        mission_condition_texts=reports['mission_conditions']['translated_texts'],mission_condition_occurrences=reports['mission_conditions']['translated_occurrences'],
        tactical_ui_fields=reports['tactical_ui']['fields'],
        compact_terrain_rows=reports['terrain_rows']['rows'],
        challenge_confirmation_questions=reports['mission_prompt']['questions'],
        setup_art_tiles=len(reports['setup_art']['tiles']),bazaar_banner_fields=len(reports['bazaar_slogan']['entries']),
        squad_followup_fields=reports['squad_followup']['text_fields'],squad_followup_tiles=reports['squad_followup']['image_tiles'],
        memory=reports['memory'],members=placements,write_ranges=len(writes),runtime='pending')
    print(json.dumps(summary,indent=2),flush=True)
    if not args.write:print('DRY RUN passed: no ISO written');return
    require(not OUT.exists(),'Versioned build already exists');require(file_sha(SOURCE)==SOURCE_SHA,'Native ISO identity drift')
    partial=OUT.with_suffix('.iso.partial');require(not partial.exists(),'Partial output already exists');shutil.copyfile(SOURCE,partial)
    with partial.open('r+b') as f:
        for at,payload,label in writes:f.seek(at);f.write(payload)
    checks=verify(partial,writes,members,textures,placements)
    receipt=dict(summary,source_sha256=SOURCE_SHA,output_sha256=file_sha(partial),validation=checks,
        source_files={str(p.relative_to(ROOT)):file_sha(p)for p in sorted((ROOT/'tools').rglob('*.py'))},
        translation_files={str(p.relative_to(ROOT)):file_sha(p)for p in sorted((ROOT/'work/translation/en').glob('*.json'))},
        glossary_files={str(p.relative_to(ROOT)):file_sha(p)for p in sorted((ROOT/'work/glossary').glob('*.json'))},
        artifact_files={str(p.relative_to(ROOT)):file_sha(p) for p in
                        (world_map_titles.BINDINGS,episode_titles.BINDINGS,deployment_ui.BINDINGS,mission_conditions.BINDINGS,tactical_ui.BINDINGS,terrain_rows.BINDINGS,mission_prompt.BINDINGS,setup_art.BINDINGS,bazaar_slogan.BINDINGS,squad_followup.BINDINGS)})
    partial.rename(OUT)
    for name,report in reports.items():(ROOT/'work/analysis'/('build-'+VERSION+'-'+name+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if args.patch:
        patch=OUT.with_suffix('.xdelta');restored=ROOT/'work/cache'/('roundtrip-'+VERSION+'.iso')
        require(not patch.exists() and not restored.exists(),'Patch scratch path already exists')
        xdelta='E:/Projects/SRW Z/xdelta3.exe'
        subprocess.run([xdelta,'-e','-9','-S','none','-s',str(SOURCE),str(OUT),str(patch)],check=True)
        subprocess.run([xdelta,'-d','-s',str(SOURCE),str(patch),str(restored)],check=True)
        require(file_sha(restored)==receipt['output_sha256'],'Patch roundtrip mismatch')
        receipt['patch']=dict(sha256=file_sha(patch),bytes=patch.stat().st_size,roundtrip_verified=True)
        require(restored.resolve().is_relative_to(ROOT.resolve()),'Scratch path outside workspace');restored.unlink()
    OUT.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Verified build:',OUT,flush=True)

if __name__=='__main__':main()
