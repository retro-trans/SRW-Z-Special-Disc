"""Repack reviewed Special Disc narration and update its native allocation tables."""
import argparse
import json
import struct
from sp_disc import ROOT, Disc, SOURCE, EXE, decode, sha, require, banlz
from narration_format import MEMBER, SOURCE_SHA, SIZE_TABLE, OFFSET_TABLE, COUNT, native_records, parse, replace_text
from narration_text import layout, width, LINE_LIMIT, ROWS
from glossary_terms import canonicalize, PATH as GLOSSARY
from battle_terms import canonicalize as scoped_names, PATH as SPELLING
from library_text import text, japanese
from menu_encoding import menu_encode

INPUT=ROOT/'work/translation/en/narration_reviewed.json'
TERMS=ROOT/'work/glossary/narration-terms.json'


def build(exe):
    native,archive,old_offsets,old_sizes,records=native_records()
    cfg=json.loads(INPUT.read_text(encoding='utf-8'))
    require(cfg['source_sha256']==SOURCE_SHA and cfg['reviewed_ids']==list(range(COUNT)),'Narration review coverage')
    require([r['id']for r in cfg['entries']]==list(range(COUNT)),'Narration entry inventory')
    require(cfg['glossary_sha256']==sha(GLOSSARY.read_bytes()) and cfg['terms_sha256']==sha(TERMS.read_bytes()),'Narration glossary drift')
    require(cfg['spelling_sha256']==sha(SPELLING.read_bytes()),'Narration source-scoped name pass drift')
    require(set(cfg['review_inputs'])=={'narration.json','narration_review.json','narration_layout_review.json'},'Narration review input inventory')
    for name,digest in cfg['review_inputs'].items():
        require(sha((INPUT.parent/name).read_bytes())==digest,'Stale narration review '+name)
    out=bytearray(exe);chunks=[];offsets=[0];sizes=[];entries=[]
    for row,(_,raw,info)in zip(cfg['entries'],records):
        i=row['id'];require(row['source_record_sha256']==sha(raw) and row['source_text_sha256']==sha(info['text']),'Narration native binding '+str(i))
        require(row['meaning_reviewed'] and not japanese(row['text']),'Narration editorial gate')
        require(canonicalize(row['text'])==row['text'],'Narration spelling gate')
        require(scoped_names(row['text'],text(info['text']),literal_breaks=False)==row['text'],'Narration source-scoped spelling gate')
        lines=layout(row['text'],i);require(lines==row['lines'],'Narration layout drift')
        value='\n'.join(lines);encoded=menu_encode(value)
        require(text(encoded)==value and encoded.count(b'\n')==12,'Narration encoding readback')
        result=replace_text(raw,encoded);packed=banlz.compress_record(result)
        require(decode(packed)[0]==result,'Narration compressed readback')
        packed+=bytes((-len(packed))%16);chunks.append(packed);offsets.append(offsets[-1]+len(packed));sizes.append(len(result))
        entries.append(dict(id=i,source_record_sha256=sha(raw),source_text_sha256=sha(info['text']),
            decoded_sha256=sha(result),decoded_bytes=len(result),compressed_offset=offsets[-2],
            text=value,line_widths=list(map(width,lines)),duration_ms=info['duration_ms'],
            source_text_bytes=len(info['text']),english_text_bytes=len(encoded),nontext_commands_preserved=True))
    changes=[]
    for at,old,new in ((SIZE_TABLE,old_sizes,sizes),(OFFSET_TABLE,old_offsets,offsets)):
        before=struct.pack('<%dI'%len(old),*old);after=struct.pack('<%dI'%len(new),*new)
        require(native[at:at+len(before)]==before and out[at:at+len(before)]==before,'Narration table preimage')
        out[at:at+len(after)]=after;changes.append(dict(offset=at,source_hex=before.hex(),payload_hex=after.hex()))
    protected=bytearray(out)
    for row in changes:at=row['offset'];before=bytes.fromhex(row['source_hex']);protected[at:at+len(before)]=before
    require(protected==exe,'Unexpected narration executable mutation')
    member=b''.join(chunks)
    for i,(lo,hi)in enumerate(zip(offsets,offsets[1:])):
        raw,consumed=decode(member[lo:hi]);info=parse(raw)
        require(len(raw)==sizes[i] and not any(member[lo+consumed:hi]),'Narration table readback')
        require(text(info['text'])==entries[i]['text'],'Narration final English readback')
    return bytes(out),member,dict(source_sha256=SOURCE_SHA,output_sha256=sha(member),records=COUNT,
        original_bytes=len(archive),output_bytes=len(member),decoded_sizes=sizes,compressed_offsets=offsets,
        entries=entries,patches=changes,row_limit=ROWS,line_limit_font_units=LINE_LIMIT,
        allocation='Native loader uses updated decoded sizes; rawt copier allocates length + 1',
        nontext_commands_preserved=True,runtime='pending by user choice')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    exe,archive,report=build(Disc(SOURCE).read(EXE))
    print(json.dumps({k:v for k,v in report.items() if k not in ('entries','patches')},indent=2))
    print(json.dumps([r for r in report['entries']if r['id']in (0,6,9)],indent=2))
    if a.write:
        (ROOT/'work/cache/nonstory/narration-MTZSPROS.BIN').write_bytes(archive)
        (ROOT/'work/analysis/narration-build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no files written')


if __name__=='__main__':main()
