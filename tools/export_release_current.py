"""Export v0.3.16 installed English for review, excluding original script corpora."""
import argparse,json
from sp_disc import ROOT,Disc,require,EXE
from battle_format import BIN,SEG,native,unique_sources,blocks,indexed
from library_text import text,japanese
from export_public import OUT,EN,read,JP

FIELDS={'id','text','lines','speaker','source_sha256','offset','capacity','kind','chunk','box',
        'rect','page','pilot_id','bank','scene','side','unit','slot'}

def corpus():
    disc=Disc(ROOT/'work/output/SRW Z Special Disc English v0.3.16.iso')
    parsed=native()[4];_,chunks=blocks(disc.read(BIN),disc.read(SEG))
    records=[indexed(c,p['index'],len(p['rows'])) if p['rows'] else [] for p,c in zip(parsed,chunks)]
    entries=[]
    for source in unique_sources():
        if source['id']==444:continue
        values={text(records[o['block']][o['record']]['raw']) for o in source['occurrences']}
        require(len(values)==1,'Conflicting installed battle variants')
        value=values.pop();require(not japanese(value),'Untranslated player-facing caption')
        entries.append(dict(id=source['id'],source_sha256=source['source_sha256'],text=value,
                            occurrences=len(source['occurrences'])))
    require(len(entries)==25521 and sum(r['occurrences'] for r in entries)==58880,'Battle coverage changed')
    result={}
    for n in range(0,len(entries),5000):
        result[f'current/battle-{n:05}.json']=dict(schema_version=1,version='0.3.16',entries=entries[n:n+5000])
    receipt=read(ROOT/'work/output/SRW Z Special Disc English v0.3.6.json')
    rows=receipt['translations']['suspend']['entries'];exe=disc.read(EXE)
    for row in rows:
        at=row['offset'];require(exe[at:exe.index(0,at)].decode('cp932')==row['text'],'Post-save text differs from receipt')
    result['current/post_save.json']=dict(schema_version=1,version='0.3.16',entries=[
        {k:v for k,v in row.items() if k in FIELDS} for row in rows])
    for name in ('battle_theater_names','bonus_results','character_setup','experience_name','battle_banners','hyakki_terminology'):
        rows=read(EN/(name+'.json'))['entries']
        result[f'current/{name}.json']=dict(schema_version=1,version='0.3.16',entries=[
            {k:v for k,v in row.items() if k in FIELDS} for row in rows])
    for name,keys in [('search_layout',('rows','ability_descriptions_checked')),('combat_forecast',('icons','names'))]:
        original=read(EN/(name+'.json'))
        result[f'current/{name}.json']=dict(schema_version=1,version='0.3.16',**{
            key:[{k:v for k,v in row.items() if k in FIELDS} for row in original[key]] for key in keys})
    result['current/stage_label.json']=dict(schema_version=1,version='0.3.16',text='Stage',font_size=24,capital_height=16,baseline_y=20)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args()
    result=corpus();total=0
    for name,obj in result.items():
        rendered=json.dumps(obj,ensure_ascii=False,indent=2)+'\n'
        require(not JP.search(rendered),'Original Japanese in public export '+name)
        total+=len(rendered.encode('utf-8'))
        if args.write:
            target=OUT/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(rendered,encoding='utf-8')
    print(f"{'Wrote' if args.write else 'Dry run:'} {len(result)} English-only files, {total:,} bytes")
    print('Battle sample:',result['current/battle-00000.json']['entries'][0])

if __name__=='__main__':main()
