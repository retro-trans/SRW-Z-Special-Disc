"""Bind existing English encyclopedia fields to native SP field identities."""
import argparse
from collections import defaultdict,Counter
import json
import struct
from pathlib import Path
from sp_disc import ROOT,Disc,SOURCE,decode,sha,require,banlz,file_sha

DONOR=Path('E:/Projects/SRW Z/SRW Z English Original v0.9.85.iso')
ORIGINAL=Path('E:/Projects/SRW Z/_work/extracted')
MASTER=Path('E:/Projects/SRW-Z/analysis/zkn_en.json')
TABLES={'RT':(0x387160,0x386C30,330),'PT':(0x3865B0,0x385F30,413),'KW':(0x387770,0x387690,52)}
CHARS=[ord(c)for c in '."\'!,-?']+list(range(48,58))+list(range(65,91))+list(range(97,123))
TEXT_TAGS={'PRDC','RBTN','PLTN','ACTR','CHFN','CHNN','WORD','SRCE','DSCR','DSC2','KANA','HEIT','WEIT'}
MAP=bytes(c if c in (0,0x5e)else c^0x5e for c in range(256))

def fields(raw):
    wrapper=struct.unpack_from('<8I',raw)
    require(wrapper[:3]==(1,32,0) and wrapper[3]==wrapper[4] and len(raw)==32+wrapper[3],'ZKAN wrapper')
    p=raw[32:].translate(MAP);require(p[:4]==b'ZKAN' and p[16:20]==b'DSIZ' and p[24:28]==b'DATA','ZKAN structure')
    end=32+struct.unpack_from('<I',p,28)[0];cursor=32;rows=[]
    while cursor<end:
        tag=p[cursor:cursor+4].decode('ascii');n=struct.unpack_from('<I',p,cursor+4)[0]
        require(cursor+8+n<=end,'ZKAN field exceeds payload');rows.append((tag,p[cursor+8:cursor+8+n]));cursor+=8+n
    require(cursor==end and not any(p[end:]),'ZKAN nonzero tail')
    return p[:16],rows

def serialize(header,rows):
    body=b''.join(tag.encode()+struct.pack('<I',len(value))+value for tag,value in rows)
    p=header+b'DSIZ'+struct.pack('<I',len(body)+8)+b'DATA'+struct.pack('<I',len(body))+body
    p+=bytes(16-len(p)%16) # Always retain a trailing zero block for linked entries.
    return struct.pack('<8I',1,32,0,len(p),len(p),0,0,0)+p.translate(MAP)

def text(raw):
    out=[];i=0
    while i<len(raw):
        b=raw[i]
        if b==0x85 and i+1<len(raw) and 0x40<=raw[i+1]<0x40+138:
            out.append(chr(CHARS[(raw[i+1]-0x40)%69]));i+=2;continue
        n=2 if 0x81<=b<=0x9f or 0xe0<=b<=0xfc else 1
        ch=raw[i:i+n].decode('cp932');out.append(ch);i+=n
    return ''.join(chr(ord(c)-0xfee0)if 0xff01<=ord(c)<=0xff5e else ' 'if c=='\u3000'else c for c in ''.join(out))

def japanese(t):return any('\u3040'<=c<='\u30ff' or '\u3400'<=c<='\u9fff'for c in t)

def encode(value):
    out=bytearray()
    for c in value:
        o=ord(c)
        # These bytes are commands in the native menu text reader. Private
        # half-width codes preserve displayed digits and dots without commands.
        if 0x2e<=o<=0x3d:
            if o in CHARS:out.extend((0x85,0x40+CHARS.index(o)))
            else:out.extend(chr(o+0xfee0).encode('cp932'))
        else:out.extend(c.encode('cp932'))
    return bytes(out)

def records(blob):return [data for start,data in banlz.decompress_all(blob)]

def binding_key(tag,raw):
    # Line wrapping and paragraph indentation changed in some SP descriptions.
    # Only whitespace is normalized; wording and field kind still must match.
    return sha(''.join(text(raw).split()).encode('utf-8')) if tag in ('DSCR','DSC2') else sha(raw)

def prepare():
    sp=Disc(SOURCE);donor=Disc(DONOR,runtime=True);master=json.loads(MASTER.read_text(encoding='utf-8'))
    targets=[];pending=[];stats={};locks={};native_cache={};donor_cache={}
    for key in TABLES:
        name='DATA/MTVZKN'+key+'.BIN';a=(ORIGINAL/name.replace('/','_')).read_bytes();b=sp.read(name);c=donor.read(name)
        aa,bb,cc=map(records,(a,b,c));require(len(aa)==len(cc),'Donor record count')
        require(len(bb)==TABLES[key][2],'SP encyclopedia count')
        answers=defaultdict(dict);owned=defaultdict(dict);counts=Counter()
        for i,(old,new)in enumerate(zip(aa,cc)):
            ah,ar=fields(old);ch,cr=fields(new);require(ah[:12]==ch[:12],'Donor document identity')
            require([k for k,v in ar]==[k for k,v in cr],'Donor tags changed')
            for (tag,source),(_,translated)in zip(ar,cr):
                if tag not in TEXT_TAGS:continue
                candidate=master.get(key,{}).get(str(i),{}).get(tag) if tag in ('DSCR','DSC2') else None
                try:en=candidate if candidate and '\ufffd'not in candidate and not japanese(candidate)else text(translated)
                except UnicodeDecodeError:continue
                if japanese(en)or '\ufffd'in en:continue
                origin=dict(record=i,origin='translation-master'if en==candidate else 'built-donor')
                bind=(tag,binding_key(tag,source));owner=dict(ar).get({'RT':'RBTN','PT':'CHFN','KW':'WORD'}[key])
                answers[bind][en]=origin;owned[(owner,bind)][en]=origin
        for i,raw in enumerate(bb):
            header,rows=fields(raw)
            for tag,source in rows:
                if tag not in TEXT_TAGS:continue
                try:jp=text(source)
                except UnicodeDecodeError:continue
                bind=(tag,binding_key(tag,source));owner=dict(rows).get({'RT':'RBTN','PT':'CHFN','KW':'WORD'}[key])
                options=answers.get(bind,{})
                if len(options)>1:options=owned.get((owner,bind),options)
                if len(options)==1:
                    en,origin=next(iter(options.items()))
                    targets.append(dict(id=f'{key}/{i}/{tag}',set=key,record=i,tag=tag,source_sha256=sha(source),text=en,donor=origin))
                    counts['bound_fields']+=1
                elif japanese(jp):
                    item=dict(id=f'{key}/{i}/{tag}',set=key,record=i,tag=tag,source_sha256=sha(source),reason='ambiguous'if options else 'SP-specific',characters=len(jp))
                    if tag not in ('DSCR','DSC2'):item['source_ui_term']=jp
                    pending.append(item);counts['pending_fields']+=1
                else:counts['native_numeric_or_non_Japanese_fields']+=1
        stats[key]=dict(records=len(bb),**counts)
        locks[name]=dict(original_sha256=sha(a),special_sha256=sha(b),english_sha256=sha(c))
        native_cache[name]=b;donor_cache[name]=c
    report=dict(schema_version=1,source='exact native field hash + field tag',master_sha256=file_sha(MASTER),locks=locks,stats=stats,entries=targets,pending=pending)
    return report,native_cache,donor_cache

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args()
    r,n,d=prepare();print(json.dumps(dict(stats=r['stats'],pending=[{k:v for k,v in p.items()if k not in ('source_sha256','set','record','tag')}for p in r['pending']]),ensure_ascii=True,indent=2))
    if a.write:
        out=ROOT/'work/translation/en/library.json';out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        for prefix,files in [('native',n),('donor',d)]:
            for name,data in files.items():
                p=ROOT/'work/cache/library'/prefix/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        (ROOT/'work/analysis/library-binding.json').write_text(json.dumps({k:v for k,v in r.items()if k!='entries'},indent=2)+'\n')
    else:print('DRY RUN: would write English fields, source hashes, and local binary cache; no Japanese description dump')

if __name__=='__main__':main()
