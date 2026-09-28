"""Bind active English caption drafts to SP source hashes and audited donor records.

Default is a dry run. Exports English/metadata only, never a Japanese corpus.
The result is a candidate inventory, not permission to patch unreviewed lines.
"""
import argparse
import collections
import json
from sp_disc import ROOT,Disc,sha,require,file_sha
from battle_format import BIN,SEG,BIN_SHA,SEG_SHA,blocks,native_layout,indexed,normalize,unique_sources
from library_text import ORIGINAL,DONOR,text,japanese

WORK=ORIGINAL.parent/'analysis/srvc_work.json'
ENGLISH=ORIGINAL.parent/'analysis/srvc_en.json'
EXPORT=ROOT/'work/translation/en/battle_reuse.json'
NEW=ROOT/'work/translation/en/battle_new_sources.json'


def prepare():
    active={};work=json.loads(WORK.read_text(encoding='utf-8'));english=json.loads(ENGLISH.read_text(encoding='utf-8'))
    for row in work:
        value=english.get(str(row['i']))
        if not value:continue
        digest=sha(row['jp'].encode('cp932'))
        require(digest not in active or active[digest]['text']==value,'Conflicting active battle source')
        require(isinstance(value,str) and value.strip() and not japanese(value),'Invalid active battle English')
        active[digest]=dict(work_id=row['i'],text=value)
    native_bin=(ORIGINAL/'BTL_SRVC.BIN').read_bytes();native_seg=(ORIGINAL/'BTL_SRVC.SEG').read_bytes()
    donor=Disc(DONOR,True);donor_bin=donor.read(BIN);donor_seg=donor.read(SEG)
    _,before=blocks(native_bin,native_seg);_,after=blocks(donor_bin,donor_seg)
    require(len(before)==len(after)==353,'Main caption donor block inventory')
    answers=collections.defaultdict(lambda:collections.defaultdict(list));unquoted=[]
    for i,(a,b)in enumerate(zip(before,after)):
        parsed=native_layout(a,0x4f00);records=parsed['rows']
        require(a[:8]==b[:8],'Main caption donor header changed')
        if not records:continue
        require(a[:parsed['index']]==b[:parsed['index']],'Main caption donor prefix changed')
        translated=indexed(b,parsed['index'],len(records))
        for old,new in zip(records,translated):
            require(old['metadata']==new['metadata'],'Main caption donor metadata changed')
            value=text(new['raw']).strip()
            quoted=value.startswith('"') and value.endswith('"')
            require(quoted or not(value.startswith('"') or value.endswith('"')),'Donor caption has partial quote wrapper')
            if quoted:value=value[1:-1].strip()
            else:unquoted.append(dict(block=i,record=old['record']))
            require(value and not japanese(value) and all(ord(c)>=32 for c in value),'Invalid donor caption')
            digest=sha(normalize(old['raw']).encode('cp932'))
            answers[digest][value].append(dict(block=i,record=old['record'],metadata=old['metadata'],
                native_raw_sha256=sha(old['raw']),donor_raw_sha256=sha(new['raw']),quote_wrapper=quoted))
    entries=[];new_rows=[];counts=collections.Counter()
    for source in unique_sources():
        digest=source['source_sha256'];candidate=active.get(digest);options=answers.get(digest,{})
        row={k:v for k,v in source.items()if k!='text'}
        row['source_line_breaks']=source['text'].count('\\n')
        row['donor_options']=[dict(text=value,bindings=bindings)for value,bindings in sorted(options.items())]
        if candidate:
            row.update(candidate)
            row['status']='donor-matched candidate'if candidate['text']in options else 'active draft differs from donor; meaning review required'
            row['english_line_breaks']=candidate['text'].count('\\n')
            if row['source_line_breaks']!=row['english_line_breaks']:counts['active_line_break_mismatches']+=1
        else:
            row.update(text=None,status='new translation required')
            new_rows.append(dict(id=len(new_rows),source_id=source['id'],source_sha256=digest,
                source_line_breaks=row['source_line_breaks'],occurrences=source['occurrences'],
                donor_options=row['donor_options']))
        counts[row['status']]+=1
        counts['indexed_records']+=len(source['occurrences'])
        entries.append(row)
    require(len(entries)==25522 and len(new_rows)==123 and counts['indexed_records']==59262,'SP caption candidate inventory drift')
    locks=dict(source_bin_sha256=BIN_SHA,source_seg_sha256=SEG_SHA,main_native_bin_sha256=sha(native_bin),
        main_native_seg_sha256=sha(native_seg),donor_bin_sha256=sha(donor_bin),donor_seg_sha256=sha(donor_seg),
        active_work_sha256=file_sha(WORK),active_english_sha256=file_sha(ENGLISH))
    report=dict(schema_version=1,status='Candidate inventory; meaning, names, layout and playback checks pending',
        locks=locks,counts=dict(counts),unquoted_donor_records=unquoted,entries=entries)
    pending=dict(schema_version=1,source_bin_sha256=BIN_SHA,source_seg_sha256=SEG_SHA,
        active_work_sha256=locks['active_work_sha256'],active_english_sha256=locks['active_english_sha256'],
        note='English authoring input with native coordinates and full SHA256; read Japanese from the clean image in memory only',entries=new_rows)
    return report,pending


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    report,pending=prepare()
    print(json.dumps(dict(counts=report['counts'],locks=report['locks'],new_entries=len(pending['entries']),
        samples=[{k:r[k]for k in ('id','status','text','source_line_breaks')}for r in report['entries'][:4]],
        new_samples=pending['entries'][:2]),indent=2))
    if a.write:
        EXPORT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        NEW.write_text(json.dumps(pending,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no files written')


if __name__=='__main__':main()
