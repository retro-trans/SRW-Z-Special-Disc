"""Install all 57 reviewed post-save scenes in the native executable text region."""
import json,struct
from sp_disc import ROOT,EXE,require,sha,file_sha
from suspend_format import native_records,TEXT_START,TEXT_END,SCRIPT_START,SCRIPT_END,COLLISION
from rand_suspend_scene import layout
from story_layout import px
from story_runtime import apply,convert,NEW_FILE,CODE_BYTES,TABLE_BYTES
from test_story_runtime import execute
from review_suspend_messages import prepare as reviewed_source

FITS=ROOT/'work/translation/en/suspend_full_fits.json'
REVIEW=ROOT/'work/translation/en/suspend_reviewed.json'


def build(exe):
    native,sources,scenes=native_records()
    reviewed=json.loads(REVIEW.read_text(encoding='utf-8'))
    fresh=reviewed_source()
    require({k:v for k,v in reviewed.items() if k!='glossary_inputs'}==
            {k:v for k,v in fresh.items() if k!='glossary_inputs'},'Suspend reviewed content changed')
    require(set(reviewed['glossary_inputs'])==set(fresh['glossary_inputs']),'Glossary dependency inventory changed')
    fits=json.loads(FITS.read_text(encoding='utf-8'))['entries'];by_id={r['id']:r for r in fits}
    require(len(by_id)==len(fits),'Duplicate suspend fit')
    require(exe[SCRIPT_START:SCRIPT_END]==native[SCRIPT_START:SCRIPT_END],'Suspend commands no longer native')
    require(exe[TEXT_START:0x3BE460]==native[TEXT_START:0x3BE460],'Untracked prior suspend translation')
    require(apply(exe)[0]==exe,'Installed text converter changed')
    table=exe[NEW_FILE+CODE_BYTES:NEW_FILE+CODE_BYTES+TABLE_BYTES]
    pool=bytearray();rows=[];out=bytearray(exe);patches=[]
    for source,row in zip(sources,reviewed['entries']):
        i=source['id'];require(row['id']==i and row['source_sha256']==source['source_sha256']
            and row['occurrences']==source['occurrences'] and row['meaning_reviewed'],'Suspend reviewed binding')
        if i>=288:
            # Preserve the exact wording and layout shipped in v0.3.5.
            value=exe[source['offset']:exe.index(0,source['offset'])].decode('cp932')
            speaker,body=value.split('\n',1);lines=body.split('\n')
            require(speaker==row['speaker'] and body.startswith('\u300c') and body.endswith('\u300d'),
                    'Prior Rand/Mel scene changed')
        else:
            speaker,body=row['text'].split('\n',1);value=body[1:-1]
            if i in by_id:
                fit=by_id[i];require(fit['was']==row['text'] and fit['source_sha256']==source['source_sha256'],'Stale suspend fit')
                value=fit['text']
            lines=layout(value);value=speaker+'\n'+'\n'.join(lines)
        require(len(lines)<=3 and max(map(px,lines))<=400,'Suspend layout limit')
        encoded=value.encode('cp932');converted=convert(encoded,table)
        require(b'$' not in encoded and len(converted)+1<=452 and max(map(len,converted.split(b'\n')))<=256,'Suspend parser/allocation bounds')
        require(execute(exe,encoded)==converted and converted.count(b'\n')==len(lines),'Suspend converter execution')
        at=TEXT_START+len(pool);pool.extend(encoded+b'\0')
        for occurrence in source['occurrences']:
            pos=occurrence['pointer_offset'];before=struct.unpack_from('<I',exe,pos)[0]
            require(before==source['address'],'Suspend typed pointer changed')
            after=at+0xFF680;struct.pack_into('<I',out,pos,after)
            patches.append(dict(offset=pos,before=before,after=after))
        rows.append(dict(id=i,speaker=speaker,text=value,offset=at,source_sha256=source['source_sha256'],
            occurrences=source['occurrences'],line_widths=list(map(px,lines)),encoded_bytes=len(encoded)+1,
            converted_bytes=len(converted)+1,compact_fit=i in by_id,retained_previous=i>=288))
    require(len(pool)<=TEXT_END-TEXT_START,'Suspend text region exhausted')
    out[TEXT_START:TEXT_END]=pool+bytes(TEXT_END-TEXT_START-len(pool))
    for row in rows:
        for o in row['occurrences']:
            at=struct.unpack_from('<I',out,o['pointer_offset'])[0]-0xFF680
            require(out[at:out.index(0,at)].decode('cp932')==row['text'],'Suspend pointer readback')
    restored=bytearray(out);restored[TEXT_START:TEXT_END]=exe[TEXT_START:TEXT_END]
    for p in patches:struct.pack_into('<I',restored,p['offset'],p['before'])
    require(restored==exe and out[COLLISION:COLLISION+4]==exe[COLLISION:COLLISION+4],'Unrelated executable/numeric table change')
    return bytes(out),dict(entries=rows,scenes=len(scenes),text_records=len(rows),typed_pointers=len(patches),
        new_translations=288,retained_translations=8,pool_bytes=len(pool),capacity=TEXT_END-TEXT_START,
        patches=patches,review_sha256=file_sha(REVIEW),fits_sha256=file_sha(FITS),
        current_glossary_inputs=fresh['glossary_inputs'],reviewed_glossary_inputs=reviewed['glossary_inputs'],
        executable_sha256=sha(out),all_other_executable_bytes_identical=True,emulator='pending')
