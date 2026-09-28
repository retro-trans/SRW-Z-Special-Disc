"""Scan spelling reports across the corpus without approving or rewriting prose."""
import argparse
import json
import re
from collections import Counter
from sp_disc import ROOT, sha
from battle_terms import PATH, rules


def prepare():
    variants = [(old, rule['english'], re.compile(r'(?<![A-Za-z])'+r'\s+'.join(map(re.escape,old.split()))+r'(?![A-Za-z])'))
                for rule in rules() for old in rule['variants']]
    hits=[]; files={}; counts=Counter()
    def walk(value, path, filename, owner=None):
        if isinstance(value, dict):
            owner=value.get('id',owner)
            for key,item in value.items():
                if key in ('text','english','name') and isinstance(item,str):
                    flat=' '.join(item.replace('\\n',' ').split())
                    for old,new,pattern in variants:
                        if pattern.search(flat):
                            hits.append(dict(file=filename,path=path+'/'+key,id=owner,variant=old,canonical_candidate=new))
                            counts[old]+=1
                elif isinstance(item,(list,dict)):walk(item,path+'/'+key,filename,owner)
        elif isinstance(value,list):
            for i,item in enumerate(value):walk(item,path+'/'+str(i),filename,owner)
    for path in sorted((ROOT/'work/translation/en').glob('*.json')):
        raw=path.read_bytes(); rel=str(path.relative_to(ROOT)); files[rel]=sha(raw)
        walk(json.loads(raw),'',rel)
    return dict(schema_version=1,spelling_sha256=sha(PATH.read_bytes()),files=files,counts=dict(counts),hits=hits,
        policy='Inventory only. Includes historical drafts, donor alternatives and review notes. Match context/native identity before changing anything; this is not a count of player-facing defects.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args()
    result=prepare();print(json.dumps(dict(files=len(result['files']),counts=result['counts'],samples=result['hits'][:8]),indent=2))
    if args.write:(ROOT/'work/analysis/battle-spelling-audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no files written')


if __name__ == '__main__':main()
