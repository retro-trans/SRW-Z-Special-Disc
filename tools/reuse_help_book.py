"""Translate the native Strategy Q&A, preserving its fixed decoded buffers.

Format research: SRW-Z/tools/nisv_rec6.py and nisv_rec6_para.py (MIT).
Every changed SP page is explicitly reviewed; native wording must never be
replaced merely because its page number matches the original game.
"""
import argparse
import json
import re
import struct
from collections import defaultdict
from library_text import *
from battle_terms import canonicalize as scoped_names, PATH as SPELLING

MEMBER='DATA/NISVDATA.BIN'
TABLE=0x384a00
HDR=struct.Struct('<BBHHH')
REVIEWED={15,32,35,59,60,70,71,75,79,81,82,88,89,93,94,95,96,97,99,100,101,102}
NATIVE_SHA='6feb4829ea687b8c9720a65bf5b5709b79e79c4c0c7cfaa5a9acea9af593f800'


def parse(book):
    count,base=struct.unpack_from('<II',book)
    require(count==103 and base==0x350,'Help book index')
    sections=[]
    for i in range(count):
        off,size=struct.unpack_from('<II',book,8+8*i)
        require(base+off+size<=len(book) and size%16==0,'Help section bounds')
        raw=book[base+off:base+off+size];runs=[]
        if i:
            n=struct.unpack_from('<H',raw)[0];p=2
            require(n and n+2<=size and not any(raw[n+2:]),'Help body length')
            while p<n+2:
                if raw[p]==0:p+=1;continue
                k,a,x,y,f=HDR.unpack_from(raw,p);z=raw.find(b'\0',p+8,n+2)
                require(k in (2,4) and f==1 and z>=0,'Help run structure')
                runs.append(dict(kind=k,attr=a,x=x,y=y,flag=f,text=text(raw[p+8:z])))
                p=z+1
        sections.append(dict(raw=raw,runs=runs))
    return sections


def pack(runs):
    body=b''.join(HDR.pack(r['kind'],r['attr'],r['x'],r['y'],r['flag'])+encode(r['text'])+b'\0' for r in runs)
    require(len(body)<65536,'Help page length overflow')
    raw=struct.pack('<H',len(body))+body
    return raw+bytes((-len(raw))%16)


def width(value):
    # The help reader uses a constant 12-pixel destination advance for Latin.
    # Reserve 19 for command-range punctuation even when encoded half-width.
    return sum(12 if ord(c)<128 and not 0x2e<=ord(c)<=0x3d else 19 for c in value)


def wrap(value,limit):
    lines=[];line=''
    for word in value.split():
        candidate=(line+' '+word).strip()
        if line and width(candidate)>limit:lines.append(line);line=word
        else:line=candidate
        require(width(line)<=limit,'Unbreakable help word: '+word)
    if line:lines.append(line)
    return lines


def authored_page(blocks):
    runs=[];y=1
    for i,block in enumerate(blocks):
        attr,value=(6,block) if i==0 else (14,block[1:]) if block.startswith('#') else (0,block)
        x=19
        for line in wrap(value,513):
            runs.append(dict(kind=4 if i==0 else 2,attr=attr,x=x,y=y,flag=1,text=line));y+=11
        y+=11
    return runs


def repair_layout(runs):
    """Retain run order and words while removing inherited table collisions.

    A donor table cell can wrap into the next row. Move the colliding tail,
    including later rows, down as a group; keep adjacent colored spans intact.
    """
    out=[];shift=0;changes=0
    for original in runs:
        r=dict(original);r['y']+=shift
        if r['text'].split():
            r['x']=min(r['x'],532-max(width(w)for w in r['text'].split()))
        lines=wrap(r['text'],532-r['x'])
        if len(lines)<=1:lines=[r['text']]
        for index,line in enumerate(lines):
            row=dict(r,text=line,y=r['y']+11*index)
            while any(o['y']==row['y'] and o['x']<row['x']+width(line) and row['x']<o['x']+width(o['text']) for o in out):
                row['y']+=11;r['y']+=11;shift+=11;changes+=1
            out.append(row)
        if len(lines)>1:shift+=11*(len(lines)-1);changes+=len(lines)-1
    require(''.join(''.join(r['text'].split())for r in out)==''.join(''.join(r['text'].split())for r in runs),'Help layout lost words')
    for i,r in enumerate(out):
        require(r['x']+width(r['text'])<=532,'Help text exceeds panel')
        require(not any(s['y']==r['y'] and s['x']<r['x']+width(r['text']) and r['x']<s['x']+width(s['text'])for s in out[:i]),'Help overlap')
    return out,changes


def no_japanese(value):
    return not japanese(value.replace('・',''))


def build(exe,archive):
    native=Disc(SOURCE).read(MEMBER);original=(ORIGINAL/MEMBER.replace('/','_')).read_bytes();english=Disc(DONOR,True).read(MEMBER)
    aa,bb,cc=map(records,(original,native,english));current=list(banlz.decompress_all(archive))
    require(len(current)==len(bb)==7 and sha(bb[6])==NATIVE_SHA,'Help native identity')
    require(current[5][1]==bb[5] and current[6][1]==bb[6],'Help archive already patched')
    require(aa[5]==bb[5] and len(cc[5])==len(bb[5]),'Shared tutorial source/buffer mismatch')
    a,b,c=map(parse,(aa[6],bb[6],cc[6]));review=json.loads((ROOT/'work/translation/en/help_overrides.json').read_text(encoding='utf-8'))
    sections=[];targets=[];changes=[]
    changed={i for i in range(1,103) if a[i]['runs']!=b[i]['runs']}
    require(changed==REVIEWED,'Help changed-page review no longer matches')
    # Section zero stores u16 string indices, followed by a sequential string
    # list. The native and donor metadata are identical, including all indices.
    require(a[0]['raw'][:0x126]==b[0]['raw'][:0x126]==c[0]['raw'][:0x126],'Help chapter metadata drift')
    lists=[s[0]['raw'][0x126:].rstrip(b'\0').split(b'\0') for s in (a,b,c)]
    require(list(map(len,lists))==[264]*3,'Help chapter string count')
    chapter=[]
    for i,(old,src,en)in enumerate(zip(*lists)):
        value=review['chapter'].get(str(i),text(en))
        require(no_japanese(value),'Untranslated help chapter '+str(i))
        require(old==src or i in (31,32,33,193,212,213,232,254,256,257,258,260,261,262,263),'Unreviewed chapter change')
        chapter.append(encode(value)+b'\0')
        targets.append(dict(id='chapter/'+str(i),source_sha256=sha(src),text=value))
    first=b[0]['raw'][:0x126]+b''.join(chapter);first+=bytes((-len(first))%16);sections.append(first)
    for i in range(1,103):
        if str(i) in review['pages']:
            runs=authored_page(review['pages'][str(i)])
        else:
            runs=[dict(r)for r in c[i]['runs']]
            for old,new in review['replacements'].get(str(i),[]):
                matches=[r for r in runs if old in r['text']]
                require(len(matches)==1,'Help phrase preimage: '+str(i)+' '+old)
                matches[0]['text']=matches[0]['text'].replace(old,new)
        require(all(no_japanese(r['text'])for r in runs),'Untranslated help page '+str(i))
        native_context=''.join(r['text'] for r in b[i]['runs'])
        for run in runs:run['text']=scoped_names(run['text'],native_context,literal_breaks=False)
        runs,repairs=repair_layout(runs)
        sections.append(pack(runs));changes.append(dict(page=i,reviewed=i in REVIEWED,layout_repairs=repairs,max_y=max(r['y']for r in runs)))
        targets.append(dict(id='page/'+str(i),source_sha256=sha(b[i]['raw']),runs=runs))
    # Keep the fixed native decompression buffer. Expanded prose uses free
    # space created by repacking, never extra runtime memory.
    book=bytearray(len(bb[6]));book[:8]=bb[6][:8];cursor=0x350
    for i,section in enumerate(sections):
        require(cursor+len(section)<=len(book),'Help book exceeds native buffer')
        struct.pack_into('<II',book,8+i*8,cursor-0x350,len(section));book[cursor:cursor+len(section)]=section;cursor+=len(section)
    parsed=parse(book)
    for i in range(1,103):require(parsed[i]['runs']==targets[264+i-1]['runs'],'Help reparse mismatch')
    chunks=[];offsets=[];position=0
    for i,(start,raw)in enumerate(current):
        end=current[i+1][0]if i+1<len(current)else len(archive)
        payload=archive[start:end]
        if i in (5,6):
            decoded=cc[5]if i==5 else bytes(book)
            flags=banlz.parse_header(payload)[1];payload=banlz.compress_record(decoded,flags=flags);payload+=bytes((-len(payload))%16)
            require(decode(payload)[0]==decoded,'Help compression roundtrip')
        offsets.append(position);position+=len(payload);chunks.append(payload)
    require(list(struct.unpack_from('<8I',exe,TABLE))==[p for p,r in current]+[len(archive)],'Help current archive offsets')
    out=bytearray(exe);struct.pack_into('<8I',out,TABLE,*offsets,position)
    require(list(struct.unpack_from('<7I',out,TABLE+32))==[len(r)for p,r in current],'Help decoded-size preimage')
    archive=b''.join(chunks)
    report=dict(pages=102,chapter_fields=264,source_sha256=sha(native),output_sha256=sha(archive),bytes=len(archive),spelling_sha256=file_sha(SPELLING),
        book_decoded_bytes=len(book),book_used_bytes=cursor,decoded_buffer_sizes_unchanged=True,
        tutorial_source_identical=True,ime_dictionary_unchanged=records(archive)[3]==bb[3],page_checks=changes,entries=targets)
    return bytes(out),archive,report


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    dest=ROOT/'work/cache/nonstory'
    exe,archive,report=build((dest/'graphics.elf').read_bytes(),(dest/MEMBER).read_bytes())
    print(json.dumps({k:v for k,v in report.items()if k!='entries'},indent=2))
    print('Samples:',json.dumps([r for r in report['entries']if r['id']in ('chapter/254','page/93','page/102')],indent=2))
    if args.write:
        (dest/'help.elf').write_bytes(exe);(dest/'help-NISVDATA.BIN').write_bytes(archive)
        (ROOT/'work/analysis/help-book.json').write_text(json.dumps({k:v for k,v in report.items()if k!='entries'},indent=2)+'\n')
        (ROOT/'work/translation/en/help_book.json').write_text(json.dumps(report['entries'],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no files written')

if __name__=='__main__':main()
