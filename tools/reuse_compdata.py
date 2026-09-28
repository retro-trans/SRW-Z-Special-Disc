"""Reuse exact English menu/name matches without changing gameplay records."""
import argparse
import json
import struct
import unicodedata
from collections import defaultdict,Counter
from library_text import *
from menu_encoding import menu_encode,TOKENS
from battle_terms import canonicalize as scoped_names, PATH as SPELLING

POOL_BASE=0x81F200

MEMBER='DATA/COMPDATA.BN'
ABASE,BBASE=0x6D6800,0x764F80
REGIONS=[('battle lines',0x904,0x1204),('parts',0x18fc,0x22ec),('pilots',0x2160,0x2b50),
 ('weapons',0x328a0,0x35a80),('abilities',0x4c8e0,0x54980),('units',0x4cae4,0x54b94),
 ('stage names',0x5e150,0x68630),('search',0x60790,0x69260),('buttons',0x61120,0x69d30)]
FIELDS=[('display',2,21),('family',23,23),('given',46,23)]

def reading_key(value):
    # Special Disc's sound-list keys remove voicing and expand small kana and
    # long vowels. Use this only within the known sound-list string pool.
    value=''.join(c for c in unicodedata.normalize('NFKD',value) if c not in '\u3099\u309a')
    value=value.translate(str.maketrans('ァィゥェォャュョッ','アイウエオヤユヨツ'))
    vowels={c:v for group,v in [('アカサタナハマヤラワ','ア'),('イキシチニヒミリ','イ'),('ウクスツヌフムユル','ウ'),('エケセテネヘメレ','エ'),('オコソトノホモヨロヲ','オ')]for c in group}
    out=''
    for c in value:out+=vowels.get(out[-1:],'') if c=='ー' else c
    return out

def region(p,edition):
    label='head'
    for name,a,b in REGIONS:
        if p >= (a if edition==0 else b):label=name
    return label

def pointers(data,base):
    for p in range(0,len(data)-3,4):
        v=struct.unpack_from('<I',data,p)[0]-base
        if 0<=v<len(data):yield p,v

def cstring(data,p):
    end=data.find(b'\0',p,min(len(data),p+4096))
    if end<0:return None
    raw=data[p:end]
    try:value=text(raw)
    except (UnicodeDecodeError,IndexError):return None
    if not value or any(ord(c)<32 and c not in '\n\t' for c in value):return None
    return raw,value

def build():
    a_stored=(ORIGINAL/MEMBER.replace('/','_')).read_bytes();b_stored=Disc(SOURCE).read(MEMBER);c_stored=Disc(DONOR,True).read(MEMBER)
    a,b,c=(decode(x)[0]for x in (a_stored,b_stored,c_stored));require(len(a)==len(c) and len(b)==652800,'Overlay sizes')
    answers=defaultdict(set);local=defaultdict(set);name_answers=defaultdict(set);weapon_variants=defaultdict(set);sound_variants=defaultdict(set)
    for p,target in pointers(a,ABASE):
        v=cstring(a,target);new=struct.unpack_from('<I',c,p)[0]-ABASE
        if not v or not japanese(v[1]) or not 0<=new<len(c):continue
        translated=cstring(c,new)
        if not translated or japanese(translated[1]):continue
        answers[v[0]].add(translated[1]);local[(region(p,0),v[0])].add(translated[1])
        if region(p,0)=='weapons':weapon_variants[v[1].replace('・','').replace(' ','')].add(translated[1])
        if 0x6ec00<=target<0x71c40:sound_variants[reading_key(v[1])].add(translated[1])
    def pilot_key(blob,start):return tuple(blob[start+off:start+off+cap].split(b'\0')[0]for label,off,cap in FIELDS)
    for i in range(933):
        key=pilot_key(a,0x2160+i*176)
        for label,off,cap in FIELDS:
            at=0x2160+i*176+off;raw=a[at:at+cap].split(b'\0')[0];en=c[at:at+cap].split(b'\0')[0]
            try:en=text(en)
            except UnicodeDecodeError:continue
            # English first/last-name order is carried by the complete source
            # identity; an intentionally empty family field is meaningful.
            if raw and not japanese(en):name_answers[(key,label)].add(en)
    # Library names provide exact native-name correspondence for newly added robots.
    lib=json.loads((ROOT/'work/translation/en/library_complete.json').read_text(encoding='utf-8'))
    for key in TABLES:
        rows=records((ROOT/'work/cache/library/native'/('DATA/MTVZKN'+key+'.BIN')).read_bytes())
        for row in lib['entries']:
            if row['set']==key and row['tag'] in ('RBTN','CHFN','CHNN','WORD','PRDC'):
                source=dict(fields(rows[row['record']])[1])[row['tag']]
                answers[source].add(row['text'])
    override_path=ROOT/'work/translation/en/menu_overrides.json'
    overrides=json.loads(override_path.read_text(encoding='utf-8')) if override_path.exists() else {}
    references=defaultdict(list)
    for p,target in pointers(b,BBASE):
        # The name/help pool starts after battle dialogue. Words inside pilot
        # records or text can accidentally look like pointers; do not use them.
        if p>=0x6a000 or 0x2b50<=p<0x35a80:continue
        if target<0x7b748 or target%4 or b[target-1]!=0:continue
        references[target].append(p)
    result=bytearray(b);changes=[];pending=[];ranges=[];pool=bytearray();pool_entries={}
    def apply(at,capacity,source,options,ident,regions,name_context=''):
        try:jp=text(source)
        except UnicodeDecodeError:return
        if not japanese(jp):return
        if jp in overrides:options={overrides[jp]}
        if ident in overrides:options={overrides[ident]}
        options={scoped_names(value,jp+'\n'+name_context,literal_breaks=False) for value in options}
        if len(options)!=1:
            pending.append(dict(id=ident,source_ui_term=jp,capacity=capacity,reason='missing' if not options else 'ambiguous',options=sorted(options),regions=regions));return
        from glossary_terms import canonicalize
        value=canonicalize(next(iter(options)));en=menu_encode(value)
        if Counter(TOKENS.findall(jp))!=Counter(TOKENS.findall(value)):
            pending.append(dict(id=ident,source_ui_term=jp,capacity=capacity,reason='tokens',text=value,regions=regions));return
        if len(en)+1>capacity:
            if ident.startswith('text/'):
                if en not in pool_entries:
                    pool_entries[en]=len(pool);pool.extend(en+b'\0');pool.extend(bytes((-len(pool))%4))
                address=POOL_BASE+pool_entries[en]
                for site in references[at]:
                    require(struct.unpack_from('<I',b,site)[0]==BBASE+at,'Relocated pointer preimage')
                    struct.pack_into('<I',result,site,address);ranges.append((site,site+4))
                changes.append(dict(id=ident,offset=at,capacity=capacity,source_sha256=sha(source),text=value,
                    relocated_address=address,pointer_sites=references[at]));return
            pending.append(dict(id=ident,source_ui_term=jp,capacity=capacity,reason='capacity',text=value,needed=len(en)+1,regions=regions));return
        require(not any(lo<at+capacity and hi>at for lo,hi in ranges),'Overlapping menu fields')
        ranges.append((at,at+capacity));result[at:at+capacity]=en+bytes(capacity-len(en))
        changes.append(dict(id=ident,offset=at,capacity=capacity,source_sha256=sha(source),text=value))
    for target,sites in sorted(references.items()):
        parsed=cstring(b,target)
        if not parsed or not japanese(parsed[1]):continue
        regions=sorted({region(p,1)for p in sites})
        if set(regions)<={'head','battle lines'}:continue
        if len(parsed[1])<2:continue
        raw=parsed[0];cap=len(raw)+1
        while (target+cap)%4 and target+cap<len(b) and b[target+cap]==0 and target+cap not in references:cap+=1
        opts=answers.get(raw,set())
        if not opts and regions==['weapons']:
            opts=weapon_variants.get(parsed[1].replace('・','').replace(' ',''),set())
        if not opts and 0x85e20<=target<=0x88640:
            opts=sound_variants.get(reading_key(parsed[1]),set())
        if len(opts)>1:
            narrowed=set().union(*(local.get((r,raw),set())for r in regions))
            if len(narrowed)==1:opts=narrowed
        apply(target,cap,raw,opts,f'text/{target:x}',regions)
    for i in range(969):
        key=pilot_key(b,0x2b50+i*178)
        for label,off,cap in FIELDS:
            at=0x2b50+i*178+off;raw=b[at:at+cap].split(b'\0')[0]
            apply(at,cap,raw,name_answers.get((key,label),set()),f'pilot/{i}/{label}',['pilots'],'\n'.join(text(part) for part in key))
    # The bytes outside explicit text slots are gameplay data and code.
    cursor=0
    for lo,hi in sorted(ranges):require(result[cursor:lo]==b[cursor:lo],'Protected overlay bytes changed');cursor=hi
    require(result[cursor:]==b[cursor:],'Protected overlay tail changed')
    for row in changes:
        actual=cstring(pool,row['relocated_address']-POOL_BASE) if 'relocated_address'in row else cstring(result,row['offset'])
        require((actual is not None and actual[1]==row['text']) or (not row['text'] and result[row['offset']]==0),'Overlay text readback '+str(row))
    packed=banlz.compress_record(bytes(result),flags=banlz.parse_header(b_stored)[1])
    require(decode(packed)[0]==result,'COMPDATA compression readback')
    return packed,bytes(pool),dict(native_sha256=sha(b_stored),original_sha256=sha(a_stored),donor_sha256=sha(c_stored),
        decoded_bytes=len(b),output_bytes=len(packed),sha256=sha(packed),changes=changes,pending=pending,spelling_sha256=file_sha(SPELLING),
        translated_fields=len(changes),pending_fields=len(pending),reasons=dict(Counter(x['reason']for x in pending)),
        gameplay_bytes_preserved=True,battle_dialogue_preserved=True,pool_base=POOL_BASE,pool_bytes=len(pool),pool_sha256=sha(pool))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    payload,pool,report=build()
    print(json.dumps({k:v for k,v in report.items()if k not in ('changes','pending')},indent=2))
    print(json.dumps(dict(samples=report['changes'][:8],pending=report['pending'][:18]),ensure_ascii=True,indent=2))
    if a.write:
        dest=ROOT/'work/cache/nonstory'/MEMBER;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(payload)
        (ROOT/'work/cache/nonstory/menu-pool.bin').write_bytes(pool)
        (ROOT/'work/analysis/compdata-reuse.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (ROOT/'work/translation/en/compdata.json').write_text(json.dumps(report['changes'],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no files written')

if __name__=='__main__':main()
