"""Consolidate independently authored/reviewed consecutive caption ranges."""
import argparse
import json
from sp_disc import ROOT, sha, require
from battle_format import BIN_SHA, SEG_SHA, unique_sources
from battle_terms import canonicalize, PATH as SPELLING
from battle_text import layout, width, flatten, LINE_LIMIT, ROWS
from glossary_terms import PATH as GLOSSARY
from library_text import japanese

BASE = ROOT/'work/translation/en'
BASELINE = BASE/'battle_release_0.2.10.json'
MANIFEST = BASE/'battle_reuse.json'
TERMS = ROOT/'work/glossary/battle-candidate-terms.json'
OUTPUT = BASE/'battle_candidates_reviewed.json'
SLICES = ((0,80),(80,160),(160,240))


def prepare(*, baseline_path=BASELINE, slices=SLICES, terms_path=TERMS,
            base_count=1003, baseline_sha=None, deferred_reasons=None):
    sources = unique_sources(); base_raw = baseline_path.read_bytes(); manifest_raw = MANIFEST.read_bytes()
    if baseline_sha is not None: require(sha(base_raw)==baseline_sha, 'Candidate baseline fingerprint')
    baseline = json.loads(base_raw); prior = {r['id']:r for r in baseline['entries']}
    require(len(prior)==base_count and len(prior)==len(baseline['entries'])
            and all(r['meaning_reviewed'] and r['layout_approved'] for r in prior.values()), 'Candidate baseline inventory')
    expected_hashes = dict(source_bin_sha256=BIN_SHA, source_seg_sha256=SEG_SHA,
        source_manifest_sha256=sha(manifest_raw),base_release_sha256=sha(base_raw))
    inputs = {baseline_path.name:sha(base_raw),MANIFEST.name:sha(manifest_raw),
        str(terms_path.relative_to(ROOT)):sha(terms_path.read_bytes())}
    entries=[];retained=[];uncertainties=[];name_changes=[];coverage=[]
    for lo,hi in slices:
        suffix=f'{lo:05d}_{hi-1:05d}.json';author_path=BASE/('battle_candidate_'+suffix)
        review_path=BASE/('battle_candidate_review_'+suffix)
        author_raw=author_path.read_bytes();review_raw=review_path.read_bytes()
        author=json.loads(author_raw);review=json.loads(review_raw)
        inputs[author_path.name]=sha(author_raw);inputs[review_path.name]=sha(review_raw)
        ids=list(range(lo,hi));occurrences=sum(len(sources[i]['occurrences']) for i in ids)
        for doc in (author,review):
            require(all(doc[k]==v for k,v in expected_hashes.items()),'Stale candidate source binding '+suffix)
            require(doc['reviewed_ids']==ids and doc['rows_in_slice']==hi-lo,'Incomplete candidate slice '+suffix)
            require(doc['rows_examined']>=hi-lo and doc['occurrences_examined']>=occurrences,'Insufficient reported source examination '+suffix)
        require(review['author_file_sha256']==sha(author_raw),'Stale independent candidate review '+suffix)
        require([r['id'] for r in author['entries']]==ids,'Candidate author inventory '+suffix)
        corrections={r['id']:r for r in review['corrections']}
        unresolved=set(review['unresolved_ids'])
        require(len(corrections)==len(review['corrections']) and set(corrections)<=set(ids),'Duplicate/unknown candidate correction')
        require(len(unresolved)==len(review['unresolved_ids']) and unresolved<=set(ids),'Invalid unresolved candidate IDs')
        for row in author['entries']:
            i=row['id'];source=sources[i]
            require(row['source_sha256']==source['source_sha256'],'Candidate native identity '+str(i))
            require(row['retained_from_base']==(i in prior),'Candidate baseline classification '+str(i))
            value=row['text'];fix=corrections.get(i)
            if fix:
                require(fix['source_sha256']==source['source_sha256'] and fix['before']==value and fix['reason'], 'Stale candidate correction '+str(i))
                value=fix['text']
            if i in prior:
                require(value==row['text']==prior[i]['text'] and i not in unresolved,
                    'Previously released text needs separate reviewed amendment '+str(i))
                retained.append(i);continue
            if value is None:
                require(i in unresolved,'Unexplained unresolved candidate '+str(i))
            require(i not in unresolved or value is None,'Unresolved candidate contains a proposed release text')
            if value is not None:
                require(isinstance(value,str) and value.strip() and not japanese(value)
                        and all(ord(c)>=32 for c in value),'Invalid candidate English '+str(i))
                require(value.count('\\n')==source['text'].count('\\n'),'Candidate changed native draft row breaks '+str(i))
                before=value;value=canonicalize(value,source['text'])
                if value!=before:name_changes.append(dict(id=i,before=before,after=value))
                lines=layout(value)
                if lines is not None:require(flatten(value)==' '.join(lines)[1:-1],'Candidate layout changed meaning '+str(i))
            else:lines=None
            entries.append(dict(id=i,review_set='candidate',review_id=i,source_sha256=source['source_sha256'],
                occurrences=source['occurrences'],text=value,meaning_reviewed=value is not None,
                layout_approved=lines is not None,lines=lines,line_widths=list(map(width,lines)) if lines else [],
                deferred_reason=None if lines else (deferred_reasons or {}).get(i,
                    'Unresolved native meaning' if value is None else 'Full meaning exceeds two rows; retain native caption')))
        uncertainties.extend(dict(slice=[lo,hi],stage='author',note=n) for n in author['uncertainties'])
        uncertainties.extend(dict(slice=[lo,hi],stage='review',note=n) for n in review['uncertainties'])
        coverage.append(dict(start=lo,end=hi,rows=hi-lo,native_occurrences=occurrences,
            author_rows_examined=author['rows_examined'],reviewer_rows_examined=review['rows_examined']))
    expected=set(i for lo,hi in slices for i in range(lo,hi))-set(prior)
    require({r['id'] for r in entries}==expected and len(entries)==len(expected),'Candidate consolidation coverage')
    return dict(schema_version=1,**expected_hashes,review_inputs=inputs,entries=entries,
        retained_base_ids=retained,slices=coverage,meaning_reviewed=sum(r['meaning_reviewed'] for r in entries),
        translated_captions=sum(r['layout_approved'] for r in entries),
        translated_records=sum(len(r['occurrences']) for r in entries if r['layout_approved']),
        deferred_ids=[r['id'] for r in entries if not r['layout_approved']],name_changes=name_changes,
        glossary_sha256=sha(GLOSSARY.read_bytes()),spelling_sha256=sha(SPELLING.read_bytes()),
        candidate_terms_sha256=sha(terms_path.read_bytes()),
        line_limit=LINE_LIMIT,row_limit=ROWS,review_notes=uncertainties,runtime='pending by user choice')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args()
    result=prepare();print(json.dumps({k:result[k] for k in ('meaning_reviewed','translated_captions','translated_records','deferred_ids','name_changes','slices')},indent=2))
    samples = [r for r in result['entries'] if r['id'] in (0,1,2,24,81,99,104,105,182,207,216)
               or not r['layout_approved']]
    print(json.dumps([{k:r[k] for k in ('id','text','lines','line_widths','deferred_reason')}
                     for r in samples],indent=2))
    if args.write:OUTPUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no files written')


if __name__=='__main__':main()
