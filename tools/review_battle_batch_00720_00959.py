"""Consolidate independently reviewed 720-959 captions without changing v0.2.13."""
import argparse
import json
from sp_disc import ROOT, sha, require
from battle_format import BIN_SHA, SEG_SHA, unique_sources
from battle_terms import canonicalize, PATH as SPELLING
from battle_text import layout, width, flatten, LINE_LIMIT, ROWS
from glossary_terms import PATH as GLOSSARY
from library_text import CHARS, japanese

BASE = ROOT/'work/translation/en'
BASELINE = BASE/'battle_release_0.2.13.json'
BASE_SHA = '3af2752da15dca8e77e41e32da02323d14c09ab205b379f0a81f092836bfea8a'
MANIFEST = BASE/'battle_reuse.json'
MANIFEST_SHA = '091423d6dbc663aac2f0c4caff74c451b293a7af768c04ae7d4955ed04d91ba3'
TERMS = ROOT/'work/glossary/battle-candidate-00720-00959-terms.json'
TERMS_SHA = '21497e930fc196dd5093b8eba4b4cff9ecd353f8c1bffa7f898cc356a15e4c10'
OUT = BASE/'battle_candidates_00720_00959_reviewed.json'
SLICES = ((720,800), (800,880), (880,960))
AUTHOR_HASHES = {
    720: '1bec23c3445b2890b0a113583f96198e5d57120ff279004b2125e9bbb6c1e9aa',
    800: 'c810374917ac09655a93565f516da06acbdcc59c5558cfeabaceaf6ba5e5b431',
    880: '1a1312fe4ab8c4477aaf4be1cd32611f7868451e542c4f2aa0583f40160fa144',
}
REVIEW_HASHES = {
    720: '442d23398a0a4914758abe3e59fc3836ea742e6e006839870578cc6f4a3aea3e',
    800: '5a6229f4ca5f7acf9a58a27d11af01431696c5560112484007ebc564ff9514d4',
    880: 'ba7aba1f188cff253db9e30ebf3065d1d3cdaf4df342cbbc545648c3f8a03d4c',
}
SUPPLEMENT_HASHES = {
    'battle_candidate_layout_00754_00768.json': '35a3743fd3ce0bc9c21d0aab34eb716af814ad5cf94f4795d2900f735f5a81b5',
    'battle_candidate_layout_00948.json': '40d2f0ba0d3d2aa645180bd6037c53d0645e8406a6f372c0c39f0958f5f15a17',
}
SUPPLEMENTS = (('battle_candidate_layout_00754_00768.json',720,[754,768]),
               ('battle_candidate_layout_00948.json',880,[948]))


def read(path):
    raw = path.read_bytes()
    return json.loads(raw), sha(raw)


def prepare():
    sources = unique_sources()
    base, digest = read(BASELINE)
    require(digest == BASE_SHA, 'Frozen v0.2.13 baseline changed')
    require(sha(MANIFEST.read_bytes()) == MANIFEST_SHA, 'Source manifest changed')
    require(sha(TERMS.read_bytes()) == TERMS_SHA, 'Batch terminology changed')
    require(base['source_bin_sha256'] == BIN_SHA and base['source_seg_sha256'] == SEG_SHA,
            'Baseline archive binding')
    prior = {r['id']:r for r in base['entries']}
    require(len(prior) == len(base['entries']) == 1681 and base['translated_captions'] == 1678
            and base['translated_records'] == 4323 and base['deferred_ids'] == [323,444,600],
            'Baseline inventory/dispositions')
    for i,row in prior.items():
        require(row['source_sha256'] == sources[i]['source_sha256']
                and row['occurrences'] == sources[i]['occurrences'], 'Baseline source identity')
        if i in (323,444,600):
            require(row['text'] is None and row['meaning_reviewed'] is False
                    and row['layout_approved'] is False and row['lines'] is None
                    and row['deferred_reason'], 'Baseline deferral changed')
        else:
            require(row['meaning_reviewed'] is True and row['layout_approved'] is True
                    and row['lines'] == layout(row['text'])
                    and row['line_widths'] == list(map(width,row['lines'])), 'Baseline approval/layout')
    bindings = dict(source_bin_sha256=BIN_SHA,source_seg_sha256=SEG_SHA,
                    source_manifest_sha256=MANIFEST_SHA,base_release_sha256=BASE_SHA)
    inputs = {BASELINE.name:BASE_SHA, MANIFEST.name:MANIFEST_SHA,
              str(TERMS.relative_to(ROOT)):TERMS_SHA}
    pending=[];retained=[];notes=[];coverage=[]
    for lo,hi in SLICES:
        suffix=f'{lo:05}_{hi-1:05}.json'
        ap=BASE/('battle_candidate_'+suffix);rp=BASE/('battle_candidate_review_'+suffix)
        author,ah=read(ap);review,rh=read(rp)
        require(ah == AUTHOR_HASHES[lo], 'Frozen author changed')
        require(rh == REVIEW_HASHES[lo], 'Frozen independent review changed')
        inputs.update({ap.name:ah,rp.name:rh})
        ids=list(range(lo,hi));occurrences=sum(len(sources[i]['occurrences']) for i in ids)
        for doc in (author,review):
            require(all(doc.get(k)==v for k,v in bindings.items()),'Stale source binding '+suffix)
            require(doc['reviewed_ids']==ids and doc['rows_in_slice']==80,'Incomplete review '+suffix)
            require(doc['rows_examined']>=80 and doc['occurrences_examined']>=occurrences,
                    'Insufficient reported source reading '+suffix)
        require(review['author_file_sha256']==ah,'Stale independent review '+suffix)
        require(not review.get('baseline_amendment_proposals',[]),'Unhandled baseline meaning amendment')
        require([r['id'] for r in author['entries']]==ids,'Author inventory')
        fixes={r['id']:r for r in review['corrections']};unresolved=set(review['unresolved_ids'])
        require(len(fixes)==len(review['corrections']) and set(fixes)<=set(ids),'Correction inventory')
        require(len(unresolved)==len(review['unresolved_ids']) and unresolved<=set(ids),'Unresolved inventory')
        for row in author['entries']:
            i=row['id'];source=sources[i];value=row['text']
            require(row['source_sha256']==source['source_sha256'],'Author native identity')
            require(row['retained_from_base'] is (i in prior),'Invalid retention classification')
            if i in fixes:
                fix=fixes[i]
                require(fix['source_sha256']==source['source_sha256'] and fix['before']==value
                        and fix['reason'],'Stale meaning correction')
                value=fix['text']
            if i in prior:
                require(value==row['text']==prior[i]['text'] and i not in unresolved,
                        'Baseline amendment requires separate review')
                retained.append(i);continue
            require((value is None)==(i in unresolved),'Unexplained/contradictory deferral')
            if value is not None:
                require(isinstance(value,str) and value.strip() and not japanese(value)
                        and all(ord(c)>=32 for c in value),'Invalid English')
                require(value.count('\\n')==source['text'].count('\\n'),'Draft break count')
            pending.append(dict(id=i,source_sha256=source['source_sha256'],
                                occurrences=source['occurrences'],text=value))
        notes.extend(dict(slice=[lo,hi],stage=stage,note=n)
                     for stage,doc in (('author',author),('review',review)) for n in doc['uncertainties'])
        coverage.append(dict(start=lo,end=hi,rows=80,native_occurrences=occurrences,
                             author_rows_examined=author['rows_examined'],reviewer_rows_examined=review['rows_examined']))
    indexed={r['id']:r for r in pending};amendments=[]
    for filename,lo,ids in SUPPLEMENTS:
        doc,dh=read(BASE/filename)
        require(dh == SUPPLEMENT_HASHES[filename], 'Frozen compact review changed')
        suffix=f'{lo:05}_{lo+79:05}.json'
        af='battle_candidate_'+suffix;rf='battle_candidate_review_'+suffix
        require(all(doc.get(k)==v for k,v in bindings.items()),'Stale compact-review sources')
        require(doc['author_file']==af and doc['review_file']==rf
                and doc['author_file_sha256']==inputs[af] and doc['review_file_sha256']==inputs[rf],
                'Stale compact-review inputs')
        require(doc['reviewed_ids']==ids and [r['id'] for r in doc['entries']]==ids,'Compact review inventory')
        for edit in doc['entries']:
            target=indexed[edit['id']]
            require(edit['source_sha256']==target['source_sha256'] and edit['before']==target['text']
                    and edit['meaning_reviewed'] is True and edit['reason'],'Compact approval/preimage')
            require(edit['occurrences']==target['occurrences'],'Compact native occurrences')
            require(isinstance(edit['text'],str) and edit['text'].strip() and not japanese(edit['text'])
                    and all(ord(c)>=32 for c in edit['text']),'Invalid compact English')
            require(edit['text'].count('\\n')==sources[edit['id']]['text'].count('\\n'),'Compact break count')
            target['text']=edit['text'];amendments.append(edit)
        inputs[filename]=dh
        notes.extend(dict(stage='compact',note=n) for n in doc.get('uncertainties',[]))
    changes=[]
    for row in pending:
        value=row['text'];lines=None
        if value is not None:
            changed=canonicalize(value,sources[row['id']]['text'])
            if changed!=value:changes.append(dict(id=row['id'],before=value,after=changed))
            value=row['text']=changed;lines=layout(value)
            if lines is not None:
                require(isinstance(lines,list) and 1 <= len(lines) <= ROWS
                        and all(isinstance(line,str) and line.strip() for line in lines),
                        'Invalid caption row structure')
                require(all(width(line) <= LINE_LIMIT for line in lines), 'Caption row exceeds width limit')
                require(flatten(value)==' '.join(lines)[1:-1],'Layout changed words')
                require(not(set(''.join(lines))-set(map(chr,CHARS))-{' ','~'}),'Unsupported caption glyph')
        row.update(review_set='candidate',review_id=row['id'],meaning_reviewed=value is not None,
                   layout_approved=lines is not None,lines=lines,line_widths=list(map(width,lines)) if lines else [],
                   deferred_reason=None if lines else ('Unresolved meaning; preserve native text' if value is None
                                                     else 'Full meaning exceeds two rows; preserve native text'))
    require(set(indexed)==set(range(720,960))-set(prior) and len(pending)==239 and retained==[807],
            'Consolidated/retained inventory')
    return dict(schema_version=1,**bindings,review_inputs=inputs,entries=pending,retained_base_ids=retained,
                preserved_baseline_deferred_ids=[323,444,600],slices=coverage,review_notes=notes,
                meaning_reviewed=sum(r['meaning_reviewed'] for r in pending),
                translated_captions=sum(r['layout_approved'] for r in pending),
                translated_records=sum(len(r['occurrences']) for r in pending if r['layout_approved']),
                deferred_ids=[r['id'] for r in pending if not r['layout_approved']],name_changes=changes,
                layout_amendments=amendments,glossary_sha256=sha(GLOSSARY.read_bytes()),
                spelling_sha256=sha(SPELLING.read_bytes()),candidate_terms_sha256=TERMS_SHA,
                line_limit=LINE_LIMIT,row_limit=ROWS,status='Unreleased reviewed candidates; no ISO changes',
                runtime='pending by user choice')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true')
    args=parser.parse_args();result=prepare()
    print(json.dumps({k:result[k] for k in ('translated_captions','translated_records','deferred_ids','name_changes','slices')},indent=2))
    print(json.dumps([{k:r[k] for k in ('id','text','lines','line_widths')}
                      for r in result['entries'] if r['id'] in (725,754,768,837,846,854,855,884,906,931,935,948)],indent=2))
    if args.write:
        require(not OUT.exists(),'Refusing to overwrite reviewed candidates')
        OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no files written')


if __name__=='__main__':main()
