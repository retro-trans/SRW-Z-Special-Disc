"""Apply reviewed SP source variants and newly authored encyclopedia text."""
import argparse
import json
import textwrap
import re
from library_text import *
from inspect_english_runtime import CAVE,CAVE_FILE
from glossary_terms import canonicalize
from battle_terms import canonicalize as scoped_names, PATH as SPELLING
from reviewed_library_corrections import corrections as reviewed_corrections

# Explicitly reviewed pairs, not a similarity threshold. Source changes are
# punctuation, spelling, grammatical corrections, or the two notes below.
REVIEWED={
 'RT':{44:44,75:75,77:77,103:102,113:112,125:124,127:126,128:127,131:130,
       133:132,144:143,146:145,160:158,161:159,163:161,164:162,165:163,
       170:168,171:169,173:171,174:172,179:177,275:272},
 'PT':{78:78,295:295,322:322,327:327},'KW':{18:18,23:23}}

def wrap(paragraphs,key):
    width={'RT':48,'PT':26,'KW':44}[key]
    return '\n'.join(textwrap.fill(p,width=width,initial_indent=' ',break_long_words=False,break_on_hyphens=False)for p in paragraphs)

def wrap_pixels(value,key):
    donor=(ROOT/'work/cache/english-runtime/english.elf').read_bytes()
    widths=donor[CAVE_FILE+0x78b960-CAVE:CAVE_FILE+0x78b960-CAVE+69]
    limit={'RT':560,'PT':280,'KW':544}[key]
    def width(line):return sum(widths[CHARS.index(ord(c))]+2 if ord(c)in CHARS else 13 if c==' ' else 24 for c in line)
    paragraphs=[]
    for line in value.splitlines():
        if not line.strip():paragraphs.append('');continue
        if line.startswith(' ') or not paragraphs or not paragraphs[-1]:paragraphs.append(line.strip())
        else:paragraphs[-1]+=' '+line.strip()
    result=[]
    for paragraph in paragraphs:
        if not paragraph:result.append('');continue
        line=' '
        for word in paragraph.split():
            candidate=line+('' if line==' ' else ' ')+word
            if width(candidate)>limit and line.strip():result.append(line);line=word
            else:line=candidate
            require(width(line)<=limit,'Unbreakable Library word exceeds panel')
        result.append(line)
    return '\n'.join(result)

def run():
    path=ROOT/'work/translation/en/library.json';current=json.loads(path.read_text(encoding='utf-8'))
    extra=json.loads((ROOT/'work/translation/en/library_new.json').read_text(encoding='utf-8'))
    corrections=json.loads((ROOT/'work/translation/en/library_corrections.json').read_text(encoding='utf-8'))['entries']
    corrections += reviewed_corrections()
    master=json.loads(MASTER.read_text(encoding='utf-8'));require(file_sha(MASTER)==current['master_sha256'],'Master changed')
    entries={r['id']:r for r in current['entries']};reviews=[];sources={};name_changes=[]
    for key in TABLES:
        name='DATA/MTVZKN'+key+'.BIN';blob=(ROOT/'work/cache/library/native'/name).read_bytes()
        require(sha(blob)==current['locks'][name]['special_sha256'],'Native library cache changed')
        native=records(blob)
        for row in entries.values():
            if row['set']==key:
                native_fields=dict(fields(native[row['record']])[1]);source=native_fields[row['tag']]
                require(sha(source)==row['source_sha256'],'Library name source drift')
                sources[row['id']]=text(source)
                if row['tag'] in ('DSCR','DSC2'):
                    sources[row['id']]+='\n'+text(native_fields[{'RT':'RBTN','PT':'CHFN','KW':'WORD'}[key]])
        for pending in [p for p in current['pending']if p['set']==key]:
            id_=pending['id'];index,tag=pending['record'],pending['tag'];source=dict(fields(native[index])[1])[tag]
            require(sha(source)==pending['source_sha256'],'Pending source drift')
            reason='new Special Disc translation';origin=None
            if id_ in extra['names']:value=extra['names'][id_]
            elif f'{key}/{index}'in extra['descriptions'] and tag in ('DSCR','DSC2'):
                value=wrap(extra['descriptions'][f'{key}/{index}'],key)
            elif index in REVIEWED.get(key,{}) and tag in ('DSCR','DSC2'):
                origin=REVIEWED[key][index];value=master[key][str(origin)][tag]
                reason='reviewed native punctuation/spelling/grammar variant'
                if key=='RT' and index==103:
                    value=value.replace('brainwashed by the Innocent',"under the Innocent's mind control")
                    reason='SP rephrases brainwashing as mind control; adapted wording'
                if key=='RT' and index==275:
                    require('New\nEmpire Forces' in value or 'New Empire Forces'in value,'Aquarion faction preimage')
                    value=value.replace('New\nEmpire Forces','New United Nations Forces').replace('New Empire Forces','New United Nations Forces')
                    reason='SP corrects New Empire to New United Nations Forces'
                if key=='RT' and index in (103,275):value=wrap([' '.join(value.split())],key)
            else:raise ValueError('Unreviewed pending field '+id_)
            require(not japanese(value) and '\ufffd'not in value,'Invalid English field '+id_)
            encode(value)
            entries[id_]=dict(id=id_,set=key,record=index,tag=tag,source_sha256=sha(source),text=value,
                             donor=dict(record=origin,origin=reason))
            sources[id_]=text(source)
            if tag in ('DSCR','DSC2'):
                sources[id_]+='\n'+text(dict(fields(native[index])[1])[{'RT':'RBTN','PT':'CHFN','KW':'WORD'}[key]])
            reviews.append(dict(id=id_,source_sha256=sha(source),donor_record=origin,decision=reason))
    # Some legacy master paragraphs use full-width Latin punctuation/digits.
    # Normalize those characters before selecting the English glyph encoding.
    for row in entries.values():
        for correction in corrections:
            if row['id'] in correction['ids']:
                if 'source_sha256' in correction:
                    require(row['source_sha256']==correction['source_sha256'],'Reviewed Library correction source drift')
                pattern=r'\s+'.join(re.escape(w)for w in correction['old'].split())
                row['text'],n=re.subn(pattern,lambda m:correction['new'],row['text'])
                require(n==1,'Library editorial preimage '+row['id'])
                row['review_note']=correction['reason']
        row['text']=canonicalize(''.join(chr(ord(c)-0xfee0) if 0xff01<=ord(c)<=0xff5e else ' ' if c=='\u3000' else c for c in row['text']))
        before=row['text'];row['text']=scoped_names(before,sources[row['id']],literal_breaks=False)
        if before!=row['text']:
            name_changes.append(dict(id=row['id'],source_sha256=row['source_sha256'],
                context_sha256=sha(sources[row['id']].encode('utf-8')),before=before,after=row['text']))
        if row['tag'] in ('DSCR','DSC2'):row['text']=wrap_pixels(row['text'],row['set'])
    result=dict(current,entries=list(entries.values()),pending=[],reviewed_overrides=reviews,
                spelling_sha256=file_sha(SPELLING),name_changes=name_changes)
    return result,reviews

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    result,reviews=run();print(json.dumps(dict(english_fields=len(result['entries']),reviewed=len(reviews),pending=result['pending'],samples=[r for r in result['entries']if r['id']in ('RT/244/DSCR','RT/275/DSCR','PT/399/DSCR')]),indent=2))
    if args.write:
        (ROOT/'work/translation/en/library_complete.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (ROOT/'work/analysis/library-review.json').write_text(json.dumps(reviews,indent=2)+'\n')
    else:print('DRY RUN: no files written')

if __name__=='__main__':main()
