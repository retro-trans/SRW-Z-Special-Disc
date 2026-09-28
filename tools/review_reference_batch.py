"""Apply the recorded 0.2.2 meaning review, then canonicalize authored names."""
import argparse
import json
from sp_disc import ROOT,require
from glossary_terms import canonicalize

FIXES={
 1:[('Barely surviving, they face','After barely repelling the Shadow Angels, they face')],
 2:[('Anemone and Cynthia see themselves in the new Phantom Pain members.',
     'Phantom Pain meets new comrades; Anemone and Cynthia see themselves in its members.')],
 9:[('the true Teral, a lost love','the real Teral, Lila\'s late lover'),
    ('causing fatal hesitation','causing Teral to hesitate to attack')],
 17:[('Their autopilot gives them a name: the Executor System.',
      'Their autonomous control mechanism earns the machines the name Executor System.')],
 18:[('Their autopilot gives them a name: the Executor System.',
      'Their autonomous control mechanism earns the machines the name Executor System.')],
 19:[('Black History\'s end in Metropolis:', 'Black History\'s end as depicted in the book Metropolis:')],
 20:[('is King Gainer from a parallel world; the two were originally one being.',
      'is King Gainer\'s counterpart from a parallel world.'),
     ('its question about humanity.', 'its question about humanity\'s meaning.')]
}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    paths=[ROOT/'work/translation/en'/p for p in ('chart_overrides.json','reference_names.json')]
    values=[json.loads(p.read_text(encoding='utf-8'))for p in paths]
    changes=[]
    for i,pairs in FIXES.items():
        for old,new in pairs:
            val=values[0]['synopses'][i]
            if new in val:continue
            require(val.count(old)==1,'Review phrase preimage '+str(i))
            values[0]['synopses'][i]=val.replace(old,new)
            changes.append(dict(row=i,old=old,new=new))
    values[0]['title_overrides']['z/52']='Grief as Power'
    def walk(value):
        if isinstance(value,str):return canonicalize(value)
        if isinstance(value,list):return [walk(x)for x in value]
        if isinstance(value,dict):return {k:walk(v)for k,v in value.items()}
        return value
    values=[walk(v)for v in values]
    values[0]['synopses']=[canonicalize(v,'chart_sp')for v in values[0]['synopses']]
    print(json.dumps(dict(meaning_fixes=changes,squad_samples=[values[1]['squads'][i]for i in (78,85,94)],
                         map_samples=values[1]['map_overrides']),indent=2))
    if args.write:
        for p,v in zip(paths,values):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no files written')


if __name__=='__main__':main()
