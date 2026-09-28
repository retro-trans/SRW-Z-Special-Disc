"""Apply narration meaning and compact reviews before glossary spelling and layout."""
import argparse
import json
from sp_disc import ROOT, sha, require
from glossary_terms import canonicalize, PATH
from battle_terms import canonicalize as scoped_names, PATH as SPELLING
from library_text import text as native_text
from narration_format import SOURCE_SHA, COUNT, native_records
from narration_text import layout, width, ROWS, LINE_LIMIT

FILES=('narration.json','narration_review.json','narration_layout_review.json')
OUT=ROOT/'work/translation/en/narration_reviewed.json'
TERMS=ROOT/'work/glossary/narration-terms.json'


def prepare():
    inputs={};documents=[]
    for name in FILES:
        raw=(OUT.parent/name).read_bytes();inputs[name]=sha(raw);documents.append(json.loads(raw))
    base,review,compact=documents
    require(base['source_sha256']==SOURCE_SHA,'Narration source identity')
    require(base['reviewed_ids']==review['reviewed_ids']==list(range(COUNT)),'Incomplete narration review')
    require([r['id']for r in base['entries']]==list(range(COUNT)),'Narration draft inventory')
    for doc in (review,compact):
        require(doc['author_file_sha256']==inputs[FILES[0]] and doc['source_member_sha256']==SOURCE_SHA,'Stale narration review')
    fixes={r['id']:r for r in review['corrections']}
    shorter={r['id']:r for r in compact['fixes']}
    require(len(fixes)==len(review['corrections']) and set(fixes)<=set(range(COUNT)),'Duplicate/unknown narration meaning fix')
    require(sorted(shorter)==compact['reviewed_ids']==[6,9] and len(shorter)==len(compact['fixes']),'Narration compact review coverage')
    require(not set(fixes)&set(shorter),'Compact review must be refreshed after overlapping meaning fix')
    rows=[];native=native_records()[-1]
    for original,(_,raw,info)in zip(base['entries'],native):
        i=original['id'];require(original['source_record_sha256']==sha(raw) and original['source_text_sha256']==sha(info['text']),'Narration source binding')
        change=shorter.get(i,fixes.get(i));value=canonicalize(change['text']if change else original['text'])
        value=scoped_names(value,native_text(info['text']),literal_breaks=False)
        lines=layout(value,i)
        if i in (4,5,6,7):
            paragraphs=[p.strip()for p in original['text'].splitlines()if p.strip()]
            require(lines[0]==canonicalize(paragraphs[0]) and lines[-1]==canonicalize(paragraphs[-1]),'Narration date/signature altered')
        elif i==9:
            attribution=[p.strip()for p in original['text'].splitlines()if p.strip()][-1]
            require(' '.join(lines[-2:])==canonicalize(attribution),'Narration attribution altered')
        row=dict(original);row.update(text=value,lines=lines,line_widths=list(map(width,lines)),meaning_reviewed=True,
            review_reason=change['reason']if change else 'Passed full native-source meaning review')
        rows.append(row)
    return dict(schema_version=1,source_sha256=SOURCE_SHA,review_inputs=inputs,glossary_sha256=sha(PATH.read_bytes()),
        terms_sha256=sha(TERMS.read_bytes()),spelling_sha256=sha(SPELLING.read_bytes()),reviewed_ids=list(range(COUNT)),entries=rows,
        review_notes=review['uncertainties']+compact['uncertainties'],
        layout=dict(rows=ROWS,line_limit_font_units=LINE_LIMIT,runtime='pending by user choice'))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    result=prepare()
    print(json.dumps(dict(records=len(result['entries']),samples=[{k:r[k]for k in ('id','lines','line_widths')}for r in result['entries']if r['id']in (0,6,9)]),indent=2))
    if a.write:OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no files written')


if __name__=='__main__':main()
