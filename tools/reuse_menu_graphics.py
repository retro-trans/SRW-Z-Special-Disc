"""Reuse only English TIM2 images with byte-identical native counterparts."""
import argparse
import json
import struct
from collections import defaultdict
from library_text import *


def images(data):
    cursor=0
    while True:
        p=data.find(b'TIM2\x04\0\x01\0',cursor)
        if p<0:return
        size=16+struct.unpack_from('<I',data,p+16)[0]
        require(size>=64 and p+size<=len(data),'TIM2 size bounds')
        yield p,data[p:p+size]
        cursor=p+size


def build(exe):
    disc=Disc(SOURCE);donor=Disc(DONOR,True);out={};report={};patched=bytearray(exe)
    for member,table in [('DATA/JTIM.BIN',None),('DATA/NISVDATA.BIN',0x384A00)]:
        original=(ORIGINAL/member.replace('/','_')).read_bytes();native=disc.read(member);english=donor.read(member)
        aa=list(banlz.decompress_all(original)) if table else [(0,original)]
        bb=list(banlz.decompress_all(native)) if table else [(0,native)]
        cc=list(banlz.decompress_all(english)) if table else [(0,english)]
        require(len(aa)==len(cc),'Donor image archive count')
        answers=defaultdict(set)
        for (_,a),(_,c) in zip(aa,cc):
            ai=list(images(a));ci=list(images(c))
            require(len(ai)==len(ci),'Donor TIM2 count')
            for (ap,im),(cp,en) in zip(ai,ci):
                require(ap==cp and len(im)==len(en) and im[:64]==en[:64],'Donor texture frame drift')
                if im!=en:answers[sha(im)].add(en)
        chunks=[];changed=[];offsets=[];cursor=0
        for i,(at,raw) in enumerate(bb):
            result=bytearray(raw);rows=[]
            for p,im in images(raw):
                options=answers.get(sha(im),set())
                require(len(options)<=1,'Ambiguous texture donor')
                if options:
                    en=next(iter(options));result[p:p+len(im)]=en
                    rows.append(dict(offset=p,bytes=len(en),native_sha256=sha(im),english_sha256=sha(en)))
            end=bb[i+1][0] if i+1<len(bb) else len(native)
            payload=native[at:end]
            if rows:
                if table:
                    flags=banlz.parse_header(payload)[1];payload=banlz.compress_record(bytes(result),flags=flags)
                    require(decode(payload)[0]==result,'Reused texture compression readback')
                    payload+=bytes((-len(payload))%16)
                else:payload=bytes(result)
                changed.append(dict(chunk=i,images=rows))
            offsets.append(cursor);cursor+=len(payload);chunks.append(payload)
        if table:
            require(len(bb)==7 and list(struct.unpack_from('<8I',exe,table))==[p for p,r in bb]+[len(native)],'NISV offset table preimage')
            struct.pack_into('<8I',patched,table,*offsets,cursor)
        out[member]=b''.join(chunks)
        report[member]=dict(native_sha256=sha(native),donor_sha256=sha(english),original_sha256=sha(original),
            images=sum(len(r['images'])for r in changed),changes=changed,bytes=len(out[member]),sha256=sha(out[member]))
    return bytes(patched),out,report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    exe,outputs,report=build((ROOT/'work/cache/nonstory/library.elf').read_bytes())
    print(json.dumps(report,indent=2))
    if a.write:
        dest=ROOT/'work/cache/nonstory';(dest/'graphics.elf').write_bytes(exe)
        for name,data in outputs.items():
            path=dest/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        (ROOT/'work/analysis/menu-graphics-reuse.json').write_text(json.dumps(report,indent=2)+'\n')
    else:print('DRY RUN: no files written')

if __name__=='__main__':main()
