"""Translate the shared Challenge confirmation and center its English text."""
import argparse,json,shutil,struct
from pathlib import Path
from sp_disc import ROOT,Disc,SOURCE,EXE,decode,banlz,sha,file_sha,require
from reuse_compdata import BBASE,pointers
from menu_encoding import menu_encode
from align_story_panels import actual_width

MEMBER='DATA/COMPDATA.BN'
BASE=0xff680
OFFSET=0x98270
CAPACITY=32
POINTER=0x6a2c8
POSITION=0x437038-BASE
BEFORE=0x2442ffac
SOURCE_TEXT='このミッションに挑戦しますか？'
TEXT='Attempt this mission?'
PREVIOUS=ROOT/'work/output/SRW Z Special Disc English v0.2.21.iso'
FOLDER=ROOT/'work/ui/mission-prompt'
BINDINGS=FOLDER/'native-inventory.json'
DRAFT=ROOT/'work/translation/en/mission_prompt_draft.json'
REVIEW=ROOT/'work/translation/en/mission_prompt_review.json'


def inventory():
    native=Disc(SOURCE);previous=Disc(PREVIOUS)
    co=decode(native.read(MEMBER))[0];prior=decode(previous.read(MEMBER))[0]
    raw=SOURCE_TEXT.encode('cp932')+b'\0'
    require(co[OFFSET:OFFSET+len(raw)]==raw,'Challenge source identity')
    hits=[];at=0
    while (at:=co.find(raw,at))>=0:hits.append(at);at+=len(raw)
    refs=[p for p,v in pointers(co,BBASE) if v==OFFSET]
    require(hits==[OFFSET] and refs==[POINTER],'Challenge question coverage changed')
    require(co[OFFSET:OFFSET+CAPACITY]==prior[OFFSET:OFFSET+CAPACITY],'Previous question already changed')
    require(co[POINTER:POINTER+4]==prior[POINTER:POINTER+4]==struct.pack('<I',BBASE+OFFSET),
            'Question pointer binding')
    exe=previous.read(EXE);original=native.read(EXE)
    start,end=0x43701c-BASE,0x43707c-BASE
    require(exe[start:end]==original[start:end],'Challenge confirmation caller changed')
    require(struct.unpack_from('<I',exe,POSITION)[0]==BEFORE,'Question coordinate preimage')
    # Both width measurement and rendering load the one shared pointer slot.
    for hi,lo in ((0x43701c,0x437020),(0x437054,0x437058)):
        h,l=(struct.unpack_from('<I',exe,v-BASE)[0] for v in (hi,lo))
        require(h>>26==15 and l>>26==35,'Question selector load kind')
        require(((h&65535)<<16)+struct.unpack('<h',struct.pack('<H',l&65535))[0]==BBASE+POINTER,
                'Question selector target')
    return dict(schema_version=1,baseline='0.2.21',member=MEMBER,offset=OFFSET,capacity=CAPACITY,
        pointer_sites=refs,source=SOURCE_TEXT,source_hex=co[OFFSET:OFFSET+CAPACITY].hex(),
        native_member_sha256=sha(native.read(MEMBER)),prior_member_sha256=sha(previous.read(MEMBER)),
        prior_exe_sha256=sha(exe),caller_offset=start,caller_bytes=end-start,caller_sha256=sha(exe[start:end]),
        position_offset=POSITION,position_before=BEFORE,question_center_x=236,question_y=111,
        scope='One shared confirmation for all 18 Challenge briefings',
        measure_call=0x437024,draw_call=0x43705c,choice_call=0x437074)


def prepare():
    inv=json.loads(BINDINGS.read_text(encoding='utf8'));draft=json.loads(DRAFT.read_text(encoding='utf8'))
    review=json.loads(REVIEW.read_text(encoding='utf8'))
    require(inv==inventory(),'Mission prompt inventory drift')
    require(draft['bindings_sha256']==file_sha(BINDINGS) and review['draft_sha256']==file_sha(DRAFT),
            'Mission prompt review binding')
    require(review['entries_examined']==review['entries_in_slice']==1 and
            review['verdict']=='pass' and review['text']==draft['text']==TEXT,'Mission prompt not approved')
    return inv


def compile_component(exe,comp,inv):
    raw=decode(comp)[0];out=bytearray(raw);patched=bytearray(exe)
    require(inv['offset']==OFFSET and inv['capacity']==CAPACITY and inv['pointer_sites']==[POINTER],
            'Mission prompt field ownership')
    require(raw[OFFSET:OFFSET+CAPACITY].hex()==inv['source_hex'],'Mission prompt text preimage')
    require(struct.unpack_from('<I',raw,POINTER)[0]==BBASE+OFFSET,'Mission prompt pointer conflict')
    start=inv['caller_offset'];size=inv['caller_bytes']
    require(sha(exe[start:start+size])==inv['caller_sha256'],'Mission prompt caller drift')
    encoded=menu_encode(TEXT);width=actual_width(TEXT);relative_x=-84-width//2
    require(len(encoded)+1<=CAPACITY and width<=560,'Mission prompt does not fit')
    out[OFFSET:OFFSET+CAPACITY]=encoded+bytes(CAPACITY-len(encoded))
    # Retain the measurement call and its side effects; replace only the final
    # x calculation with the measured English position. Choice logic is intact.
    word=0x24020000|(relative_x&65535)
    struct.pack_into('<I',patched,POSITION,word)
    restored=bytearray(out);restored[OFFSET:OFFSET+CAPACITY]=raw[OFFSET:OFFSET+CAPACITY]
    require(restored==raw,'Prompt edit escaped text slot')
    restored_exe=bytearray(patched);struct.pack_into('<I',restored_exe,POSITION,BEFORE)
    require(restored_exe==exe,'Prompt edit escaped position word')
    packed=banlz.compress_record(bytes(out),flags=banlz.parse_header(comp)[1])
    require(decode(packed)[0]==out,'Mission prompt compression readback')
    return bytes(patched),packed,dict(text=TEXT,questions=1,challenge_briefings=18,
        text_offset=OFFSET,text_capacity=CAPACITY,text_hex=out[OFFSET:OFFSET+CAPACITY].hex(),
        coordinate_offset=POSITION,coordinate_before=BEFORE,coordinate_after=word,
        actual_width=width,relative_x=relative_x,absolute_x=320+relative_x,center_x=236,
        decoded_before_sha256=sha(raw),decoded_after_sha256=sha(out),
        pointers_and_choice_logic_unchanged=True,runtime='pending by user choice')


def build(exe,comp):
    out,packed,report=compile_component(exe,comp,prepare())
    return out,packed,dict(report,bindings_sha256=file_sha(BINDINGS),draft_sha256=file_sha(DRAFT),
                          review_sha256=file_sha(REVIEW))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepare',action='store_true')
    p.add_argument('--write',action='store_true');a=p.parse_args()
    require(not a.write or a.prepare,'Only preparation writes metadata; use the main builder for binaries')
    if a.prepare:
        inv=inventory();draft=dict(source=SOURCE_TEXT,full_text='Do you want to attempt this mission?',text=TEXT)
        print(json.dumps(dict(inventory=inv,translation=draft),ensure_ascii=True,indent=2))
        if a.write:
            FOLDER.mkdir(parents=True,exist_ok=True)
            BINDINGS.write_text(json.dumps(inv,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
            DRAFT.write_text(json.dumps(dict(draft,bindings_sha256=file_sha(BINDINGS)),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
            src=Path(__import__('tempfile').gettempdir())/'codex-clipboard-e635343b-3bf6-4428-b670-cee4485b54ca.png'
            target=FOLDER/'user.png'
            if target.exists():require(file_sha(target)==file_sha(src),'Screenshot destination conflict')
            else:shutil.copyfile(src,target)
        else:print('DRY RUN: no metadata or screenshots written')
    else:
        previous=Disc(PREVIOUS);_,_,report=build(previous.read(EXE),previous.read(MEMBER))
        print(json.dumps(report,indent=2));print('DRY RUN: no binaries written')


if __name__=='__main__':main()
