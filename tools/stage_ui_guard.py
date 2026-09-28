"""Protect every story/gameplay byte while allowing typed display pointers only."""
import json,struct
from sp_disc import ROOT,Disc,SOURCE,decode,require
from inspect_mission_conditions import inventory,TARGET

ROSTER_SITES=[base+i*32+28 for base,count in ((0x3fa0,12),(0x4140,3),(0x41c0,12)) for i in range(count)]

def assert_decoded(before,after,sites):
    require(len(after)==len(before),'Story decoded length changed')
    restored=bytearray(after)
    for p in sites:
        require(p%4==0 and 0<=p<=len(before)-4,'Invalid display pointer site')
        restored[p:p+4]=before[p:p+4]
    require(restored==before,'Story dialogue/gameplay changed outside UI pointers')

def check(stage,include_conditions=False,include_bazaar=False):
    d=Disc(SOURCE);native=d.read('DATA/STAGE.BIN');offsets=struct.unpack_from('<69I',d.read('HEDBDY/HB.BIN'),0x5170)
    require(len(stage)==len(native),'STAGE archive length changed')
    allowed={13:set(ROSTER_SITES)}
    if include_bazaar:
        from bazaar_slogan import SLOTS,validate_slot
        for i in SLOTS:allowed.setdefault(i,set())
    if include_conditions:
        inv=json.loads(TARGET.read_text(encoding='utf8'))
        require(inv==inventory(),'Mission source table bindings drift')
        for row in inv['entries']:
            if row['source']=='？？？':continue
            for o in row['occurrences']:allowed.setdefault(o['chunk'],set()).add(o['pointer_site'])
    changed=[];identical=0
    for i,(lo,hi) in enumerate(zip(offsets,offsets[1:])):
        if i==0:continue
        if i not in allowed:
            require(stage[lo:hi]==native[lo:hi],'Unrelated story chunk changed: '+str(i));identical+=1;continue
        before=decode(native[lo:hi])[0];after,used=decode(stage[lo:hi])
        require(len(after)==len(before) and not any(stage[lo+used:hi]),'Story decoded length/padding: '+str(i))
        if include_bazaar and i in SLOTS:after=validate_slot(before,after,i)
        assert_decoded(before,after,allowed[i])
        if stage[lo:hi]!=native[lo:hi]:changed.append(i)
        else:identical+=1
    return dict(changed_ui_chunks=changed,unchanged_compressed_story_chunks=identical,
                allowed_display_pointer_words=sum(map(len,allowed.values())),
                bazaar_banner_fields=3 if include_bazaar else 0,
                all_other_decoded_story_bytes_identical=True,story_dialogue_and_gameplay_unchanged=True)
