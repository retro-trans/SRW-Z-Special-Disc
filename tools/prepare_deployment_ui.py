"""Draft the missed menu-table text and tournament squad display names."""
import argparse,json
from sp_disc import ROOT,file_sha,require
from glossary_terms import canonicalize

MENU={
0:'Check equipped parts.',
1:'Find Spirit Commands, special skills and abilities.',
2:'View abilities from the pilot list.',
3:'Improve pilot stats and learn skills.',
4:'Assign a different pilot to a unit.',
5:'End the intermission.',
6:'Change squad members.',
7:'Buy and sell power parts.',
8:'Change game settings.',
9:'Save or load data.',
10:'Open unit commands.',
11:'Open pilot commands.',
12:'End the SETUP mission.',
13:'Units cannot be upgraded in EX Hard Mode.',
14:'Pilots cannot be trained in EX Hard Mode.',
15:'Basic Order',16:'Balance Order',17:'Keyword',18:'Pilot',19:'Unit',20:'Random',
21:'Arrange all squads using the preset plan,\nincluding pilot reassignments.',
22:'Keep the selected squads and reorganize\nthe others into balanced squads.',
23:'Name squads using keywords linked to their members.',
24:"Name squads after their leaders.",
25:"Name squads after their leaders' units.",
26:'Automatically choose a naming method for each squad.',
27:'Use the name of a pilot in the squad.',
28:'Use the name of a unit in the squad.',
29:'Automatically choose from the methods above.',
35:'Selected Squad',
36:'Rename squads using one of the methods above.',
37:'Select a naming method.',
38:'<Keep playing the battle music after animations.>',
39:'<Return to the map music after battle animations.>',
40:'<Use the team music during battle animations.>',
41:'<Use each unit\'s music during battle animations.>',
42:'<Choose detailed settings for battle music.>',
43:'<Set quick commands.>',
44:'<Remember the sort and sub-info positions.>',
45:'<Do not remember the sort and sub-info positions.>',
46:'<Enable controller vibration during play.>',
47:'<Disable controller vibration.>',
48:'<Show the map grid.>',
49:'<Hide the map grid.>',
50:'<Move the cursor along the screen directions.>',
51:'<Move the cursor along the map grid.>',
52:'<Scroll to the destination when moving the cursor.>',
53:'<Jump directly to the cursor destination.>',
54:'<Set unit movement speed to slow.>',
55:'<Set unit movement speed to normal.>',
56:'<Set unit movement speed to fast.>',
57:'<Rename the team.>',
58:'<Use Support Defense when a unit is available.>',
59:'<Do not automatically use Support Defense.>',
60:'Tri Formation',61:'Center Formation',62:'Wide Formation',63:'Tri',64:'Center',65:'Wide',
66:'<Formation> Choose formation and order.',
67:'<Group Formation> Set formations for your squads.',
68:'<Ship Deployment> Select ships to deploy.',
69:'<Ship Deployment> Select a ship to move.',
70:'<Ship Deployment> Select a ship or position to swap.',
71:'<Deploy> Prepare for deployment.',
72:'<Deploy Units> Select a squad to move.',
73:'<Deploy Units> Select a squad or position to swap.',
74:'<Forced Deployment> Check the map.',
75:'No squads are ready to deploy,\nso deployment selection is unavailable.\nSelect "Squad Setup" to form a deployable squad.',
76:'~[Allied Forces] Select Unit~',
77:'~[Third Force] Select Unit~',
78:'~[Fourth Force] Select Unit~',
79:'~[Enemy Forces] Select Unit~',
80:'~[Allied Forces] Select Squad~',
81:'~[Third Force] Select Squad~',
82:'~[Fourth Force] Select Squad~',
83:'~[Enemy Forces] Select Squad~',
84:'~"    :Tri" Select Squad~',
85:'~"   :Center" Select Squad~',
86:'~"    :Wide" Select Squad~',
87:'~[Individual Kills] Check Unit~',
88:'~[Downed Units] Check Unit~',
89:'~"Launch List" Select Squad~',
90:'~"Launch List" Select Unit~',
91:'<Change game system settings.>',
92:'<Browse the game data library.>',
93:'System Settings',94:'Library',
95:'View data on robots that appear in the game.',
96:'View data on characters that appear in the game.',
97:'Read explanations of special terms used in the game.',
98:'Listen to music used in the game.',
99:'Review the scenarios and routes you have played.',
100:'Read gameplay tips and useful information.',
}

def draft():
    p=ROOT/'work/ui/deployment/native-inventory.json';inv=json.loads(p.read_text(encoding='utf-8'))
    require(len(inv['menu_entries'])==101,'Missed menu-table inventory drift')
    rows=[]
    for i,r in enumerate(inv['menu_entries']):
        if i not in MENU:continue
        rows.append(dict(id=f'menu/{r["offset"]:x}',**r,text=MENU[i]))
    labels=['Quarterfinal Group 6','First-Round Losers','Quarterfinal Group 1','Quarterfinal Group 7',
            'Quarterfinal Group 2','Quarterfinal Group 8','Quarterfinal Group 3','Quarterfinal Group 4',
            'Quarterfinal Group 5','Argama','Minerva','King Beal']
    for r,label in zip(inv['stage_names'],labels):rows.append(dict(id=f'stage/13/{r["offset"]:x}',**r,text=label))
    rows.extend([dict(id='heading',source='小隊編成',text='Squads',note='Compact screen heading; full translation is Squad Setup. Keep the menu command named Squad Setup.'),
                 dict(id='graphic/new',source='新規編成',text='New Squad'),
                 dict(id='graphic/reserve',source='リザーブへ',text='To Reserve'),
                 dict(id='graphic/squads',source='小隊群へ',text='To Squads'),
                 dict(id='graphic/deployed',source='出撃済',text='Deployed')])
    return dict(status='draft',bindings_sha256=file_sha(p),entries=rows,
                deferred=[dict(id=f'menu/{r["offset"]:x}',source=r['source'],reason='Dynamic text fragments: must prove composition and position before changing')
                          for i,r in enumerate(inv['menu_entries']) if i not in MENU])

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args()
    d=draft();print(json.dumps(dict(entries=len(d['entries']),deferred=d['deferred'],samples=d['entries'][60:74]),ensure_ascii=True,indent=2))
    if not a.write:print('DRY RUN: no files written');return
    (ROOT/'work/translation/en/deployment_ui_draft.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
