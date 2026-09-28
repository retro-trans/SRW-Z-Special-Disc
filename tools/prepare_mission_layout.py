"""Propose compact equivalents only after the full condition meaning review."""
import argparse,json
from sp_disc import ROOT,file_sha,require
from save_summary_text import width
from inspect_mission_conditions import TARGET as BINDINGS

REVIEW=ROOT/'work/translation/en/mission_conditions_review.json'
TARGET=ROOT/'work/translation/en/mission_conditions_layout_draft.json'
COMPACT={
13:'Defeat 100+ foes in 4 turns.\nBattle continues past 100 kills;\nends on turn 5. Each 20 Gaza C downed\nbrings 20 more Gaza C.',
17:'Fail to deal 30,000+ damage to Science Fortress Island in one attack.',
23:'Earn 350,000+ funds in 5 turns.\nEach enemy defeated yields 10,000 funds.\nEven after earning 350,000, battle\ncontinues until turn 6.',
25:'Under 350,000 funds when turn 6 starts.',
26:'All foes defeated with under 350,000 funds.',
32:'Defeat 150+ foes in 4 turns.\nBattle continues past 150 kills;\nends on turn 5. Each 20 foes downed\nbrings 20 reinforcements.',
40:'Defeat all foes in 5 turns; earn\n450,000+ funds. Funds per kill:\nDaughtress Neo: 10,000; Gadeel: 15,000.\nDefeating the Frost Brothers is optional.',
42:'All unmanned MS defeated with under 450,000 funds.',
46:'Defeat 100 foes in 3 turns.\nNo Spirit Commands or MAP weapons.\nEvery 20 kills brings 20 reinforcements;\n100 foes appear in total.',
50:'Reach turn 6. No Spirit Commands\nor MAP weapons. Coralians: 3 per squad.\nEach 5 squads wiped out brings\n5 reinforcement squads.',
52:'4 turns: defeat all foes and earn\n800,000+ funds; 3 units/enemy squad.\n10,000 funds/kill; no Spirit Commands.\nNo funds for third-force kills.',
53:'An allied battleship falls (deploy: 2).',
54:'All foes defeated with under 800,000 funds.',
60:'\n- No special requirements.',
}

def wrap(value,limit=460):
    lines=[]
    for paragraph in value.split('\n'):
        if not paragraph:lines.append('');continue
        line=''
        for word in paragraph.split():
            require(width(word)<=limit,'Condition word exceeds the panel')
            candidate=(line+' '+word).strip()
            if line and width(candidate)>limit:lines.append(line);line=word
            else:line=candidate
        lines.append(line)
    return lines

def prepare():
    inv=json.loads(BINDINGS.read_text(encoding='utf8'));review=json.loads(REVIEW.read_text(encoding='utf8'))
    require(review['entries_examined']==review['entries_in_slice']==61,'Incomplete full meaning review')
    checked={r['id']:r for r in review['entries']};rows=[];bysha={}
    for i,src in enumerate(inv['entries']):
        full=checked[src['id']]['text'];value=COMPACT.get(i,full);lines=wrap(value)
        row=dict(id=src['id'],source=src['source'],full_text=full,text=value,lines=lines,
                 line_widths=list(map(width,lines)),compact=i in COMPACT,retain_native=i==2,
                 occurrences=src['occurrences']);rows.append(row);bysha[src['source_sha256']]=row
    layouts=[]
    for ch in inv['chunks']:
        for group in ch['tables']:
            count=sum(len(bysha[r['source_sha256']]['lines']) for r in group['entries'])
            layouts.append(dict(chunk=ch['chunk'],kind=group['kind'],rows=count))
    return dict(status='layout draft',full_review_sha256=file_sha(REVIEW),bindings_sha256=file_sha(BINDINGS),
                line_limit=460,row_limit=4,entries=rows,groups=layouts)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();d=prepare()
    bad=[g for g in d['groups'] if g['rows']>4]
    print(json.dumps(dict(entries=len(d['entries']),compact=sum(r['compact'] for r in d['entries']),
        overfull_groups=bad,samples=[{k:r[k] for k in ('id','text','lines','line_widths')} for r in d['entries'] if r['compact']]),indent=2))
    require(not bad,'Condition group exceeds four native rows')
    if not a.write:print('DRY RUN: no files written');return
    TARGET.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

if __name__=='__main__':main()
