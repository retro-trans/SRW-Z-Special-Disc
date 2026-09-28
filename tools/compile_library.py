"""Compile the reviewed encyclopedia while preserving every non-text field."""
import argparse
import json
import struct
from library_text import *


def build(exe):
    source=ROOT/'work/translation/en/library_complete.json'
    translation=json.loads(source.read_text(encoding='utf-8'))
    require(not translation['pending'],'Untranslated library entries')
    targets={r['id']:r for r in translation['entries']};used=set();output={};report={}
    patched=bytearray(exe)
    for key,(offset_at,size_at,count) in TABLES.items():
        member='DATA/MTVZKN'+key+'.BIN'
        native=(ROOT/'work/cache/library/native'/member).read_bytes()
        require(sha(native)==translation['locks'][member]['special_sha256'],'Library source drift')
        original=list(banlz.decompress_all(native));require(len(original)==count,'Library count drift')
        old_offsets=[p for p,r in original];old_sizes=[len(r) for p,r in original]
        require(list(struct.unpack_from('<%dI'%count,exe,offset_at))==old_offsets,'Library offset preimage')
        require(list(struct.unpack_from('<%dI'%count,exe,size_at))==old_sizes,'Library size preimage')
        chunks=[];offsets=[];sizes=[];cursor=0;preserved=0
        for i,(at,raw) in enumerate(original):
            header,rows=fields(raw);changed=[]
            for tag,value in rows:
                ident=f'{key}/{i}/{tag}'
                if ident in targets:
                    row=targets[ident];require(sha(value)==row['source_sha256'],'Library field preimage '+ident)
                    value=encode(row['text']);require(text(value)==row['text'],'Library encoding roundtrip '+ident)
                    used.add(ident)
                else:
                    if tag in TEXT_TAGS:require(not japanese(text(value)),'Japanese field remains '+ident)
                    preserved+=1
                changed.append((tag,value))
            result=serialize(header,changed)
            # Reparse rather than trusting the serializer's accounting.
            rh,rr=fields(result);require(rh==header and rr==changed,'ZKAN readback')
            packed=banlz.compress_record(result)
            require(decode(packed)[0]==result,'Library compression readback')
            packed+=bytes((-len(packed))%16)
            offsets.append(cursor);sizes.append(len(result));chunks.append(packed);cursor+=len(packed)
        output[member]=b''.join(chunks)
        struct.pack_into('<%dI'%count,patched,offset_at,*offsets)
        struct.pack_into('<%dI'%count,patched,size_at,*sizes)
        require(len(records(output[member]))==count,'Final archive count')
        report[key]=dict(records=count,translated_fields=sum(r['set']==key for r in targets.values()),
            preserved_fields=preserved,original_bytes=len(native),output_bytes=cursor,sha256=sha(output[member]))
    require(used==set(targets),'Unconsumed library translations')
    return bytes(patched),output,dict(sets=report,translation_sha256=file_sha(source),fields=len(used),remaining_japanese_fields=0)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    exe,outputs,report=build((ROOT/'work/cache/nonstory/runtime.elf').read_bytes())
    print(json.dumps(report,indent=2))
    if a.write:
        dest=ROOT/'work/cache/nonstory';(dest/'library.elf').write_bytes(exe)
        for name,data in outputs.items():
            path=dest/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        (ROOT/'work/analysis/library-build.json').write_text(json.dumps(report,indent=2)+'\n')
    else:print('DRY RUN: no files written')

if __name__=='__main__':main()
