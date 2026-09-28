"""Full-meaning mission-condition drafts; layout comes after independent review."""
import argparse,json
from sp_disc import ROOT,file_sha,require
from inspect_mission_conditions import TARGET as BINDINGS

FULL=[
'Defeat all enemies.',
'An allied battleship is shot down.',
'???',
'Any allied unit is shot down.',
'Defeat Shurouga.',
'Defeat the Lemures Test Type.',
'Gekko-Goh is shot down.',
'Defeat the Eldar Battleship.',
'Adette is shot down.',
'Defeat both Grave Cherubim in the same turn.',
'Aquarion is shot down.',
'Assault Aquarion is shot down.',
'Defeat XAN -Zan-.',
'Defeat at least 100 enemies within 4 turns. The battle continues after 100 kills and ends on turn 5. Every time 20 Gaza C are defeated, another 20 appear as reinforcements.',
'Argama is shot down.',
'Fewer than 100 total kills at the start of turn 5.',
'Deal at least 30,000 damage in one attack to the Science Fortress Island, which appears on turn 5.',
'Fail to deal at least 30,000 damage to the Science Fortress Island in one attack.',
'Turn 6 begins.',
'All allied units are defeated.',
'Defend Vodara Shrine until turn 6.',
'Defeat all enemies. No reinforcements will appear.',
'An enemy reaches Vodara Shrine.',
'Earn at least 350,000 funds within 5 turns. Each defeated enemy yields 10,000 funds. The map continues until turn 6 even after 350,000 funds have been earned.',
'Iron Gear is shot down.',
'Fewer than 350,000 funds earned at the start of turn 6.',
'Fewer than 350,000 funds earned when all enemies have been defeated.',
'Defeat Rushrod, Golem and Planeta within 7 turns.',
'Turn 8 begins.',
'Defeat all enemies within 9 turns. There are no reinforcements.',
'Soleil or Freeden is shot down.',
'Turn 10 begins.',
'Defeat at least 150 enemies within 4 turns. The battle continues after 150 kills and ends on turn 5. Every time 20 enemies are defeated, another 20 appear as reinforcements.',
'Fewer than 150 total kills at the start of turn 5.',
'Defeat all enemies within 5 turns, then defeat the Bandock that appears afterward in one attack.',
'Fail to defeat Bandock in one attack.',
'King Beal is shot down.',
'Turn 6 begins.',
'The Emaan Battleship is shot down.',
'Glomar is shot down.',
'Defeat all enemies and earn at least 450,000 funds within 5 turns. Each Daughtress Neo defeated yields 10,000 funds; each Gadeel yields 15,000. Defeating the Frost Brothers is optional.',
'Freeden is shot down.',
'Fewer than 450,000 funds earned when all unmanned mobile suits have been defeated.',
'Defeat Gear Gear, Mecha Yosaiki, Planeta, Dominator, The O, Nirvash the END and Big Duo Inferno within 8 turns.',
'Turn 9 begins.',
'Eternal or Glomar is shot down.',
'Defeat 100 enemies within 3 turns. Spirit Commands and MAP weapons cannot be used. Every 20 enemies defeated brings 20 more as reinforcements, with 100 enemies appearing in total.',
'An allied battleship is shot down. Only 1 battleship can be deployed.',
'Turn 4 begins.',
'Defeat the Artificial Sun within 5 turns. Spirit Commands cannot be used.',
'Reach turn 6. Spirit Commands and MAP weapons cannot be used. All Coralians form squads of 3 units. Each time 5 squads are wiped out, another 5 squads appear as reinforcements.',
'An enemy reaches the edge of the map.',
'Defeat all enemies and earn at least 800,000 funds within 4 turns. Enemy squads contain 3 units, and each unit defeated yields 10,000 funds. Spirit Commands cannot be used. Enemies defeated by the third force yield no funds for you.',
'An allied battleship is shot down. Only 2 battleships can be deployed.',
'Fewer than 800,000 funds earned when all enemies have been defeated.',
'Turn 5 begins.',
'Defeat Haman, Scirocco, Shagia, Olba and Ghingnham within 5 turns. Spirit Commands cannot be used.',
'Defeat all enemies within 12 turns.',
'An allied battleship is shot down. Only 4 battleships can be deployed.',
'Turn 13 begins.',
'No special requirements.',
]

def draft():
    inv=json.loads(BINDINGS.read_text(encoding='utf8'));require(len(inv['entries'])==len(FULL)==61,'Mission draft ordering')
    return dict(status='full-meaning draft',bindings_sha256=file_sha(BINDINGS),entries=[dict(r,text=t,
        retain_native=r['source']=='？？？') for r,t in zip(inv['entries'],FULL)],
        notes=['Condition table role determines Defeat versus is shot down; Assault Aquarion is a defeat condition.',
               'Full drafts are reviewed before any compact wording. Source numbers, time limits, prohibitions, reinforcements and exceptions are mandatory.',
               'Do not edit story_extra drafts or dialogue. The 38 question-mark placeholders remain native.'])

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();d=draft()
    print(json.dumps(dict(entries=len(d['entries']),samples=[{k:r[k] for k in ('id','source','text','retain_native')} for r in d['entries'] if r['id'] in ('m_689b6707d93c','m_c45cd84bf830','m_e6f4d3687445','m_24470a24cf72')]),ensure_ascii=True,indent=2))
    if not a.write:print('DRY RUN: no files written');return
    (ROOT/'work/translation/en/mission_conditions_draft.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

if __name__=='__main__':main()
