"""Build 24 selection/briefing panels in VT1's native 56-byte line slots.

The executable copies 56 bytes, terminates the copy and passes it to the menu
text renderer; it then advances 57 bytes. Latin text can therefore use the
existing half-width renderer without changing the grid or page pointers.
"""
import argparse
import json
from library_text import encode,text,CHARS
from glossary_terms import canonicalize
from sp_disc import *
from inspect_english_runtime import CAVE,CAVE_FILE
from align_story_panels import INTRO_LIMIT


def build(challenge_limit=560):
    disc,exe,archive,offsets=source_records()
    targets=json.loads((ROOT/'work/translation/en/briefings.json').read_text(encoding='utf-8'))
    donor=(ROOT/'work/cache/english-runtime/english.elf').read_bytes()
    widths=donor[CAVE_FILE+0x78b960-CAVE:CAVE_FILE+0x78b960-CAVE+69]
    def px(s):return sum(widths[CHARS.index(ord(c))]+2 if ord(c)in CHARS else 13 if c==' ' else 24 for c in s)
    limit=560
    def fits(s):return len(encode(s))<=56 and px(s)<=limit
    def wrap(value):
        lines=[];line=''
        for word in canonicalize(value).split():
            candidate=(line+' '+word).strip()
            if line and not fits(candidate):lines.append(line);line=word
            else:line=candidate
            require(fits(line),'Briefing word too wide')
        if line:lines.append(line)
        return lines
    changes=[];pages=[]
    for chunk,per_page,key in ((40,9,'intro'),(50,7,'challenge')):
        limit=INTRO_LIMIT if key=='intro' else challenge_limit
        lo,hi=offsets[chunk:chunk+2];raw=decode(archive[lo:hi])[0];source=raw.splitlines(keepends=True)
        require(all(len(line)==57 and line[-1:]==b'\n'for line in source),'Native briefing grid')
        require(len(source)==len(targets[key])*per_page,'Briefing page count')
        out=bytearray()
        for index,target in enumerate(targets[key]):
            lines=wrap(target['text'] if key=='intro' else target)
            require(len(lines)<=7,f'{key}/{index}: needs {len(lines)} lines, maximum 7')
            lines+=['']*(7-len(lines))
            if key=='intro':lines=[target['title']]+lines+[target['question']]
            for line in lines:
                require(fits(line),'Briefing heading too wide');encoded=encode(line)
                out.extend(encoded+bytes(56-len(encoded))+b'\n')
                require(text(encoded)==line,'Briefing encoding roundtrip')
            src=b''.join(source[index*per_page:(index+1)*per_page])
            if key=='intro':require(' '.join(lines[1:-1]).split()==canonicalize(target['text']).split(),'Briefing words changed')
            pages.append(dict(id=f'{chunk}/{index}',source_sha256=sha(src),lines=lines,widths=[px(line)for line in lines],line_pixel_limit=limit))
        require(len(out)==len(raw),'Briefing buffer changed')
        flags=banlz.parse_header(archive[lo:hi])[1];packed=banlz.compress_record(bytes(out),flags=flags)
        if len(packed)>hi-lo:packed=banlz.compress_record_optimal(bytes(out),flags=flags)
        require(len(packed)<=hi-lo,f'Briefing chunk {chunk}: {len(packed)} bytes exceeds slot {hi-lo}')
        require(decode(packed)[0]==out,'Briefing compression readback')
        changes.append(dict(chunk=chunk,label=key+' panels',start=lo,end=hi,payload=packed+bytes(hi-lo-len(packed)),
            source_sha256=sha(raw),decoded_sha256=sha(out),compressed_bytes=len(packed),headroom=hi-lo-len(packed)))
    return changes,dict(pages=pages,decoded_sizes_unchanged=True,line_stride=57,text_bytes_per_line=56,
        line_pixel_limits=dict(intro=INTRO_LIMIT,challenge=challenge_limit),renderer_evidence=['0x436FB0: copy 56 bytes, terminate, render; advance 57',
            '0x437580: same loop; seven body rows', '0x37D790: menu text path; width routine 0x13A5A0'])


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args()
    changes,report=build();print(json.dumps(dict(chunks=[{k:v for k,v in r.items()if k!='payload'}for r in changes],**report),indent=2))
    if args.write:(ROOT/'work/ui/briefing-layout.json').write_text(json.dumps(report,indent=2)+'\n')
    else:print('DRY RUN: no files written')

if __name__=='__main__':main()
