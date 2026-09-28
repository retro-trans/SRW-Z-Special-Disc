"""Translate the three fixed Bazaar banner fields; never edit dialogue."""
import argparse,json,struct
from sp_disc import ROOT,Disc,SOURCE,decode,banlz,sha,file_sha,require
from menu_encoding import menu_encode
from align_story_panels import actual_width

MEMBER='DATA/STAGE.BIN'
SLOTS={44:0x1d44,49:0x2b24,50:0x1d84}
SOURCE_TEXT='勝負を分けるのは精神力？'
TEXT='Does willpower decide the outcome?'
FOLDER=ROOT/'work/ui/setup-art'
BINDINGS=FOLDER/'bazaar-slogan-inventory.json'
DRAFT=ROOT/'work/translation/en/bazaar_slogan_draft.json'
REVIEW=ROOT/'work/translation/en/bazaar_slogan_review.json'
CAPACITY=128
PRIOR=ROOT/'work/output/SRW Z Special Disc English v0.2.22.iso'

def inventory():
    d=Disc(SOURCE);stage=d.read(MEMBER);offsets=struct.unpack_from('<69I',d.read('HEDBDY/HB.BIN'),0x5170)
    hits=[];rows=[]
    for i,(lo,hi)in enumerate(zip(offsets,offsets[1:])):
        raw=decode(stage[lo:hi])[0];needle=SOURCE_TEXT.encode('cp932')+b'\0';p=0
        while (p:=raw.find(needle,p))>=0:hits.append((i,p));p+=len(needle)
        if i not in SLOTS:continue
        p=SLOTS[i];expected=needle+bytes(CAPACITY-len(needle))
        require(raw[p:p+CAPACITY]==expected,'Bazaar fixed banner identity')
        # The same inline banner layout follows the shop setup fields in all
        # three mission records. Pin its entire adjacent structure, not prose.
        rows.append(dict(chunk=i,start=lo,end=hi,offset=p,capacity=CAPACITY,
            source_hex=expected.hex(),context_sha256=sha(raw[p-48:p+CAPACITY+12]),
            context_hex=raw[p-48:p].hex(),native_sha256=sha(raw)))
    require(hits==list(SLOTS.items()),'Bazaar slogan occurrence coverage')
    return dict(schema_version=1,source=SOURCE_TEXT,text=TEXT,entries=rows,
                source_sha256=sha(stage),prior_sha256=sha(Disc(PRIOR).read(MEMBER)),
                width=actual_width(TEXT),field_kind='128-byte inline Bazaar banner; same preceding shop configuration')

def validate_slot(before,after,chunk):
    p=SLOTS[chunk];native=SOURCE_TEXT.encode('cp932');en=menu_encode(TEXT)
    require(before[p:p+CAPACITY]==native+bytes(CAPACITY-len(native)),'Native Bazaar slot')
    require(after[p:p+CAPACITY]==en+bytes(CAPACITY-len(en)),'English Bazaar banner readback')
    require(after[p-48:p]==before[p-48:p] and after[p+CAPACITY:p+CAPACITY+12]==before[p+CAPACITY:p+CAPACITY+12],
            'Bazaar shop structure changed')
    result=bytearray(after);result[p:p+CAPACITY]=before[p:p+CAPACITY];return bytes(result)

def build(stage):
    inv=json.loads(BINDINGS.read_text(encoding='utf8'));draft=json.loads(DRAFT.read_text(encoding='utf8'));review=json.loads(REVIEW.read_text(encoding='utf8'))
    require(inv==inventory() and draft['bindings_sha256']==file_sha(BINDINGS),'Bazaar input drift')
    require(review['draft_sha256']==file_sha(DRAFT) and review['verdict']=='pass' and
            review['entries_examined']==review['entries_in_slice']==1 and review['text']==TEXT,'Bazaar meaning review')
    result=bytearray(stage);rows=[];en=menu_encode(TEXT)
    require(len(en)<CAPACITY and actual_width(TEXT)<=500,'Bazaar banner overflow')
    for row in inv['entries']:
        lo,hi,p=row['start'],row['end'],row['offset'];old=decode(stage[lo:hi])[0];new=bytearray(old)
        require(old[p:p+CAPACITY].hex()==row['source_hex'],'Bazaar banner conflicts with prior changes')
        new[p:p+CAPACITY]=en+bytes(CAPACITY-len(en))
        require(validate_slot(old,new,row['chunk'])==old,'Bazaar edit escaped banner')
        packed=banlz.compress_record(bytes(new),flags=banlz.parse_header(stage[lo:hi])[1])
        if len(packed)>hi-lo:packed=banlz.compress_record_optimal(bytes(new),flags=banlz.parse_header(stage[lo:hi])[1])
        require(len(packed)<=hi-lo and decode(packed)[0]==new,'Bazaar compression bounds/readback')
        result[lo:hi]=packed+bytes(hi-lo-len(packed))
        rows.append(dict(row,before_sha256=sha(old),after_sha256=sha(new),compressed_bytes=len(packed)))
    return bytes(result),dict(entries=rows,text=TEXT,width=actual_width(TEXT),story_dialogue_unchanged=True,
        bindings_sha256=file_sha(BINDINGS),draft_sha256=file_sha(DRAFT),review_sha256=file_sha(REVIEW))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepare',action='store_true');p.add_argument('--write',action='store_true');a=p.parse_args()
    if a.prepare:
        inv=inventory();draft=dict(source=SOURCE_TEXT,full_text=TEXT,text=TEXT)
        print(json.dumps(dict(inventory=inv,draft=draft),ensure_ascii=True,indent=2))
        if a.write:
            BINDINGS.write_text(json.dumps(inv,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
            DRAFT.write_text(json.dumps(dict(draft,bindings_sha256=file_sha(BINDINGS)),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    else:print(json.dumps(build(Disc(PRIOR).read(MEMBER))[1],indent=2))
    if not a.write:print('DRY RUN: no files written')

if __name__=='__main__':main()
