"""Merge complete source reviews, then apply source-sensitive glossary rules."""
import argparse
import json
from sp_disc import ROOT,sha,require
from glossary_terms import canonicalize,PATH
from compile_chart import wrap,SOURCE_SHA

FILES=('chart_main.json','chart_main_review_first.json','chart_main_review_last.json')
OUT=ROOT/'work/translation/en/chart_main_reviewed.json'


def prepare():
    inputs={};data=[]
    for name in FILES:
        path=ROOT/'work/translation/en'/name;raw=path.read_bytes()
        inputs[name]=sha(raw);data.append(json.loads(raw))
    base,first,last=data
    require(base['source_sha256']==SOURCE_SHA,'Chart review source identity')
    require([r['id']for r in base['entries']]==list(range(110)),'Chart review source inventory')
    edits={};reviewed=[];notes=[]
    for review,expected in ((first,list(range(55))),(last,list(range(55,110)))):
        require(sorted(review['reviewed_ids'])==expected,'Incomplete chart meaning review')
        require(set(map(int,review['corrections'])).issubset(expected),'Review outside assigned rows')
        reviewed.extend(review['reviewed_ids']);edits.update(review['corrections'])
        notes.extend(review.get('uncertainties',[]))
    entries=[]
    for row in base['entries']:
        item=dict(row);edit=edits.get(str(row['id']))
        value=edit['text']if edit else row['text']
        value=canonicalize(value,'chart_main',row['id'])
        formatted,widths=wrap(value)
        item.update(text=value,line_widths=widths,meaning_reviewed=True,
                    review_reason=edit['reason']if edit else 'Passed native-source meaning review')
        entries.append(item)
    return dict(source_sha256=SOURCE_SHA,review_inputs=inputs,glossary_sha256=sha(PATH.read_bytes()),
        reviewed_ids=sorted(reviewed),meaning_corrections=len(edits),entries=entries,review_notes=notes,
        layout=dict(line_limit_font_units=560,row_limit=11,runtime_acceptance='pending by user choice'))


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    result=prepare()
    print(json.dumps(dict(reviewed=len(result['reviewed_ids']),meaning_corrections=result['meaning_corrections'],
        max_lines=max(len(r['line_widths'])for r in result['entries']),
        samples=[{k:r[k]for k in ('id','text','review_reason')}for r in result['entries']if r['id']in (6,77,103)]),indent=2))
    if args.write:OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no files written')


if __name__=='__main__':main()
