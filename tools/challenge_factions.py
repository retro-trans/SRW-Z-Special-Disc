"""v0.3.8 Challenge layout and fixed stage squad headings."""
import json,struct
from sp_disc import ROOT,SOURCE,EXE,VT1,Disc,decode,require,sha
from library_text import text
from menu_encoding import menu_encode
from align_story_panels import actual_width
from glossary_terms import canonicalize
from build_story import repack,STAGE,HB,TABLE
from compile_briefings import build as briefings

PREVIOUS=ROOT/'work/output/SRW Z Special Disc English v0.3.7.iso'
LABELS=ROOT/'work/translation/en/stage_squad_headings.json'
BASE=0xFF680
COORDS=(0x436F88,0x436FDC)


def inventory(native):
    stage=native.read(STAGE);hb=native.read(HB)
    offsets=struct.unpack_from('<69I',hb,TABLE);entries={};chunks={}
    for c in range(1,68):
        raw=decode(stage[offsets[c]:offsets[c+1]])[0];chunks[c]=raw
        for at in range(4,len(raw)-24):
            if raw[at]!=12:continue
            slot=raw[at+1:at+24];value=slot.split(b'\0')[0]
            if not value or len(value)%2 or slot!=value+bytes(23-len(value)):continue
            try:source=value.decode('cp932')
            except UnicodeError:continue
            if not all(ord(ch)>=0x3000 for ch in source):continue
            entries.setdefault(source,[]).append(dict(chunk=c,offset=at+1,following=raw[at+24:at+29].hex()))
    require(len(entries)==81 and sum(map(len,entries.values()))==1012,'Native squad heading inventory changed')
    return entries,chunks


def build(disc):
    native=Disc(SOURCE);inv,nchunks=inventory(native)
    draft=json.loads(LABELS.read_text(encoding='utf-8'))
    require({e['source']:e['occurrences'] for e in draft['entries']}==inv,'Squad heading bindings drift')
    stage=disc.read(STAGE);hb=disc.read(HB);offs=struct.unpack_from('<69I',hb,TABLE)
    changed={};before={};allowed={};fields=[]
    for e in draft['entries']:
        value=e['text'];encoded=menu_encode(value)
        require(len(encoded)<23 and actual_width(value)<=200,'Squad heading exceeds field')
        require(text(encoded)==value and value==canonicalize(value),'Squad heading encoding/terminology')
        for o in e['occurrences']:
            c,at=o['chunk'],o['offset']
            if c not in changed:
                before[c]=decode(stage[offs[c]:offs[c+1]])[0];changed[c]=bytearray(before[c]);allowed[c]=[]
            source=nchunks[c][at:at+23]
            require(before[c][at-1:at+23]==b'\x0c'+source,'Squad field already changed')
            require(source==e['source'].encode('cp932')+bytes(23-len(e['source'].encode('cp932'))),'Squad field padding')
            changed[c][at:at+23]=encoded+bytes(23-len(encoded))
            allowed[c].append(at)
            fields.append(dict(chunk=c,offset=at,text=value,source_sha256=sha(source),bytes=len(encoded),width=actual_width(value)))
    for c,raw in changed.items():
        restored=bytearray(raw)
        for at in allowed[c]:restored[at:at+23]=before[c][at:at+23]
        require(restored==before[c],'Squad translation changed command/deployment data')
    new_stage,new_hb,sizes=repack(stage,hb,{c:bytes(raw) for c,raw in changed.items()})
    newoffs=struct.unpack_from('<69I',new_hb,TABLE)
    for c,(lo,hi) in enumerate(zip(newoffs,newoffs[1:])):
        old=stage[offs[c]:offs[c+1]];new=new_stage[lo:hi]
        require(decode(new)[0]==changed[c] if c in changed else new==old,'Stage chunk verification '+str(c))
    restored=bytearray(new_hb);restored[TABLE:TABLE+276]=hb[TABLE:TABLE+276]
    require(restored==hb,'HB change outside chunk table')
    exe=disc.read(EXE);out=bytearray(exe);patches=[]
    for va in COORDS:
        at=va-BASE;old=struct.unpack_from('<I',exe,at)[0]
        require(old==0x2406FECC,'Challenge margin preimage') # -308
        new=0x2406FEAC # -340: 32 units left, measured x96 to x64
        struct.pack_into('<I',out,at,new)
        patches.append(dict(address=va,offset=at,before=old,after=new))
    changes,layout=briefings(challenge_limit=500);change=next(c for c in changes if c['chunk']==50)
    archive=disc.read(VT1);lo,hi=change['start'],change['end']
    oldrows=decode(archive[lo:hi])[0].splitlines();newrows=decode(change['payload'])[0].splitlines()
    require(len(oldrows)==len(newrows)==18*7,'Challenge briefing row count')
    fits=json.loads((ROOT/'work/translation/en/challenge_fits_0.3.8.json').read_text())
    fitmap={e['index']:e for e in fits}
    pages=[p for p in layout['pages'] if p['id'].startswith('50/')]
    for i,p in enumerate(pages):
        prior=' '.join(text(r[:56].split(b'\0')[0]) for r in oldrows[i*7:i*7+7]).split()
        after=' '.join(p['lines']).split()
        if i in fitmap:
            require(prior==canonicalize(fitmap[i]['before']).split() and after==canonicalize(fitmap[i]['text']).split(),'Briefing fit binding')
        else:require(prior==after,'Unintended briefing wording change')
        require(max(p['widths'])<=500 and len(p['lines'])==7,'Briefing display limit')
    return bytes(out),new_stage,new_hb,change,dict(version='0.3.8',squad_headings=dict(unique=81,occurrences=len(fields),
        chunks=sorted(changed),capacity=23,fields=fields,all_other_decoded_bytes_identical=True),
        briefings=dict(pages=pages,changed_wording_pages=sorted(fitmap),left_x=64,conservative_right_x=564,
            relative_x=-340,line_limit=500,source_chunk_sha256=sha(archive[lo:hi]),new_chunk_sha256=sha(change['payload'])),
        executable_patches=patches,source_executable_sha256=sha(exe),executable_sha256=sha(out),emulator='pending')
