"""Merge the next independently reviewed batch onto the immutable v0.2.11 input."""
import argparse
import copy
import json
from sp_disc import ROOT, sha, require
from battle_format import unique_sources, BIN_SHA, SEG_SHA
from battle_terms import canonicalize, PATH as SPELLING
from battle_text import layout, width, flatten
from review_battle_candidates import prepare as review_candidates
from battle_placeholder import verify as verify_placeholder
from library_text import CHARS

BASE = ROOT/'work/translation/en'
BASELINE = BASE/'battle_release_0.2.11.json'
BASE_SHA = 'cd7de3c2c9f6215dd68bccfb693e6ae219de00b1865f54a8e48819236102583c'
TERMS = ROOT/'work/glossary/battle-candidate-next-terms.json'
CANDIDATES = BASE/'battle_candidates_00240_00479_reviewed.json'
OUT = BASE/'battle_release_0.2.12.json'
SLICES = ((240,320),(320,400),(400,480))
DEFERRED = {
    323: 'Unresolved coined term; retain native caption pending substantiated meaning review',
    444: 'Production placeholder; retain native bytes. Static suppression evidence is recorded separately; emulator testing remains pending',
}


def candidates():
    for lo,hi in SLICES:
        review=json.loads((BASE/f'battle_candidate_review_{lo:05d}_{hi-1:05d}.json').read_text(encoding='utf-8'))
        require(not review.get('baseline_amendment_proposals',[]),'Unhandled baseline meaning amendment')
    result=review_candidates(baseline_path=BASELINE, slices=SLICES, terms_path=TERMS,
        base_count=1232, baseline_sha=BASE_SHA, deferred_reasons=DEFERRED)
    path=BASE/'battle_candidate_layout_00240_00479.json';raw=path.read_bytes();review=json.loads(raw)
    require(review['source_bin_sha256']==BIN_SHA and review['source_seg_sha256']==SEG_SHA
            and review['base_release_sha256']==BASE_SHA
            and review['source_manifest_sha256']==result['source_manifest_sha256'], 'Stale punctuation supplement sources')
    require(review['author_file']=='battle_candidate_00240_00319.json'
            and review['review_file']=='battle_candidate_review_00240_00319.json'
            and review['author_file_sha256']==result['review_inputs'][review['author_file']]
            and review['review_file_sha256']==result['review_inputs'][review['review_file']], 'Stale punctuation supplement review')
    require(review['reviewed_ids']==[270] and [r['id'] for r in review['entries']]==[270], 'Punctuation supplement inventory')
    edit=review['entries'][0];row=next(r for r in result['entries'] if r['id']==270)
    require(edit['source_sha256']==row['source_sha256'] and edit['before']==row['text']
            and edit['meaning_reviewed'] and edit['reason']
            and edit['text']=='What will be offered up, body or heart?'
            and review['context']['native_occurrences']==row['occurrences'], 'Punctuation supplement preimage/meaning')
    value=canonicalize(edit['text'],unique_sources()[270]['text']);lines=layout(value)
    require(lines is not None and flatten(value)==' '.join(lines)[1:-1], 'Punctuation supplement layout')
    row.update(text=value,lines=lines,line_widths=list(map(width,lines)))
    result['review_inputs'][path.name]=sha(raw)
    result['layout_amendments']=[edit]
    for row in result['entries']:
        if row['layout_approved']:
            require(not(set(''.join(row['lines']))-set(map(chr,CHARS))-{' ','~'}),
                    'Unsupported new caption glyph '+str(row['id']))
    return result


def prepare():
    base_raw=BASELINE.read_bytes(); require(sha(base_raw)==BASE_SHA, 'Frozen v0.2.11 baseline changed')
    result=copy.deepcopy(json.loads(base_raw)); native=unique_sources()
    require(result['source_bin_sha256']==BIN_SHA and result['source_seg_sha256']==SEG_SHA,
            'Baseline native archive binding')
    require(len(result['entries'])==1232 and len({r['id'] for r in result['entries']})==1232
            and result['translated_records']==3429 and not result['deferred_ids'], 'Baseline release inventory')
    # The pinned release contains the earlier source-bound meaning reviews.
    # Re-running those with today's spelling rules would silently rewrite history.
    amendments=[]
    for row in result['entries']:
        source=native[row['id']]
        require(row['source_sha256']==source['source_sha256'] and row['occurrences']==source['occurrences'],
                'Baseline caption native identity')
        require(row['meaning_reviewed'] and row['layout_approved'] and row['lines']==layout(row['text'])
                and row['line_widths']==list(map(width,row['lines'])), 'Baseline caption approval/layout')
        before=row['text']; value=canonicalize(before,source['text'])
        if value==before: continue
        require(row['id'] in (7845,20485,23507,25192) and 'アサキム' in source['text']
                and 'ドーウィン' in source['text'] and value==before.replace('Asakim Dowin','Asakim Dowen'),
                'Unexpected baseline name amendment')
        lines=layout(value)
        require(lines is not None and flatten(value)==' '.join(lines)[1:-1], 'Name amendment layout')
        row.update(text=value,lines=lines,line_widths=list(map(width,lines)))
        amendments.append(dict(id=row['id'],source_sha256=source['source_sha256'],before=before,after=value,
            reason='Source-bound Asakim Dowen spelling, supported by licensed English product text and wiki',
            terms_sha256=sha(TERMS.read_bytes())))
    require({r['id'] for r in amendments}=={7845,20485,23507,25192}, 'Incomplete baseline name pass')
    fresh=candidates()
    require(json.loads(CANDIDATES.read_text(encoding='utf-8'))==fresh, 'Refresh independently reviewed next batch')
    require(fresh['retained_base_ids']==[331,453,454,458,459,464,470]
            and fresh['deferred_ids']==[323,444] and fresh['translated_captions']==231, 'Next batch coverage')
    require(not({r['id'] for r in result['entries']} & {r['id'] for r in fresh['entries']}), 'Duplicate next caption')
    result['historical_review_inputs']=result.pop('review_inputs')
    result['review_inputs']=dict(fresh['review_inputs'], **{CANDIDATES.name:sha(CANDIDATES.read_bytes())})
    result['baseline_release']=dict(file=BASELINE.name,sha256=BASE_SHA)
    result['entries'].extend(fresh['entries'])
    result['review_notes'].extend(fresh['review_notes'])
    result['name_changes'].extend(fresh['name_changes'])
    result['baseline_name_amendments']=amendments
    result['runtime_dispositions']=[verify_placeholder()]
    result.update(spelling_sha256=sha(SPELLING.read_bytes()),candidate_terms_sha256=sha(TERMS.read_bytes()),
        reviewed_captions=len(result['entries']),translated_captions=sum(r['layout_approved'] for r in result['entries']),
        translated_records=sum(len(r['occurrences']) for r in result['entries'] if r['layout_approved']),
        deferred_ids=[r['id'] for r in result['entries'] if not r['layout_approved']],candidate_coverage=fresh['slices'])
    require(result['reviewed_captions']==1465 and result['translated_captions']==1463, 'Release inventory')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidates',action='store_true')
    p.add_argument('--write',action='store_true');a=p.parse_args()
    result=candidates() if a.candidates else prepare();out=CANDIDATES if a.candidates else OUT
    print(json.dumps({k:result[k] for k in ('translated_captions','translated_records','deferred_ids')},indent=2))
    print(json.dumps(dict(amendments=result.get('baseline_name_amendments',[]),
        name_changes=result.get('name_changes',[]) if a.candidates else [],
        samples=[{k:r[k] for k in ('id','text','lines','line_widths','deferred_reason')}
                 for r in result['entries'] if r['id'] in (248,272,313,319,323,325,444,447,471)]),indent=2))
    if a.write:out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no files written')


if __name__=='__main__':main()
