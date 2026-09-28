"""Read back every mission-condition pointer from the completed disc."""
import json,struct
from sp_disc import ROOT,Disc,SOURCE,decode,sha,file_sha,require
from inspect_mission_conditions import inventory,BASE
from glossary_terms import canonicalize
from library_text import text,CHARS
from menu_encoding import menu_encode,TOKENS
from save_summary_text import WIDTHS
from stage_ui_guard import check


def line_width(value):
    return sum(WIDTHS[CHARS.index(ord(c))]+2 if ord(c) in CHARS else 13 if c==' ' else 24 for c in value)


def layout_check(value,lines):
    require(lines and ' '.join(lines).split()==value.split(),'Condition layout lost words')
    require(all('\n' not in s and line_width(s)<=460 for s in lines),'Condition horizontal overflow')
    require(len(lines)<=4,'Condition vertical overflow')


def audit(disc,exe,loaded,report):
    folder=ROOT/'work/translation/en';binding=ROOT/'work/ui/mission-conditions/native-inventory.json'
    paths={'target_sha256':folder/'mission_conditions.json','bindings_sha256':binding,
           'full_review_sha256':folder/'mission_conditions_review.json',
           'layout_review_sha256':folder/'mission_conditions_layout_review.json'}
    for key,path in paths.items():require(file_sha(path)==report[key],'Mission audit input drift: '+key)
    cfg=json.loads(paths['target_sha256'].read_text(encoding='utf8'))
    inv=json.loads(binding.read_text(encoding='utf8'));require(inv==inventory(),'Native condition initializer/table binding drift')
    full=json.loads(paths['full_review_sha256'].read_text(encoding='utf8'))
    review=json.loads(paths['layout_review_sha256'].read_text(encoding='utf8'))
    require(full['entries_examined']==full['entries_in_slice']==review['entries_examined']==review['entries_in_slice']==61,
            'Incomplete mission meaning review')
    require(review['full_review_sha256']==file_sha(paths['full_review_sha256']) and
            review['bindings_sha256']==cfg['bindings_sha256']==file_sha(binding) and
            review['layout_draft_sha256']==file_sha(folder/'mission_conditions_layout_draft.json'),
            'Mission layout review ancestry')
    require(full['draft_sha256']==file_sha(folder/'mission_conditions_draft.json') and
            full['bindings_sha256']==file_sha(binding),'Mission full review ancestry')
    require(cfg['full_review_sha256']==report['full_review_sha256'] and
            cfg['layout_review_sha256']==report['layout_review_sha256'] and
            cfg['spelling_sha256']==file_sha(ROOT/'work/glossary/english.json'),'Mission configuration ancestry')
    expected={r['id']:r for r in inv['entries']};approved={r['id']:r for r in review['entries']}
    target={r['id']:r for r in cfg['entries']};actual={r['id']:r for r in report['entries']}
    require(set(expected)==set(approved)==set(target)==set(actual) and
            len(expected)==len(approved)==len(cfg['entries'])==len(report['entries'])==61,'Mission text coverage')
    stage=disc.read('DATA/STAGE.BIN');native=Disc(SOURCE).read('DATA/STAGE.BIN')
    current={};sources={};chunk_reports={r['chunk']:r for r in report['chunks']}
    require(set(chunk_reports)=={r['chunk'] for r in inv['chunks']} and len(report['chunks'])==39,'Mission module coverage')
    for ch in inv['chunks']:
        i=ch['chunk'];lo,hi=ch['start'],ch['end'];current[i],used=decode(stage[lo:hi]);sources[i]=decode(native[lo:hi])[0]
        r=chunk_reports[i]
        require((r['start'],r['end'],r['decoded_bytes'])==(lo,hi,len(current[i])) and
                sha(current[i])==r['decoded_sha256'],'Final mission chunk binding')
        require(not any(stage[lo+used:hi]) and r['compressed_bytes']==used and r['headroom']==hi-lo-used,
                'Mission chunk allocation/padding')
    translated=0;occurrences=0;hidden=0;seen=set();bysha={}
    for key,source in expected.items():
        row=actual[key];frozen=target[key];decision=approved[key]
        require(decision['verdict'] in ('pass','fixed') and row['text']==canonicalize(decision['text']),
                'Mission text differs from approved meaning')
        require(all(row[k]==v for k,v in frozen.items()),'Mission report differs from frozen target')
        require(row['source_sha256']==source['source_sha256'] and row['occurrences']==source['occurrences'],
                'Mission occurrence/source identity')
        retain=source['source']=='？？？';require(row['retain_native']==retain,'Mission placeholder policy')
        layout_check(row['text'],row['lines'])
        require(row['line_widths']==list(map(line_width,row['lines'])),'Mission metric mismatch')
        bysha[source['source_sha256']]=row
        if retain:require('relocated_address' not in row,'Hidden condition was revealed')
        else:
            address=row['relocated_address'];at=loaded(address);value='\n'.join(row['lines']);encoded=menu_encode(value)+b'\0'
            require(not TOKENS.search(value),'Unexpected condition text command')
            require(loaded(address+len(encoded)-1)==at+len(encoded)-1 and exe[at:at+len(encoded)]==encoded,
                    'Mission English memory readback')
            require(text(exe[at:at+len(encoded)-1])==value,'Mission displayed glyph readback')
            translated+=1
        for o in source['occurrences']:
            i=o['chunk'];p=o['pointer_site'];off=o['offset'];require((i,p) not in seen,'Duplicate mission pointer');seen.add((i,p))
            require(struct.unpack_from('<I',sources[i],p)[0]==BASE+off and
                    sha(sources[i][off:].split(b'\0')[0])==source['source_sha256'],'Native mission pointer ownership')
            wanted=BASE+off if retain else address
            require(struct.unpack_from('<I',current[i],p)[0]==wanted,'Final mission pointer readback')
            if retain:hidden+=1
            else:occurrences+=1
    groups=[]
    for ch in inv['chunks']:
        for group in ch['tables']:
            rows=sum(len(bysha[e['source_sha256']]['lines']) for e in group['entries'])
            require(rows<=4,'Combined condition group exceeds renderer slots')
            groups.append(dict(chunk=ch['chunk'],kind=group['kind'],rows=rows))
    require(groups==cfg['groups']==report['groups'],'Mission group layout mismatch')
    require((translated,occurrences,hidden)==(60,114,38),'Mission translated/hidden coverage')
    guard=check(stage,True)
    require(guard==report['story'] and guard['unchanged_compressed_story_chunks']==28 and
            guard['allowed_display_pointer_words']==141,'Mission story protection coverage')
    return dict(texts_read_back=translated,condition_pointers_read_back=occurrences,native_hidden_placeholders=hidden,
                stage_modules=39,groups_checked=len(groups),maximum_group_rows=max(r['rows'] for r in groups),
                maximum_line_width=max(max(r['line_widths']) for r in actual.values()),
                thresholds_and_punctuation_read_back=True,story=guard)
