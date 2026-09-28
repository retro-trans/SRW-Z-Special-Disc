"""Bind executable UI strings by exact source text; exclude suspend dialogue."""
import argparse
from collections import defaultdict,Counter
import json
import re
import struct
from library_text import *
from menu_encoding import menu_encode,TOKENS
from reuse_compdata import cstring
from reuse_compdata import POOL_BASE
from battle_terms import canonicalize as scoped_names
from inspect_english_runtime import hi_pair,s16,u32,B_BASE

AREAS=[(0x375c00,0x375e00),(0x3a7f00,0x3b8be0),(0x3be700,0x3c5180)]

def strings(data,areas):
    for lo,hi in areas:
        p=lo
        while p<hi:
            if data[p]==0:p+=1;continue
            end=data.find(b'\0',p,hi)
            if end<0:break
            parsed=cstring(data,p)
            if parsed and japanese(parsed[1]) and len(parsed[1])>=2:
                cap=end+1-p
                while (p+cap)%4 and p+cap<hi and data[p+cap]==0:cap+=1
                yield p,parsed[0],parsed[1],cap
            p=end+1

def build(exe):
    native=(ROOT/'work/cache/english-runtime/special.elf').read_bytes()
    original=(ROOT/'work/cache/english-runtime/original.elf').read_bytes()
    english=(ROOT/'work/cache/english-runtime/english.elf').read_bytes()
    answers=defaultdict(set)
    for p,raw,jp,cap in strings(original,[(0x300000,0x34d770)]):
        en=cstring(english,p)
        if en and not japanese(en[1]) and en[0]!=raw:answers[raw].add(en[1])
    overrides_file=ROOT/'work/translation/en/system_overrides.json'
    overrides=json.loads(overrides_file.read_text(encoding='utf-8')) if overrides_file.exists() else {}
    names=defaultdict(set)
    library=json.loads((ROOT/'work/translation/en/library_complete.json').read_text(encoding='utf-8'))
    for key in TABLES:
        docs=records((ROOT/'work/cache/library/native'/('DATA/MTVZKN'+key+'.BIN')).read_bytes())
        for row in library['entries']:
            if row['set']==key and row['tag'] in ('CHFN','CHNN','RBTN','WORD','PRDC'):
                jp=text(dict(fields(docs[row['record']])[1])[row['tag']]);names[jp].add(row['text'])
    words={jp:next(iter(en))for jp,en in names.items()if len(en)==1}
    words.update({jp:en for jp,en in overrides.items()if not jp.startswith('exe/')})
    def derived(jp):
        base=jp.strip();match=re.fullmatch(r'(.*?)\s*(\([0-9]+\)|Ver\.[A-Z])',base)
        if match and match[1] in words:return words[match[1]]+' '+match[2]
        match=re.fullmatch(r'(.*?)\(コスチューム\)',base)
        if match and match[1] in words:return words[match[1]]+' (Costume)'
        if base in words:return words[base]
        match=re.fullmatch(r'(壁紙|バトルセレクション|スライド|回転|ワイプ)([0-9]+)',base)
        if match:return words[match[1]]+' '+match[2]
        if base.startswith('・'):
            tail=base[1:]
            en=words.get(tail)
            if en is None:
                opts=answers.get(tail.encode('cp932'),set())
                if len(opts)==1:en=next(iter(opts))
            if en is not None:return '* '+en
        if re.fullmatch(r'[<・]?ー+[>.]?',base):return base.replace('ー','-').replace('・','*')
        if base.startswith('「') and base.endswith('」') and base[1:-1] in words:return '"'+words[base[1:-1]]+'"'
        return None
    candidates=list(strings(native,AREAS));addresses={p+B_BASE for p,r,j,c in candidates}
    refs=defaultdict(list);pairs=defaultdict(list)
    # Read-only analysis of the pristine executable. Only dedicated address
    # construction (lui r; addiu/ori r,r) is eligible for code relocation.
    for p in range(0x34e000,0x3c5180,4):
        va=u32(native,p)
        if va in addresses:refs[va].append(p)
    def read(p):return u32(native,p)
    for p in range(0x980,0x34e000,4):
        w=read(p);op=w>>26
        if op not in (9,13) or (w>>21)&31!=(w>>16)&31:continue
        pair=hi_pair(read,p,w,0x980)
        if not pair:continue
        hp,hw=pair;value=((hw&65535)<<16)+((w&65535)if op==13 else s16(w))
        if value in addresses:pairs[value].append((hp,p))
    pool=bytearray((ROOT/'work/cache/nonstory/menu-pool.bin').read_bytes())
    out=bytearray(exe);changes=[];pending=[];excluded=[]
    for p,raw,jp,cap in candidates:
        if cap<=4 or p%4 or jp.startswith(('Error:', 'Warning:', 'エラー :')) or p in (0x3a7fd0,0x3b0de8,0x3b0df8,0x3b0e10,0x3b0e30,0x3b0e50,0x3b0e58) or ('\n'in jp and (any(k in jp for k in ('NULL','Error:','KTSortLampTbl','_SORT_','Kv_PieceList','now(%d)','max = 0','設定されてませんYo','越えてます','ソート用のテーブル')))):
            excluded.append(dict(offset=p,reason='diagnostic or unaligned/binary candidate'));continue
        opts=answers.get(raw,set());ident=f'exe/{p:x}'
        inferred=derived(jp)
        if not opts and inferred is not None:opts={inferred}
        if jp in overrides:opts={overrides[jp]}
        if ident in overrides:opts={overrides[ident]}
        reason=None
        if len(opts)!=1:reason='ambiguous' if opts else 'missing'
        else:
            from glossary_terms import canonicalize
            en=scoped_names(canonicalize(next(iter(opts))),jp,literal_breaks=False);encoded=menu_encode(en)
            if Counter(TOKENS.findall(jp))!=Counter(TOKENS.findall(en)):reason='tokens'
            elif len(encoded)+1>cap and not refs[p+B_BASE] and not pairs[p+B_BASE]:reason='capacity'
        if reason:
            pending.append(dict(id=ident,source_ui_term=jp,capacity=cap,reason=reason,options=sorted(opts)));continue
        row=dict(id=ident,offset=p,capacity=cap,source_sha256=sha(raw),text=en)
        if len(encoded)+1>cap:
            va=POOL_BASE+len(pool);pool.extend(encoded+b'\0');pool.extend(bytes((-len(pool))%4))
            for at in refs[p+B_BASE]:
                require(u32(out,at)==p+B_BASE,'UI pointer conflicts with previous patch')
                struct.pack_into('<I',out,at,va)
            for hp,lp in pairs[p+B_BASE]:
                require(out[hp:hp+4]==native[hp:hp+4] and out[lp:lp+4]==native[lp:lp+4],'UI code relocation conflict')
                upper=va>>16 if read(lp)>>26==13 else (va+0x8000)>>16
                struct.pack_into('<I',out,hp,(read(hp)&0xffff0000)|upper)
                struct.pack_into('<I',out,lp,(read(lp)&0xffff0000)|(va&65535))
            row.update(relocated_address=va,pointer_sites=refs[p+B_BASE],instruction_pairs=pairs[p+B_BASE])
            require(cstring(pool,va-POOL_BASE)[1]==en,'Relocated UI readback')
        else:
            require(out[p:p+cap]==native[p:p+cap],'UI field overlaps previous component '+ident)
            out[p:p+cap]=encoded+bytes(cap-len(encoded))
            require((not en and out[p]==0) or cstring(out,p)[1]==en,'UI readback '+ident)
        changes.append(row)
    require(out[0x3b8be0:0x3be700]==native[0x3b8be0:0x3be700],'Suspend dialogue changed')
    return bytes(out),bytes(pool),dict(changes=changes,pending=pending,excluded=excluded,translated_fields=len(changes),pending_fields=len(pending),
        reasons=dict(Counter(r['reason']for r in pending)),suspend_dialogue_preserved=True,sha256=sha(out))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    exe,pool,r=build((ROOT/'work/cache/nonstory/graphics.elf').read_bytes())
    print(json.dumps({k:v for k,v in r.items()if k not in ('changes','pending','excluded')},indent=2));print(json.dumps(r['changes'][:8],indent=2))
    if a.write:
        (ROOT/'work/cache/nonstory/system.elf').write_bytes(exe)
        (ROOT/'work/cache/nonstory/system-pool.bin').write_bytes(pool)
        (ROOT/'work/analysis/system-text-reuse.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (ROOT/'work/translation/en/system.json').write_text(json.dumps(r['changes'],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:print('DRY RUN: no files written')

if __name__=='__main__':main()
