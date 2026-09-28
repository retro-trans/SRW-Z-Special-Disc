"""Merge source and layout reviews, then apply glossary spelling and fit gates."""
import argparse
import json
from sp_disc import ROOT, sha, require
from glossary_terms import canonicalize, PATH
from save_summary_text import wrap, LINE_LIMIT, ROWS

FILES=('save_summaries.json','save_summaries_review.json',
       'save_summaries_layout.json','save_summaries_layout_review.json')
OUT=ROOT/'work/translation/en/save_summaries_reviewed.json'


def prepare():
    inputs={};data=[]
    for name in FILES:
        raw=(ROOT/'work/translation/en'/name).read_bytes();inputs[name]=sha(raw);data.append(json.loads(raw))
    base,full_review,layout,review=data
    require(full_review['reviewed_draft_sha256']==inputs[FILES[0]],'Stale full recap review')
    require(review['reviewed_layout_sha256']==inputs[FILES[2]],'Stale recap layout review')
    require(layout['base_draft_sha256']==inputs[FILES[0]] and layout['source_sha256']==base['source_sha256'],'Stale recap layout draft')
    for obj in (base,full_review,review):
        require(obj['source_sha256']==base['source_sha256'],'Recap review source mismatch')
        require(sorted(obj['reviewed_ids'])==list(range(66)),'Incomplete recap meaning review')
    require([r['id']for r in base['entries']]==list(range(66)),'Native recap inventory')
    require([r['id']for r in layout['entries']]==list(range(66)),'Layout recap inventory')
    require(set(map(int,review['corrections'])).issubset(range(66)),'Recap review outside inventory')
    rejected=set(review.get('rejected_ids',[]));entries=[];deferred=[];duplicates={}
    for source,proposed in zip(base['entries'],layout['entries']):
        i=source['id'];edit=review['corrections'].get(str(i))
        value=canonicalize(edit['text']if edit else proposed['text']);value=' '.join(value.split())
        lines,widths=wrap(value,strict=False);approved=len(lines)<=ROWS and i not in rejected
        require(source['source_sha256']==proposed['source_sha256'],'Layout recap source binding')
        row=dict(source);row.update(text=value,lines=lines,line_widths=widths,meaning_reviewed=i not in rejected,
            layout_approved=approved,review_reason=edit['reason']if edit else 'Passed independent native-source layout review')
        if not approved:
            row['deferred_reason']='Meaning requires further review; keep native record'if i in rejected else 'Full meaning does not fit three lines at 520 units; keep native record'
            deferred.append(i)
        digest=source['source_sha256']
        require(digest not in duplicates or duplicates[digest]==(value,approved),'Duplicate recap translation differs')
        duplicates[digest]=(value,approved);entries.append(row)
    return dict(schema_version=1,source_sha256=base['source_sha256'],review_inputs=inputs,
        glossary_sha256=sha(PATH.read_bytes()),reviewed_ids=list(range(66)),entries=entries,
        translated_records=66-len(deferred),deferred_ids=deferred,
        review_notes=full_review.get('uncertainties',[])+review.get('uncertainties',[]),
        layout=dict(line_limit_font_units=LINE_LIMIT,row_limit=ROWS,runtime_acceptance='pending by user choice'))


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    result=prepare()
    print(json.dumps(dict(reviewed=66,translated_records=result['translated_records'],deferred_ids=result['deferred_ids'],
        samples=[{k:r[k]for k in ('id','text','lines','line_widths','layout_approved')}for r in result['entries']if r['id']in (0,2,3,13,27,50,65)]),indent=2))
    if args.write:OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no files written')


if __name__=='__main__':main()
