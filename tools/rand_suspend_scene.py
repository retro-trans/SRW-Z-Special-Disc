"""Install the complete Rand/Mel console-care scene in its original text slots."""
import argparse,itertools,json,struct,shutil
from sp_disc import ROOT,SOURCE,Disc,EXE,require,sha,file_sha
from story_layout import px
from story_runtime import apply,convert,NEW_FILE,CODE_BYTES,TABLE_BYTES
from test_story_runtime import execute

BASE_SHA='569af1b96e1ea4a5fae7907417bdde618d61561737bcc59f49dc96929c51cbbf'
REVIEW=ROOT/'work/translation/en/suspend_reviewed.json'
FOLDER=ROOT/'work/ui/rand-suspend-scene'
LIMIT=400
SLOTS=((0x3BE460,128),(0x3BE4E0,112),(0x3BE550,32),(0x3BE570,80),
       (0x3BE5C0,64),(0x3BE600,96),(0x3BE660,96),(0x3BE6C0,48))
TEXTS=(
 "We're Beater Services, the familiar roving repair crew! Known for honest service and our staff's smiles.",
 "Today, we'll give all you players a few tips on getting along with your game consoles.",
 'In a word...!',
 "Love! That's the key to the bond between people and machines!",
 "...Darling. Gunleon seems to be acting up...",
 'Then give the console a full-force chop at a 45-degree angle to the right!',
 "That's what NOT to do. Please take good care of your game consoles, everyone.",
 'Well, see you next time!',
)


def layout(value):
    words=value.split()
    for count in (1,2,3):
        choices=[]
        for cuts in itertools.combinations(range(1,len(words)),count-1):
            bounds=(0,)+cuts+(len(words),)
            lines=[' '.join(words[a:b]) for a,b in zip(bounds,bounds[1:])]
            lines[0]='\u300c'+lines[0];lines[-1]+='\u300d'
            widths=list(map(px,lines))
            if max(widths)<=LIMIT:choices.append((max(widths)-min(widths),lines))
        if choices:return min(choices)[1]
    raise ValueError('Scene text exceeds three rows')


def build(exe):
    require(sha(exe)==BASE_SHA,'Expected v0.3.4 executable')
    native=Disc(SOURCE).read(EXE);review=json.loads(REVIEW.read_text(encoding='utf-8'))
    reviewed={r['id']:r for r in review['entries']};out=bytearray(exe);rows=[]
    checked,_=apply(exe);require(checked==exe,'Story converter must already be installed')
    table=exe[NEW_FILE+CODE_BYTES:NEW_FILE+CODE_BYTES+TABLE_BYTES]
    for i,((at,cap),value) in enumerate(zip(SLOTS,TEXTS),288):
        source=reviewed[i];raw=native[at:native.index(0,at)]
        require(source['offset']==at and source['source_sha256']==sha(raw) and source['meaning_reviewed'],
                'Reviewed source identity')
        require(exe[at:at+cap]==native[at:at+cap] and not any(native[at+len(raw):at+cap]),'Native slot preimage')
        require(len(source['occurrences'])==1 and source['occurrences'][0]['scene']==56,'Scene membership')
        for occurrence in source['occurrences']:
            pos=occurrence['command_offset']
            require(list(struct.unpack_from('<8I',exe,pos))==occurrence['command_words'],'Typed command preimage')
            require(struct.unpack_from('<I',exe,occurrence['pointer_offset'])[0]==at+0xFF680,'Text pointer')
        lines=layout(value);full=source['speaker']+'\n'+'\n'.join(lines);encoded=full.encode('cp932')
        require(len(encoded)+1<=cap and b'$' not in encoded,'Text slot or macro expansion')
        converted=convert(encoded,table)
        require(execute(exe,encoded)==converted,'Installed converter execution differs')
        # Audited message allocation is 464 bytes, with text beginning at +12.
        require(len(converted)+1<=452 and max(map(len,converted.split(b'\n')))<=256,
                'Message allocation or line-parser bound')
        require(converted.count(b'\n')==len(lines),'Converter changed row count')
        out[at:at+cap]=encoded+bytes(cap-len(encoded))
        require(out[at:out.index(0,at)].decode('cp932')==full,'Installed text readback')
        rows.append(dict(id=i,offset=at,capacity=cap,speaker=source['speaker'],text=value,lines=lines,
            line_widths=list(map(px,lines)),encoded_bytes=len(encoded)+1,converted_bytes=len(converted)+1,
            source_sha256=source['source_sha256'],reviewed_text=source['text'],
            pointer_offsets=[o['pointer_offset'] for o in source['occurrences']]))
    restored=bytearray(out)
    for at,cap in SLOTS:restored[at:at+cap]=exe[at:at+cap]
    require(restored==exe,'Change outside selected text slots')
    return bytes(out),dict(scene=56,entries=rows,review_sha256=file_sha(REVIEW),
        source_executable_sha256=sha(exe),result_executable_sha256=sha(out),line_limit=LIMIT,
        unchanged_commands_pointers_portraits_and_timing=True,emulator='pending')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepare',action='store_true')
    p.add_argument('--screenshot',type=type(ROOT))
    a=p.parse_args()
    exe=Disc(ROOT/'work/output/SRW Z Special Disc English v0.3.4.iso').read(EXE)
    _,report=build(exe);print(json.dumps(report,indent=2))
    if a.prepare:
        FOLDER.mkdir(parents=True,exist_ok=True)
        (FOLDER/'build-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        (ROOT/'work/translation/en/rand_suspend_scene.json').write_text(json.dumps(dict(version='0.3.5',entries=report['entries']),indent=2)+'\n',encoding='utf-8')
        if a.screenshot and not (FOLDER/'user-before.png').exists():
            shutil.copyfile(a.screenshot,FOLDER/'user-before.png')
    else:print('DRY RUN: no files written')

if __name__=='__main__':main()
