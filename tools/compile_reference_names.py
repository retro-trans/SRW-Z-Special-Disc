"""Translate squad presets and map labels with exact source ownership checks."""
import argparse
import json
import re
import struct
from collections import defaultdict
from library_text import *
from glossary_terms import canonicalize
from menu_encoding import menu_encode

NISV='DATA/NISVDATA.BIN'
MAPS='MAP/MAPNAME.BIN'
TABLE=0x384a00
SQUAD_SHA='bd23eef4110c12800c8749bae21f0f4655d6b1fdaf8b9197a84dfc41e5159df5'
MAP_SHA='b60f533808abe45453cea4a61234922f3f919bee1164788efa2221fc88e4669d'


def fixed(out,at,size,value):
    value=canonicalize(value);raw=menu_encode(value)
    require(not japanese(value) and len(raw)<size,'Invalid/oversize reference name: '+value)
    out[at:at+size]=raw+bytes(size-len(raw))
    require(text(out[at:at+size].split(b'\0')[0])==value,'Reference name readback')
    return value


def build(exe,archive):
    cfg=json.loads((ROOT/'work/translation/en/reference_names.json').read_text(encoding='utf-8'))
    current=list(banlz.decompress_all(archive));raw=current[4][1]
    require(sha(raw)==SQUAD_SHA and len(current)==7,'Squad source identity')
    require(struct.unpack_from('<H',raw,0x20)[0]==len(cfg['squads'])==113,'Squad count')
    result=bytearray(raw);entries=[]
    for i,value in enumerate(cfg['squads']):
        at=0x22+i*286;source=raw[at:at+28];z=source.index(0)
        require(not any(source[z:]),'Squad name padding ownership')
        value=fixed(result,at,28,value)
        entries.append(dict(id='squad/'+str(i),source_sha256=sha(source),text=value,offset=at,capacity=28))
    protected=bytearray(result)
    for i in range(113):
        at=0x22+i*286;protected[at:at+28]=raw[at:at+28]
    require(protected==raw,'Squad membership or header changed')
    offsets=[];chunks=[];cursor=0
    for i,(lo,decoded)in enumerate(current):
        hi=current[i+1][0]if i+1<len(current)else len(archive);packed=archive[lo:hi]
        if i==4:
            packed=banlz.compress_record(bytes(result),flags=banlz.parse_header(packed)[1]);packed+=bytes((-len(packed))%16)
            require(decode(packed)[0]==result,'Squad compression readback')
        offsets.append(cursor);cursor+=len(packed);chunks.append(packed)
    require(list(struct.unpack_from('<8I',exe,TABLE))==[p for p,r in current]+[len(archive)],'Squad archive table preimage')
    patched=bytearray(exe);struct.pack_into('<8I',patched,TABLE,*offsets,cursor)
    require(list(struct.unpack_from('<7I',exe,TABLE+32))==[len(r)for p,r in current],'Squad decoded buffer sizes')

    native=Disc(SOURCE).read(MAPS);old=(ORIGINAL/MAPS.replace('/','_')).read_bytes();english=Disc(DONOR,True).read(MAPS)
    require(sha(native)==MAP_SHA and len(native)==200*256 and len(old)==len(english)==195*256,'Map source identity')
    answers=defaultdict(set)
    for i in range(195):
        source=old[256*i:256*(i+1)].split(b'\0')[0];target=text(english[256*i:256*(i+1)].split(b'\0')[0])
        if not japanese(target):answers[source].add(target)
    maps=bytearray(native);reuse=0
    for i in range(200):
        at=i*256;field=native[at:at+256];source=field.split(b'\0')[0];jp=text(source)
        require(not any(field[len(source):]),'Map field padding ownership')
        if str(i)in cfg['map_overrides']:value=cfg['map_overrides'][str(i)];origin='SP reviewed map label'
        elif jp=='■-ワールドマップダミー':value='#World Map Dummy';origin='SP placeholder'
        elif re.fullmatch('■[0-9]+SP-未来\\([23]\\)',jp):value=jp.replace('■','#').replace('未来','Future');origin='SP future map variant'
        else:
            options=answers[source];require(len(options)==1,'Missing/ambiguous source map '+str(i))
            value=next(iter(options));origin='exact native source match';reuse+=1
        value=fixed(maps,at,256,value)
        entries.append(dict(id='map/'+str(i),source_sha256=sha(field),text=value,offset=at,capacity=256,origin=origin))
    report=dict(squad_names=113,map_names=200,exact_map_reuse=reuse,squad_membership_unchanged=True,
        decoded_sizes_unchanged=True,squad_source_sha256=SQUAD_SHA,map_source_sha256=MAP_SHA,entries=entries)
    return bytes(patched),{NISV:b''.join(chunks),MAPS:bytes(maps)},report


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    cache=ROOT/'work/cache/nonstory'
    exe,files,report=build((cache/'help.elf').read_bytes(),(cache/'help-NISVDATA.BIN').read_bytes())
    print(json.dumps({k:v for k,v in report.items()if k!='entries'},indent=2))
    print(json.dumps([r for r in report['entries']if r['id']in ('squad/9','squad/112','map/48','map/75','map/194')],indent=2))
    if args.write:
        (ROOT/'work/translation/en/reference_names_bound.json').write_text(json.dumps(report,indent=2)+'\n')
    else:print('DRY RUN: no files written')


if __name__=='__main__':main()
