"""Compile all reviewed mission conditions into persistent English memory."""
import argparse,json,struct
from sp_disc import ROOT,Disc,SOURCE,decode,banlz,sha,file_sha,require,EXE
from inspect_mission_conditions import inventory,TARGET as BINDINGS,BASE
from prepare_mission_layout import wrap
from save_summary_text import width
from glossary_terms import canonicalize
from menu_encoding import menu_encode
from reuse_compdata import POOL_BASE
import stage_ui_guard

TARGET=ROOT/'work/translation/en/mission_conditions.json'
REVIEW=ROOT/'work/translation/en/mission_conditions_review.json'
LAYOUT_REVIEW=ROOT/'work/translation/en/mission_conditions_layout_review.json'
LAYOUT_DRAFT=ROOT/'work/translation/en/mission_conditions_layout_draft.json'
MEMBER='DATA/STAGE.BIN';CACHE=ROOT/'work/cache/mission-conditions'

def prepare():
    inv=json.loads(BINDINGS.read_text(encoding='utf8'));require(inv==inventory(),'Mission inventory source drift')
    reviewed=json.loads(LAYOUT_REVIEW.read_text(encoding='utf8'))
    require(reviewed['layout_draft_sha256']==file_sha(LAYOUT_DRAFT) and
            reviewed['full_review_sha256']==file_sha(REVIEW) and reviewed['bindings_sha256']==file_sha(BINDINGS),
            'Stale mission meaning/layout review')
    require(reviewed['entries_examined']==reviewed['entries_in_slice']==61,'Incomplete mission layout review')
    checks={r['id']:r for r in reviewed['entries']};rows=[];bysha={}
    for src in inv['entries']:
        row=checks[src['id']];require(row['verdict'] in ('pass','fixed'),'Mission layout not approved')
        value=canonicalize(row['text']);lines=wrap(value);widths=list(map(width,lines))
        require(' '.join(lines).split()==value.split(),'Mission wrapping lost words')
        require(max(widths)<=460 and len(lines)<=4,'Mission layout overflow')
        entry=dict(id=src['id'],source_sha256=src['source_sha256'],text=value,lines=lines,line_widths=widths,
                   occurrences=src['occurrences'],retain_native=src['source']=='？？？')
        rows.append(entry);bysha[src['source_sha256']]=entry
    groups=[]
    for ch in inv['chunks']:
        for group in ch['tables']:
            count=sum(len(bysha[r['source_sha256']]['lines']) for r in group['entries'])
            require(count<=4,'Combined mission conditions exceed four rows')
            groups.append(dict(chunk=ch['chunk'],kind=group['kind'],rows=count))
    return dict(status='reviewed',entries=rows,groups=groups,line_limit=460,row_limit=4,
                bindings_sha256=file_sha(BINDINGS),full_review_sha256=file_sha(REVIEW),
                layout_review_sha256=file_sha(LAYOUT_REVIEW),spelling_sha256=file_sha(ROOT/'work/glossary/english.json'))

def relocate(pool,stage,cfg):
    inv=json.loads(BINDINGS.read_text(encoding='utf8'));native=Disc(SOURCE).read(MEMBER)
    pool=bytearray(pool);rows=[];chunks={r['chunk']:dict(r,before=decode(stage[r['start']:r['end']])[0]) for r in inv['chunks']}
    for ch in chunks.values():ch['after']=bytearray(ch['before'])
    shared={}
    for row in cfg['entries']:
        if row['retain_native']:rows.append(dict(row));continue
        encoded=menu_encode('\n'.join(row['lines']))+b'\0'
        if encoded not in shared:
            shared[encoded]=POOL_BASE+len(pool);pool.extend(encoded);pool.extend(bytes(-len(pool)%4))
        address=shared[encoded]
        for o in row['occurrences']:
            ch=chunks[o['chunk']];at=o['offset'];p=o['pointer_site'];source=decode(native[ch['start']:ch['end']])[0]
            require(sha(source[at:].split(b'\0')[0])==row['source_sha256'],'Mission source text identity')
            require(struct.unpack_from('<I',ch['after'],p)[0]==BASE+at,'Mission pointer conflicts with earlier edit')
            struct.pack_into('<I',ch['after'],p,address)
        rows.append(dict(row,relocated_address=address))
    for ch in chunks.values():
        restored=bytearray(ch['after'])
        for group in ch['tables']:
            for entry in group['entries']:
                p=entry['pointer_site'];restored[p:p+4]=ch['before'][p:p+4]
        require(restored==ch['before'],'Mission compiler edited non-pointer bytes')
    return bytes(pool),rows,chunks

def packed_chunk(raw,flags,allocation,write_cache=False):
    key=f'{sha(raw)}-{flags:02x}.bin';path=CACHE/key
    if path.exists():
        packed=path.read_bytes();require(decode(packed)[0]==raw,'Mission compressed cache mismatch')
    else:
        packed=banlz.compress_record(raw,flags=flags)
        if len(packed)>allocation:packed=banlz.compress_record_optimal(raw,flags=flags)
        require(len(packed)<=allocation and decode(packed)[0]==raw,'Mission compression/slot overflow')
        if write_cache:CACHE.mkdir(parents=True,exist_ok=True);path.write_bytes(packed)
    require(len(packed)<=allocation,'Mission compressed slot overflow')
    return packed

def compile_component(pool,stage,cfg,write_cache=False):
    pool,rows,chunks=relocate(pool,stage,cfg);out=bytearray(stage);reports=[]
    for i,ch in chunks.items():
        lo,hi=ch['start'],ch['end'];raw=bytes(ch['after']);flags=banlz.parse_header(stage[lo:hi])[1]
        packed=packed_chunk(raw,flags,hi-lo,write_cache)
        out[lo:hi]=packed+bytes(hi-lo-len(packed))
        reports.append(dict(chunk=i,start=lo,end=hi,decoded_bytes=len(raw),before_sha256=sha(ch['before']),
            decoded_sha256=sha(raw),compressed_bytes=len(packed),headroom=hi-lo-len(packed)))
        if write_cache:print('Verified condition chunk',i,'headroom',hi-lo-len(packed),flush=True)
    guard=stage_ui_guard.check(bytes(out),True)
    report=dict(translated_texts=60,translated_occurrences=114,retained_native_placeholders=38,
                stage_modules=39,entries=rows,chunks=reports,groups=cfg['groups'],story=guard,
                target_sha256=file_sha(TARGET),bindings_sha256=file_sha(BINDINGS),
                full_review_sha256=file_sha(REVIEW),layout_review_sha256=file_sha(LAYOUT_REVIEW),
                runtime='pending by user choice')
    return bytes(pool),bytes(out),report

def build(pool,stage):
    cfg=json.loads(TARGET.read_text(encoding='utf8'));require(cfg==prepare(),'Mission frozen target drift')
    return compile_component(pool,stage,cfg)

def previous_inputs():
    path=ROOT/'work/output/SRW Z Special Disc English v0.2.18.iso';disc=Disc(path);exe=disc.read(EXE)
    receipt=json.loads(path.with_suffix('.json').read_text());po=struct.unpack_from('<I',exe,28)[0];es,n=struct.unpack_from('<HH',exe,42)
    for i in range(n):
        s=struct.unpack_from('<8I',exe,po+i*es)
        if s[0]==1 and s[2]<=POOL_BASE<s[2]+s[4]:
            at=s[1]+POOL_BASE-s[2];pool=exe[at:at+receipt['memory']['pool_bytes']];break
    else:raise ValueError('Prior English memory missing')
    stage=disc.read(MEMBER);require(sha(stage)==receipt['members'][MEMBER]['sha256'],'Prior STAGE changed')
    require(sha(exe)==receipt['members'][EXE]['sha256'],'Prior executable changed')
    return pool,stage

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--prepare',action='store_true');ap.add_argument('--write',action='store_true');ap.add_argument('--cache',action='store_true');a=ap.parse_args()
    cfg=prepare();pool,stage=previous_inputs();newpool,rows,chunks=relocate(pool,stage,cfg)
    print(json.dumps(dict(texts=60,occurrences=114,chunks=len(chunks),pool_growth=len(newpool)-len(pool),
        maximum_width=max(max(r['line_widths']) for r in rows),maximum_rows=max(g['rows'] for g in cfg['groups']),
        samples=[{k:r[k] for k in ('id','text','lines')} for r in rows[:2]],
        planned_cache_files=[f'{sha(bytes(ch["after"]))}-{banlz.parse_header(stage[ch["start"]:ch["end"]])[1]:02x}.bin' for ch in chunks.values()][:3]),indent=2),flush=True)
    if not a.write:print('DRY RUN: no files written; compression cache will be verified when requested');return
    if a.prepare:TARGET.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    else:require(json.loads(TARGET.read_text(encoding='utf8'))==cfg,'Prepare mission target first')
    if a.cache:
        _,_,report=compile_component(pool,stage,cfg,write_cache=True)
        (ROOT/'work/analysis/mission-conditions-preflight.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')

if __name__=='__main__':main()
