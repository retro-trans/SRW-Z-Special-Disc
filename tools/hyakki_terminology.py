"""Normalize the faction name in existing allocations, preserving line breaks."""
import json,re,struct
from sp_disc import ROOT,EXE,VT1,VT1_TABLE,Disc,decode,banlz,require,sha
from build_story import STAGE,HB,TABLE,repack
from library_text import text
from save_summary_text import width

INPUT=ROOT/'work/translation/en/hyakki_terminology.json'
OLD=re.compile(rb'Hundred(?P<a>[ \n]+)Demon(?P<b>[ \n]+)Empire',re.I)

def replacement(m):
    breaks=(m['a']+m['b']).count(b'\n')
    return b'Hyakki'+(b'\n'*breaks if breaks else b' ')+b'Empire'

def substitute(raw):
    out=OLD.sub(replacement,raw)
    require(out!=raw and len(out)<len(raw),'Expected shorter faction name')
    a=text(raw).splitlines();b=text(out).splitlines()
    require(len(a)==len(b) and all(width(y)<=width(x) for x,y in zip(a,b)),'Faction replacement increased a row')
    require(not OLD.search(out),'Uncorrected faction name')
    return out

def string_changes(raw,kind,chunk=None):
    spans=set()
    for m in OLD.finditer(raw):
        start=raw.rfind(b'\0',0,m.start())+1;end=raw.find(b'\0',m.end())
        require(end>=m.end(),'No string terminator')
        spans.add((start,end))
    entries=[]
    for start,end in sorted(spans):
        old=raw[start:end];new=substitute(old)
        entries.append(dict(kind=kind,chunk=chunk,offset=start,capacity=end-start+1,
            before_hex=(old+b'\0').hex(),after_hex=(new+bytes(len(old)+1-len(new))).hex(),
            text=text(new),occurrences=len(OLD.findall(old)),line_widths=list(map(width,text(new).splitlines()))))
    return entries

def prepare(disc):
    exe=disc.read(EXE);stage=disc.read(STAGE);hb=disc.read(HB)
    off=struct.unpack_from('<69I',hb,TABLE);rows=string_changes(exe,'exe')
    for c in range(68):
        raw=decode(stage[off[c]:off[c+1]])[0]
        rows+=string_changes(raw,'stage',c)
    vt=disc.read(VT1);vo=struct.unpack_from('<109I',exe,VT1_TABLE)
    for c in (40,50):
        raw=decode(vt[vo[c]:vo[c+1]])[0]
        require(len(raw)%57==0,'Briefing row stride')
        for at in range(0,len(raw),57):
            slot=raw[at:at+56];require(raw[at+56]==10,'Briefing newline')
            old=slot.split(b'\0')[0]
            if not OLD.search(old):continue
            new=substitute(old)
            rows.append(dict(kind='briefing',chunk=c,offset=at,capacity=56,before_hex=slot.hex(),
                after_hex=(new+bytes(56-len(new))).hex(),text=text(new),occurrences=len(OLD.findall(old)),line_widths=[width(text(new))]))
    require(len(rows)==23 and sum(r['occurrences'] for r in rows)==23,'Expected 23 installed faction references')
    return dict(version='0.3.14',base_hashes={n:sha(disc.read(n)) for n in (EXE,STAGE,HB,VT1)},entries=rows)

def patch(raw,rows):
    out=bytearray(raw);spans=[]
    for e in rows:
        at=e['offset'];old=bytes.fromhex(e['before_hex']);new=bytes.fromhex(e['after_hex'])
        require(len(old)==len(new)==e['capacity'] and raw[at:at+len(old)]==old,'Faction string binding changed')
        out[at:at+len(old)]=new;spans.append((at,at+len(old)))
    require(all(b<=c for (a,b),(c,d) in zip(sorted(spans),sorted(spans)[1:])),'Overlapping text spans')
    restored=bytearray(out)
    for a,b in spans:restored[a:b]=raw[a:b]
    require(restored==raw,'Unrelated bytes changed')
    return bytes(out)

def build(disc):
    inv=json.loads(INPUT.read_text(encoding='utf-8'))
    require(inv==prepare(disc),'Faction inventory drift')
    rows=inv['entries'];exe=patch(disc.read(EXE),[r for r in rows if r['kind']=='exe'])
    stage=disc.read(STAGE);hb=disc.read(HB);off=struct.unpack_from('<69I',hb,TABLE);changed={}
    for c in sorted({r['chunk'] for r in rows if r['kind']=='stage'}):
        raw=decode(stage[off[c]:off[c+1]])[0]
        changed[c]=patch(raw,[r for r in rows if r['kind']=='stage' and r['chunk']==c])
    newstage,newhb,_=repack(stage,hb,changed);new_off=struct.unpack_from('<69I',newhb,TABLE)
    for c in range(68):
        a=stage[off[c]:off[c+1]];b=newstage[new_off[c]:new_off[c+1]]
        require(decode(b)[0]==changed[c] if c in changed else a==b,'Stage preservation')
        require(not OLD.search(decode(b)[0]),'Remaining faction name in stage')
    restored=bytearray(newhb);restored[TABLE:TABLE+276]=hb[TABLE:TABLE+276];require(restored==hb,'HB table boundary')
    vt=disc.read(VT1);vo=struct.unpack_from('<109I',exe,VT1_TABLE);newvt=bytearray(vt);writes=[]
    for c in (40,50):
        lo,hi=vo[c:c+2];raw=decode(vt[lo:hi])[0]
        out=patch(raw,[r for r in rows if r['kind']=='briefing' and r['chunk']==c])
        flags=banlz.parse_header(vt[lo:hi])[1];packed=banlz.compress_record(out,flags=flags)
        if len(packed)>hi-lo:packed=banlz.compress_record_optimal(out,flags=flags)
        require(len(packed)<=hi-lo and decode(packed)[0]==out,'Briefing slot/readback')
        payload=packed+bytes(hi-lo-len(packed));newvt[lo:hi]=payload;writes.append(dict(start=lo,end=hi))
        require(not OLD.search(out),'Remaining briefing faction name')
    restored=bytearray(newvt)
    for w in writes:restored[w['start']:w['end']]=vt[w['start']:w['end']]
    require(restored==vt and not OLD.search(exe),'Protected VT1 or remaining EXE name')
    return {EXE:exe,STAGE:newstage,HB:newhb,VT1:bytes(newvt)},dict(entries=rows,
        stage_chunks=sorted(changed),briefing_spans=writes,occurrences=23,
        line_breaks_and_allocations_preserved=True,all_68_stage_chunks_verified=True,emulator='pending')
