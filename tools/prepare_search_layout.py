"""Prepare three-line Search ability help from the v0.3.10 field bindings."""
import struct,json
from sp_disc import *
from reuse_compdata import BBASE
from library_text import text
from squad_followup import loaded
from save_summary_text import width
from menu_encoding import menu_encode

COMPACT={
0x54b00:'Shield Defend cuts damage more than Defend. With Blocking, it can also trigger when an enemy attack hits.',
0x54b08:'Full EN and ammo for one unit in your or an adjacent squad. Squad EN +10% at turn start. Also works from a squad member.',
0x54b0c:'Repairs all units in your or an adjacent squad. Squad HP +10% at turn start. Also works from a squad member.',
0x54b78:'Oversense L5+, Will 130+: foes within 5 tiles lose 50% accuracy and evasion, 20% attack and defense.',
0x54b7c:'Will 130: Agi/Sight +30. Blocks Daunt and Analyze. Each turn: Strike, Alert, Awaken, Pierce. Evades foes with Skill 20+ lower.'}


def wrap(value):
    lines=[];line=''
    for word in value.split():
        candidate=(line+' '+word).strip()
        if line and width(candidate)>510:lines.append(line);line=word
        else:line=candidate
    if line:lines.append(line)
    return '\n'.join(lines)


def prepare():
    base=Disc(ROOT/'work/output/SRW Z Special Disc English v0.3.10.iso')
    co=decode(base.read('DATA/COMPDATA.BN'))[0];ex=base.read(EXE)
    native=decode(Disc(SOURCE).read('DATA/COMPDATA.BN'))[0]
    rows=[];seen=set();checked=[]
    for p in range(0x54a60,0x54b84,4):
        source=struct.unpack_from('<I',native,p)[0]-BBASE
        if not 0x81f20<=source<=0x837d0:continue
        a=struct.unpack_from('<I',co,p)[0]
        if a in seen:continue
        seen.add(a);kind='comp' if BBASE<=a<BBASE+len(co) else 'exe'
        at=a-BBASE if kind=='comp' else loaded(ex,a);blob=co if kind=='comp' else ex
        raw=blob[at:].split(b'\0')[0];old=text(raw);require(bool(old),'Empty ability description')
        overflow=len(old.splitlines())>3 or max(map(width,old.splitlines()))>510
        new=wrap(COMPACT.get(p,old)) if overflow else old
        require(len(new.splitlines())<=3 and max(map(width,new.splitlines()))<=510,'Overflow '+hex(p)+' '+new)
        require(len(menu_encode(new))<=len(raw),'Allocation overflow '+hex(p))
        checked.append(dict(pointer=p,address=a,text=new,line_widths=list(map(width,new.splitlines()))))
        if new!=old:rows.append(dict(kind=kind,offset=at,capacity=len(raw)+1,pointer=p,address=a,
            before=old,text=new,line_widths=list(map(width,new.splitlines())),before_hex=(raw+b'\0').hex()))
    refs=json.loads((ROOT/'work/translation/en/compdata.json').read_text(encoding='utf-8'))
    for source_at,new in [(0x8a180,'Search Item'),(0x8a1a0,'Search Filter'),(0x8a1c0,'Search Use')]:
        r=next(r for r in refs if r['offset']==source_at);a=r.get('relocated_address')
        kind='exe' if a else 'comp';at=loaded(ex,a) if a else source_at;blob=ex if a else co
        raw=blob[at:].split(b'\0')[0];old=text(raw)
        require(old==r['text'],'Header preimage');require(width(new)<=150,'Prompt/button spacing')
        rows.append(dict(kind=kind,offset=at,capacity=len(raw)+1,pointer=r.get('pointer_sites',[None])[0],
            address=a,before=old,text=new,line_widths=[width(new)],before_hex=(raw+b'\0').hex()))
    return dict(version='0.3.11',rows=rows,ability_descriptions_checked=checked,
        ability_limit=dict(rows=3,width=510),prompt_limit=150,
        source_members={n:sha(base.read(n)) for n in [EXE,'DATA/COMPDATA.BN']})

if __name__=='__main__':
    spec=prepare()
    (ROOT/'work/translation/en/search_layout.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Checked',len(spec['ability_descriptions_checked']),'ability descriptions; changes',len(spec['rows']))
    for r in spec['rows']:
        if r['pointer'] in COMPACT:print(hex(r['pointer']),repr(r['text']),r['line_widths'])
