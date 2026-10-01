"""Translate the two reported SEED Destiny demo captions in shared SRVC data."""
import argparse,json,struct,shutil
from collections import defaultdict
from sp_disc import ROOT,Disc,SOURCE,require,sha
from battle_format import BIN,SEG,native,unique_sources,indexed,blocks
from battle_text import layout,LINE_LIMIT,ROWS
from save_summary_text import width
from menu_encoding import menu_encode
from library_text import text

BASE_BIN_SHA='95129e95924b860addc31ab2a01d209f6131ff21d66089059467ccf59fe3f16f'
BASE_SEG_SHA='db584ccb8d2c122a8851127796694f49ab59dd1a0c7a409a8b2f07cbda8eb8a4'
ENTRIES=(
 (10385,'d26b479d7a93ff43eefb5361127cba58bef5260902fe47df01172965694d4db3',"You're not even that good!",'Shinn'),
 (10946,'bf3b36f8810c02adfba8c630dda4f86293a39e348c41c35ac11841481ed8e9d7','Hyaa-ha-ha-ha!\\nThis is awesome!','Sting'),
)
FOLDER=ROOT/'work/ui/demo-battle-captions'


def build(data,seg, *, caption_entries=ENTRIES, base_bin_sha=BASE_BIN_SHA, base_seg_sha=BASE_SEG_SHA):
    require(sha(data)==base_bin_sha and sha(seg)==base_seg_sha,'Unexpected caption archive identity')
    _,_,_,native_chunks,parsed=native();sources=unique_sources()
    offsets,chunks=blocks(data,seg);changes=defaultdict(dict);entries=[]
    for source_id,digest,value,speaker in caption_entries:
        source=sources[source_id];require(source['source_sha256']==digest,'Caption source identity')
        lines=layout(value);require(lines and len(lines)<=ROWS,'Caption row limit')
        encoded=menu_encode('\\n'.join(lines));spans=list(map(width,lines))
        require(max(spans)<=LINE_LIMIT and len(encoded)+1<=96,'Native minimum caption buffer/layout limit')
        require(text(encoded)=='\\n'.join(lines),'Caption encoding roundtrip')
        for o in source['occurrences']:
            block,record=o['block'],o['record'];p=parsed[block]
            before=indexed(chunks[block],p['index'],len(p['rows']))[record]
            require(before['raw']==p['rows'][record]['raw'] and before['metadata']==o['metadata'],
                    'Reported caption is no longer native')
            changes[block][record]=encoded
        entries.append(dict(id=source_id,speaker=speaker,text=value,lines=lines,line_widths=spans,
            source_sha256=digest,occurrences=source['occurrences'],encoded_bytes=len(encoded)))
    result_chunks=[];result_offsets=[0];patches=[]
    for block,chunk in enumerate(chunks):
        p=parsed[block];replacements=changes.get(block,{})
        if not replacements:
            result_chunks.append(chunk);result_offsets.append(result_offsets[-1]+len(chunk));continue
        before=indexed(chunk,p['index'],len(p['rows']));out=bytearray(chunk)
        if out[-1]:out.append(0)
        for record,value in sorted(replacements.items()):
            target=len(out);out.extend(value+b'\0');at=p['index']+record*8+4
            struct.pack_into('<I',out,at,target-p['pool'])
            patches.append(dict(block=block,record=record,offset_word=at,appended_at=target))
        out.extend(bytes((-len(out))%16));after=indexed(out,p['index'],len(p['rows']))
        restored=bytearray(out[:len(chunk)])
        for record in replacements:
            at=p['index']+record*8+4;restored[at:at+4]=chunk[at:at+4]
        require(restored==chunk,'Unexpected existing block change')
        for a,b in zip(before,after):
            require(a['metadata']==b['metadata'],'Voice metadata changed')
            require(b['raw']==replacements.get(a['record'],a['raw']),'Unexpected caption change')
        result_chunks.append(bytes(out));result_offsets.append(result_offsets[-1]+len(out))
    result=b''.join(result_chunks);result_seg=struct.pack('<%dI'%len(result_offsets),*result_offsets)
    got,check=blocks(result,result_seg);require(list(got)==result_offsets and check==result_chunks,'Container readback')
    return result,result_seg,dict(entries=entries,patches=patches,changed_blocks=sorted(changes),
        translated_occurrences=sum(map(len,changes.values())),indexed_records=59262,
        source_bin_sha256=sha(data),source_seg_sha256=sha(seg),result_bin_sha256=sha(result),
        result_seg_sha256=sha(result_seg),voice_metadata_unchanged=True,
        existing_captions_and_opaque_tails_preserved=True,emulator='pending')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepare',action='store_true')
    p.add_argument('--sting-screenshot',type=type(ROOT))
    p.add_argument('--shinn-screenshot',type=type(ROOT))
    a=p.parse_args()
    disc=Disc(ROOT/'work/output/SRW Z Special Disc English v0.3.3.iso')
    _,_,report=build(disc.read(BIN),disc.read(SEG));print(json.dumps(report,indent=2))
    if a.prepare:
        FOLDER.mkdir(parents=True,exist_ok=True)
        (FOLDER/'build-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        (ROOT/'work/translation/en/demo_battle_captions.json').write_text(json.dumps(dict(version='0.3.4',entries=report['entries']),indent=2)+'\n',encoding='utf-8')
        for label,source in [('sting',a.sting_screenshot),('shinn',a.shinn_screenshot)]:
            dst=FOLDER/(label+'-before.png')
            if source and not dst.exists():shutil.copyfile(source,dst)
    else:print('DRY RUN: no files written')

if __name__=='__main__':main()
