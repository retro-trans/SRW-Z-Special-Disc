"""Create an English-only review queue for active/donor caption disagreements."""
import argparse
import json
from sp_disc import ROOT,sha,require

BASE=ROOT/'work/translation/en'
SOURCE=BASE/'battle_reuse.json'
OUT=BASE/'battle_reuse_review_sources.json'


def prepare():
    raw=SOURCE.read_bytes();cfg=json.loads(raw);rows=[]
    for candidate in cfg['entries']:
        if not candidate['status'].startswith('active draft differs'):continue
        row=dict(candidate);row['source_id']=row.pop('id');row['id']=len(rows)
        rows.append(row)
    require(len(rows)==877,'Battle disagreement queue inventory')
    return dict(schema_version=1,status='Meaning review queue; not a build input',
        source_manifest_sha256=sha(raw),source_bin_sha256=cfg['locks']['source_bin_sha256'],
        source_seg_sha256=cfg['locks']['source_seg_sha256'],entries=rows)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    result=prepare()
    print(json.dumps(dict(entries=len(result['entries']),samples=[dict(id=r['id'],source_id=r['source_id'],
        active=r['text'],donor_options=[o['text']for o in r['donor_options']])for r in result['entries'][:5]]),indent=2))
    if a.write:OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no files written')


if __name__=='__main__':main()
