"""Merge the next reviewed caption slices into the current SRVC archive."""
import json,struct
from collections import defaultdict
from sp_disc import ROOT,require,sha,file_sha
from battle_format import native,unique_sources,blocks,indexed,BIN,SEG,BIN_SHA,SEG_SHA
from review_battle_batch_00960_01119 import prepare,MANIFEST_SHA,BASE_SHA
from battle_terms import canonicalize
from battle_text import layout,width
from menu_encoding import menu_encode
from library_text import text

BASE=ROOT/'work/translation/en'


def candidates():
    first=prepare();sources=unique_sources();rows=list(first['entries'])
    author_path=BASE/'battle_candidate_01120_01199.json';review_path=BASE/'battle_candidate_review_01120_01199.json'
    compact_path=BASE/'battle_candidate_compact_review_01120_01199.json'
    a=json.loads(author_path.read_text(encoding='utf-8'));r=json.loads(review_path.read_text(encoding='utf-8'))
    c=json.loads(compact_path.read_text(encoding='utf-8'));prior=json.loads((BASE/'battle_release_0.2.14.json').read_text(encoding='utf-8'))
    prior={x['id']:x for x in prior['entries']};ids=list(range(1120,1200))
    for doc in (a,r,c):
        require(doc['source_bin_sha256']==BIN_SHA and doc['source_seg_sha256']==SEG_SHA and
            doc['source_manifest_sha256']==MANIFEST_SHA and doc['base_release_sha256']==BASE_SHA,'Caption review source drift')
    require(a['reviewed_ids']==r['reviewed_ids']==ids and [x['id'] for x in a['entries']]==ids,'Caption slice coverage')
    require(r['author_file_sha256']==file_sha(author_path) and not r['unresolved_ids'] and not r['baseline_amendment_proposals'],'Unresolved or stale battle review')
    require(c['author_file_sha256']==file_sha(author_path) and c['review_file_sha256']==file_sha(review_path),'Stale compact review')
    fixes={x['id']:x for x in r['corrections']};compact={x['id']:x for x in c['entries']}
    require(set(compact)==set(c['reviewed_ids'])=={1122},'Compact correction inventory')
    for row in a['entries']:
        i=row['id'];source=sources[i];value=row['text']
        require(row['source_sha256']==source['source_sha256'],'Battle identity')
        if i in fixes:
            fix=fixes[i];require(fix['before']==value and fix['source_sha256']==source['source_sha256'],'Stale correction');value=fix['text']
        if i in prior:
            require(row['retained_from_base'] and value==prior[i]['text'],'Changed existing caption');continue
        require(not row['retained_from_base'],'Invalid retained caption')
        if i in compact:
            fix=compact[i];require(fix['before']==value and fix['source_sha256']==source['source_sha256'] and fix['occurrences']==source['occurrences'] and fix['meaning_reviewed'],'Stale compact correction');value=fix['text']
        value=canonicalize(value,source['text']);lines=layout(value)
        require(lines and max(map(width,lines))<=460,'Caption does not fit')
        rows.append(dict(id=i,source_sha256=source['source_sha256'],occurrences=source['occurrences'],text=value,lines=lines,meaning_reviewed=True,layout_approved=True))
    require(len({r['id'] for r in rows})==len(rows),'Duplicate battle candidates')
    return rows,dict(first['review_inputs'],**{p.name:file_sha(p) for p in (author_path,review_path,compact_path)})


def build(data,seg):
    selected,inputs=candidates();sources=unique_sources();parsed=native()[4]
    offsets,chunks=blocks(data,seg);replacements=defaultdict(dict)
    for row in selected:
        source=sources[row['id']];require(row['source_sha256']==source['source_sha256'] and row['occurrences']==source['occurrences'],'Battle source binding')
        encoded=menu_encode('\\n'.join(row['lines']))
        require(row['meaning_reviewed'] and row['layout_approved'] and text(encoded)=='\\n'.join(row['lines']), 'Caption approval or encoding')
        require(len(encoded)+1<=96,'Caption exceeds unchanged buffer')
        for o in source['occurrences']:
            bank,record=o['block'],o['record'];p=parsed[bank]
            existing=indexed(chunks[bank],p['index'],len(p['rows']))[record]
            require(existing['raw']==p['rows'][record]['raw'] and existing['metadata']==o['metadata'],'Caption is already modified')
            replacements[bank][record]=encoded
    result=[];new_offsets=[0];changed=0
    for bank,chunk in enumerate(chunks):
        changes=replacements.get(bank,{})
        if not changes:result.append(chunk);new_offsets.append(new_offsets[-1]+len(chunk));continue
        p=parsed[bank];before=indexed(chunk,p['index'],len(p['rows']));out=bytearray(chunk);dedup={}
        if out[-1]:out.append(0)
        for record,value in sorted(changes.items()):
            if value not in dedup:dedup[value]=len(out);out.extend(value+b'\0')
            struct.pack_into('<I',out,p['index']+record*8+4,dedup[value]-p['pool'])
        out.extend(bytes((-len(out))%16));after=indexed(out,p['index'],len(p['rows']));restore=bytearray(out[:len(chunk)])
        for record in changes:
            at=p['index']+record*8+4;restore[at:at+4]=chunk[at:at+4]
        require(restore==chunk,'Unrelated caption bank change')
        for old,new in zip(before,after):
            require(old['metadata']==new['metadata'] and new['raw']==changes.get(old['record'],old['raw']),'Caption/voice readback')
        changed+=len(changes);result.append(bytes(out));new_offsets.append(new_offsets[-1]+len(out))
    data=b''.join(result);seg=struct.pack('<%dI'%len(new_offsets),*new_offsets)
    require(blocks(data,seg)[1]==result,'Caption archive readback')
    return data,seg,dict(entries=selected,review_inputs=inputs,new_captions=len(selected),changed_records=changed,
        changed_banks=sorted(replacements),bin_sha256=sha(data),seg_sha256=sha(seg),emulator='pending')
