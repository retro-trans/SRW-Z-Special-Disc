"""Apply the two independent new-caption reviews, then normalize spelling.

This creates meaning-reviewed prose, not layout-approved build input.
"""
import argparse
import json
from sp_disc import ROOT,sha,require
from battle_format import BIN_SHA,SEG_SHA,unique_sources
from library_text import japanese
from glossary_terms import canonicalize,PATH as GLOSSARY

BASE=ROOT/'work/translation/en'
MANIFEST=BASE/'battle_new_sources.json'
TERMS=ROOT/'work/glossary/battle-terms.json'
OUT=BASE/'battle_new_reviewed.json'
SLICES=((0,80),(80,123))


def prepare():
    raw=MANIFEST.read_bytes();manifest=json.loads(raw);digest=sha(raw)
    require(manifest['source_bin_sha256']==BIN_SHA and manifest['source_seg_sha256']==SEG_SHA,'Battle source identity')
    source=unique_sources();bound=manifest['entries'];rows=[];inputs={};notes=[];name_changes=[]
    require([r['id']for r in bound]==list(range(123)),'New-caption manifest inventory')
    for lo,hi in SLICES:
        suffix=f'{lo:03d}_{hi-1:03d}.json';author_name='battle_new_'+suffix;review_name='battle_review_'+suffix
        a=(BASE/author_name).read_bytes();b=(BASE/review_name).read_bytes()
        draft=json.loads(a);review=json.loads(b);inputs[author_name]=sha(a);inputs[review_name]=sha(b)
        for doc in (draft,review):
            require(doc['source_manifest_sha256']==digest and doc['source_bin_sha256']==BIN_SHA,'Stale new-caption source review')
            require(doc['reviewed_ids']==list(range(lo,hi)),'Incomplete new-caption review')
        require(review['author_file_sha256']==sha(a),'Stale new-caption author review')
        require([r['id']for r in draft['entries']]==list(range(lo,hi)),'New-caption draft inventory')
        fixes={r['id']:r for r in review['corrections']}
        require(len(fixes)==len(review['corrections']) and set(fixes)<=set(range(lo,hi)),'Duplicate/unknown caption fix')
        notes.extend(review['uncertainties'])
        for original in draft['entries']:
            i=original['id'];binding=bound[i];native=source[binding['source_id']]
            require(original['source_id']==binding['source_id']==native['id'],'New-caption source ID')
            require(original['source_sha256']==binding['source_sha256']==native['source_sha256'],'New-caption source hash')
            change=fixes.get(i);before=change['text']if change else original['text'];value=canonicalize(before)
            require(value and not japanese(value) and all(ord(c)>=32 for c in value),'Non-English new-caption prose')
            require(value.count('\\n')==binding['source_line_breaks'],'New-caption line-break change needs review')
            if value!=before:name_changes.append(dict(id=i,before=before,after=value))
            rows.append(dict(id=i,source_id=native['id'],source_sha256=native['source_sha256'],
                occurrences=binding['occurrences'],text=value,source_line_breaks=binding['source_line_breaks'],
                meaning_reviewed=True,layout_approved=False,
                review_reason=change['reason']if change else 'Independent native-source meaning review passed'))
    require(len(rows)==123 and sum(len(r['occurrences'])for r in rows)==250,'Reviewed new-caption coverage')
    return dict(schema_version=1,status='Meaning reviewed; layout, relocation and playback acceptance pending',
        source_manifest_sha256=digest,source_bin_sha256=BIN_SHA,source_seg_sha256=SEG_SHA,
        review_inputs=inputs,glossary_sha256=sha(GLOSSARY.read_bytes()),terms_sha256=sha(TERMS.read_bytes()),
        reviewed_ids=list(range(123)),entries=rows,name_changes=name_changes,review_notes=notes)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    result=prepare()
    print(json.dumps(dict(entries=len(result['entries']),records=250,name_changes=result['name_changes'],
        samples=[{k:r[k]for k in ('id','text','meaning_reviewed','layout_approved')}for r in result['entries']if r['id']in (0,36,83,113)]),indent=2))
    if a.write:OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no files written')


if __name__=='__main__':main()
