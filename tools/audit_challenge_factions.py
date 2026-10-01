"""Read back v0.3.8 and execute every translated heading through its reader."""
import json,struct
from sp_disc import ROOT,Disc,EXE,VT1,decode,require
from challenge_factions import STAGE,HB,TABLE,COORDS,BASE,LABELS
from library_text import text
from menu_encoding import menu_encode
from save_summary_text import width
from test_menu_reader_fix import Reader


def main():
    before=Disc(ROOT/'work/output/SRW Z Special Disc English v0.3.7.iso')
    after=Disc(ROOT/'work/output/SRW Z Special Disc English v0.3.8.iso')
    exe=after.read(EXE);oldexe=before.read(EXE)
    restored=bytearray(exe)
    for va in COORDS:
        require(struct.unpack_from('<I',exe,va-BASE)[0]==0x2406FEAC,'Challenge coordinate')
        restored[va-BASE:va-BASE+4]=oldexe[va-BASE:va-BASE+4]
    require(restored==oldexe,'Executable changed outside two margin words')
    draft=json.loads(LABELS.read_text(encoding='utf-8'))['entries']
    oldstage,newstage=before.read(STAGE),after.read(STAGE)
    oldhb,newhb=before.read(HB),after.read(HB)
    oo=struct.unpack_from('<69I',oldhb,TABLE);no=struct.unpack_from('<69I',newhb,TABLE)
    grouped={};occ=0;hyakki=0
    for e in draft:
        encoded=menu_encode(e['text'])
        m=Reader(exe,encoded)
        require([v[0]for v in m.run()]==[encoded] and max(m.reads)==len(encoded),'Heading scanner overread')
        for o in e['occurrences']:grouped.setdefault(o['chunk'],[]).append((o['offset'],encoded));occ+=1
        if e['text']=='Hyakki Empire':hyakki=len(e['occurrences'])
    require(hyakki==58 and occ==1012,'Faction occurrence coverage')
    for c in range(68):
        old=decode(oldstage[oo[c]:oo[c+1]])[0];new=decode(newstage[no[c]:no[c+1]])[0]
        restored=bytearray(new)
        for at,encoded in grouped.get(c,[]):
            require(new[at:at+23]==encoded+bytes(23-len(encoded)),'Squad field readback')
            require(old[at-1]==new[at-1]==12 and new[at+23:at+28]==old[at+23:at+28],
                    'Squad marker / following deployment bytes changed')
            restored[at:at+23]=old[at:at+23]
        require(restored==old,'Unrelated decoded stage byte changed')
    lo,hi=197091632,197095616
    old,new=before.read(VT1),after.read(VT1)
    require(old[:lo]==new[:lo] and old[hi:]==new[hi:],'Unrelated VT1 byte changed')
    rows=decode(new[lo:hi])[0].splitlines(keepends=True)
    require(len(rows)==126 and all(len(r)==57 and r[-1:]==b'\n' for r in rows),'Briefing slots')
    maximum=0
    for row in rows:
        raw=row[:56].split(b'\0')[0];value=text(raw);maximum=max(maximum,width(value))
        require(width(value)<=500,'Briefing overflow')
        m=Reader(exe,raw)
        require([v[0] for v in m.run()]==([raw] if raw else []),'Briefing scanner output')
        require(max(m.reads)==len(raw),'Briefing scanner overread')
    result=dict(briefings=18,rows=126,maximum_conservative_width=maximum,squad_labels=81,
        occurrences=occ,hyakki_empire_occurrences=hyakki,stage_chunks_checked=68,
        native_reader_verified=True,unrelated_stage_bytes_preserved=True,emulator='pending')
    (ROOT/'work/ui/challenge-factions/audit-0.3.8.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
